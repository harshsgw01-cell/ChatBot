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
for key, default in [
    ("chat_history", []),
    ("mode", "chat"),
    ("saved_chats", []),
    ("current_chat_index", None),
    ("user_name", ""),
    ("dark_mode", False),
    ("chip_prompt", None),
    ("delete_index", None),
    ("open_index", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if "theme_base" not in st.session_state:
    st.session_state.theme_base = st.get_option("theme.base") or "light"


# ── Colour palette ───────────────────────────────────────────────────────────
_D = st.session_state.dark_mode
if _D:
    _BG   = "#0D1117"; _BG2  = "#161B22"; _CARD = "#1C2333"; _HOVER = "#21283A"
    _BDR  = "rgba(255,255,255,0.10)";     _BDRA = "rgba(129,140,248,0.55)"
    _T1   = "#F0F6FC"; _T2   = "#CDD9E5"; _T3   = "#8B949E"; _T4    = "#6E7681"
    _ACC  = "#818CF8"; _TEAL = "#2DD4BF"
    _CHIP_BG   = "#1C2333"; _CHIP_BDR  = "rgba(255,255,255,0.10)"
    _CHIP_HBG  = "#21283A"; _CHIP_HBDR = "rgba(129,140,248,0.45)"
    _ROW_BG    = "#1C2333"; _ROW_HOVER = "#21283A"
    _ROW_BDR   = "rgba(255,255,255,0.06)"
    _DEL_CLR   = "#6E7681"; _DEL_HCLR  = "#EF4444"
    _DEL_HBG   = "rgba(239,68,68,0.15)"
else:
    _BG   = "#FFFFFF"; _BG2  = "#F8F9FC"; _CARD = "#FFFFFF"; _HOVER = "#F1F4F9"
    _BDR  = "rgba(0,0,0,0.07)";           _BDRA = "rgba(99,102,241,0.35)"
    _T1   = "#0F1523"; _T2   = "#4B5675"; _T3   = "#6B7280"; _T4    = "#9BA3B8"
    _ACC  = "#6366F1"; _TEAL = "#0D9488"
    _CHIP_BG   = "#F4F5FB"; _CHIP_BDR  = "rgba(99,102,241,0.12)"
    _CHIP_HBG  = "#ECEEFF"; _CHIP_HBDR = "rgba(99,102,241,0.35)"
    _ROW_BG    = "#F8F9FC"; _ROW_HOVER = "#F1F4F9"
    _ROW_BDR   = "rgba(0,0,0,0.05)"
    _DEL_CLR   = "#9BA3B8"; _DEL_HCLR  = "#EF4444"
    _DEL_HBG   = "rgba(239,68,68,0.10)"

st.session_state["is_dark"] = _D
st.session_state["plotly_theme"] = dict(
    paper_bgcolor=_CARD, plot_bgcolor=_CARD,
    font=dict(color=_T1, family="DM Sans, sans-serif"),
    xaxis=dict(gridcolor=_BDR, zerolinecolor=_BDR, color=_T2),
    yaxis=dict(gridcolor=_BDR, zerolinecolor=_BDR, color=_T2),
    legend=dict(font=dict(color=_T1)),
)


# =========================
# CUSTOM CSS
# =========================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

:root {{
  --bg-primary:{_BG}; --bg-secondary:{_BG2}; --bg-card:{_CARD}; --bg-hover:{_HOVER};
  --border:{_BDR}; --border-accent:{_BDRA};
  --text-primary:{_T1}; --text-secondary:{_T2}; --text-muted:{_T4};
  --accent-indigo:{_ACC}; --accent-teal:{_TEAL};
  --gradient-main:linear-gradient(135deg,#6366F1 0%,#8B5CF6 50%,#06B6D4 100%);
  --shadow-sm:0 1px 4px rgba(0,0,0,0.06); --shadow-md:0 4px 16px rgba(0,0,0,0.08);
  --toolbar-height:3rem;
}}

* {{ font-family:'DM Sans',-apple-system,sans-serif; box-sizing:border-box; }}
footer {{ visibility:hidden; }}
[data-testid="stDecoration"] {{ display:none; }}

html,body,#root,[data-testid="stAppViewContainer"],[data-testid="stAppViewBlockContainer"],
.main,.stApp,section.main {{ background-color:{_BG} !important; color:{_T1} !important; }}
main > div > div > section > div {{ background-color:{_BG} !important; }}

header[data-testid="stHeader"] {{
    background:{_BG} !important; border-bottom:1px solid {_BDR} !important;
    box-shadow:var(--shadow-sm) !important; z-index:999 !important;
}}

.block-container {{
    padding-top:calc(var(--toolbar-height) + 1rem) !important;
    padding-bottom:2rem; max-width:1400px;
    animation:contentSlideUp 0.7s ease-out 0.1s both;
}}
@media(max-width:768px) {{
    .block-container {{
        padding-top:calc(var(--toolbar-height) + 0.5rem) !important;
        padding-left:0.75rem !important; padding-right:0.75rem !important;
    }}
}}

.stApp {{ background:{_BG}; color:{_T1}; min-height:100vh; animation:pageFadeIn 0.7s ease-out both; }}
main [data-testid="stVerticalBlock"] {{ animation:contentSlideUp 0.7s ease-out 0.15s both; }}

/* TOP BAR */
.topbar-row {{ display:flex; align-items:center; justify-content:space-between;
    flex-wrap:nowrap; padding:0.65rem 0 0.55rem 0; gap:0.5rem; }}
.topbar-left {{ flex:1 1 auto; min-width:0; }}
.topbar-title {{ font-family:'DM Serif Display',Georgia,serif; font-size:1.5rem;
    font-weight:400; color:{_T1}; letter-spacing:-0.02em; line-height:1.2;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.topbar-subtitle {{ font-size:0.78rem; color:{_T4}; letter-spacing:0.04em;
    margin-top:0.15rem; text-transform:uppercase; white-space:nowrap; }}
.topbar-icons {{ display:flex; align-items:center; gap:0.35rem; flex-shrink:0; }}
.topbar-icon-btn {{ display:inline-flex; align-items:center; justify-content:center;
    width:40px; height:40px; border:1px solid {_BDR}; border-radius:10px;
    background:{_CARD}; font-size:1.1rem; cursor:pointer; text-decoration:none;
    transition:background 0.2s,border-color 0.2s,box-shadow 0.2s; box-shadow:var(--shadow-sm); }}
.topbar-icon-btn:hover {{ background:{_HOVER}; border-color:{_BDRA};
    box-shadow:0 4px 12px rgba(99,102,241,0.12); }}
.topbar-icon-active {{ background:rgba(99,102,241,0.15) !important;
    border-color:rgba(99,102,241,0.5) !important; box-shadow:0 0 0 3px rgba(99,102,241,0.12) !important; }}
@media(max-width:576px) {{
    .topbar-title {{ font-size:1.05rem; }} .topbar-subtitle {{ font-size:0.6rem; }}
    .topbar-icon-btn {{ width:36px; height:36px; font-size:1rem; }}
}}

/* ══════════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    background:{_BG2} !important;
    border-right:1px solid {_BDR} !important;
    box-shadow:2px 0 12px rgba(0,0,0,0.04) !important;
    margin-top:3.5rem !important;
    overflow:hidden !important;
}}

/* Let the inner content scroll naturally */
[data-testid="stSidebar"] > div:first-child {{
    height:calc(100vh - 3.5rem) !important;
    overflow-y:auto !important;
    overflow-x:hidden !important;
    padding:0 !important;
    scrollbar-width:thin !important;
    scrollbar-color:{_T3} transparent !important;
    -webkit-overflow-scrolling:touch !important;
}}
[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar {{ width:4px !important; }}
[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb {{
    background:{_T3} !important; border-radius:4px !important;
}}
[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-track {{
    background:transparent !important;
}}

[data-testid="stSidebar"] section[data-testid="stSidebarContent"] {{
    padding:0 !important;
    overflow:visible !important;
}}

[data-testid="stSidebar"] section[data-testid="stSidebarContent"] > div[data-testid="stVerticalBlock"] {{
    padding:0 0.75rem !important;
    gap:0 !important;
    overflow:visible !important;
}}

[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label,[data-testid="stSidebar"] small,[data-testid="stSidebar"] a,
[data-testid="stSidebarContent"] p,[data-testid="stSidebarContent"] span,
[data-testid="stSidebarContent"] div,[data-testid="stSidebarContent"] label {{ color:{_T2} !important; }}
[data-testid="stSidebar"] button {{ color:{_T2} !important; }}

.sidebar-header-card {{ padding:1.1rem 0.9rem 0.9rem; border-bottom:1px solid {_BDR}; margin-bottom:0.4rem; }}
.sidebar-header-title {{ font-family:"DM Serif Display",Georgia,serif; font-size:1.05rem;
    font-weight:500; color:{_T1} !important; letter-spacing:-0.01em; margin-bottom:0.1rem; }}
.sidebar-header-subtitle {{ font-size:0.68rem; color:{_T3} !important; letter-spacing:0.12em; text-transform:uppercase; }}

.sidebar-newchat-wrap {{ padding:0 0.15rem 0.6rem; }}
.sidebar-newchat-wrap div[data-testid="stButton"] > button {{
    width:100%; justify-content:center;
    background:linear-gradient(135deg,#6366F1 0%,#8B5CF6 50%,#06B6D4 100%) !important;
    border:none !important; color:#FFFFFF !important; font-size:0.88rem; font-weight:600;
    border-radius:999px; padding:0.55rem 0.9rem;
    box-shadow:0 8px 20px rgba(99,102,241,0.25) !important; }}
.sidebar-newchat-wrap div[data-testid="stButton"] > button:hover {{
    opacity:0.95; box-shadow:0 10px 26px rgba(99,102,241,0.32) !important; }}

/* Generic sidebar buttons (except delete icon) */
[data-testid="stSidebar"] div[data-testid="stButton"]:not(.del-btn) > button {{
    background:transparent !important;
    border:none !important;
    border-radius:8px;
    padding:0.5rem 0.75rem;
    font-size:0.875rem;
    color:{_T2} !important;
    font-weight:400;
    box-shadow:none !important;
    transition:all 0.2s ease;
    letter-spacing:0.01em;
}}
[data-testid="stSidebar"] div[data-testid="stButton"]:not(.del-btn) > button:hover {{
    background:{_HOVER} !important;
    color:{_T1} !important;
}}

.clear-btn div[data-testid="stButton"] > button {{ color:#EF4444 !important; font-size:0.82rem !important; }}
.clear-btn div[data-testid="stButton"] > button:hover {{ background:rgba(239,68,68,0.07) !important; }}

[data-testid="stSidebar"] {{ width:300px !important; }}
@media(max-width:1024px) {{ [data-testid="stSidebar"] {{ width:260px !important; }} }}
@media(max-width:768px)  {{ [data-testid="stSidebar"] {{ width:220px !important; }} }}
@media(max-width:576px)  {{ [data-testid="stSidebar"] {{ width:200px !important; }} }}

/* CHAT ROW — full-width button with hover delete icon (ChatGPT style) */

/* Wrapper for each chat history row */
.chat-row-wrap {{
    position:relative;
    width:100%;
    margin-bottom:2px;
}}

/* The open-chat button fills the full row */
.chat-row-wrap > div[data-testid="stButton"] > button {{
    width:100% !important;
    text-align:left !important;
    padding:0.5rem 2.2rem 0.75rem 0.75rem !important;
    font-size:0.84rem !important;
    color:{_T2} !important;
    background:{_ROW_BG} !important;
    border:1px solid {_ROW_BDR} !important;
    border-radius:8px !important;
    white-space:nowrap !important;
    overflow:hidden !important;
    text-overflow:ellipsis !important;
    display:block !important;
    box-shadow:none !important;
}}
.chat-row-wrap > div[data-testid="stButton"] > button:hover {{
    background:{_ROW_HOVER} !important;
    color:{_T1} !important;
    border-color:{_BDR} !important;
}}

/* Delete button wrapper — absolutely positioned top-right of the row */
.del-wrap {{
    position:absolute;
    top:50%;
    right:4px;
    transform:translateY(-50%);
    z-index:10;
    width:28px;
    height:28px;
    display:flex;
    align-items:center;
    justify-content:center;

    /* hide by default */
    opacity:0;
    pointer-events:none;
}}

/* show delete icon only when hover row */
.chat-row-wrap:hover .del-wrap {{
    opacity:1;
    pointer-events:auto;
}}

.del-wrap div[data-testid="stButton"] {{
    width:28px !important;
    height:28px !important;
}}
.del-wrap div[data-testid="stButton"] > button {{
    width:28px !important;
    height:28px !important;
    min-width:0 !important;
    padding:0 !important;
    font-size:0.75rem !important;
    color:{_DEL_CLR} !important;
    background:transparent !important;
    border:none !important;
    border-radius:6px !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    box-shadow:none !important;
    line-height:1 !important;
}}

[data-testid="stSidebar"] [data-testid="stExpander"],
[data-testid="stSidebar"] [data-testid="stExpander"] > details,
[data-testid="stSidebar"] [data-testid="stExpander"] > details > summary,
[data-testid="stSidebar"] [data-testid="stExpander"] > details > div {{
    background-color:{_CARD} !important; border-color:{_BDR} !important;
    color:{_T1} !important; border-radius:10px !important; }}
[data-testid="stSidebar"] [data-testid="stExpander"] * {{ color:{_T1} !important; }}
[data-testid="stSidebar"] input {{ background-color:{_CARD} !important; color:{_T1} !important; border-color:{_BDR} !important; }}
[data-testid="stSidebar"] input::placeholder {{ color:{_T4} !important; }}
.section-label {{ display:block; font-size:0.68rem; font-weight:600; letter-spacing:0.12em;
    text-transform:uppercase; color:{_T4} !important; padding:0.5rem 0.1rem 0.25rem; }}

p,span,li,td,th,caption,label,h1,h2,h3,h4,h5,h6,
.stMarkdown,.stMarkdown *,[data-testid="stMarkdownContainer"],[data-testid="stMarkdownContainer"] *,
.element-container p,.element-container span {{ color:{_T1} !important; }}

[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,
div[data-baseweb="input"] input,div[data-baseweb="textarea"] textarea,
div[data-testid="stDateInput"] input,div[data-testid="stNumberInput"] input,
div[data-baseweb="select"] input {{
    background-color:{_CARD} !important; color:{_T1} !important; border-color:{_BDR} !important;
    border-radius:8px !important; caret-color:{_ACC} !important; box-shadow:var(--shadow-sm) !important; }}
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder {{ color:{_T4} !important; }}

div[data-baseweb="select"] > div,div[data-baseweb="popover"],div[data-baseweb="menu"] {{
    background:{_CARD} !important; border-color:{_BDR} !important; color:{_T1} !important; }}
li[role="option"] {{ background:{_CARD} !important; color:{_T1} !important; }}
li[role="option"]:hover {{ background:{_HOVER} !important; }}

[data-testid="stBottom"],[data-testid="stBottom"] > div,
.stChatFloatingInputContainer,.stChatFloatingInputContainer > div {{
    background:{_BG} !important; background-color:{_BG} !important; border-top:1px solid {_BDR} !important; }}
.stChatInputContainer,[data-testid="stChatInputContainer"] {{
    background:{_CARD} !important; border:1px solid {_BDR} !important;
    border-radius:14px !important; box-shadow:var(--shadow-sm) !important; }}
.stChatInputContainer:focus-within,[data-testid="stChatInputContainer"]:focus-within {{
    border-color:{_BDRA} !important; box-shadow:0 0 0 3px rgba(99,102,241,0.10),var(--shadow-sm) !important; }}
.stChatInputContainer textarea,[data-testid="stChatInputContainer"] textarea {{
    background:transparent !important; color:{_T1} !important; }}
.stChatInputContainer textarea::placeholder,[data-testid="stChatInputContainer"] textarea::placeholder {{ color:{_T4} !important; }}
[data-testid="stChatInputContainer"] button,.stChatInputContainer button {{
    background:transparent !important; color:{_ACC} !important; border:none !important; }}

[data-testid="stChatMessage"] {{ background:{_CARD} !important; border:1px solid {_BDR} !important;
    border-radius:12px !important; animation:slideInLeft 0.4s ease-out; }}
[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {{ color:{_T1} !important; }}

[data-testid="stMetric"] {{ background:{_CARD} !important; border:1px solid {_BDR} !important;
    border-radius:12px !important; padding:1rem !important; }}
[data-testid="stMetricLabel"],[data-testid="stMetricLabel"] * {{ color:{_T2} !important; }}
[data-testid="stMetricValue"],[data-testid="stMetricValue"] * {{ color:{_T1} !important; font-weight:700 !important; }}
[data-testid="stMetricDelta"],[data-testid="stMetricDelta"] * {{ color:{_TEAL} !important; }}

[data-testid="stDataFrame"],[data-testid="stTable"] {{ background:{_CARD} !important;
    border:1px solid {_BDR} !important; border-radius:12px !important; overflow:hidden; }}
[data-testid="stDataFrame"] th,[data-testid="stTable"] th {{ background:{_BG2} !important;
    color:{_T2} !important; border-bottom:1px solid {_BDR} !important; }}
[data-testid="stDataFrame"] td,[data-testid="stTable"] td {{ color:{_T1} !important; border-bottom:1px solid {_BDR} !important; }}

[data-testid="stExpander"] {{ background:{_CARD} !important; border:1px solid {_BDR} !important; border-radius:10px !important; }}
[data-testid="stExpander"] summary {{ color:{_T1} !important; }}
[data-testid="stExpander"] * {{ color:{_T1} !important; }}

.stRadio label,.stRadio label *,.stCheckbox label,.stCheckbox label *,
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] * {{ color:{_T2} !important; }}

[data-testid="stPlotlyChart"] {{ background:{_CARD} !important; border:1px solid {_BDR} !important;
    border-radius:14px !important; padding:0.5rem !important; box-shadow:var(--shadow-sm) !important; }}
[data-testid="stTabs"] button {{ color:{_T2} !important; }}
[data-testid="stTabs"] button[aria-selected="true"] {{ color:{_ACC} !important; border-bottom-color:{_ACC} !important; }}
[data-testid="stAlert"] {{ background:{_CARD} !important; border-color:{_BDRA} !important;
    color:{_T1} !important; border-radius:10px !important; }}
[data-testid="stAlert"] * {{ color:{_T1} !important; }}

.stMarkdown code {{ background:{_BG2} !important; color:{_ACC} !important;
    border:1px solid {_BDR} !important; border-radius:4px; padding:0.1rem 0.35rem; }}
.stMarkdown pre {{ background:{_BG2} !important; border:1px solid {_BDR} !important;
    border-radius:8px !important; color:{_T1} !important; }}

hr {{ border-color:{_BDR} !important; margin:0.5rem 0 1rem 0 !important; }}
::-webkit-scrollbar {{ width:4px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:{_T4}; border-radius:4px; }}
::-webkit-scrollbar-thumb:hover {{ background:{_T3}; }}

/* ── WELCOME ── */
.welcome-container {{
    display:flex; flex-direction:column; align-items:center;
    justify-content:center; min-height:38vh; text-align:center;
    padding:3rem 2rem 0.5rem;
    animation:contentSlideUp 0.8s ease-out 0.2s both;
}}
.welcome-orb {{
    width:80px; height:80px;
    background:conic-gradient(from 180deg,#6366F1,#8B5CF6,#06B6D4,#6366F1);
    border-radius:50%; margin-bottom:1.75rem;
    animation:orbSpin 10s linear infinite,orbPulse 3s ease-in-out infinite;
    box-shadow:0 8px 40px rgba(99,102,241,0.35),0 0 80px rgba(99,102,241,0.15);
}}
.welcome-greeting {{
    font-family:'DM Serif Display',Georgia,serif; font-size:2.4rem;
    font-weight:400; color:{_T1}; letter-spacing:-0.03em; margin-bottom:0.5rem;
}}
.welcome-sub {{
    font-size:0.92rem; color:{_T3}; line-height:1.6; margin-bottom:1.6rem;
}}

/* ── CHIP ROW ── */
.chip-row {{
    display:flex; justify-content:center; gap:0.6rem; flex-wrap:wrap;
    margin:0 auto 0.5rem auto; max-width:680px; padding:0 1rem;
}}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {{
    display:inline-flex !important; align-items:center !important; gap:0.35rem !important;
    padding:0.48rem 1.15rem !important; background:{_CHIP_BG} !important;
    border:1px solid {_CHIP_BDR} !important; border-radius:999px !important;
    font-size:0.83rem !important; font-weight:500 !important; color:{_T2} !important;
    cursor:pointer !important; white-space:nowrap !important;
    font-family:'DM Sans',-apple-system,sans-serif !important;
    transition:background 0.18s,border-color 0.18s,color 0.18s,box-shadow 0.18s !important;
    letter-spacing:0.01em !important; outline:none !important;
    box-shadow:none !important; width:auto !important; min-width:0 !important;
}}
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button:hover {{
    background:{_CHIP_HBG} !important; border-color:{_CHIP_HBDR} !important;
    color:{_ACC} !important; box-shadow:0 2px 12px rgba(99,102,241,0.15) !important;
}}
div[data-testid="stHorizontalBlock"] {{
    justify-content:center !important; gap:0.5rem !important; flex-wrap:wrap !important;
}}
@media(max-width:768px) {{
    div[data-testid="stHorizontalBlock"] {{
        justify-content:center !important; align-items:center !important;
        flex-wrap:wrap !important; margin:0 auto !important; width:100% !important; gap:0.4rem !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
        flex:0 0 auto !important; width:auto !important; min-width:0 !important;
    }}
    .welcome-container {{
        padding:2rem 1rem 0.5rem !important; width:100% !important;
        align-items:center !important; text-align:center !important;
    }}
}}
@media(max-width:576px) {{
    .chip-row {{ gap:0.4rem; padding:0 0.5rem; }}
    div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {{
        font-size:0.76rem !important; padding:0.4rem 0.85rem !important;
    }}
    .welcome-greeting {{ font-size:1.7rem; }}
    .welcome-orb {{ width:64px; height:64px; }}
    div[data-testid="stHorizontalBlock"] {{
        justify-content:center !important; align-items:center !important;
        flex-wrap:wrap !important; margin:0 auto !important; width:100% !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
        flex:0 0 auto !important; width:auto !important; min-width:0 !important;
    }}
    .welcome-container {{
        padding:1.5rem 0.75rem 0.5rem !important; width:100% !important;
        align-items:center !important; text-align:center !important;
    }}
}}

@keyframes orbSpin  {{ from {{ transform:rotate(0deg); }} to {{ transform:rotate(360deg); }} }}
@keyframes orbPulse {{
    0%,100% {{ box-shadow:0 8px 40px rgba(99,102,241,0.25),0 0 80px rgba(99,102,241,0.1); }}
    50%      {{ box-shadow:0 8px 60px rgba(99,102,241,0.35),0 0 100px rgba(99,102,241,0.18); }}
}}
@keyframes pageFadeIn     {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}
@keyframes contentSlideUp {{ from {{ opacity:0; transform:translateY(20px); }} to {{ opacity:1; transform:translateY(0); }} }}
@keyframes slideInLeft    {{ from {{ opacity:0; transform:translateX(-10px); }} to {{ opacity:1; transform:translateX(0); }} }}
</style>
""", unsafe_allow_html=True)


# =========================
# API CLIENT
# =========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
MODEL = "gpt-4o-mini"


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
    title = first_user_msg[:40] + ("..." if len(first_user_msg) > 40 else "")
    chat_data = {
        "title": title,
        "messages": st.session_state.chat_history.copy(),
        "timestamp": datetime.now().isoformat(),
    }
    idx = st.session_state.current_chat_index
    if idx is not None:
        st.session_state.saved_chats[idx] = chat_data
    else:
        st.session_state.saved_chats.append(chat_data)
        st.session_state.current_chat_index = len(st.session_state.saved_chats) - 1


# =========================
# LOAD DATA
# =========================
employee_metrics = fetch_employee_data()
employees_df     = fetch_employee_details()

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

st.markdown(f"""
<div class="topbar-row">
  <div class="topbar-left">
    <div class="topbar-title">CEO AI Assistant</div>
    <div class="topbar-subtitle">Strategic HR &amp; Workforce Intelligence</div>
  </div>
  <div class="topbar-icons">
    <a class="topbar-icon-btn {_active_chat}"
       href="?mode=chat"
       target="_self"
       title="Chat">💬</a>
    <a class="topbar-icon-btn {_active_dash}"
       href="?mode=dashboard"
       target="_self"
       title="Dashboard">📊</a>
  </div>
</div>
<hr style="border:none;border-top:1px solid {_BDR};margin:0 0 1rem 0;"/>
""", unsafe_allow_html=True)


# =========================
# HANDLE DEFERRED ACTIONS
# =========================
if st.session_state.open_index is not None:
    idx = st.session_state.open_index
    st.session_state.open_index = None
    saved_list = st.session_state.saved_chats
    if 0 <= idx < len(saved_list):
        st.session_state.current_chat_index = idx
        st.session_state.chat_history = saved_list[idx]["messages"].copy()
        st.session_state.chip_prompt = None
    st.rerun()

if st.session_state.delete_index is not None:
    idx = st.session_state.delete_index
    st.session_state.delete_index = None
    saved_list = st.session_state.saved_chats
    if 0 <= idx < len(saved_list):
        saved_list.pop(idx)
        if st.session_state.current_chat_index == idx:
            st.session_state.chat_history = []
            st.session_state.current_chat_index = None
            st.session_state.chip_prompt = None
        elif st.session_state.current_chat_index and st.session_state.current_chat_index > idx:
            st.session_state.current_chat_index -= 1
    st.rerun()


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header-card">
      <div class="sidebar-header-title">CEO AI Assistant</div>
      <div class="sidebar-header-subtitle">Executive Workspace</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-newchat-wrap">', unsafe_allow_html=True)
    if st.button("＋  New Chat", key="new_chat_btn"):
        st.session_state.chat_history = []
        st.session_state.current_chat_index = None
        st.session_state.chip_prompt = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)
    search_query = st.text_input(
        "Search",
        placeholder="Search conversations...",
        label_visibility="collapsed",
        key="search_chats",
    )
    st.markdown("<hr/>", unsafe_allow_html=True)

    with st.expander("⚙  Settings"):
        st.session_state.user_name = st.text_input(
            "Your Name",
            value=st.session_state.get("user_name", ""),
            key="user_name_input",
        )
        theme_choice = st.radio(
            "Theme",
            ["Light", "Dark"],
            index=1 if st.session_state.dark_mode else 0,
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
        st.session_state.chip_prompt = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)

    saved = st.session_state.get("saved_chats", [])

    # ── Chat row with hover delete (ChatGPT style) ──
    def render_chat_row(i, chat, key_prefix):
        title = chat.get("title", f"Chat {i+1}")
        short = (title[:24] + "…") if len(title) > 24 else title

        st.markdown('<div class="chat-row-wrap">', unsafe_allow_html=True)

        if st.button(short, key=f"{key_prefix}_open_{i}"):
            st.session_state.open_index = i
            st.rerun()

        # mark delete wrapper as del-btn so generic sidebar CSS skips it
        st.markdown('<div class="del-wrap del-btn">', unsafe_allow_html=True)
        if st.button("🗑", key=f"{key_prefix}_del_{i}", help="Delete chat"):
            st.session_state.delete_index = i
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)  # .del-wrap

        st.markdown("</div>", unsafe_allow_html=True)  # .chat-row-wrap

    if search_query:
        st.markdown(
            "<span class='section-label'>Search Results</span>",
            unsafe_allow_html=True,
        )
        filtered = [
            (i, c)
            for i, c in enumerate(saved)
            if search_query.lower() in c.get("title", "").lower()
        ]
        if filtered:
            for i, chat in filtered:
                render_chat_row(i, chat, "search")
        else:
            st.markdown(
                f"<p style='font-size:0.82rem;color:{_T4};padding:0 0.1rem;'>No results found</p>",
                unsafe_allow_html=True,
            )
    else:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        groups = {
            "Today": [],
            "Yesterday": [],
            "Previous 7 Days": [],
            "Older": [],
        }
        for i, chat in enumerate(reversed(saved)):
            real_idx = len(saved) - 1 - i
            chat_date = None
            try:
                chat_date = datetime.fromisoformat(
                    chat.get("timestamp", "")
                ).date()
            except Exception:
                pass

            if chat_date == today:
                groups["Today"].append((real_idx, chat))
            elif chat_date == yesterday:
                groups["Yesterday"].append((real_idx, chat))
            elif chat_date and (today - chat_date).days <= 7:
                groups["Previous 7 Days"].append((real_idx, chat))
            else:
                groups["Older"].append((real_idx, chat))

        if not any(groups.values()):
            st.markdown(
                f"<p style='font-size:0.82rem;color:{_T4};padding:0 0.1rem;'>No conversations yet</p>",
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
# LOAD DB DATA
# =========================
employee          = fetch_employee_data()
new_joiners_df    = fetch_new_joiners()
instructor_df     = fetch_instructor_performance()
employee_trend_df = fetch_employee_trend()
former_df         = fetch_former_employees()


# =========================
# SUGGESTION CHIPS
# =========================
CHIPS = [
    ("📊", "Workforce Summary",  "Give me an executive summary of workforce and key HR risks."),
    ("📉", "Turnover Analysis",  "Which departments have the highest turnover and why?"),
    ("🎯", "Probation Risk",     "How are new joiners performing and how many are at risk in probation?"),
]


# =========================
# HELPER: process a prompt
# =========================
def process_prompt(prompt: str):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("Analyzing..."):
        answer = answer_ceo_question(prompt)
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)
    save_current_chat()


# =========================
# MAIN CONTENT
# =========================
if st.session_state.mode == "chat":

    if st.session_state.chip_prompt:
        pending = st.session_state.chip_prompt
        st.session_state.chip_prompt = None
        process_prompt(pending)
        st.rerun()

    if len(st.session_state.chat_history) == 0:
        st.markdown(
            '<div class="welcome-container">'
            '<div class="welcome-orb"></div>'
            f'<div class="welcome-greeting">{get_greeting()}</div>'
            '<div class="welcome-sub">What can I help you with today?</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(len(CHIPS), gap="small")
        for col, (icon, label, prompt) in zip(cols, CHIPS):
            with col:
                if st.button(f"{icon}  {label}", key=f"chip_{label}"):
                    st.session_state.chip_prompt = prompt
                    st.rerun()
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_input = st.chat_input("Ask your CEO Assistant anything...")
    if user_input:
        process_prompt(user_input)
        st.rerun()

else:
    render_dashboard(
        employee=employee, employees_df=employees_df,
        new_joiners_df=new_joiners_df, instructor_df=instructor_df,
        employee_trend_df=employee_trend_df, former_df=former_df,
    )
