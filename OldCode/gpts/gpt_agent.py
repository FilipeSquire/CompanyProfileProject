import os, textwrap
import io

from typing import List, Dict, Optional
from xml.sax.saxutils import escape

from gpts.gpt_assistants import general_assistant
from dotenv import load_dotenv, find_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.core.exceptions import HttpResponseError
from azure.search.documents.models import HybridSearch


from openai import AzureOpenAI, APIConnectionError, OpenAI
from prompts import new_system_finance_prompt

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from prompts4 import system_mod, finance_calculations, finance_pairs, capital_pairs, stakeholders_pairs, biz_overview_pairs, revenue_pairs, default_gpt_prompt, section4a, section4b, section5, section3, biz_overview_web, stakeholders_web
from pages.design.func_tools import *
from pages.design.formatting import *
from pages.design.func_tools import docx_bytes_to_pdf_bytes
import re, time
 
# load_dotenv(find_dotenv(), override=True)

# ---- Config (expects the same envs you already used) ----
SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_INDEX    = os.environ["AZURE_SEARCH_INDEX"]
SEARCH_KEY      = os.getenv("AZURE_SEARCH_API_KEY")  # omit if using AAD/RBAC
VECTOR_FIELD    = os.getenv("VECTOR_FIELD")
TEXT_FIELD      = os.getenv("TEXT_FIELD")

AOAI_ENDPOINT   = os.environ["AZURE_OPENAI_ENDPOINT"]            # https://<resource>.openai.azure.com
AOAI_API_VER    = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21")
AOAI_DEPLOYMENT = os.environ["AZURE_OPENAI_DEPLOYMENT"]          # e.g., gpt-4o-mini / o3-mini / gpt-5 preview
AOAI_KEY        = os.getenv("AZURE_OPENAI_API_KEY")              # omit if using AAD
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")        # required

# ------------------ CODE

