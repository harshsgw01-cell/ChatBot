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
# CUSTOM CSS — PREMIUM LIGHT THEME + ANIMATIONS + MOBILE FIX
# =========================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

:root {
    --bg-primary: #FFFFFF;
    --bg-secondary: #FFFFFF;
    --bg-card: #FFFFFF;
    --bg-hover: #F1F4F9;
    --border: rgba(0,0,0,0.07);
    --border-accent: rgba(99,102,241,0.35);
    --text-primary: #0F1523;
    --text-secondary: #4B5675;
    --text-muted: #9BA3B8;
    --accent-indigo: #6366F1;
    --accent-teal: #0D9488;
    --gradient-main: linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #06B6D4 100%);
    --shadow-sm: 0 1px 4px rgba(0,0,0,0.06);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
    --shadow-lg: 0 12px 40px rgba(0,0,0,0.10);
    --shadow-glow: 0 0 30px rgba(99,102,241,0.12);
    /* Streamlit toolbar height — adjust if needed */
    --toolbar-height: 3rem;
}

* { font-family: 'DM Sans', -apple-system, sans-serif; box-sizing: border-box; }
footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ─────────────────────────────────────────
   STREAMLIT TOOLBAR / TOP-CHROME FIX
   Push ALL main content below the toolbar
   so it never overlaps your header.
───────────────────────────────────────── */

/* The fixed top bar that Streamlit injects */
header[data-testid="stHeader"] {
    background: #FFFFFF !important;
    border-bottom: 1px solid var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
    z-index: 999 !important;
}

/* Make the main block-container start BELOW the header */
.block-container {
    padding-top: calc(var(--toolbar-height) + 1rem) !important;
    padding-bottom: 2rem;
    max-width: 1400px;
    animation: contentSlideUp 0.7s ease-out 0.1s both;
}

/* On mobile the toolbar can be taller — add extra breathing room */
@media (max-width: 768px) {
    .block-container {
        padding-top: calc(var(--toolbar-height) + 0.5rem) !important;
        padding-left: 0.75rem  !important;
        padding-right: 0.75rem !important;
    }
}

/* ── MAIN APP BACKGROUND + PAGE LOAD ANIM ── */
.stApp {
    background: #FFFFFF;
    color: var(--text-primary);
    min-height: 100vh;
    animation: pageFadeIn 0.7s ease-out both;
}

/* Help animate main vertical content block as well */
main [data-testid="stVerticalBlock"] {
    animation: contentSlideUp 0.7s ease-out 0.15s both;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04) !important;
}
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] {
    padding: 1.25rem 0.85rem;
}
div[data-testid="collapsedControl"] {
    background: #FFFFFF !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px;
    color: var(--text-secondary) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── SIDEBAR BUTTONS ── */
[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    width: 100%;
    text-align: left;
    background: transparent !important;
    border: none !important;
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    color: var(--text-secondary) !important;
    font-weight: 400;
    box-shadow: none !important;
    transition: all 0.2s ease;
    letter-spacing: 0.01em;
}
[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: var(--bg-hover) !important;
    color: var(--text-primary) !important;
}

/* New Chat Button */
.new-chat-btn div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(6,182,212,0.06) 100%) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    color: #4F46E5 !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    transition: all 0.25s ease !important;
}
.new-chat-btn div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, rgba(99,102,241,0.14) 0%, rgba(6,182,212,0.1) 100%) !important;
    border-color: rgba(99,102,241,0.5) !important;
    color: #4338CA !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.15) !important;
}

/* Clear Chat Button */
.clear-btn div[data-testid="stButton"] > button {
    color: #EF4444 !important;
    font-size: 0.82rem !important;
}
.clear-btn div[data-testid="stButton"] > button:hover {
    background: rgba(239,68,68,0.07) !important;
    color: #DC2626 !important;
}

/* Delete Button (sidebar, for chats) */
.del-btn div[data-testid="stButton"] > button {
    color: #9BA3B8 !important;
    font-size: 0.8rem !important;
    padding: 0.2rem 0.5rem !important;
    border-radius: 999px !important;
    width: 100% !important;
    text-align: center !important;
}
.del-btn div[data-testid="stButton"] > button:hover {
    color: #EF4444 !important;
    background: rgba(239,68,68,0.10) !important;
}

