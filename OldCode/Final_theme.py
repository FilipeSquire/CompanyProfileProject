import streamlit as st
import streamlit as st

def apply_theme(mode: str):
    # Your palette
    PRIMARY = "#0C6CF2"
    DARK_BG  = "#0B1220"
    DARK_SEC = "#111827"
    DARK_TXT = "#FFFFFF"

    # Light/white mode targets (greys)
    LIGHT_BG   = "#F3F6FA"  # page background
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
        chrome_bg = LIGHT_BG           # header & bottom bars WHITE
        input_bg  = GREY_050
        border    = "rgba(0,0,0,0.12)"

    # 1) Variables block (f-string)
    css_vars = f"""
<style>
:root {{
  --primary-color: {PRIMARY};
  --accent: {PRIMARY};
  --page-bg: {page_bg};
  --sidebar-bg: {side_bg};
  --text: {text_col};
  --panel-bg: {panel_bg};
  --button-bg: {button_bg};
  --chrome-bg: {chrome_bg};
  --input-bg: {input_bg};
  --border-col: {border};
  --muted: {'rgba(255,255,255,.7)' if mode == 'dark' else '#667085'};
  --bubble-bot: {'#374151' if mode == 'dark' else '#E5E7EB'};
  --bubble-user: {'#1F2937' if mode == 'dark' else '#E6F0FF'};
  --card-bord: {'rgba(255,255,255,0.12)' if mode == 'dark' else '#E5E7EB'};
  --card-hov:  {'#0F172A' if mode == 'dark' else '#EFF6FF'};
}}
"""

    # 2) All your normal CSS (plain string – no escaping)
    css_rules = """
:root{
  --radius-lg: 16px;
  --radius-md: 12px;
  --shadow: 0 4px 18px rgba(0,0,0,.06);

  --bg:    var(--page-bg);
  --panel: var(--panel-bg);
  --ink:   var(--text);
  --line:  var(--border-col);
}

/* base page */
*,
*::before,*::after{ box-sizing: border-box; }
body{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  font-size: 16px;
  line-height: 1.5;
}

/* full width container */
[data-testid="stAppViewContainer"]{
  margin: 0;
  background: var(--bg) !important;
}

/* header label */
header[data-testid="stHeader"]{
  position: relative;              /* define a positioning context */
  background: var(--bg) !important;
}

/* custom centered title in the top bar */
header[data-testid="stHeader"]::before {
  content: "Oraculum";
  color: #2563EB;
  font-weight: 700;
  font-size: 30px;
  line-height: 1;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* true center */
  pointer-events: none;            /* don't block header buttons */
  white-space: nowrap;
}
.page-sub{ color: var(--muted) !important; }

/* sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {
  background: var(--panel-bg) !important;
  border: 1px solid var(--border-col) !important;
  color: var(--text) !important;
  text-align: left !important;
  font-weight: 500 !important;
  padding: 8px 10px !important;
  border-radius: 8px !important;
  box-shadow: none !important;
  transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--input-bg) !important;
  border: 1px solid var(--primary-color) !important;
  color: var(--primary-color) !important;
}

/* chat panel */
.section{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 16px;
}
.chat-panel{
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 0;
  min-height: 520px;
  overflow: hidden;
}
.msg{ display:inline-block; max-width:70%; padding:10px 14px; border-radius:12px; margin:8px 0; font-size:15px; line-height:1.4; }
.msg.bot{ background: var(--bubble-bot); color: var(--ink); border-top-left-radius:8px; }
.msg.user{ background: var(--bubble-user); color: var(--ink); border-top-right-radius:8px; margin-left:auto; }
.chat-panel .head{
  display:flex; align-items:center; gap:8px;
  padding:10px 14px; font-weight:600;
  background: var(--input-bg);
  color: var(--text);
  border-bottom:1px solid var(--border-col);
}
.chat-panel .body{
  padding:14px 16px; background: var(--panel);
  max-height:560px; overflow:auto;
}

/* links + selection */
a{ color: var(--accent); text-decoration: none; }
a:hover{ text-decoration: underline; }
::selection{ background: var(--accent); color: #fff; }

/* scrollbars */
::-webkit-scrollbar{ width: 10px; }
::-webkit-scrollbar-track{ background: #EFF2F6; }
::-webkit-scrollbar-thumb{ background: #C9D1E0; border-radius: 6px; }
::-webkit-scrollbar-thumb:hover{ background: #AEB8CA; }

/* home cards */
.home-wrap [data-testid="stButton"] > button {  /* <- replace the long selector with this */
  display: block !important;
  text-align: left !important;
  width: 100% !important;
  border-radius: 16px !important;
  background: #F8FAFC !important;
  border: 1px solid #E5E7EB !important;
  padding: 28px 22px !important;
  min-height: 500px !important;
  box-shadow: 0 2px 6px rgba(0,0,0,.04) !important;
  color: #0F172A !important;
  transition: all 0.2s ease !important;
}
.home-wrap {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 10vh;  /* centers the content mid-page */
  text-align: center;
}

/* titles */
/* Home (centered, big) */
.hero-title, .hero-sub {
  text-align: center !important;
}
.hero-title { font-size: 36px !important; font-weight: 700 !important; color: #2563EB !important; }
.hero-sub   { font-size: 18px !important; color: var(--muted) !important; }

/* Other pages (left, smaller) */
.page-h2    { text-align: left !important; font-size: 28px !important; font-weight: 700 !important; color: #2563EB !important; }
.page-sub   { text-align: left !important; font-size: 16px !important; color: var(--muted) !important; }


/* universal hover for all buttons */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
  transition: all 0.2s ease-in-out !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
  background: #EFF6FF !important;
  border-color: #1E40AF !important;
  color: #1E40AF !important;
  box-shadow: 0 2px 6px rgba(30, 64, 175, 0.15) !important;
  transform: translateY(-1px);
}

/* ensure all containers use the page bg */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] .main {
  background: var(--bg) !important;
}
/* core content wrapper */
.block-container { background: var(--bg) !important; }
[data-testid="stSidebar"] .block-container { background: var(--sidebar-bg) !important; }

/* quick actions row sticks above the chat input */
.qa-sticky{
  position: sticky;
  bottom: 76px;           /* sits just above the chat input */
  z-index: 10;
  background: var(--bg);  /* so it doesn’t look transparent */
  padding: 6px 0;
}



</style>
"""

    st.markdown(css_vars + css_rules, unsafe_allow_html=True)