class profileAgent():

    """Hybrid (dense+sparse) RAG over Vector Store

    This Agent is responsible for creating Company Profiles. 
    It operates with gpt5.
    It is activated by a call on main rag when it is typed 'Create company profile'
    """

    def __init__(self, company_name, k, max_text_recall_size, max_chars, model, profile_prompt = system_mod, finance_calculations = finance_calculations):
        
        self.company_name = company_name

        self.k = k
        self.max_text_recall_size = max_text_recall_size
        self.model = model
        self.max_chars = max_chars

        self.azure_credentials = AzureKeyCredential(SEARCH_KEY) if SEARCH_KEY else DefaultAzureCredential()
        self.search_client = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, credential=self.azure_credentials)

        self.az_openai = AzureOpenAI(azure_endpoint=AOAI_ENDPOINT, api_key=AOAI_KEY, api_version=AOAI_API_VER)
        self.profile_prompt = profile_prompt
        self.web_openai = OpenAI(api_key=OPENAI_API_KEY)

        self.reasoning_effort = "medium"
        self.verbosity = "medium"

        self.finance_calculations = finance_calculations

    def _company_filter(self) -> str:
        v = (self.company_name or "").replace("'", "''").strip()
        return f"company_name eq '{v}'" if v else None
    
    def assemble_bm25_from_llm(self, slots: dict) -> str:
        def q(s: str) -> str:
            # sanitize: remove internal quotes and trim
            s = (s or "").strip().replace('"', ' ')
            return f"\"{s}\"" if s else ""
        groups = []

        # must-have phrases (ANDed)
        for p in slots.get("must_have_phrases", []):
            qp = q(p)
            if qp:
                groups.append(qp)

        # metric / statement synonym groups (ORed within each group)
        for key in ["metric", "statement"]:
            syns = slots.get("synonyms", {}).get(key, []) or slots.get(key, [])
            syns = [q(s) for s in syns if s]
            if syns:
                groups.append("(" + " OR ".join(syns) + ")")

        return " AND ".join(groups) if groups else "\"financial statements\""


    def bm25_creator(self, prompt):

        instruction = (
            "Extract finance search slots for Azure AI Search. "
            "Return strict JSON: {\"metric\":[], \"statement\":[], \"synonyms\":{}, \"must_have_phrases\":[]} "
            "(include IFRS/US GAAP variants)."
        )
        resp = general_assistant(instruction, prompt, OPENAI_API_KEY, 'gpt-4o')

        try:
            slots = getattr(resp, "output_json", None)
            if slots is None:
                import json
                slots = json.loads(resp.output_text)
        except Exception:
            # fallback: minimal anchors from prompt
            slots = {"must_have_phrases": [prompt], "metric": [], "statement": [], "synonyms": {}}
        return self.assemble_bm25_from_llm(slots)

    def _retrieve_hybrid_enhanced(self, query_nl, k: int = 50, top_n = 30, fields=VECTOR_FIELD, max_text_recall_size:int = 800):
        sc = self.search_client
        flt = self._company_filter()
        
        try:
            vq = VectorizableTextQuery(text=query_nl, k=k, fields=VECTOR_FIELD)
            # Prefer vector-only search (integrated vectorization). If your index isn't set up for it, this raises.
            results = sc.search(
                search_text=self.bm25_creator(query_nl), 
                vector_queries=[vq], 
                top=top_n, 
                query_type="semantic",
                query_caption="extractive", 
                hybrid_search=HybridSearch(max_text_recall_size=self.max_text_recall_size),
                query_caption_highlight_enabled=True,
                filter=flt
                )
            mode = "hybrid + semantic"
        except HttpResponseError as e:
            # Fall back to lexical so you still get results while fixing vector config
            results = sc.search(search_text=self.bm25_creator(query_nl), top=k)
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


    def _build_context(self, hits: List[Dict], text_field: str = TEXT_FIELD, max_chars: int = 20000):
        """Build a compact, numbered context block and also return the selected chunk metadata."""
        lines = []
        total = 0
        selected = []  # <- we'll return this

        for i, h in enumerate(hits, 1):
            title     = h.get("title")
            chunk_id  = h.get("chunk_id")
            full_text = (h.get(text_field) or "")
            if not full_text:
                continue

            preview = textwrap.shorten(full_text, width=700, placeholder=" ...")
            block = f"[{i}] title={title!r} | chunk_id={chunk_id} | score={h.get('score'):.4f}\n{full_text}"

            if total + len(block) > self.max_chars:
                break

            total += len(block)
            lines.append(block)

            # keep rich metadata so you can show or log it later
            selected.append({
                "i": i,
                "title": title,
                "chunk_id": chunk_id,
                "score": h.get("score"),
                "caption": h.get("caption"),
                "preview": preview,
                "text": full_text,  # full chunk text (not shortened)
                # include any other fields you index, if available:
                "metadata_storage_path": h.get("metadata_storage_path"),
                "page_number": h.get("page_number"),
                "doc_type": h.get("doc_type"),
            })

        return "\n\n---\n\n".join(lines), selected

        
    def _generate_pdf(self, text: str) -> bytes:

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter)
        styles = getSampleStyleSheet()
        body = styles["BodyText"]

        story = []
        # Treat double newlines as paragraph breaks; keep single newlines as <br/>
        for para in (text or "").split("\n\n"):
            safe = escape(para).replace("\n", "<br/>")
            story.append(Paragraph(safe if safe.strip() else "&nbsp;", body))
            story.append(Spacer(1, 8))

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()
    
    def _extract_cited_idxs(self, answer: str) -> list[int]:
        # Matches [#1], [#12], etc. (also tolerates stray [1])
        nums = set(int(n) for n in re.findall(r"\[#?(\d+)\]", answer))
        return sorted(nums)

    def _rag_answer(self, rag_nl, question, k: int = 5, temperature: float = 0.2):

        # question = f'CREATE A SECTION OF COMPANY PROFILE USING LAST YEARS OF ANNUAL REPORT PRESENT IN THE CONTEXT FOR {self.company_name}. IF ANY INFORMATION IS NOT FOUND STATE AS n.a. .\n\n THIS IS THE SECTION TO BE BUILT: \n {section7}  \n USE THIS TO GUIDE YOURSELF ON SEMANTIC TERMS AND HOW TO CALCULATE: \n {finance_calculations}'
        
        mode, hits = self._retrieve_hybrid_enhanced(
            # query=rag_q, 
            query_nl=rag_nl,
            k=25
            )
        ctx_text, ctx_items = self._build_context(hits)

        system_msg = self.profile_prompt + (
            "\nWhen you use a fact from the context, add citations like [#1], [#2]."
            "\nOnly rely on the numbered context; if a value is missing, say 'n.a.'."
            f"\nIF ANY INFORMATION IS NOT FOUND STATE AS n.a. .\n\n USE THIS TO GUIDE YOURSELF ON SEMANTIC TERMS AND HOW TO CALCULATE: \n {finance_calculations}"
        )
        user_msg = f"Question:\n{question}\n\nContext snippets (numbered):\n{ctx_text}"

        client = self.az_openai
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ]

        # Try streaming first (SSE). Some networks/proxies block streaming; if so, fall back.
        
        resp = client.chat.completions.create(
            model=AOAI_DEPLOYMENT,
            messages=messages,
            reasoning_effort="high"
        )
        answer = resp.choices[0].message.content
        mode_model = "non-streaming (fallback)"

        cited = self._extract_cited_idxs(answer)
        used_chunks = [c for c in ctx_items if c["i"] in cited]

        # return self._generate_pdf(answer)
        return {
            "answer": answer,
            "citations": cited,          # [1, 3, 7]
            "used_chunks": used_chunks,  # detailed dicts for each cited snippet
            "all_chunks": ctx_items,     # everything you sent (optional)
            "mode": mode                 # retrieval mode info (optional)
        }

    def _web_search(self, messages):
        resp = self.web_openai.responses.create(
            model='gpt-5',
            input=messages,
            tools=[{"type": "web_search"}],
            tool_choice="auto",
            # max_output_tokens=self.max_output_tokens,
            reasoning={"effort": self.reasoning_effort},
            text={"verbosity": self.verbosity},
        )
        
        return resp.output_text
    
    def _answer(self, question, ctx_text, k: int = 5, temperature: float = 0.2):

        system_msg = self.profile_prompt + (
            "\nWhen you use a fact from the context, preserve any existing citations like [#1], [#2], [#5, p.41] that are already in the context text."
            "\nOnly rely on the provided context; if a value is missing, say 'n.a.'."
            "\nIMPORTANT: If the formatting instructions request a Sources section, you MUST include it at the end."
            "\nFor the Sources section, list all citation numbers/references that appear in your answer, and describe what document/source each refers to based on information in the context."
        )
        user_msg = f"Question:\n{question}\n\nContext snippets:\n{ctx_text}"

        client = self.az_openai
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ]

        # Try streaming first (SSE). Some networks/proxies block streaming; if so, fall back.

        resp = client.chat.completions.create(
            model=AOAI_DEPLOYMENT,
            messages=messages,
            reasoning_effort="high"
        )
        answer = resp.choices[0].message.content

        cited = self._extract_cited_idxs(answer)

        # return self._generate_pdf(answer)
        return {
            "answer": answer,
            "citations": cited,          # [1, 3, 7]
        }   
    
    @staticmethod
    def has_na(text: str) -> bool:
        # match "n.a." or "n/a" (case-insensitive)
        return bool(re.search(r"\b(n\.a\.|n/a)\b", text, flags=re.I))

    def _sections(self, pairs):

        answers = []

        max_extra_na_retries = 1        # try again at most 2 times (total <= 3 calls per item)
        base_delay_seconds = 3.0        # polite delay between attempts


        for q, r in pairs:
            tries = 0
            while True:
                if tries > 0:
                    # small incremental delay before re-trying
                    time.sleep(base_delay_seconds + 0.5 * tries)

                resp = self._rag_answer(rag_nl=r[0], question=q[0])
                answer_text = resp["answer"]

                # stop if good answer OR we've exhausted retries
                if not profileAgent.has_na(answer_text) or tries >= max_extra_na_retries:
                    answers.append(answer_text)
                    break

                # otherwise, try again
                tries += 1

            # optional small gap between different (r,q) items
            time.sleep(5.0)
        
        return answers
    
    def _generate_section(self, section):

        if section == 'GENERATE BUSINESS OVERVIEW':
            # =========== GENERATE BUSINESS OVERVIEW
            biz_overview_pairs_flat = list(zip(biz_overview_pairs[1], biz_overview_pairs[0]))  # [(r, q), (r, q), ...]
            section_built = self._sections(pairs = biz_overview_pairs_flat)

            #getting web search sections
            new_section = f'All instructions applies to the company: {self.company_name}\n\n{biz_overview_web} \n\n Mention in the Beggining of the answer that this is WEBSEARCH SOURCE'
            messages = [
                {"role": "system", "content": default_gpt_prompt},
                {"role": "user",   "content": new_section},
            ]
            resp_web = self._web_search(messages)

            section_built.append(resp_web)

            # Join all context sections - they already contain their own citations
            # Just concatenate them so the model can synthesize
            ctx_text_formatted = "\n\n".join(section_built)

            resp = self._answer(question=biz_overview_mix_formatting, ctx_text=ctx_text_formatted)
            return resp['answer']
        elif section == 'GENERATE KEY STAKEHOLDERS':
        # =========== GENERATE KEY STAKEHOLDERS
            stakeholders_pairs_flat = list(zip(stakeholders_pairs[1], stakeholders_pairs[0]))  # [(r, q), (r, q), ...]
            section_built = self._sections(pairs= stakeholders_pairs_flat)

            #getting web search sections
            new_section = f'All instructions applies to the company: {self.company_name}\n\n{stakeholders_web} \n\n Mention in the Beggining of the answer that this is WEBSEARCH SOURCE'
            messages = [
                {"role": "system", "content": default_gpt_prompt},
                {"role": "user",   "content": new_section},
            ]
            resp_web = self._web_search(messages)

            section_built.append(resp_web)

            # Join all context sections - they already contain their own citations
            # Just concatenate them so the model can synthesize
            ctx_text_formatted = "\n\n".join(section_built)

            resp = self._answer(question=stakeholders_web_mix, ctx_text=section_built)
            return resp['answer']
        elif section == 'GENERATE FINANCIAL HIGHLIGHTS':
            # =========== GENERATE FINANCIAL HIGHLIGHTS
            finance_pairs_flat = list(zip(finance_pairs[1], finance_pairs[0]))  # [(r, q), (r, q), ...]
            section_built = self._sections(pairs=finance_pairs_flat)
            resp = self._answer(question=finance_formatting_2, ctx_text=section_built)
            return resp['answer']
        elif section == 'GENERATE CAPITAL STRUCTURE':
            # =========== GENERATE CAPITAL STRUCTURE
            capital_pairs_flat = list(zip(capital_pairs[1], capital_pairs[0]))  # [(r, q), (r, q), ...]
            section_built = self._sections(pairs= capital_pairs_flat)
            resp = self._answer(question=capital_structure_formatting_2, ctx_text=section_built)
            return resp['answer']
        elif section == 'GENERATE REVENUE SPLIT':
            # =========== GENERATE CAPITAL STRUCTURE
            revenue_pairs_flat = list(zip(revenue_pairs[1], revenue_pairs[0]))  # [(r, q), (r, q), ...]
            section_built = self._sections(pairs= revenue_pairs_flat)
            resp = self._answer(question=section3, ctx_text=section_built)
            return resp['answer']
        elif section == 'GENERATE PRODUCTS SERVICES OVERVIEW':
            # =========== GENERATE CAPITAL STRUCTURE
            new_section = f'All instructions applies to the company: {self.company_name}\n\n{section4a}'
            messages = [
                {"role": "system", "content": default_gpt_prompt},
                {"role": "user",   "content": new_section},
            ]
            resp = self._web_search(messages)
            return resp 
        elif section == 'GENERATE GEO FOOTPRINT':
            # =========== GENERATE CAPITAL STRUCTURE
            new_section = f'All instructions applies to the company: {self.company_name}\n\n{section4b}'
            messages = [
                {"role": "system", "content": default_gpt_prompt},
                {"role": "user",   "content": new_section},
            ]
            resp = self._web_search(messages)
            return resp
        elif section == 'GENERATE DEVELOPMENTS HIGHLIGHTS':
            # =========== GENERATE CAPITAL STRUCTURE
            new_section = f'All instructions applies to the company: {self.company_name}\n\n{section5}'
            messages = [
                {"role": "system", "content": default_gpt_prompt},
                {"role": "user",   "content": new_section},
            ]
            resp = self._web_search(messages)
            return resp


    def generate_company_profile(self):

        # =========== GENERATE BUSINESS OVERVIEW
        biz_overview_pairs_flat = list(zip(biz_overview_pairs[1], biz_overview_pairs[0]))  # [(r, q), (r, q), ...]
        section1 = self._sections(pairs = biz_overview_pairs_flat)
        resp = self._answer(question=business_overview_formatting, ctx_text=section1)
        doc = insert_biz_overview(resp['answer'])

        time.sleep(60)
        # =========== GENERATE KEY STAKEHOLDERS
        stakeholders_pairs_flat = list(zip(stakeholders_pairs[1], stakeholders_pairs[0]))  # [(r, q), (r, q), ...]
        section2 = self._sections(pairs= stakeholders_pairs_flat)
        resp = self._answer(question=stakeholders_formatting, ctx_text=section2)
        doc = insert_stakeholders(resp['answer'], doc=doc)
        
        time.sleep(60)
        # =========== GENERATE FINANCIAL HIGHLIGHTS
        finance_pairs_flat = list(zip(finance_pairs[1], finance_pairs[0]))  # [(r, q), (r, q), ...]
        section3 = self._sections(pairs=finance_pairs_flat)
        resp = self._answer(question=finance_formatting, ctx_text=section3)
        doc = insert_finance(resp['answer'], doc=doc)

        time.sleep(60)
        # =========== GENERATE CAPITAL STRUCTURE
        capital_pairs_flat = list(zip(capital_pairs[1], capital_pairs[0]))  # [(r, q), (r, q), ...]
        section4 = self._sections(pairs= capital_pairs_flat)
        resp = self._answer(question=capital_structure_formatting_2, ctx_text=section4)
        doc = insert_capital_structure(resp['answer'], doc=doc)

        pdf_bytes = docx_bytes_to_pdf_bytes(doc)

        return pdf_bytes
        # =========== UNION