/* Section Labels */
.section-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 1rem 0.75rem 0.3rem 0.75rem;
    display: block;
}

/* Sidebar Divider */
.sidebar-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 0.6rem 0;
}

/* Sidebar Search Input */
[data-testid="stSidebar"] input[type="text"] {
    background: var(--bg-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    color: var(--text-primary) !important;
    transition: border-color 0.2s ease;
}
[data-testid="stSidebar"] input[type="text"]:focus {
    border-color: var(--border-accent) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.08) !important;
}

/* Expander */
[data-testid="stSidebar"] details {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
[data-testid="stSidebar"] summary {
    font-size: 0.875rem;
    color: var(--text-secondary);
    padding: 0.45rem 0.75rem;
    border-radius: 8px;
    transition: all 0.2s ease;
}
[data-testid="stSidebar"] summary:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
}

/* ── METRICS ── */
[data-testid="stMetricValue"] {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-primary);
    animation: slideUpFadeIn 0.8s ease-out forwards;
}
[data-testid="stMetricLabel"] {
    font-size: 0.85rem;
    color: var(--text-secondary);
    letter-spacing: 0.02em;
}
[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
    animation: fadeInScale 0.6s ease-out 0.1s both;
}

/* ── TOP BAR ── */
.topbar-wrap {
    /* sits in the normal document flow, already below the Streamlit header
       because of the block-container padding we set above */
    padding: 0.75rem 0 0.65rem 0;
}
.topbar-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.5rem;
    font-weight: 400;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1.2;
    animation: slideDownFadeIn 0.8s ease-out 0.1s both;
}
.topbar-subtitle {
    font-size: 0.78rem;
    color: var(--text-muted);
    letter-spacing: 0.04em;
    margin-top: 0.15rem;
    text-transform: uppercase;
    animation: slideUpFadeIn 0.8s ease-out 0.15s both;
}

/* Mobile: shrink title text */
@media (max-width: 576px) {
    .topbar-title   { font-size: 1.15rem !important; }
    .topbar-subtitle{ font-size: 0.68rem !important; }
}

/* ── WELCOME SCREEN ── */
.welcome-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 42vh;
    text-align: center;
    padding: 3rem 2rem;
    animation: contentSlideUp 0.8s ease-out 0.2s both;
}

