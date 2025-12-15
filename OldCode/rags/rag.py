# --- Cell A: wire Search + Azure OpenAI into a tiny RAG helper ---

import os, textwrap
from typing import List, Dict, Optional

from dotenv import load_dotenv, find_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery
from azure.core.exceptions import HttpResponseError
from azure.search.documents.models import HybridSearch

from openai import AzureOpenAI, APIConnectionError

load_dotenv(find_dotenv(), override=True)

# ---- Config (expects the same envs you already used) ----
SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_INDEX    = os.environ["AZURE_SEARCH_INDEX"]
SEARCH_KEY      = os.getenv("AZURE_SEARCH_API_KEY")  # omit if using AAD/RBAC
VECTOR_FIELD    = os.getenv("VECTOR_FIELD", "text_vector_v4")
TEXT_FIELD      = os.getenv("TEXT_FIELD", "chunk")

AOAI_ENDPOINT   = os.environ["AZURE_OPENAI_ENDPOINT"]            # https://<resource>.openai.azure.com
AOAI_API_VER    = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21")
AOAI_DEPLOYMENT = os.environ["AZURE_OPENAI_DEPLOYMENT"]          # e.g., gpt-4o-mini / o3-mini / gpt-5 preview
AOAI_KEY        = os.getenv("AZURE_OPENAI_API_KEY")              # omit if using AAD

# ---- Clients ----
def get_search_client() -> SearchClient:
    cred = AzureKeyCredential(SEARCH_KEY) if SEARCH_KEY else DefaultAzureCredential()
    return SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, credential=cred)

def get_aoai_client() -> AzureOpenAI:
    if AOAI_KEY:
        return AzureOpenAI(azure_endpoint=AOAI_ENDPOINT, api_key=AOAI_KEY, api_version=AOAI_API_VER)
    return AzureOpenAI(azure_endpoint=AOAI_ENDPOINT, azure_ad_token_provider=DefaultAzureCredential().get_token, api_version=AOAI_API_VER)

# ---- Retrieval (integrated vectorization first, lexical fallback) ----
def retrieve(query: str, k: int = 10):
    sc = get_search_client()
    try:
        vq = VectorizableTextQuery(text=query, k=k, fields=VECTOR_FIELD)
        # Prefer vector-only search (integrated vectorization). If your index isn't set up for it, this raises.
        results = sc.search(
            search_text=query, 
            vector_queries=[vq], 
            top=k,
            )
        mode = "vector (integrated)"
    except HttpResponseError as e:
        # Fall back to lexical so you still get results while fixing vector config
        results = sc.search(search_text=query, top=k)
        mode = f"lexical (fallback due to: {e.__class__.__name__})"

    hits: List[Dict] = []
    for r in results:
        d = dict(r)
        d["score"] = r["@search.score"]
        hits.append(d)
    return mode, hits

def retrieve_semantic(query: str, k: int = 10):
    sc = get_search_client()
    try:
        vq = VectorizableTextQuery(text=query, k=k, fields=VECTOR_FIELD)
        # Prefer vector-only search (integrated vectorization). If your index isn't set up for it, this raises.
        results = sc.search(
            search_text=query, 
            vector_queries=[vq], 
            top=k, 
            query_type="semantic",
            query_caption="extractive", 
            query_caption_highlight_enabled=True,
            )
    except HttpResponseError as e:
        # Fall back to lexical so you still get results while fixing vector config
        results = sc.search(search_text=query, top=k)
        mode = f"lexical (fallback due to: {e.__class__.__name__})"

    hits: List[Dict] = []
    for r in results:
        d = r.copy() if hasattr(r, "copy") else {key: r[key] for key in r}
        # Prefer semantic reranker score when present
        d["score"] = d.get("@search.reranker_score", d.get("@search.score"))
        # Pull first caption if present
        caps = d.get("@search.captions")
        if isinstance(caps, list) and caps:
            cap0 = caps[0]
            d["caption"] = getattr(cap0, "text", cap0.get("text") if isinstance(cap0, dict) else None)
        hits.append(d)
    return "semantic-only", hits

