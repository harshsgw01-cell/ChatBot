import streamlit as st
import plotly.express as px
import pandas as pd
from openai import OpenAI
from ai_logic import answer_ceo_question
from dashboard import render_dashboard
from db import get_connection
from data import (
    fetch_employee_data,
    fetch_employee_details,
    fetch_instructor_performance,
    fetch_new_joiners,
    fetch_employee_trend,
    fetch_former_employees,
)
from datetime import datetime, timedelta


# =========================
# TIME-BASED GREETING
# =========================
def get_greeting() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 17:
        greeting = "Good afternoon"
    elif 17 <= hour < 21:
        greeting = "Good evening"
    else:
        greeting = "Good night"
    return f"{greeting}, CEO"


# =========================
# SESSION STATE
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mode" not in st.session_state:
    st.session_state.mode = "chat"
if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = []
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "theme_base" not in st.session_state:
    st.session_state.theme_base = st.get_option("theme.base") or "light"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ── Colour palette ──────────────────────────────────────────────────────────
_D = st.session_state.dark_mode
if _D:
    _BG = "#0D1117"
    _BG2 = "#161B22"
    _CARD = "#1C2333"
    _HOVER = "#21283A"
    _BDR = "rgba(255,255,255,0.10)"
    _BDRA = "rgba(129,140,248,0.55)"
    _T1 = "#F0F6FC"
    _T2 = "#CDD9E5"
    _T3 = "#8B949E"
    _T4 = "#6E7681"
    _ACC = "#818CF8"
    _TEAL = "#2DD4BF"
else:
    _BG = "#FFFFFF"
    _BG2 = "#FFFFFF"
    _CARD = "#FFFFFF"
    _HOVER = "#F1F4F9"
    _BDR = "rgba(0,0,0,0.07)"
    _BDRA = "rgba(99,102,241,0.35)"
    _T1 = "#0F1523"
    _T2 = "#4B5675"
    _T3 = "#6B7280"
    _T4 = "#9BA3B8"
    _ACC = "#6366F1"
    _TEAL = "#0D9488"

# Share with dashboard.py
st.session_state["is_dark"] = _D
st.session_state["plotly_theme"] = dict(
    paper_bgcolor=_CARD,
    plot_bgcolor=_CARD,
    font=dict(color=_T1, family="DM Sans, sans-serif"),
    xaxis=dict(gridcolor=_BDR, zerolinecolor=_BDR, color=_T2),
    yaxis=dict(gridcolor=_BDR, zerolinecolor=_BDR, color=_T2),
    legend=dict(font=dict(color=_T1)),
)

# =========================
# CUSTOM CSS
# =========================
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

:root {{
  --bg-primary:    {_BG};
  --bg-secondary:  {_BG2};
  --bg-card:       {_CARD};
  --bg-hover:      {_HOVER};
  --border:        {_BDR};
  --border-accent: {_BDRA};
  --text-primary:  {_T1};
  --text-secondary:{_T2};
  --text-muted:    {_T4};
  --accent-indigo: {_ACC};
  --accent-teal:   {_TEAL};
  --gradient-main: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #06B6D4 100%);
  --shadow-sm:     0 1px 4px rgba(0,0,0,0.06);
  --shadow-md:     0 4px 16px rgba(0,0,0,0.08);
  --shadow-lg:     0 12px 40px rgba(0,0,0,0.10);
  --shadow-glow:   0 0 30px rgba(99,102,241,0.12);
  --toolbar-height:3rem;
}}

* {{ font-family: 'DM Sans', -apple-system, sans-serif; box-sizing: border-box; }}
footer {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}

/* ROOT BACKGROUNDS */
html, body, #root,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .stApp, section.main {{
    background-color: {_BG} !important;
    color: {_T1} !important;
}}
/* Extra force for occasional white wrapper */
main > div > div > section > div {{
    background-color: {_BG} !important;
}}

header[data-testid="stHeader"] {{
    background: {_BG} !important;
    border-bottom: 1px solid {_BDR} !important;
    box-shadow: var(--shadow-sm) !important;
    z-index: 999 !important;
}}

