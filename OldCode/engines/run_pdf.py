# pdf_agent.py
from io import BytesIO
from typing import Tuple, Annotated, TypedDict, List, Dict, Any
import time
import sys, pathlib

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# Make sure engines.engine is importable
repo_root = pathlib.Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from engines.engine import HybridEngine  # your OCR/semantic retriever
# try:
#     from engines.calc_tool import calc_script as _calc_impl
# except Exception:
_calc_impl = None


class PDFState(TypedDict):
    messages: Annotated[list, add_messages]


class PDFChatModel:
    """
    This class encapsulates:
    - building the OCR/semantic index across uploaded PDFs (HybridEngine)
    - building a LangGraph agent with tools (pdf_search, web_search, calc_script)
    - answering questions via that agent

    After you create one instance per user session, you can:
        model.load_pdfs(uploaded_files)
        answer = model.answer("what's revenue growth?")
    """

    def __init__(self):
        self.engine = None               # HybridEngine
        self.graph = None                # compiled LangGraph
        self.timings = {}
        self.thread_id = None
        self._memory = MemorySaver()
        self._last_file_names: Tuple[str, ...] = tuple()

    def _build_engine_from_files(
        self,
        files_bytes: Tuple[bytes, ...],
        files_names: Tuple[str, ...]
    ):
        """
        Build/Rebuild HybridEngine using uploaded PDFs.
        """
        pdf_streams = tuple((BytesIO(b), n) for b, n in zip(files_bytes, files_names))

        engine = HybridEngine(pdf_streams)
        t0 = time.perf_counter()
        engine.main()
        build_s = time.perf_counter() - t0

        timings = getattr(engine, "timings", {})
        timings["total_build_s"] = build_s

        self.engine = engine
        self.timings = timings
        self._last_file_names = files_names

        # assign thread_id lazily
        if not self.thread_id:
            self.thread_id = f"ui-{int(time.time())}"

    def _build_graph(self):
        """
        Build the LangGraph agent wired to pdf_search / web_search / calc_script
        using the *current* engine.
        """
        if self.engine is None:
            raise RuntimeError("Engine not ready. Call load_pdfs(...) first.")

        @tool
        def pdf_search(query: str) -> str:
            """Retrieve top snippets from the indexed PDFs for a query."""
            docs = self.engine.hybrid.get_relevant_documents(query)
            if not docs:
                return "NO_MATCH"
            return "\n---\n".join([d.page_content[:500] for d in docs[:3]])

        @tool
        def web_search(query: str) -> str:
            """
            Web fallback tool. If you DON'T want PDF chat to hit web,
            just return 'WEB_DISABLED' here.
            """
            try:
                from openai import OpenAI
                client = OpenAI()
                resp = client.responses.create(
                    model="gpt-5",
                    tools=[{"type": "web_search"}],
                    input=(
                        f"Search the web for: {query}\n"
                        "Return up to 3 bullets, each exactly as:\n"
                        "[web] <title> — <one-line snippet> <url>\n"
                        "If nothing is found, return exactly: WEB_NO_RESULTS"
                    ),
                )
                text = (getattr(resp, "output_text", "") or "").strip()
                bullets = [
                    ln.strip()
                    for ln in text.split("\n")
                    if ln.strip().startswith("[web] ")
                ][:3]
                if not bullets:
                    return "WEB_NO_RESULTS"
                return "\n---\n".join(bullets)
            except Exception:
                return "WEB_NO_RESULTS"

        if _calc_impl:
            @tool
            def calc_script(data: str) -> str:
                """Financial calculations tool."""
                return _calc_impl(data)
        else:
            @tool
            def calc_script(data: str) -> str:
                """Financial calculations tool (placeholder)."""
                return "CALC_NOT_IMPLEMENTED"

        tools = [pdf_search, web_search, calc_script]

        llm = ChatOpenAI(model="gpt-5")
        llm_with_tools = llm.bind_tools(tools)

        def chatbot(state: PDFState) -> PDFState:
            ai_msg = llm_with_tools.invoke(state["messages"])
            return {"messages": [ai_msg]}

        builder = StateGraph(PDFState)
        builder.add_node("chatbot", chatbot)
        builder.add_node("tools", ToolNode(tools))
        builder.add_edge(START, "chatbot")
        builder.add_conditional_edges("chatbot", tools_condition)
        builder.add_edge("tools", "chatbot")
        builder.add_edge("chatbot", END)

        self.graph = builder.compile(checkpointer=self._memory)

    def load_pdfs(self, uploaded_files: List[Any]):
        """
        Call this once after the user uploads PDFs (or re-uploads different PDFs).

        uploaded_files is Streamlit's list of UploadedFile objects.
        """
        if not uploaded_files:
            return

        files_bytes = tuple(f.getvalue() for f in uploaded_files)
        files_names = tuple(f.name for f in uploaded_files)

        # Only rebuild if new set of files is different
        if self.engine is None or files_names != self._last_file_names:
            self._build_engine_from_files(files_bytes, files_names)
            self._build_graph()  # rebuild graph bound to new engine

    def answer(self, question: str) -> str:
        """
        One-turn Q&A. Returns assistant text.
        """
        if self.graph is None or self.engine is None:
            return "Please upload PDFs first so I can index them."

        state_in = {
            "messages": [
                {"role": "system", "content": "You are a financial assistant."},
                {"role": "user", "content": question},
            ]
        }

        out = self.graph.invoke(
            state_in,
            {"configurable": {"thread_id": self.thread_id}},
        )

        bot_msg = out["messages"][-1].content
        return bot_msg

    def get_timings(self) -> Dict[str, float]:
        """
        For debugging / UI display.
        """
        return self.timings or {}
