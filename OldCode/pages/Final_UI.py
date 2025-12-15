# ---------- PAGE CONFIG ----------
import importlib
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Final_theme import apply_theme
import time
import re 
# app.py
import os
import textwrap
from dotenv import load_dotenv, find_dotenv
from openai import APIConnectionError
import json
import streamlit as st
from uuid import uuid4 
from azure.blob_functions import get_companies
from pages.design.dialogues import *
from prompts import default_gpt_prompt

import difflib

from rags.rag import (
    retrieve,
    retrieve_hybrid,
    retrieve_semantic,
    retrieve_hybrid_enhanced,
    build_context,
    get_aoai_client,
    AOAI_DEPLOYMENT,
    TEXT_FIELD,
)
from prompts import new_system_finance_prompt, finance_prompt_web

from gpts.gpt_agent import profileAgent
from io import BytesIO
from typing import Tuple
import time
# from engines.hybrig_eng_enhanced import HybridEngine
from gpts.gpt_assistants import general_assistant
from prompts4 import section7, finance_calculations, system_mod

from gpts.gpt5_web import WebAgent

from gpts.gpt_assistants import maybe_route_to_action
from azure.blob_functions import companyHouseListAdd
from azure.adf_functions import trigger_function
from azure.search_functions import run_indexer

from pathlib import Path

from engines.run_pdf import PDFChatModel


load_dotenv(find_dotenv(), override=True)
OPENAI_API_KEY  = os.getenv("FELIPE_OPENAI_API_KEY")        # required


# =====================================================

st.set_page_config(page_title="Oraculum", layout="wide", initial_sidebar_state="collapsed")
# st.title("Oraculum")

# -------- Session state --------

if "greeted" not in st.session_state:
    st.session_state.greeted = False

if "companieshouse" not in st.session_state:
    st.session_state.companieshouse = False
if "websearch" not in st.session_state:
    st.session_state.websearch = False
if "mixsource" not in st.session_state:
    st.session_state.mixsource = False
if "pdf" not in st.session_state:
    st.session_state.pdf = False

if "convos" not in st.session_state:
    cid = str(uuid4())
    st.session_state.convos = {cid: {"title": "New chat", "messages": []}}
    st.session_state.current_cid = cid

if "history" not in st.session_state:
    st.session_state.history = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None  # used by sidebar suggestion buttons
# Force light theme always
st.session_state.theme = "light"
if "rag" not in st.session_state:
    st.session_state.rag = "FIND THE VARIABLES 'Net cash from operating activities' and 'Net cash used in investing activities' in the statement of cash flows. FILES FROM 2024."
if "sys_message_mod" not in st.session_state:
    st.session_state.sys_message_mod = system_mod
if "calculations" not in st.session_state:
    st.session_state.calculations = finance_calculations
if "company_name" not in st.session_state:
    st.session_state.company_name = None
if "companies_name" not in st.session_state:
    st.session_state.companies_name = ['Seaport Topco Limited']
if "companies_name_dic" not in st.session_state:
    st.session_state.companies_name_dic = {'Seaport Topco Limited':"SEAPORT_TOPCO_LIMITED",
                                           'Radley Co': 'RADLEY_+_CO._LIMITED',
                                           'James Donaldson': 'JAMES_DONALDSON_GROUP_LTD'}
if "profile_mod" not in st.session_state:
    st.session_state.profile_mod = new_system_finance_prompt
if "profile_mod_web" not in st.session_state:
    st.session_state.profile_mod_web = finance_prompt_web

if "pdf_mod" not in st.session_state:
    st.session_state.pdf_mod = False
if "just_ingested" not in st.session_state:
    st.session_state.just_ingested = False
if "just_ingested_msg" not in st.session_state:
    st.session_state.just_ingested_msg = ""

if "ocr_chain" not in st.session_state:
    st.session_state.ocr_chain = None
if "ocr_chain_with_sources" not in st.session_state:
    st.session_state.ocr_chain_with_sources = None
if "ocr_timings" not in st.session_state:
    st.session_state.ocr_timings = None

