# ADD AT TOP OF FILE (needed once)
import json
from typing import Tuple
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

from openai import AzureOpenAI, APIConnectionError
from prompts import new_system_finance_prompt

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from prompts4 import section2_json, section6_json, section7_json, section8_json
load_dotenv(find_dotenv(), override=True)

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

class profileAgent():

    """Hybrid (dense+sparse) RAG over Vector Store

    This Agent is responsible for creating Company Profiles. 
    It operates with gpt5.
    It is activated by a call on main rag when it is typed 'Create company profile'
    """

    def __init__(self, company_name, k, max_text_recall_size, max_chars, model, profile_prompt = new_system_finance_prompt):
        self.company_name = company_name

        self.k = k
        self.max_text_recall_size = max_text_recall_size
        self.model = model
        self.max_chars = max_chars

        self.azure_credentials = AzureKeyCredential(SEARCH_KEY) if SEARCH_KEY else DefaultAzureCredential()
        self.search_client = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, credential=self.azure_credentials)

        self.az_openai = AzureOpenAI(azure_endpoint=AOAI_ENDPOINT, api_key=AOAI_KEY, api_version=AOAI_API_VER)
        self.profile_prompt = profile_prompt

    # NEW: company_name -> OData filter (the *only* filter you requested)
    def _company_filter(self) -> str:
        v = (self.company_name or "").replace("'", "''").strip()
        return f"company_name eq '{v}'" if v else None

    # MODIFIED: pass filter=self._company_filter() into Azure Search calls
    def _retrieve_hybrid_enhanced(self, query: str, k: int = 10, fields=VECTOR_FIELD, max_text_recall_size:int = 200):
        sc = self.search_client
        flt = self._company_filter()  # << only filter we use
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
                filter=flt,                                    # << APPLY FILTER
            )
            mode = "hybrid + semantic"
        except HttpResponseError as e:
            results = sc.search(search_text=query, top=k, filter=flt)  # << APPLY FILTER IN FALLBACK
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

    # NEW: tiny dedupe helper (by doc + chunk) and trim
    def _dedupe_and_trim(self, hits: List[Dict], top: int = 20) -> List[Dict]:
        seen, out = set(), []
        for h in sorted(hits, key=lambda x: x.get("score", 0), reverse=True):
            doc_id = h.get("doc_id") or h.get("id") or h.get("metadata_storage_name")
            key = (doc_id, h.get("chunk_id"))
            if key in seen:
                continue
            seen.add(key)
            out.append(h)
            if len(out) >= top:
                break
        return out

    # NEW: run the new sections_json plan (retrieve per intent → merge → dedupe)
    def _retrieve_by_sections_plan(self, sections_json: Dict, top_per_intent: int = 20) -> Tuple[Dict[str, List[Dict]], List[Dict]]:
        hits_by_intent: Dict[str, List[Dict]] = {}
        all_hits: List[Dict] = []
        sections = (sections_json or {}).get("sections", {})
        for intent, cfg in sections.items():
            intent_hits: List[Dict] = []
            for q in cfg.get("queries", []):
                _, h = self._retrieve_hybrid_enhanced(q, k=self.k)
                intent_hits.extend(h)
            intent_hits = self._dedupe_and_trim(intent_hits, top=top_per_intent)
            hits_by_intent[intent] = intent_hits
            all_hits.extend(intent_hits)
        all_hits = self._dedupe_and_trim(all_hits, top=80)
        return hits_by_intent, all_hits

    # NEW: grouped context (global numbering across intents for [#] citations)
    def _build_grouped_context(self, hits_all: List[Dict], text_field: str = TEXT_FIELD) -> str:
        lines, total = [], 0
        for i, h in enumerate(hits_all, 1):
            title    = h.get("title")
            chunk_id = h.get("chunk_id")
            snippet  = (h.get(text_field) or "")
            if not snippet:
                continue
            snippet = textwrap.shorten(snippet, width=700, placeholder=" ...")
            block = f"[{i}] title={title!r} | chunk_id={chunk_id} | score={h.get('score'):.4f}\n{snippet}"
            if total + len(block) > self.max_chars:
                break
            total += len(block)
            lines.append(block)
        return "\n\n---\n\n".join(lines)

    # NEW: final step using a sections_json plan (no abrupt change to your original _rag_answer)
    def rag_answer_with_sections(self, sections_json: Dict, section_title: str, temperature: float = 0.2):
        """
        Deterministic plan-driven RAG:
          - retrieve per intent from sections_json (queries only),
          - build one grouped context for citations,
          - ask the model to synthesize the specified section using the plan as guidance.
        """
        hits_by_intent, hits_all = self._retrieve_by_sections_plan(sections_json)
        ctx = self._build_grouped_context(hits_all)

        # Keep your existing system prompt but add a light guard: use ONLY context, follow plan
        system_msg = (
            self.profile_prompt +
            "\n\nRules:\n- Use ONLY the provided context snippets.\n"
            "- Follow the formatting & intent implied by the supplied section spec.\n"
            "- Cite claims using [#] matching the snippet numbers.\n"
            "- Do not fabricate numbers; if data is not present in context, write n.a./omit per spec."
        )

        # Hand the section spec to the model as guidance (no calculations here—pure retrieval → synthesis)
        user_msg = (
            f"Task: Produce the section '{section_title}' for company '{self.company_name}'.\n\n"
            f"Section spec (plan):\n{json.dumps(sections_json, ensure_ascii=False)}\n\n"
            f"Context snippets (numbered):\n{ctx}"
        )

        client = self.az_openai
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ]

        resp = client.chat.completions.create(
            model=AOAI_DEPLOYMENT,
            messages=messages,
            temperature=temperature,
        )
        answer = resp.choices[0].message.content
        return self._generate_pdf(answer)

    # (UNCHANGED) Your legacy “single-shot” profile builder still works
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

    # (UNCHANGED) Your original method
    def _rag_answer(self, k: int = 5, temperature: float = 0.2):
        question = f'Create the company profile of {self.company_name}. USE ONLY the information from latest annual report.'

        mode, hits = self._retrieve_hybrid_enhanced(query=question, k=k)
        ctx = self._build_context(hits)

        system_msg = self.profile_prompt
        user_msg = f"Question:\n{question}\n\nContext snippets (numbered):\n{ctx}"

        client = self.az_openai
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ]
        resp = client.chat.completions.create(
            model=AOAI_DEPLOYMENT,
            messages=messages,
        )
        answer = resp.choices[0].message.content
        return self._generate_pdf(answer)
