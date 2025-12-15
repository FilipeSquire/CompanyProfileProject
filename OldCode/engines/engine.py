import io
import time
import uuid
import base64
import binascii
from typing import Any, Iterable, List, Optional, Tuple, Dict

try:
    import pysqlite3  # bundled modern sqlite
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except Exception:
    pass

from dotenv import  load_dotenv
from unstructured.partition.pdf import partition_pdf

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser

from langchain_community.vectorstores import Chroma
from langchain.storage import InMemoryStore
from langchain_core.documents import Document
from langchain.retrievers.multi_vector import MultiVectorRetriever

from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import SystemMessage, HumanMessage

from engines.prompts import system_finance_prompt


load_dotenv()



class HybridEngine:
    """Hybrid (dense+sparse) RAG over multi-PDF corpus — optimized.

    Speed-ups:
    - Idempotent build via `_built` guard.
    - Faster partition: keep OCR, disable heavy table structure inference.
    - Summarize only *long* chunks; embed short chunks directly (no LLM call).
    - Lower retrieval fanout (k) and cap images included in prompt.
    - Concurrency for LLM summarization.
    - Stage timings exposed in `self.timings`.
    """

    def __init__(self, pdfs: Optional[Iterable[Tuple[io.BytesIO, str]]] = None) -> None:
        # Inputs
        self._files: List[Tuple[io.BytesIO, str]] = []
        self._built: bool = False
        self.timings: Dict[str, float] = {}

        # Extracted elements
        self.chunks: Optional[List[Any]] = None
        self.tables: List[Any] = []
        self.texts: List[Any] = []
        self.images: List[Any] = []
        self.table_sources: List[str] = []
        self.text_sources: List[str] = []
        self.image_sources: List[str] = []


        # Vector & store
        self.vectorstore = Chroma(collection_name="multi_modal_rag", embedding_function=OpenAIEmbeddings())
        self.store = InMemoryStore()
        self.id_key = "doc_id"
        self.dense_retriever = MultiVectorRetriever(
            vectorstore=self.vectorstore,
            docstore=self.store,
            id_key=self.id_key,
            search_kwargs={"k": 16},  # changed from 12 to 16
        )

        # Retrievers & chains
        self.hybrid = None
      

        if pdfs:
            for f_like, name in pdfs:
                self.add_file(f_like, name)

    def add_file(self, file_like: io.BytesIO, name: str) -> None:
        try:
            file_like.seek(0)
        except Exception:
            pass
        self._files.append((file_like, name))

    def _unstructured(self) -> None:
        t0 = time.perf_counter()
        all_chunks: List[Any] = []
        tables, texts, images = [], [], []
        t_src, x_src, i_src = [], [], []

        for f_like, fname in self._files:
            f_like.seek(0)
            chunks = partition_pdf(
                file=f_like,
                infer_table_structure=False,   
                strategy="hi_res",             
                extract_image_block_types=["Image"],
                extract_image_block_to_payload=True,
                chunking_strategy="by_title",
                max_characters=6000,
                combine_text_under_n_chars=1500,
                new_after_n_chars=4000,
            )
            all_chunks.extend(chunks)

            for chunk in chunks:
                if hasattr(chunk, "metadata") and getattr(chunk.metadata, "orig_elements", None):
                    for el in chunk.metadata.orig_elements:
                        t = str(type(el))
                        if "Table" in t:
                            tables.append(el); t_src.append(fname)
                        elif "Image" in t:
                            images.append(el); i_src.append(fname)
                        else:
                            texts.append(el); x_src.append(fname)

        self.chunks = all_chunks
        self.tables, self.texts, self.images = tables, texts, images
        self.table_sources, self.text_sources, self.image_sources = t_src, x_src, i_src
        self.timings["unstructured_s"] = time.perf_counter() - t0
        print(f"Finished unstructured — texts={len(texts)} tables={len(tables)} images={len(images)}")

    def _el_text(self, el: Any) -> str:
        if hasattr(el, "to_text"):
            return el.to_text()
        return getattr(el, "text", str(el)) or "" 