if "section_build" not in st.session_state:
    st.session_state.section_build = None

if "view" not in st.session_state:
    st.session_state.view = "home"

if "convos" not in st.session_state:
    cid = str(uuid4())
    st.session_state.convos = {cid: {"title": "New chat", "messages": []}}
    st.session_state.current_cid = cid

if "pdf_model" not in st.session_state:
    st.session_state.pdf_model = PDFChatModel()

# optional: track that we've already told the user about uploading
if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False

LOGO = 'LGGAdvisors_Logo.png'

st.logo(
    str(LOGO),                 # main logo
    size="large",             # "small" | "medium" | "large"
)

# def go(view: str):
#     st.session_state.view = view
#     st.session_state.websearch      = (view == "web")
#     st.session_state.mixsource      = (view == "mix")
#     st.session_state.pdf            = (view == "pdf")
#     st.session_state.companieshouse = (view == "companies")

output_placeholder = st.empty()
# apply_theme(st.session_state.theme)

# =====================================================

def check_actions(prompt, client, deployment) -> bool:

    calls = maybe_route_to_action(prompt, client.az_openai, deployment)

    if not calls:
        return False

    for call in calls:
        if call.function.name == "create_company_profile":
            args = json.loads(call.function.arguments or "{}")
            company = args.get("companyName") or "(unknown)"

            out_pdf = client.generate_company_profile()

            st.download_button(
                "Download Profile PDF",
                data=out_pdf,
                file_name=f"{company}_profile.pdf",
                mime="application/pdf",
            )
            st.success("Profile creation done.")
            st.markdown(f"**Functionality in construction..**  (requested company: `{company}`)")

            # Also persist this turn in the chat history so it shows up on rerun
            st.session_state.history.append({
                "q": prompt,
                "a": f"Created a company profile for **{company}**. Use the button above to download the PDF."
            })
            return True
        elif call.function.name == 'add_company':
            args = json.loads(call.function.arguments or "{}")
            companyNumber = args.get("companyNumber") or "(unknown)"
            
            try:
                companyHouseListAdd(CompanyNumber = companyNumber)
                st.success(f"Added {companyNumber} to internal list...")
            except Exception as e:
                print(f'Adding to internal list problem \n{e}')

            time.sleep(5)

            try:
                trigger_function(companyNumber = companyNumber)
                st.success(f"Downloaded {companyNumber} files...")
            except Exception as e:
                print(f'Downloading file problem \n{e}')


            time.sleep(10)
            try:
                with st.spinner('Running OCR and Vectorization... Please wait.'):
                    success = run_indexer()

                if success:
                    st.success("OCR and Vectorization done.")
                    st.rerun()

                else:
                    st.error("Something went wrong during indexing. Please check terminal logs for details.")

            except Exception as e:
                st.error(f"OCR and Vectorization error: {str(e)}")
                print(f'OCR and Vector problem \n{e}')
            
            return True


    return False