/* Fully filled gradient orb */
.welcome-orb {
    width: 88px;
    height: 88px;
    background: conic-gradient(from 180deg, #6366F1, #8B5CF6, #06B6D4, #6366F1);
    border-radius: 50%;
    margin-bottom: 2rem;
    position: relative;
    animation: orbSpin 10s linear infinite, orbPulse 3s ease-in-out infinite, fadeInScale 0.7s ease-out 0.1s both;
    box-shadow: 0 8px 40px rgba(99,102,241,0.25), 0 0 80px rgba(99,102,241,0.1);
}
.welcome-orb::after { content: none; }

.welcome-greeting {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.4rem;
    font-weight: 400;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    margin-bottom: 0.75rem;
    animation: slideDownFadeIn 0.8s ease-out 0.2s both;
}
.welcome-sub {
    font-size: 0.95rem;
    color: var(--text-secondary);
    max-width: 480px;
    line-height: 1.75;
    animation: slideUpFadeIn 0.8s ease-out 0.4s both;
}

/* ── SUGGESTION BUTTONS ── */
.suggestion button {
    height: auto !important;
    min-height: 90px !important;
    white-space: pre-wrap !important;
    text-align: left !important;
    padding: 1.25rem 1.5rem !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    color: var(--text-secondary) !important;
    font-size: 0.875rem !important;
    line-height: 1.6 !important;
    font-weight: 400 !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.25s ease !important;
    animation: slideUpFadeIn 0.6s ease-out both;
}
.suggestion > div:nth-child(1) button { animation-delay: 0.1s; }
.suggestion > div:nth-child(2) button { animation-delay: 0.2s; }
.suggestion > div:nth-child(3) button { animation-delay: 0.3s; }
.suggestion button:hover {
    background: var(--bg-hover) !important;
    border-color: rgba(99,102,241,0.3) !important;
    color: var(--text-primary) !important;
    transform: translateY(-3px) !important;
    box-shadow: var(--shadow-md) !important;
}

/* ── CHAT MESSAGES ── */
.stChatMessage { animation: slideInLeft 0.4s ease-out; }

/* ── CHAT INPUT ── */
.stChatInputContainer {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stChatInputContainer:focus-within {
    border-color: var(--border-accent) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.08), var(--shadow-sm) !important;
}

/* ── HR DIVIDER ── */
hr {
    border-color: var(--border) !important;
    margin: 0.5rem 0 1rem 0 !important;
}

/* ── PLOTLY CHARTS ── */
[data-testid="stPlotlyChart"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 0.5rem !important;
    box-shadow: var(--shadow-sm) !important;
    animation: fadeInScale 0.5s ease-out 0.2s both;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #E2E5EF; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ── KEYFRAMES ── */
@keyframes orbSpin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes orbPulse {
    0%, 100% { box-shadow: 0 8px 40px rgba(99,102,241,0.25), 0 0 80px rgba(99,102,241,0.1); }
    50% { box-shadow: 0 8px 60px rgba(99,102,241,0.35), 0 0 100px rgba(99,102,241,0.18); }
}
@keyframes slideUpFadeIn {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
@keyframes slideDownFadeIn {
    from { transform: translateY(-20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
@keyframes slideInLeft {
    from { transform: translateX(-15px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
@keyframes fadeInScale {
    from { transform: scale(0.97); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}
@keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes contentSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── RESPONSIVE ── */
@media (max-width: 768px) {
    .welcome-greeting { font-size: 1.8rem; }
    [data-testid="stSidebar"] { width: 240px !important; }
}
@media (max-width: 576px) {
    .welcome-greeting { font-size: 1.5rem; }
    [data-testid="stMetricValue"] { font-size: 1.4rem; }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# API & SESSION STATE
# =========================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
MODEL = "gpt-4o-mini"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mode" not in st.session_state:
    st.session_state.mode = "chat"
if "saved_chats" not in st.session_state:
    st.session_state.saved_chats = []
if "current_chat_index" not in st.session_state:
    st.session_state.current_chat_index = None
if "user_name" not in st.session_state:
    st.session_state.user_name = "Harsh"


# =========================
# SAVE CHAT HELPER
# =========================
def save_current_chat():
    if not st.session_state.chat_history:
        return
    first_user_msg = next(
        (m["content"] for m in st.session_state.chat_history if m["role"] == "user"),
        "Untitled Chat"
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
# TOP BAR  (fixed: wrapped in .topbar-wrap so it sits below Streamlit toolbar)
# =========================
col_title, col_icons = st.columns([9, 1])

with col_title:
    st.markdown(
        """
        <div class="topbar-wrap">
          <div class="topbar-title">CEO AI Assistant</div>
          <div class="topbar-subtitle">Strategic HR &amp; Workforce Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_icons:
    # small spacer to vertically align icons with the title
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    icon1, icon2 = st.columns([1, 1])
    with icon1:
        chat_clicked = st.button("💬", key="chat_mode_icon", help="Chat")
    with icon2:
        dash_clicked = st.button("📊", key="dash_mode_icon", help="Dashboard")

if chat_clicked:
    st.session_state.mode = "chat"
    st.rerun()
if dash_clicked:
    st.session_state.mode = "dashboard"
    st.rerun()

st.markdown("""<hr/>""", unsafe_allow_html=True)


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] div[data-testid="stButton"] > button {
            width: 100%;
            text-align: left;
            background: transparent !important;
            border: none !important;
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
            color: #4B5675 !important;
            font-weight: 400;
            box-shadow: none !important;
            transition: all 0.2s ease;
        }
        [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
            background: #F1F4F9 !important;
            color: #0F1523 !important;
        }
        .new-chat-btn div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(6,182,212,0.05) 100%) !important;
            border: 1px solid rgba(99,102,241,0.25) !important;
            color: #4F46E5 !important;
            font-weight: 600 !important;
        }
        .new-chat-btn div[data-testid="stButton"] > button:hover {
            background: linear-gradient(135deg, rgba(99,102,241,0.14) 0%, rgba(6,182,212,0.1) 100%) !important;
            box-shadow: 0 4px 16px rgba(99,102,241,0.15) !important;
            color: #4338CA !important;
        }
        .clear-btn div[data-testid="stButton"] > button {
            color: #EF4444 !important;
            font-size: 0.82rem !important;
        }
        .clear-btn div[data-testid="stButton"] > button:hover {
            background: rgba(239,68,68,0.07) !important;
        }
        .del-btn div[data-testid="stButton"] > button {
            color: #9BA3B8 !important;
            font-size: 0.8rem !important;
            padding: 0.2rem 0.5rem !important;
            border-radius: 999px !important;
            width: 100% !important;
            text-align: center !important;
        }
        .del-btn div[data-testid="stButton"] > button:hover {
            color: #EF4444 !important;
            background: rgba(239,68,68,0.10) !important;
        }
        .section-label {
            font-size: 0.68rem;
            font-weight: 600;
            color: #9BA3B8;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            padding: 1rem 0.75rem 0.3rem 0.75rem;
            display: block;
        }
        .sidebar-divider {
            border: none;
            border-top: 1px solid rgba(0,0,0,0.07);
            margin: 0.6rem 0;
        }
        [data-testid="stSidebar"] input[type="text"] {
            background: #F8F9FC !important;
            border: 1px solid rgba(0,0,0,0.07) !important;
            border-radius: 8px !important;
            font-size: 0.875rem !important;
            color: #0F1523 !important;
        }
        [data-testid="stSidebar"] details {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }
        [data-testid="stSidebar"] summary {
            font-size: 0.875rem;
            color: #4B5675;
            padding: 0.45rem 0.75rem;
            border-radius: 8px;
        }
        [data-testid="stSidebar"] summary:hover {
            background: #F1F4F9;
            color: #0F1523;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── HEADER ──────────────────
    st.markdown(
        """
        <div style='margin-top: 2.5rem; padding: 0.5rem 0.5rem 1.25rem 0.5rem;'>
          <div style='font-family:"DM Serif Display",Georgia,serif; font-size:1.2rem; font-weight:400; color:#0F1523; letter-spacing:-0.02em;'>
            CEO AI Assistant
          </div>
          <div style='font-size:0.68rem; color:#9BA3B8; margin-top:0.2rem; letter-spacing:0.08em; text-transform:uppercase;'>
            Executive Workspace
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── NEW CHAT ─────────────────
    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("＋   New Chat", key="new_chat_btn"):
        st.session_state.chat_history = []
        st.session_state.current_chat_index = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr class='sidebar-divider'/>", unsafe_allow_html=True)

    # ── SEARCH ───────────────────
    search_query = st.text_input(
        "Search",
        placeholder="Search conversations...",
        label_visibility="collapsed",
        key="search_chats",
    )

    st.markdown("<hr class='sidebar-divider'/>", unsafe_allow_html=True)

    # ── SETTINGS ─────────────────
    with st.expander("⚙  Settings"):
        new_name = st.text_input(
            "Your Name",
            value=st.session_state.get("user_name", ""),
            key="user_name_input"
        )
        st.session_state.user_name = new_name

    # ── CLEAR CHAT ───────────────
    st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
    if st.button("Clear Current Chat", key="clear_chat_btn"):
        st.session_state.chat_history = []
        st.session_state.current_chat_index = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<hr class='sidebar-divider'/>", unsafe_allow_html=True)

    # ── RECENTS ──────────────────
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
            st.markdown('</div>', unsafe_allow_html=True)

    if search_query:
        st.markdown(
            "<span class='section-label'>Search Results</span>",
            unsafe_allow_html=True,
        )
        filtered = [
            (i, chat) for i, chat in enumerate(saved)
            if search_query.lower() in chat.get("title", "").lower()
        ]
        if filtered:
            for i, chat in filtered:
                render_chat_row(i, chat, "search")
        else:
            st.markdown(
                "<p style='font-size:0.82rem;color:#9BA3B8;padding:0 0.75rem;'>No results found</p>",
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
                "<p style='font-size:0.82rem;color:#9BA3B8;padding:0 0.75rem;'>No conversations yet</p>",
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
# MAIN CONTENT: CHAT OR DASHBOARD
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

        st.markdown('<div class="suggestion">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        user_q = None
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
        st.markdown("</div>", unsafe_allow_html=True)

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