import streamlit as st
import streamlit as st

def apply_theme(mode: str):
    # Your palette
    PRIMARY = "#0C6CF2"
    DARK_BG  = "#0B1220"
    DARK_SEC = "#111827"
    DARK_TXT = "#FFFFFF"

    # Light/white mode targets (greys)
    LIGHT_BG   = "#FFFFFF"   # page background
    LIGHT_TXT  = "#000000"   # text
    GREY_050   = "#F9FAFB"
    GREY_100   = "#F3F4F6"
    GREY_200   = "#E5E7EB"
    GREY_300   = "#D1D5DB"

    if mode == "dark":
        page_bg   = DARK_BG
        side_bg   = DARK_SEC
        text_col  = DARK_TXT
        panel_bg  = DARK_SEC
        button_bg = "#1F2937"            # dark grey buttons
        chrome_bg = DARK_SEC             # header + bottom bars
        input_bg  = "#0F172A"
        border    = "rgba(255,255,255,0.1)"
    else:
        page_bg   = LIGHT_BG
        side_bg   = GREY_100             # sidebar
        text_col  = LIGHT_TXT
        panel_bg  = GREY_100             # expanders/cards
        button_bg = GREY_200             # grey button boxes
        chrome_bg = "#FFFFFF"            # header & bottom bars WHITE
        input_bg  = GREY_050
        border    = "rgba(0,0,0,0.12)"

    st.markdown(f"""
    <style>
    :root {{
      --primary-color: {PRIMARY};
      --page-bg: {page_bg};
      --sidebar-bg: {side_bg};
      --text: {text_col};
      --panel-bg: {panel_bg};
      --button-bg: {button_bg};
      --chrome-bg: {chrome_bg};
      --input-bg: {input_bg};
      --border-col: {border};
    }}

    /* Page + typography */
    .stApp {{ background: var(--page-bg) !important; color: var(--text) !important; }}
    html, body, [class^="st-"], [class*=" st-"] {{ color: var(--text) !important; }}

    /* Header (top bar) */
    header[data-testid="stHeader"] {{
      background: var(--chrome-bg) !important;
      border-bottom: 1px solid var(--border-col);
    }}

    /* Ensure main container itself isn't painting a dark strip */
    [data-testid="stAppViewContainer"] .main {{
      background: var(--page-bg) !important;
    }}

    /* ----- BOTTOM CHAT AREA FIX (cover multiple Streamlit versions) ----- */

    /* Preferred: wrapper that directly contains the chat input (modern browsers) */
    [data-testid="stAppViewContainer"] .main > div:has(> [data-testid="stChatInput"]) {{
      background: var(--chrome-bg) !important;
      border-top: 1px solid var(--border-col);
    }}

    /* Fallbacks: target common wrappers used across versions */
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stBottomBlockContainer"],
    .stChatFloatingInputContainer,
    .stChatInputContainer,
    /* Often the last child of .main is the bottom bar shell */
    [data-testid="stAppViewContainer"] .main > div:last-child {{
      background: var(--chrome-bg) !important;
      border-top: 1px solid var(--border-col);
    }}

    /* Textarea inside the chat input */
    [data-testid="stChatInput"] textarea {{
      background: var(--input-bg) !important;
      color: var(--text) !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] > div:first-child {{
      background: var(--sidebar-bg) !important;
      color: var(--text) !important;
    }}

    /* Buttons (including suggestion boxes & download buttons) */
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
      background-color: var(--button-bg) !important;
      color: var(--text) !important;
      border: 1px solid var(--border-col) !important;
      border-radius: 10px !important;
      box-shadow: none !important;
    }}

    /* Inputs */
    input, textarea, select {{
      background: var(--input-bg) !important;
      color: var(--text) !important;
    }}

    /* Dropdowns / expanders (both main area & sidebar) */
    [data-testid="stExpander"] {{
      background: var(--panel-bg) !important;
      border: 1px solid var(--border-col) !important;
      border-radius: 10px !important;
    }}
    [data-testid="stExpander"] details > summary {{
      color: var(--text) !important;
      background: transparent !important;
    }}

    /* Selectbox/Multiselect popover (BaseWeb) */
    div[data-baseweb="select"] > div {{
      background: var(--panel-bg) !important;
      color: var(--text) !important;
      border-color: var(--border-col) !important;
    }}

    /* Expander content & generic containers */
    .block-container, .stMarkdown, .stDataFrame {{ color: var(--text) !important; }}
    </style>
    """, unsafe_allow_html=True)