.block-container {{
    padding-top: calc(var(--toolbar-height) + 1rem) !important;
    padding-bottom: 2rem;
    max-width: 1400px;
    animation: contentSlideUp 0.7s ease-out 0.1s both;
}}
@media (max-width: 768px) {{
    .block-container {{
        padding-top: calc(var(--toolbar-height) + 0.5rem) !important;
        padding-left: 0.75rem  !important;
        padding-right: 0.75rem !important;
    }}
}}

.stApp {{
    background: {_BG};
    color: {_T1};
    min-height: 100vh;
    animation: pageFadeIn 0.7s ease-out both;
}}
main [data-testid="stVerticalBlock"] {{
    animation: contentSlideUp 0.7s ease-out 0.15s both;
}}

/* TOP BAR */
.topbar-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: nowrap;
    padding: 0.65rem 0 0.55rem 0;
    gap: 0.5rem;
}}
.topbar-left {{ flex: 1 1 auto; min-width: 0; }}
.topbar-title {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.5rem;
    font-weight: 400;
    color: {_T1};
    letter-spacing: -0.02em;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.topbar-subtitle {{
    font-size: 0.78rem;
    color: {_T4};
    letter-spacing: 0.04em;
    margin-top: 0.15rem;
    text-transform: uppercase;
    white-space: nowrap;
}}
.topbar-icons {{
    display: flex;
    align-items: center;
    gap: 0.35rem;
    flex-shrink: 0;
}}
.topbar-icon-btn {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: 1px solid {_BDR};
    border-radius: 10px;
    background: {_CARD};
    font-size: 1.1rem;
    cursor: pointer;
    text-decoration: none;
    transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
    box-shadow: var(--shadow-sm);
}}
.topbar-icon-btn:hover {{
    background: {_HOVER};
    border-color: {_BDRA};
    box-shadow: 0 4px 12px rgba(99,102,241,0.12);
}}
.topbar-icon-active {{
    background: rgba(99,102,241,0.15) !important;
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}}
@media (max-width: 576px) {{
    .topbar-title   {{ font-size: 1.05rem; }}
    .topbar-subtitle{{ font-size: 0.6rem;  }}
    .topbar-icon-btn{{ width: 36px; height: 36px; font-size: 1rem; }}
}}

/* SIDEBAR */
[data-testid="stSidebar"] {{
    background: {_BG2} !important;
    border-right: 1px solid {_BDR} !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04) !important;
    margin-top: 3.5rem !important;
}}

[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] {{
    display: flex !important;
    flex-direction: column !important;
    height: 100vh !important;
    overflow: hidden !important;
    padding: 0 !important;
}}

[data-testid="stSidebar"] section[data-testid="stSidebarContent"] > div[data-testid="stVerticalBlock"] {{
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    overflow: hidden !important;
    padding: 0 0.85rem !important;
    gap: 0 !important;
}}

[data-testid="stSidebar"] section[data-testid="stSidebarContent"] > div[data-testid="stVerticalBlock"] > div {{
    flex-shrink: 0 !important;
}}

[data-testid="stSidebar"] section[data-testid="stSidebarContent"] > div[data-testid="stVerticalBlock"] > div:last-child {{
    flex: 1 1 auto !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding-bottom: 1.5rem !important;
    scrollbar-width: thin !important;
    scrollbar-color: {_T4} transparent !important;
    margin-top: 0.25rem !important;
}}
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] > div[data-testid="stVerticalBlock"] > div:last-child::-webkit-scrollbar {{
    width: 3px !important;
}}
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] > div[data-testid="stVerticalBlock"] > div:last-child::-webkit-scrollbar-thumb {{
    background: {_T4} !important;
    border-radius: 4px !important;
}}

/* SIDEBAR TEXT */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] a,
[data-testid="stSidebarContent"] p,
[data-testid="stSidebarContent"] span,
[data-testid="stSidebarContent"] div,
[data-testid="stSidebarContent"] label {{
    color: {_T2} !important;
}}
[data-testid="stSidebar"] button {{
    color: {_T2} !important;
}}