def retrieve_hybrid(query: str, k: int = 10):
    sc = get_search_client()
    try:
        vq = VectorizableTextQuery(text=query, k=k, fields=VECTOR_FIELD)
        # Prefer vector-only search (integrated vectorization). If your index isn't set up for it, this raises.
        results = sc.search(
            search_text=query, 
            vector_queries=[vq], 
            top=k, 
            query_type="semantic",
            query_caption="extractive", 
            query_caption_highlight_enabled=True,
            )
        mode = "hybrid + semantic"
    except HttpResponseError as e:
        # Fall back to lexical so you still get results while fixing vector config
        results = sc.search(search_text=query, top=k)
        mode = f"lexical (fallback due to: {e.__class__.__name__})"

    hits: List[Dict] = []
    for r in results:
        d = r.copy() if hasattr(r, "copy") else {k2: r[k2] for k2 in r}
        d["score"] = d.get("@search.reranker_score") or d.get("@search.score") or 0.0
        caps = d.get("@search.captions")
        if isinstance(caps, list) and caps:
            cap0 = caps[0]                 # QueryCaptionResult
            d["caption"] = getattr(cap0, "text", None)
        hits.append(d)

    return mode, hits

def _company_filter(company_name) -> str:
    v = (company_name or "").replace("'", "''").strip()
    return f"company_name eq '{v}'" if v else None


def retrieve_hybrid_enhanced(company_name, query: str, top: int = 20, k: int = 50, max_text_recall_size:int = 1000):
    sc = get_search_client()
    flt = _company_filter(company_name)
    try:
        vq = VectorizableTextQuery(
            text=query, 
            k=k, 
            fields=VECTOR_FIELD, 
            weight=1.8
            )
        
        # Prefer vector-only search (integrated vectorization). If your index isn't set up for it, this raises.
        results = sc.search(
            search_text=query, 
            vector_queries=[vq],
            top=top, 
            query_type="semantic",
            query_caption="extractive", 
            query_answer='extractive',
            hybrid_search=HybridSearch(max_text_recall_size=max_text_recall_size),
            query_caption_highlight_enabled=True,
            semantic_error_mode="partial",
            filter=flt
            )
        mode = "hybrid + semantic"
    except HttpResponseError as e:
        # Fall back to lexical so you still get results while fixing vector config
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

def build_context(hits: List[Dict], text_field: str = TEXT_FIELD, max_chars: int = 20000) -> str:
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
        if total + len(block) > max_chars:
            break
        total += len(block)
        lines.append(block)
    return "\n\n---\n\n".join(lines)

# ---- RAG ask with streaming + non-streaming fallback ----
def rag_answer(question: str, k: int = 5, temperature: float = 0.2):
    mode, hits = retrieve(question, k=k)
    ctx = build_context(hits)

    system_msg = (
        "You are a financial analyst. Use ONLY the provided context to answer. "
        "All the files that you will be working with and PROVIDED in the context are annual reports. The name of the company that own the annual report is in the first page."
        "Cite sources using [#] that match the snippet numbers. "
        "If the answer isn't in the context, say you don't know."
    )
    user_msg = f"Question:\n{question}\n\nContext snippets (numbered):\n{ctx}"

    client = get_aoai_client()
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user",   "content": user_msg},
    ]

    # Try streaming first (SSE). Some networks/proxies block streaming; if so, fall back.
    try:
        text = ""
        stream = client.chat.completions.create(
            model=AOAI_DEPLOYMENT,
            messages=messages,
            stream=True,
            stream_options={"include_usage": True},
        )
        for chunk in stream:
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            if not delta:
                continue
            piece = getattr(delta, "content", None)
            if piece:
                text += piece
        answer = text if text else "(no text returned)"
        mode_model = "streaming"
    except APIConnectionError:
        resp = client.chat.completions.create(
            model=AOAI_DEPLOYMENT,
            messages=messages,
        )
        answer = resp.choices[0].message.content
        mode_model = "non-streaming (fallback)"

    return {
        "search_mode": mode,
        "model_mode": mode_model,
        "answer": answer,
        "sources": [
            {"n": i+1, "title": h.get("title"), "chunk_id": h.get("chunk_id"), "score": h.get("score")}
            for i, h in enumerate(hits)
        ],
    }
