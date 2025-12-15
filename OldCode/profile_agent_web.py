import os, textwrap
import io
from typing import List, Dict, Optional
from xml.sax.saxutils import escape

from dotenv import load_dotenv, find_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.core.exceptions import HttpResponseError
from azure.search.documents.models import HybridSearch

# 🔁 OpenAI (standard) SDK — Responses API
from openai import OpenAI, APIConnectionError

from prompts import finance_prompt_web

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

load_dotenv(find_dotenv(), override=True)

# ---- Config (same Azure Search envs you already use) ----
SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_INDEX    = os.environ["AZURE_SEARCH_INDEX"]
SEARCH_KEY      = os.getenv("AZURE_SEARCH_API_KEY")  # omit if using AAD/RBAC
VECTOR_FIELD    = os.getenv("VECTOR_FIELD")
TEXT_FIELD      = os.getenv("TEXT_FIELD")

# ---- OpenAI (standard) config ----
OPENAI_API_KEY  = os.getenv("FELIPE_OPENAI_API_KEY")        # required
OPENAI_MODEL    = os.getenv("FELIPE_OPENAI_MODEL", "gpt-5")  # e.g., "gpt-5" or "gpt-5-mini"

# ------------------ CODE

class profileAgentWeb():
    """
    Hybrid (dense+sparse) RAG over Azure AI Search.
    Generates Company Profiles with OpenAI GPT-5 (Responses API).
    Activated by 'Create company profile'.
    """

    def __init__(
        self,
        company_name: str,
        k: int,
        max_text_recall_size: int,
        max_chars: int,
        model: Optional[str] = None,
        *,
        # 🧠 GPT-5 tunables (defaults are sensible; override per call if you like)
        # temperature: float = 0.2,
        # top_p: float = 1.0,
        max_output_tokens: int = 1200,
        reasoning_effort: str = "medium",      # "minimal" | "low" | "medium" | "high"
        verbosity: str = "medium",                 # "low" | "medium" | "high"
        enable_web_search: bool = True,        # keep OFF by default to honor RAG "use only context"
        tool_choice: str = "none",              # "none" | "auto" | {"type":"tool","name":"..."}
        streaming: bool = False,
        profile_prompt = finance_prompt_web
    ):
        self.company_name = company_name
        self.k = k
        self.max_text_recall_size = max_text_recall_size
        self.max_chars = max_chars

        # LLM settings
        self.model = model or OPENAI_MODEL
        # self.temperature = temperature
        # self.top_p = top_p
        self.max_output_tokens = max_output_tokens
        self.reasoning_effort = reasoning_effort
        self.verbosity = verbosity
        self.enable_web_search = enable_web_search
        self.tool_choice = tool_choice
        self.streaming = streaming

        self.profile_prompt = profile_prompt

        # Azure Search (unchanged)
        self.azure_credentials = AzureKeyCredential(SEARCH_KEY) if SEARCH_KEY else DefaultAzureCredential()
        self.search_client = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, credential=self.azure_credentials)

        # OpenAI standard client
        self.web_openai = OpenAI(api_key=OPENAI_API_KEY)

    def _retrieve_hybrid_enhanced(self, query: str, k: int = 10, max_text_recall_size:int = 200):
        sc = self.search_client
        try:
            vq = VectorizableTextQuery(text=query, k=k, fields=VECTOR_FIELD)
            results = sc.search(
                search_text=query,
                vector_queries=[vq],
                top=self.k,
                query_type="semantic",
                query_caption="extractive",
                hybrid_search=HybridSearch(max_text_recall_size=self.max_text_recall_size),
                query_caption_highlight_enabled=True,
            )
            mode = "hybrid + semantic"
        except HttpResponseError as e:
            results = sc.search(search_text=query, top=k)
            mode = f"lexical (fallback due to: {e.__class__.__name__})"

        hits: List[Dict] = []
        for r in results:
            d = r.copy() if hasattr(r, "copy") else {k2: r[k2] for k2 in r}
            d["score"] = d.get("@search.reranker_score") or d.get("@search.score") or 0.0
            caps = d.get("@search.captions")
            if isinstance(caps, list) and caps:
                d["caption"] = getattr(caps[0], "text", None)
            hits.append(d)
        return mode, hits

    def _build_context(self, hits: List[Dict], text_field: str = TEXT_FIELD, max_chars: int = 20000) -> str:
        """Build a compact, numbered context block to feed the model."""
        lines = []
        total = 0
        for i, h in enumerate(hits, 1):
            title     = h.get("title")
            chunk_id  = h.get("chunk_id")
            snippet   = (h.get(text_field) or "")
            if not snippet:
                continue
            snippet = textwrap.shorten(snippet, width=700, placeholder=" ...")
            block = f"[{i}] title={title!r} | chunk_id={chunk_id} | score={h.get('score'):.4f}\n{snippet}"
            if total + len(block) > self.max_chars:
                break
            total += len(block)
            lines.append(block)
        return "\n\n---\n\n".join(lines)

    def _generate_pdf(self, text: str) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter)
        styles = getSampleStyleSheet()
        body = styles["BodyText"]
        story = []
        for para in (text or "").split("\n\n"):
            safe = escape(para).replace("\n", "<br/>")
            story.append(Paragraph(safe if safe.strip() else "&nbsp;", body))
            story.append(Spacer(1, 8))
        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

    def _rag_answer(self, k: int = 5):
        question = f"Create the company profile of {self.company_name}. USE ONLY the information from latest annual report."

        mode, hits = self._retrieve_hybrid_enhanced(question, k=k)
        ctx = self._build_context(hits)

        system_msg = self.profile_prompt
        user_msg = f"Question:\n{question}\n\nContext snippets (numbered):\n{ctx}"

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ]

        # 🧰 Tools (optional web search). Keep OFF by default to honor RAG purity.
        tools = [{"type": "web_search"}] if self.enable_web_search else []

        try:
            resp = self.web_openai.responses.create(
                model=self.model,
                input=messages,
                tools=tools if tools else None,
                tool_choice=self.tool_choice if tools else "none",
                # temperature=self.temperature,
                # top_p=self.top_p,
                max_output_tokens=self.max_output_tokens,
                reasoning={"effort": self.reasoning_effort},
                text={"verbosity": self.verbosity},
            )
            answer_text = resp.output_text

            # (Optional) Collect URL citations if web search was used
            if tools:
                urls = set()
                for item in getattr(resp, "output", []) or []:
                    if getattr(item, "type", "") == "message":
                        for c in getattr(item, "content", []) or []:
                            for ann in getattr(c, "annotations", []) or []:
                                if getattr(ann, "type", "") == "url_citation" and getattr(ann, "url", None):
                                    urls.add(ann.url)
                if urls:
                    answer_text += "\n\nSources (web):\n" + "\n".join(f"- {u}" for u in urls)

        except APIConnectionError as e:
            answer_text = f"Connection error calling OpenAI: {e}"

        return self._generate_pdf(answer_text)