.sidebar-header-card {{
    padding: 1.1rem 0.9rem 0.9rem 0.9rem;
    border-bottom: 1px solid {_BDR};
    margin-bottom: 0.4rem;
}}
.sidebar-header-title {{
    font-family:"DM Serif Display",Georgia,serif;
    font-size:1.05rem;
    font-weight:500;
    color:{_T1} !important;
    letter-spacing:-0.01em;
    margin-bottom:0.1rem;
}}
.sidebar-header-subtitle {{
    font-size:0.68rem;
    color:{_T3} !important;
    letter-spacing:0.12em;
    text-transform:uppercase;
}}

.sidebar-newchat-wrap {{ padding: 0 0.9rem 0.6rem 0.9rem; }}
.sidebar-newchat-wrap div[data-testid="stButton"] > button {{
    width: 100%;
    justify-content: center;
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #06B6D4 100%) !important;
    border: none !important;
    color: #FFFFFF !important;
    font-size: 0.88rem;
    font-weight: 600;
    border-radius: 999px;
    padding: 0.55rem 0.9rem;
    box-shadow: 0 8px 20px rgba(99,102,241,0.25) !important;
}}
.sidebar-newchat-wrap div[data-testid="stButton"] > button:hover {{
    opacity: 0.95;
    box-shadow: 0 10px 26px rgba(99,102,241,0.32) !important;
}}

[data-testid="stSidebar"] div[data-testid="stButton"] > button {{
    background: transparent !important;
    border: none !important;
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    color: {_T2} !important;
    font-weight: 400;
    box-shadow: none !important;
    transition: all 0.2s ease;
    letter-spacing: 0.01em;
}}
[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{
    background: {_HOVER} !important;
    color: {_T1} !important;
}}

.clear-btn div[data-testid="stButton"] > button {{
    color: #EF4444 !important;
    font-size: 0.82rem !important;
}}
.clear-btn div[data-testid="stButton"] > button:hover {{
    background: rgba(239,68,68,0.07) !important;
}}
.del-btn div[data-testid="stButton"] > button {{
    color: {_T4} !important;
    font-size: 0.8rem !important;
    padding: 0.2rem 0.5rem !important;
    border-radius: 999px !important;
    width: 100% !important;
    text-align: center !important;
}}
.del-btn div[data-testid="stButton"] > button:hover {{
    color: #EF4444 !important;
    background: rgba(239,68,68,0.10) !important;
}}

[data-testid="stSidebar"] {{ width: 300px !important; }}
@media (max-width: 1024px) {{ [data-testid="stSidebar"] {{ width: 260px !important; }} }}
@media (max-width: 768px)  {{ [data-testid="stSidebar"] {{ width: 220px !important; }} }}
@media (max-width: 576px)  {{ [data-testid="stSidebar"] {{ width: 200px !important; }} }}

[data-testid="stSidebar"] [data-testid="stExpander"],
[data-testid="stSidebar"] [data-testid="stExpander"] > details,
[data-testid="stSidebar"] [data-testid="stExpander"] > details > summary,
[data-testid="stSidebar"] [data-testid="stExpander"] > details > div {{
    background-color: {_CARD} !important;
    border-color: {_BDR} !important;
    color: {_T1} !important;
    border-radius: 10px !important;
}}
[data-testid="stSidebar"] [data-testid="stExpander"] * {{ color: {_T1} !important; }}

[data-testid="stSidebar"] input {{
    background-color: {_CARD} !important;
    color: {_T1} !important;
    border-color: {_BDR} !important;
}}
[data-testid="stSidebar"] input::placeholder {{ color: {_T4} !important; }}

.section-label {{
    display: block;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {_T4} !important;
    padding: 0.5rem 0.75rem 0.25rem 0.75rem;
}}

/* MAIN TEXT */
p, span, li, td, th, caption, label,
h1, h2, h3, h4, h5, h6,
.stMarkdown, .stMarkdown *,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] *,
.element-container p, .element-container span {{
    color: {_T1} !important;
}}