#    part above changed<<<<

    def _store_load(self) -> None:
        t0 = time.perf_counter()
        # Texts → vector + parents
        text_ids = [str(uuid.uuid4()) for _ in self.texts]

        child_text_docs = [
            Document(
            page_content=self._el_text(el),
            metadata={self.id_key: text_ids[i], "source": self.text_sources[i], "type": "text"}
            )
            for i, el in enumerate(self.texts)
        ]
        if child_text_docs:
            print("\n[DEBUG] Adding text docs:")
            for d in child_text_docs[:5]:
                print(repr(d.page_content))
            self.dense_retriever.vectorstore.add_documents(child_text_docs)
       

        parent_text_docs = [
            Document(page_content=self._el_text(el), metadata={"source": self.text_sources[i], "type": "text"})
            for i, el in enumerate(self.texts)
        ]
        if parent_text_docs:
            self.dense_retriever.docstore.mset(list(zip(text_ids, parent_text_docs)))

        # Tables → vector + parents
        table_ids = [str(uuid.uuid4()) for _ in self.tables]
        # Children: raw table chunks → vectorstore (each points to its parent via id_key)
        child_table_docs = [
            Document(
                page_content=self._el_text(el),
                metadata={self.id_key: table_ids[i], "source": self.table_sources[i], "type": "table"}
                )
                for i, el in enumerate(self.tables)
                ]
        if child_table_docs:
            print("\n[DEBUG] Adding table docs:")
            for d in child_table_docs[:5]:
                print(repr(d.page_content))
            self.dense_retriever.vectorstore.add_documents(child_table_docs)
        

       

        parent_table_docs = [
            Document(page_content=self._el_text(el), metadata={"source": self.table_sources[i], "type": "table"})
            for i, el in enumerate(self.tables)
        ]
        if parent_table_docs:
            self.dense_retriever.docstore.mset(list(zip(table_ids, parent_table_docs)))

        # Images → parents only (cap stored count if huge)
        image_ids = [str(uuid.uuid4()) for _ in self.images]
        parent_image_docs: List[Document] = []
        for i, el in enumerate(self.images):
            b64 = getattr(el, "payload", None) or getattr(el, "data", None) or ""
            if not isinstance(b64, str):
                b64 = str(b64)
            parent_image_docs.append(Document(page_content=b64, metadata={"source": self.image_sources[i], "type": "image"}))
        if parent_image_docs:
            self.dense_retriever.docstore.mset(list(zip(image_ids, parent_image_docs)))

        self.timings["store_load_s"] = time.perf_counter() - t0
        print("Finished store load")


    # --- in HybridEngine._hydra ---
    def _hydra(self) -> None:
        t0 = time.perf_counter()

        # Pull parents from the docstore
        keys = list(self.store.yield_keys())
        raw_items = self.store.mget(keys) if keys else []

        parent_docs: List[Document] = []
        for item in raw_items:
            if not item:
                continue
            parent_docs.append(item if isinstance(item, Document)
                            else Document(page_content=str(item)))

        if parent_docs:
            # BM25 needs at least 1 document; try from_documents and fall back to from_texts for older versions
            try:
                bm25 = BM25Retriever.from_documents(parent_docs)
            except Exception:
                bm25 = BM25Retriever.from_texts(
                    [d.page_content for d in parent_docs],
                    metadatas=[getattr(d, "metadata", {}) for d in parent_docs],
                )
            bm25.k = 16 #changed from 12 to 24
            self.hybrid = EnsembleRetriever(retrievers=[bm25, self.dense_retriever], weights=[0.3, 0.7])
        else:
            # Nothing indexed → fall back to dense retriever only
            self.hybrid = self.dense_retriever

        self.timings["retriever_build_s"] = time.perf_counter() - t0
        print(f"Finished hydra — parents={len(parent_docs)}")


    # ---------------------------- RAG PIPE ---------------------------------
    def _looks_like_b64(self, s: str) -> bool:
        if not isinstance(s, str) or len(s) < 40:
            return False
        try:
            base64.b64decode(s, validate=True)
            return True
        except binascii.Error:
            return False

    def _to_str(self, obj) -> str:
        if isinstance(obj, str):
            return obj
        if hasattr(obj, "page_content"):
            return obj.page_content
        if hasattr(obj, "text"):
            return obj.text
        return str(obj)

    def _parse_docs(self, docs):
        images, texts = [], []
        for d in docs:
            payload = self._to_str(d)
            (images if self._looks_like_b64(payload) else texts).append(payload)
        return {"images": images[:6], "texts": texts}  # cap images in prompt

    def _build_prompt_two(self, kwargs) -> ChatPromptTemplate:
        ctx = kwargs["context"]; question = kwargs["question"]
        parts = [{"type": "text", "text": f"Context:{ctx.get('texts', [])[:6]}Question: {question}"}]
        for b64 in ctx.get("images", [])[:6]:
            parts.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})
        messages = [SystemMessage(content=system_finance_prompt), HumanMessage(content=parts)]
        return ChatPromptTemplate.from_messages(messages)



    # ------------------------- outputs ------------------------------------
    def _generate_pdf(self, text: str) -> bytes:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter)
        styles = getSampleStyleSheet()
        body = styles["BodyText"]
        story = []
        for line in (text or "").splitlines():
            story.append(Paragraph(line or " ", body))
            story.append(Spacer(1, 4))
        doc.build(story)
        buf.seek(0)
        return buf.read()


    def main(self) -> None:
        if self._built:
            return
        self._unstructured()
        self._store_load()
        self._hydra()
        self._built = True
        print("Finished pipeline")