def stream_answer(prompt: str, section_build = False, section = ''):

    start_time = time.perf_counter()

    try:
        agent = profileAgent(
            company_name = st.session_state.company_name,
            k=50, 
            max_text_recall_size=35, 
            max_chars=10000,
            model='gpt-5', 
            profile_prompt= st.session_state.sys_message_mod, 
            finance_calculations= st.session_state.calculations
        )

        if section_build:
            answer_text = agent._generate_section(section = section)

        else:
            if check_actions(prompt,
                             agent, 
                             'gpt-5'
                             ):
                pass
            else:
                resp = agent._rag_answer(rag_nl = prompt, question= prompt)
                answer_text = resp['answer']

    except Exception as e:
        answer_text = f"ERROR. \n {e}"

    # 3. measure total time
    elapsed = time.perf_counter() - start_time
    mins = int(elapsed // 60)
    # secs = int(elapsed % 60)
    timing_note = f"\n\n_Generated in {mins}m"

    if section_build:
        final_output = answer_text + timing_note
        st.session_state.history.append({"q": section, "a": final_output})
    else:
        final_output = answer_text + timing_note
        st.session_state.history.append({"q": prompt, "a": final_output})

    final_output = answer_text + timing_note
    ph = st.empty()
    ph.markdown(final_output)

def pick_company(user_text):
    # 1. Check if the user is explicitly trying to select a company.
    #    Pattern: "select company <company_name>"
    #    - ignores leading/trailing spaces
    #    - case-insensitive for the words "select company"
    #    - grabs whatever comes after "select company " as the candidate company name
    m = re.match(r'^\s*select\s+company\s+(.+?)\s*$', user_text, flags=re.IGNORECASE)
    if not m:
        # User didn't say "select company ..."
        return None, None

    candidate = m.group(1).strip()

    # 2. Load company list
    name_map, names = get_companies()
    # name_map: {original_name: CLEANED_NAME}
    # names:    [CLEANED_NAME, CLEANED_NAME, ...] (possibly with dups)

    # we'll dedupe but keep order
    unique_names = list(dict.fromkeys(names))

    # reverse map CLEANED_NAME -> original_name
    reverse_map = {v: k for k, v in name_map.items()}

    # 3. Normalize candidate the same way you normalized in original code
    cleaned_candidate = candidate.upper()

    # 4. Fuzzy match against the official list with strict 0.9 cutoff
    matches = difflib.get_close_matches(
        cleaned_candidate,
        unique_names,
        n=1,
        cutoff=0.95  # strict matching - user must type almost exactly
    )

    if matches:
        best_clean = matches[0]
        original_name = reverse_map.get(best_clean, best_clean)
        # return (original_for_display, cleaned_canonical)
        return original_name, best_clean

    return None, None

def go(view: str):
    st.session_state.view = view
    st.session_state.websearch      = (view == "web")
    st.session_state.mixsource      = (view == "mix")
    st.session_state.pdf            = (view == "pdf")
    st.session_state.companieshouse = (view == "companies")

    if st.session_state.websearch:
        st.session_state.history.append({"a": greeting_2})
        st.rerun()
    elif st.session_state.mixsource:
        name_map, names = get_companies()
        st.session_state.history.append({"a": f"{greeting_3}\n\n Companies Available: \n" + "\n".join(f"- {n}" for n in names)})
        st.rerun()
    elif st.session_state.pdf:
        pass
    elif st.session_state.companieshouse:
        # _ , names = get_companies()
        # st.session_state.history.append({"a":f"{greeting_1}\n\n" + "\n".join(f"- {n}" for n in names)})
        # st.rerun()
        pass

if st.session_state.pdf:
    uploaded_files = st.file_uploader("Upload PDF", type=["pdf"], accept_multiple_files=True)
    if uploaded_files:
        # Build / refresh the PDF agent model with these files.
        st.session_state.pdf_model.load_pdfs(uploaded_files)
        st.session_state.pdf_ready = True

        st.success("OCR index ready.")

        # Show timings / debug info if you'd like:
        st.subheader("Timings")
        st.json(st.session_state.pdf_model.get_timings())
    else:
        st.info("Upload PDFs to start chatting.")

# ---------- Dark/White Mode----------

apply_theme(st.session_state.theme)


# ---------- NAV STATE ----------


if st.session_state.view == "home":
    L, C, R = st.columns([0.25, 14, 0.25], gap="large")
    with C:
        st.markdown("<div class='home-wrap'>", unsafe_allow_html=True)
        st.markdown("<div class='hero-wrap'>", unsafe_allow_html=True)

        st.markdown("<h1 class='hero-title'>Welcome to Oraculum</h1>", unsafe_allow_html=True)
        st.markdown("<p class='hero-sub'>Your AI assistant for financial documents and company research, Please select a mode to get started.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Cards row (clickable; no business logic yet)
        c1, c2, c3, c4 = st.columns([0.5, 0.5, 0.5, 0.5], gap="medium")

        with c1:
            st.button("**Research with Companies House**  \n_Access comprehensive company data from Companies House. Search for companies, view financial filings, and analyze company structures._", 
                         icon=":material/domain:", key="open_companies", use_container_width=True, on_click=go, args=("companies",))
        with c2:
            st.button("**Research with Web Search**  \n_Leverage real-time web search capabilities to find the latest news, market data, and insights. Stay updated with current information about companies and industries._", 
                         icon=":material/language:", key="open_web", use_container_width=True, on_click=go, args=("web",))
        with c3:
            st.button("**Research with Companies House & Web Search**  \n_Extract key figures, generate summaries, and identify important metrics from financial reports, contracts, and other documents._", 
                         icon=":material/picture_as_pdf:", key="mix", use_container_width=True, on_click=go, args=("mix",))
        with c4:
            st.button("**Talk with Your PDF**  \n_Upload and analyze PDF documents with advanced OCR. This methodology works with an entire independent system that doesn't save the section for privacy concerns_", 
                         icon=":material/picture_as_pdf:", key="open_pdf", use_container_width=True, on_click=go, args=("pdf",))

        st.markdown("</div>", unsafe_allow_html=True)

# ---------- SIDEBAR (static for now) ----------

with st.sidebar:

    # ---- New Chat ----
    if st.session_state.get("view") != "home":
        if st.button("✚ New chat", use_container_width=True, key="new_chat"):
            cid = str(uuid4())
            st.session_state.convos[cid] = {"title": "New chat", "messages": []}
            st.session_state.current_cid = cid
            st.rerun()

        ids = list(st.session_state.convos.keys())
        pick = st.radio(
            "Chat History",
            options=ids,
            key="chat_history_radio",  # <-- important to avoid duplicate-ID error
            format_func=lambda x: st.session_state.convos[x]["title"],
        )
        st.session_state.current_cid = pick


    # Each button uses Streamlit’s native Material icon support
    st.markdown("### Select Mode")

    # Companies House (PDF) mode
    if st.button("Research with Companies House PDF", icon=":material/domain:", use_container_width=True):
        st.session_state.websearch = False
        st.session_state.mixsource = False
        st.session_state.pdf = False
        st.session_state.companieshouse = True
        
        for k in ["history", "messages", "pending_prompt"]:
            st.session_state.pop(k, None)
        if "history" not in st.session_state:
            st.session_state.history = []

        _ , names = get_companies()
        st.session_state.history.append({"a":f"{greeting_1}\n\n" + "\n".join(f"- {n}" for n in names)})
        st.rerun()

    # Web Search mode
    if st.button("Research with Web Search", icon=":material/language:", use_container_width=True, key="mode_web"):
        st.session_state.websearch = False
        st.session_state.mixsource = False
        st.session_state.pdf = False
        st.session_state.companieshouse = False
        for k in ["history", "messages", "pending_prompt"]:
            st.session_state.pop(k, None)
        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append({"a": greeting_2})
        st.session_state.websearch = True
        st.rerun()

    # Both (Web + CH) mode
    if st.button("Research with Companies House and Web Search", icon=":material/picture_as_pdf:", use_container_width=True, key="mode_both"):
        st.session_state.websearch = False
        st.session_state.mixsource = True
        st.session_state.pdf = False
        st.session_state.companieshouse = False
        for k in ["history", "messages", "pending_prompt"]:
            st.session_state.pop(k, None)
        if "history" not in st.session_state:
            st.session_state.history = []
        name_map, names = get_companies()
        st.session_state.history.append({"a": f"{greeting_3}\n\n Companies Available: \n" + "\n".join(f"- {n}" for n in names)})
        st.rerun()

    # Both PDF mode
    if st.button("Talk with Your PDF", icon=":material/picture_as_pdf:", use_container_width=True, key="mode_pdf"):
        st.session_state.websearch = False
        st.session_state.mixsource = False
        st.session_state.pdf = True
        st.session_state.companieshouse = False
        # st.session_state.view = "pdf"
        for k in ["history", "messages", "pending_prompt"]:
            st.session_state.pop(k, None)
        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append({"a": "Upload your PDF and have a chat!"})
        
        st.rerun()

if st.session_state.websearch or st.session_state.mixsource or st.session_state.pdf:
    pass
else:
    with st.sidebar.expander("Profile Sections", expanded=False):
        st.write('Take in mind that building a section might take between 11-25 minutes in average')
        if st.button("1.Get Business Overview", use_container_width=True, key="overview_btn"):
            if not st.session_state.company_name:
                with st.chat_message("assistant"):
                    st.session_state.history.append({"q": f"1.Get Business Overview", "a": "Please select a company out of the list and write it down, before asking a question."})
                st.rerun()
            else:
                st.session_state.section_build = "GENERATE BUSINESS OVERVIEW"
                stream_answer(prompt='', section_build=True, section=st.session_state.section_build)
            st.rerun()
        if st.button("2.Get Key Stakeholders", use_container_width=True, key="stakeholder_btn"):
            if not st.session_state.company_name:
                with st.chat_message("assistant"):
                    st.session_state.history.append({"q": f"2.Get Key Stakeholders", "a": "Please select a company out of the list and write it down, before asking a question."})

                st.rerun()
            else:
                st.session_state.section_build = "GENERATE KEY STAKEHOLDERS"
                stream_answer(prompt='', section_build=True, section=st.session_state.section_build)
            st.rerun()
        if st.button("3.Revenue split (NEW)", use_container_width=True, key="revenue_btn"):
            if not st.session_state.company_name:
                with st.chat_message("assistant"):
                    st.session_state.history.append({"q": f"3.Revenue split", "a": "Please select a company out of the list and write it down, before asking a question."})
                
                st.rerun()
            else:
                st.session_state.section_build = "GENERATE REVENUE SPLIT"
                stream_answer(prompt='', section_build=True, section=st.session_state.section_build)
            st.rerun()
        if st.button("4a.Products/Services Overview (NEW)", use_container_width=True, key="prod_btn"):
            if not st.session_state.company_name:
                with st.chat_message("assistant"):
                    st.session_state.history.append({"q": f"4a.Products/Services Overview", "a": "Please select a company out of the list and write it down, before asking a question."})
                
                st.rerun()
            else:
                st.session_state.section_build = "GENERATE PRODUCTS SERVICES OVERVIEW"
                stream_answer(prompt='', section_build=True, section=st.session_state.section_build)
            st.rerun()
        if st.button("4b.Geographical Footprint (NEW)", use_container_width=True, key="geo_btn"):
            if not st.session_state.company_name:
                with st.chat_message("assistant"):
                    st.session_state.history.append({"q": f"4b.Geographical Footprint", "a": "Please select a company out of the list and write it down, before asking a question."})
                
                st.rerun()
            else:
                st.session_state.section_build = "GENERATE GEO FOOTPRINT"
                stream_answer(prompt='', section_build=True, section=st.session_state.section_build)
            st.rerun()
        if st.button("5.Key Recent Developments (NEW)", use_container_width=True, key="recent_btn"):
            if not st.session_state.company_name:
                with st.chat_message("assistant"):
                    st.session_state.history.append({"q": f"5.Key Recent Developments", "a": "Please select a company out of the list and write it down, before asking a question."})
                
                st.rerun()
            else:
                st.session_state.section_build = "GENERATE DEVELOPMENTS HIGHLIGHTS"
                stream_answer(prompt='', section_build=True, section=st.session_state.section_build)
            st.rerun()
        if st.button("6.Get Financial Highlights", use_container_width=True, key="finance_btn"):
            if not st.session_state.company_name:
                with st.chat_message("assistant"):
                    st.session_state.history.append({"q": f"5.Get Financial Highlights", "a": "Please select a company out of the list and write it down, before asking a question."})
                
                st.rerun()
            else:
                st.session_state.section_build = "GENERATE FINANCIAL HIGHLIGHTS"
                stream_answer(prompt='', section_build=True, section=st.session_state.section_build)
            st.rerun()
        if st.button("7.Get Capital Structure", use_container_width=True, key="capital_btn"):
            if not st.session_state.company_name:
                with st.chat_message("assistant"):
                    st.session_state.history.append({"q": f"6.Get Capital Structure", "a": "Please select a company out of the list and write it down, before asking a question."})
                
                st.rerun()
            else:
                st.session_state.section_build = "GENERATE CAPITAL STRUCTURE"
                stream_answer(prompt='', section_build=True, section=st.session_state.section_build)
            st.rerun()

# companies = st.session_state.get("companies_name") or []

if not st.session_state.greeted and st.session_state.view == "companies":
    _, names = get_companies()
    st.session_state.history.append({
        "a": f"{greeting_1}\n\n" + "\n".join(f"- {n}" for n in names)
    })
    st.session_state.companieshouse = True
    st.session_state.greeted = True
elif st.session_state.view == "pdf":
    st.session_state.pdf = True
    st.session_state.greeted = True
    # uploaded_files = st.file_uploader("Upload PDF", type=["pdf"], accept_multiple_files=True)
    # if uploaded_files:
    #     # Build / refresh the PDF agent model with these files.
    #     st.session_state.pdf_model.load_pdfs(uploaded_files)
    #     st.session_state.pdf_ready = True

    #     st.success("OCR index ready.")

    #     # Show timings / debug info if you'd like:
    #     st.subheader("Timings")
    #     st.json(st.session_state.pdf_model.get_timings())
    # else:
    #     st.info("Upload PDFs to start chatting.")
elif st.session_state.view == "mix":
    for k in ["history", "messages", "pending_prompt"]:
        st.session_state.pop(k, None)
    if "history" not in st.session_state:
        st.session_state.history = []
    name_map, names = get_companies()
    st.session_state.history.append({"a": f"{greeting_3}\n\n Companies Available: \n" + "\n".join(f"- {n}" for n in names)})
    st.session_state.mixsource = True
    st.session_state.greeted = True
    # st.rerun()
    

# if st.session_state.pdf:
#     uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
#     if uploaded_file:
#         st.success(f"Uploaded: {uploaded_file.name}")



# =====================================================

client = get_aoai_client()

# Render prior turns every run so the conversation persists
# ---------- CHAT RENDERING ----------
if st.session_state.view != "home":
    header_map = {
        "companies": ("Companies House Research", "Search and manage company data."),
        "pdf": ("PDF Analysis", "Upload and analyze PDFs."),
        "web": ("Research with Web Search", "Find latest news and insights."),
        "combo": ("Research with Companies House and Web Search", "Use both ingested filings and the live web.")
    }

    # NEW: resolve mode from flags first, then fallback to view
    mode = ("web" if st.session_state.get("websearch") else
            "combo" if st.session_state.get("mixsource") else
            "pdf" if st.session_state.get("pdf") else
            "companies" if st.session_state.get("companieshouse") else
            st.session_state.view)

    title, subtitle = header_map.get(
        mode, 
        ("Companies House Research", "Search and manage company data.")
    )

    st.markdown(
        f"<h2 class='page-h2'>{title}</h2><p class='page-sub'>{subtitle}</p>",
        unsafe_allow_html=True
    )
    for turn in st.session_state.history:
        if turn.get("q"):
            with st.chat_message("user"):
                st.write(turn["q"])
        with st.chat_message("assistant"):
            st.markdown(turn["a"])
    
    placeholder = (
        "Ask a question about your PDFs…" 
        if st.session_state.pdf_mod 
        else "Ask about the ingested PDFs…"
    )

    typed = st.chat_input(placeholder)
    pending = st.session_state.pop("pending_prompt", None)
    prompt = typed or pending

    if prompt and mode not in ('web', 'pdf'):
        _name_company_coded, _name_company = pick_company(prompt)
        if _name_company:
            st.session_state.company_name = _name_company_coded
            answer_text = f"You have selected the \n {_name_company}"
            st.session_state.history.append({"a": answer_text})
            # Clear the prompt so it doesn't get processed again
            prompt = None
            st.rerun()
            # st.stop()
        else:
            pass


    if st.session_state.companieshouse:
            qa1, qa2, qa3, qa4 = st.columns([0.5,0.5,0.5,0.5])
            with qa1:
                if st.button("List Companies", use_container_width=True, key="list_companies_btn"):
                    _, names = get_companies()
                    answer_text = f"{companies_available}\n\n" + "\n".join(f"- {n}" for n in names)
                    st.session_state.history.append({"q": "Which companies are available?", "a": answer_text})
                    st.rerun()
            with qa2:
                if st.button("Add New from CH", use_container_width=True, key="add_company_btn"):
                    answer_text = f"{add_company_tutorial_1}\n\n"
                    st.session_state.history.append({"q": "How do I add new companies?", "a": answer_text})
                    st.rerun()
            with qa3:
                if st.button("Create Company Profile", use_container_width=True, key="create_profile_btn"):
                    answer_text = f"{profile_tutorial_1}\n\n"
                    st.session_state.history.append({"q": "How do I ask for a Company Profile?", "a": answer_text})
                    st.rerun()
            with qa4:
                if st.button("Create Profile Section", use_container_width=True, key="create_section_btn"):
                    answer_text = f"{section_tutorial_1}\n\n"
                    st.session_state.history.append({"q": "How can I build a Company Profile Section?", "a": answer_text})
                    st.rerun()
else:
    # Home view → no chat shown
    prompt = None

# Web Answer
def web_answer(prompt):

    agent = WebAgent()

    messages = [
    {"role": "system", "content": default_gpt_prompt},
    {"role": "user",   "content": prompt},
    ]

    try: 
        answer_text = agent._web_search(messages)
    except Exception as e:
        answer_text = f"ERROR. \n {e}"

    st.session_state.history.append({"q": prompt, "a": answer_text})

    ph = st.empty()
    ph.write(answer_text)

def mix_answer(prompt):

    agent = WebAgent()

    try: 
        answer_text = agent._answer(question=prompt)
    except Exception as e:
        answer_text = f"ERROR. \n {e}"

    st.session_state.history.append({"q": prompt, "a": answer_text})

    ph = st.empty()
    ph.write(answer_text)


if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):

        # Try tool routing first
        model_profile = "gpt-5" #if model_profile_mod else "o3"

        if st.session_state.websearch:
            web_answer(prompt)
        elif st.session_state.mixsource:
            if not st.session_state.company_name:
                with st.chat_message("assistant"):
                    st.write("Please select a company out of the list and write it down, before asking a question.")
                # st.session_state.history.append({"q": prompt, "a": "Please select a company first."})
                st.stop()
            else:
                with st.chat_message("assistant"):
                    mix_answer(prompt)
        elif st.session_state.pdf:
            if not st.session_state.pdf_ready:
                bot_reply = "Please upload PDFs first so I can index them."
            else:
                bot_reply = st.session_state.pdf_model.answer(prompt)

            st.write(bot_reply)

            # Push to history for the chat transcript
            st.session_state.history.append({
                "q": prompt,
                "a": bot_reply
            })
        else:
            # Check for actions that don't require a company selection (like add_company)
            try:
                agent = profileAgent(
                    company_name=st.session_state.company_name,
                    k=50,
                    max_text_recall_size=35,
                    max_chars=10000,
                    model='gpt-5',
                    profile_prompt=st.session_state.sys_message_mod,
                    finance_calculations=st.session_state.calculations
                )

                # Check if this is an action (like add_company) that doesn't need a selected company
                if check_actions(prompt, agent, 'gpt-5'):
                    # Action was handled, stop here
                    st.stop()
            except Exception as e:
                # If there's an error creating the agent, continue to normal flow
                pass

            # For regular queries, require company selection
            if not st.session_state.company_name:
                # get_company(prompt)
                with st.chat_message("assistant"):
                    st.write("Please select a company out of the list and write it down, before asking a question.")
                # st.session_state.history.append({"q": prompt, "a": "Please select a company first."})
                st.stop()
            else:
                with st.chat_message("assistant"):
                    stream_answer(prompt)
        