/* INPUTS */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-testid="stDateInput"] input,
div[data-testid="stNumberInput"] input,
div[data-baseweb="select"] input {{
    background-color: {_CARD} !important;
    color: {_T1} !important;
    border-color: {_BDR} !important;
    border-radius: 8px !important;
    caret-color: {_ACC} !important;
    box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {{
    color: {_T4} !important;
}}

div[data-baseweb="select"] > div,
div[data-baseweb="popover"],
div[data-baseweb="menu"] {{
    background: {_CARD} !important;
    border-color: {_BDR} !important;
    color: {_T1} !important;
}}
li[role="option"] {{ background: {_CARD} !important; color: {_T1} !important; }}
li[role="option"]:hover {{ background: {_HOVER} !important; }}

/* CHAT INPUT + BOTTOM BAR */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div {{
    background: {_BG} !important;
    background-color: {_BG} !important;
    border-top: 1px solid {_BDR} !important;
}}

.stChatInputContainer,
[data-testid="stChatInputContainer"] {{
    background: {_CARD} !important;
    border: 1px solid {_BDR} !important;
    border-radius: 14px !important;
    box-shadow: var(--shadow-sm) !important;
}}
.stChatInputContainer:focus-within,
[data-testid="stChatInputContainer"]:focus-within {{
    border-color: {_BDRA} !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.10), var(--shadow-sm) !important;
}}
.stChatInputContainer textarea,
[data-testid="stChatInputContainer"] textarea {{
    background: transparent !important;
    color: {_T1} !important;
}}
.stChatInputContainer textarea::placeholder,
[data-testid="stChatInputContainer"] textarea::placeholder {{
    color: {_T4} !important;
}}
[data-testid="stChatInputContainer"] button,
.stChatInputContainer button {{
    background: transparent !important;
    color: {_ACC} !important;
    border: none !important;
}}

/* CHAT MESSAGES */
[data-testid="stChatMessage"] {{
    background: {_CARD} !important;
    border: 1px solid {_BDR} !important;
    border-radius: 12px !important;
    animation: slideInLeft 0.4s.ease-out;
}}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {{ color: {_T1} !important; }}

/* METRICS */
[data-testid="stMetric"] {{
    background: {_CARD} !important;
    border: 1px solid {_BDR} !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {{ color: {_T2} !important; }}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {{ color: {_T1} !important; font-weight: 700 !important; }}
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] * {{ color: {_TEAL} !important; }}

/* DATAFRAMES */
[data-testid="stDataFrame"], [data-testid="stTable"] {{
    background: {_CARD} !important;
    border: 1px solid {_BDR} !important;
    border-radius: 12px !important;
    overflow: hidden;
}}
[data-testid="stDataFrame"] th, [data-testid="stTable"] th {{
    background: {_BG2} !important;
    color: {_T2} !important;
    border-bottom: 1px solid {_BDR} !important;
}}
[data-testid="stDataFrame"] td, [data-testid="stTable"] td {{
    color: {_T1} !important;
    border-bottom: 1px solid {_BDR} !important;
}}

/* EXPANDER (main) */
[data-testid="stExpander"] {{
    background: {_CARD} !important;
    border: 1px solid {_BDR} !important;
    border-radius: 10px !important;
}}
[data-testid="stExpander"] summary {{ color: {_T1} !important; }}
[data-testid="stExpander"] * {{ color: {_T1} !important; }}

/* RADIO / CHECKBOX */
.stRadio label, .stRadio label *,
.stCheckbox label, .stCheckbox label *,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] * {{ color: {_T2} !important; }}

/* PLOTLY */
[data-testid="stPlotlyChart"] {{
    background: {_CARD} !important;
    border: 1px solid {_BDR} !important;
    border-radius: 14px !important;
    padding: 0.5rem !important;
    box-shadow: var(--shadow-sm) !important;
}}

/* TABS */
[data-testid="stTabs"] button {{ color: {_T2} !important; }}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {_ACC} !important;
    border-bottom-color: {_ACC} !important;
}}

/* ALERTS */
[data-testid="stAlert"] {{
    background: {_CARD} !important;
    border-color: {_BDRA} !important;
    color: {_T1} !important;
    border-radius: 10px !important;
}}
[data-testid="stAlert"] * {{ color: {_T1} !important; }}

/* CODE */
.stMarkdown code {{
    background: {_BG2} !important;
    color: {_ACC} !important;
    border: 1px solid {_BDR} !important;
    border-radius: 4px;
    padding: 0.1rem 0.35rem;
}}
.stMarkdown pre {{
    background: {_BG2} !important;
    border: 1px solid {_BDR} !important;
    border-radius: 8px !important;
    color: {_T1} !important;
}}

hr {{ border-color: {_BDR} !important; margin: 0.5rem 0 1rem 0 !important; }}

/* SCROLLBARS */
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {_T4}; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: {_T3}; }}

/* WELCOME */
.welcome-container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 42vh;
    text-align: center;
    padding: 3rem 2rem;
    animation: contentSlideUp 0.8s ease-out 0.2s both;
}}
.welcome-orb {{
    width: 88px;
    height: 88px;
    background: conic-gradient(from 180deg, #6366F1, #8B5CF6, #06B6D4, #6366F1);
    border-radius: 50%;
    margin-bottom: 2rem;
    position: relative;
    animation: orbSpin 10s linear infinite, orbPulse 3s ease-in-out infinite, fadeInScale 0.7s ease-out 0.1s both;
    box-shadow: 0 8px 40px rgba(99,102,241,0.25), 0 0 80px rgba(99,102,241,0.1);
}}
.welcome-greeting {{
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.4rem;
    font-weight: 400;
    color: {_T1};
    letter-spacing: -0.03em;
    margin-bottom: 0.75rem;
}}
.welcome-sub {{
    font-size: 0.95rem;
    color: {_T2};
    max-width: 480px;
    line-height: 1.75;
}}

/* SUGGESTION CARDS - force dark bg / white text */
section.main .block-container > div .stColumns div[data-testid="column"] div[data-testid="stButton"] > button {{
    height: auto !important;
    min-height: 90px !important;
    white-space: pre-wrap !important;
    text-align: left !important;
    padding: 1.25rem 1.5rem !important;
    background-color: {_CARD} !important;
    background: {_CARD} !important;
    border: 1px solid {_BDR} !important;
    border-radius: 14px !important;
    color: {_T1} !important;
    font-size: 0.875rem !important;
    line-height: 1.6 !important;
    font-weight: 400 !important;
    box-shadow: var(--shadow-sm) !important;
    transition: background 0.2s, border-color 0.2s, box-shadow 0.2s !important;
}}
section.main .block-container > div .stColumns div[data-testid="column"] div[data-testid="stButton"] > button:hover {{
    background-color: {_HOVER} !important;
    background: {_HOVER} !important;
    border-color: {_BDRA} !important;
    color: {_T1} !important;
}}
section.main .block-container > div .stColumns div[data-testid="column"] div[data-testid="stButton"] > button * {{
    color: {_T1} !important;
}}

/* GENERIC MAIN BUTTONS */
.stApp main div[data-testid="stButton"] > button {{
    background-color: {_CARD} !important;
    background: {_CARD} !important;
    color: {_T2} !important;
    border: 1px solid {_BDR} !important;
    border-radius: 8px !important;
}}
.stApp main div[data-testid="stButton"] > button:hover {{
    background-color: {_HOVER} !important;
    background: {_HOVER} !important;
    color: {_T1} !important;
    border-color: {_BDRA} !important;
}}

.stChatMessage {{ animation: slideInLeft 0.4s ease-out; }}

/* KEYFRAMES */
@keyframes orbSpin {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
@keyframes orbPulse {{
    0%, 100% {{ box-shadow: 0 8px 40px rgba(99,102,241,0.25), 0 0 80px rgba(99,102,241,0.1); }}
    50%       {{ box-shadow: 0 8px 60px rgba(99,102,241,0.35), 0 0 100px rgba(99,102,241,0.18); }}
}}
@keyframes pageFadeIn      {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@keyframes contentSlideUp  {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}

@media (max-width: 576px) {{
    .welcome-greeting {{ font-size: 1.5rem; }}
    [data-testid="stMetricValue"] {{ font-size: 1.4rem; }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# API & SESSION STATE
# =========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
MODEL = "gpt-4o-mini"

# =========================
# THEME TOGGLE
# =========================
def apply_theme():
    base = st.session_state.theme_base
    st._config.set_option("theme.base", base)  # type: ignore
    st.rerun()

# =========================
# SAVE CHAT HELPER
# =========================
def save_current_chat():
    if not st.session_state.chat_history:
        return
    first_user_msg = next(
        (m["content"] for m in st.session_state.chat_history if m["role"] == "user"),
        "Untitled Chat",
    )
    title = first_user_msg[:40] + "..." if len(first_user_msg) > 40 else first_user_msg
    timestamp = datetime.now().isoformat()
    chat_data = {
        "title": title,
        "messages": st.session_state.chat_history.copy(),
        "timestamp": timestamp,
    }
    if st.session_state.current_chat_index is not None:
        st.session_state.saved_chats[st.session_state.current_chat_index] = chat_data
    else:
        st.session_state.saved_chats.append(chat_data)
        st.session_state.current_chat_index = len(st.session_state.saved_chats) - 1

# =========================
# LOAD STATIC / BASE DATA
# =========================
employee_metrics = fetch_employee_data()
employees_df = fetch_employee_details()

# =========================
# Connect to PostgreSQL
# =========================
conn = get_connection()
if conn:
    cursor = conn.cursor()
else:
    st.error("Failed to connect to the database!")

# =========================
# TOP BAR
# =========================
_qp = st.query_params.get("mode", None)
if _qp in ("chat", "dashboard"):
    st.session_state.mode = _qp
    st.query_params.clear()

_active_chat = "topbar-icon-active" if st.session_state.mode == "chat" else ""
_active_dash = "topbar-icon-active" if st.session_state.mode == "dashboard" else ""

st.markdown(
    f"""
    <div class="topbar-row">
      <div class="topbar-left">
        <div class="topbar-title">CEO AI Assistant</div>
        <div class="topbar-subtitle">Strategic HR &amp; Workforce Intelligence</div>
      </div>
      <div class="topbar-icons">
        <a class="topbar-icon-btn {_active_chat}"
           href="?mode=chat" title="Chat">💬</a>
        <a class="topbar-icon-btn {_active_dash}"
           href="?mode=dashboard" title="Dashboard">📊</a>
      </div>
    </div>
    <hr style="border:none;border-top:1px solid {_BDR};margin:0 0 1rem 0;"/>
    """,
    unsafe_allow_html=True,
)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-header-card">
          <div class="sidebar-header-title">CEO AI Assistant</div>
          <div class="sidebar-header-subtitle">Executive Workspace</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-newchat-wrap">', unsafe_allow_html=True)
    if st.button("＋  New Chat", key="new_chat_btn"):
        st.session_state.chat_history = []
        st.session_state.current_chat_index = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr class='sidebar-divider'/>", unsafe_allow_html=True)

    search_query = st.text_input(
        "Search",
        placeholder="Search conversations...",
        label_visibility="collapsed",
        key="search_chats",
    )

    st.markdown("<hr class='sidebar-divider'/>", unsafe_allow_html=True)

    with st.expander("⚙  Settings"):
        new_name = st.text_input(
            "Your Name",
            value=st.session_state.get("user_name", ""),
            key="user_name_input",
        )
        st.session_state.user_name = new_name

        theme_choice = st.radio(
            "Theme",
            options=["Light", "Dark"],
            index=0 if not st.session_state.dark_mode else 1,
            horizontal=True,
            key="theme_radio",
        )
        if theme_choice == "Dark" and not st.session_state.dark_mode:
            st.session_state.dark_mode = True
            st.rerun()
        elif theme_choice == "Light" and st.session_state.dark_mode:
            st.session_state.dark_mode = False
            st.rerun()

    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("Clear Current Chat", key="clear_chat_btn"):
        st.session_state.chat_history = []
        st.session_state.current_chat_index = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr class='sidebar-divider'/>", unsafe_allow_html=True)

    saved = st.session_state.get("saved_chats", [])

    def render_chat_row(i, chat, key_prefix):
        title = chat.get("title", f"Chat {i+1}")
        short = title[:25] + "..." if len(title) > 25 else title
        col_t, col_d = st.columns([4, 1])
        with col_t:
            if st.button(short, key=f"{key_prefix}_open_{i}"):
                st.session_state.current_chat_index = i
                st.session_state.chat_history = chat["messages"].copy()
                st.rerun()
        with col_d:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("✕", key=f"{key_prefix}_del_{i}", help="Delete"):
                st.session_state.saved_chats.pop(i)
                if st.session_state.current_chat_index == i:
                    st.session_state.chat_history = []
                    st.session_state.current_chat_index = None
                elif (
                    st.session_state.current_chat_index is not None
                    and st.session_state.current_chat_index > i
                ):
                    st.session_state.current_chat_index -= 1
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    if search_query:
        st.markdown(
            "<span class='section-label'>Search Results</span>",
            unsafe_allow_html=True,
        )
        filtered = [
            (i, chat)
            for i, chat in enumerate(saved)
            if search_query.lower() in chat.get("title", "").lower()
        ]
        if filtered:
            for i, chat in filtered:
                render_chat_row(i, chat, "search")
        else:
            st.markdown(
                f"<p style='font-size:0.82rem;color:{_T4};padding:0 0.75rem;'>No results found</p>",
                unsafe_allow_html=True,
            )
    else:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        groups = {"Today": [], "Yesterday": [], "Previous 7 Days": [], "Older": []}

        for i, chat in enumerate(reversed(saved)):
            real_index = len(saved) - 1 - i
            ts = chat.get("timestamp")
            chat_date = None
            if ts:
                try:
                    chat_date = datetime.fromisoformat(ts).date()
                except Exception:
                    pass
            if chat_date == today:
                groups["Today"].append((real_index, chat))
            elif chat_date == yesterday:
                groups["Yesterday"].append((real_index, chat))
            elif chat_date and (today - chat_date).days <= 7:
                groups["Previous 7 Days"].append((real_index, chat))
            else:
                groups["Older"].append((real_index, chat))

        has_any = any(groups.values())
        if not has_any:
            st.markdown(
                f"<p style='font-size:0.82rem;color:{_T4};padding:0 0.75rem;'>No conversations yet</p>",
                unsafe_allow_html=True,
            )
        else:
            for group_name, chats in groups.items():
                if chats:
                    st.markdown(
                        f"<span class='section-label'>{group_name}</span>",
                        unsafe_allow_html=True,
                    )
                    for i, chat in chats:
                        render_chat_row(i, chat, "recent")

# =========================
# LOAD DATA FROM DATABASE
# =========================
employee = fetch_employee_data()
new_joiners_df = fetch_new_joiners()
instructor_df = fetch_instructor_performance()
employee_trend_df = fetch_employee_trend()
former_df = fetch_former_employees()

# =========================
# MAIN CONTENT
# =========================
if st.session_state.mode == "chat":
    if len(st.session_state.chat_history) == 0:
        st.markdown(
            f"""
            <div class="welcome-container">
                <div class="welcome-orb"></div>
                <div class="welcome-greeting">{get_greeting()}</div>
                <div class="welcome-sub">
                    What Can I Help You With Today
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        user_q = None
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                "Show me a summary of our workforce and key risks", key="s1"
            ):
                user_q = (
                    "Give me an executive summary of workforce and key HR risks."
                )
        with col2:
            if st.button(
                "Which departments have the highest turnover?", key="s2"
            ):
                user_q = "Which departments have the highest turnover and why?"
        with col3:
            if st.button(
                "How are new joiners performing in probation?", key="s3"
            ):
                user_q = (
                    "How are new joiners performing and how many are at risk in probation?"
                )

        if user_q:
            st.session_state.chat_history.append(
                {"role": "user", "content": user_q}
            )
            with st.chat_message("user"):
                st.markdown(user_q)
            with st.spinner("Analyzing..."):
                answer = answer_ceo_question(user_q)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": answer}
            )
            with st.chat_message("assistant"):
                st.markdown(answer)
            save_current_chat()
            st.rerun()

    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_input = st.chat_input("Ask your CEO Assistant anything...")
    if user_input:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.spinner("Analyzing..."):
            answer = answer_ceo_question(user_input)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )
        with st.chat_message("assistant"):
            st.markdown(answer)
        save_current_chat()
        st.rerun()

else:
    render_dashboard(
        employee=employee,
        employees_df=employees_df,
        new_joiners_df=new_joiners_df,
        instructor_df=instructor_df,
        employee_trend_df=employee_trend_df,
        former_df=former_df,
    )
