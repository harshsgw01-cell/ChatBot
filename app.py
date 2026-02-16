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
from datetime import datetime

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
    return f"{greeting}, CEO "

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
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="CEO AI Assistant",
    layout="wide",
    initial_sidebar_state="auto",
)

# =========================
# CUSTOM CSS WITH ANIMATIONS
# =========================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css');
* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
footer {visibility: hidden;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stSidebar"] {background-color: #FAFAFA; border-right: 1px solid #E5E5E5;}
div[data-testid="collapsedControl"] {background-color: #F5F5F5; border: 1px solid #E0E0E0; border-radius: 8px; color: #666;}
.block-container {padding-top: 2rem; padding-bottom: 2rem;}

/* SMOOTH PAGE TRANSITIONS */
.stApp {
    animation: fadeIn 0.6s ease-in-out;
}

/* METRIC ANIMATIONS */
[data-testid="stMetricValue"] { 
    font-size: 1.8rem; 
    font-weight: 600; 
    color: #1A1A1A;
    transform: translateY(20px);
    opacity: 0;
    animation: slideUpFadeIn 0.8s ease-out forwards;
}
[data-testid="stMetricLabel"] {font-size: 0.9rem; color: #737373;}

/* BUTTON ANIMATIONS */
[data-testid="stSidebar"] .stButton > button {
    border-radius: 8px !important;
    border: 1px solid #E5E5E5 !important;
    background-color: #FFFFFF !important;
    color: #404040 !important;
    font-weight: 500 !important;
    height: auto !important;
    padding: 0.75rem 1rem !important;
    text-align: left !important;
    white-space: normal !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    transform: translateY(0);
}
[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

/* NEW CHAT BUTTON */
.new-chat-btn .stButton > button {
    background: linear-gradient(135deg, #667EEA 0%, #764BA2 50%, #F093FB 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 600 !important;
    transition: all 0.4s ease;
    transform: scale(1);
}
.new-chat-btn .stButton > button:hover {
    transform: scale(1.05) rotate(2deg);
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
}

/* TOP BUTTONS */
.top-btn > button { 
    border-radius: 999px !important;
    transition: all 0.3s ease;
    transform: scale(1);
}
.top-btn > button:hover {
    transform: scale(1.1);
    box-shadow: 0 5px 20px rgba(0,0,0,0.2);
}

/* SUGGESTION BUTTONS */
.suggestion button {
    height: 120px !important;
    white-space: pre-wrap !important;
    text-align: left !important;
    padding: 1.5rem !important;
    background-color: #FAFAFA !important;
    border: 1px solid #E5E5E5 !important;
    border-radius: 12px !important;
    color: #404040 !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    transform: translateY(20px);
    opacity: 0;
}
.suggestion button:nth-child(1) { animation: slideUpFadeIn 0.6s ease-out 0.1s forwards; }
.suggestion button:nth-child(2) { animation: slideUpFadeIn 0.6s ease-out 0.2s forwards; }
.suggestion button:nth-child(3) { animation: slideUpFadeIn 0.6s ease-out 0.3s forwards; }
.suggestion button:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    border-color: #667EEA !important;
}

/* WELCOME CONTAINER */
.welcome-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 40vh;
    text-align: center;
    padding: 2rem;
}
.welcome-orb {
    width: 100px;
    height: 100px;
    background: linear-gradient(135deg, #667EEA 0%, #764BA2 50%, #F093FB 100%);
    border-radius: 50%;
    margin-bottom: 2rem;
    box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);

    /* 1) bounce only once on load
       2) pulseGlow forever */
    animation-name: bounceIn, pulseGlow;
    animation-duration: 0.8s, 2s;
    animation-timing-function: ease-out, ease-in-out;
    animation-iteration-count: 1, infinite;
    animation-delay: 0s, 0.8s;  /* pulse starts right after bounce finishes */
}

    animation: pulseGlow 2s ease-in-out infinite, bounceIn 1s ease-out;
}
.welcome-container h1 {
    animation: slideDownFadeIn 0.8s ease-out 0.3s both;
    transform: translateY(30px);
    opacity: 0;
}
.welcome-container p {
    animation: slideUpFadeIn 0.8s ease-out 0.5s both;
    transform: translateY(20px);
    opacity: 0;
    max-width: 520px;
    color: #525252;
    font-size: 0.95rem;
}

/* CHAT MESSAGES */
.stChatMessage {
    animation: slideInLeft 0.5s ease-out;
}
.chat-user { animation: slideInRight 0.5s ease-out; }

/* INPUT ANIMATIONS */
.stTextInput input, .stChatInputContainer textarea {
    border-radius: 8px;
    transition: all 0.3s ease;
    transform: scale(1);
}
.stTextInput input:focus, .stChatInputContainer textarea:focus {
    transform: scale(1.02);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* DASHBOARD MODE */
[data-testid="stPlotlyChart"] {
    animation: fadeInScale 0.6s ease-out;
}

/* KEYFRAME ANIMATIONS */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes slideUpFadeIn {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
@keyframes slideDownFadeIn {
    from { transform: translateY(-30px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
@keyframes slideInLeft {
    from { transform: translateX(-30px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
@keyframes slideInRight {
    from { transform: translateX(30px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
@keyframes fadeInScale {
    from { transform: scale(0.95); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
}
@keyframes pulseGlow {
    0%, 100% {
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        transform: scale(1);
    }
    50% {
        box-shadow: 0 0 60px rgba(102, 126, 234, 0.6);
        transform: scale(1.05);
    }
}

@keyframes bounceIn {
    0% { transform: scale(0.3); }
    50% { transform: scale(1.05); }
    70% { transform: scale(0.9); }
    100% { transform: scale(1); }
}

/* RESPONSIVE */
@media (max-width: 992px) {
    .block-container {padding-top: 1.5rem; padding-bottom: 1.5rem; padding-left: 1.25rem; padding-right: 1.25rem;}
    .welcome-container {min-height: 30vh; padding: 1.5rem;}
    .welcome-container h1 {font-size: 1.9rem !important;}
    [data-testid="stSidebar"] {width: 230px !important;}
}
@media (max-width: 768px) {
    .block-container {padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.75rem; padding-right: 0.75rem;}
    .welcome-orb {width: 80px; height: 80px; margin-bottom: 1.25rem;}
    .welcome-container h1 {font-size: 1.6rem !important;}
    .suggestion button {height: auto !important; padding: 1rem !important; font-size: 0.85rem !important;}
    [data-testid="stSidebar"] {width: 210px !important;}
    .row-widget.stHorizontal {flex-wrap: wrap;}
}
@media (max-width: 576px) {
    [data-testid="stSidebar"] {border-right: none; width: 200px !important;}
    .welcome-container h1 {font-size: 1.4rem !important;}
    [data-testid="stMetricValue"] {font-size: 1.3rem;}
    [data-testid="stMetricLabel"] {font-size: 0.8rem;}
    .stColumn {min-width: 100% !important;}
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# API & SESSION STATE (UNCHANGED)
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
# LOAD DATA FROM DATABASE (HR ONLY)
# =========================
employee = fetch_employee_data()
new_joiners_df = fetch_new_joiners()
instructor_df = fetch_instructor_performance()
employee_trend_df = fetch_employee_trend()
former_df = fetch_former_employees()

# =========================
# SIDEBAR WITH SMART SEARCH
# =========================
with st.sidebar:
    st.markdown(
        """
<div style='padding: 1rem 0; border-bottom: 1px solid #E5E5E5; margin-bottom: 1rem;'>
 <h2 style='margin: 0; font-size: 1.25rem; font-weight: 600; color: #1A1A1A;'>CEO AI Assistant</h2>
 <p style='margin: 0.25rem 0 0 0; font-size: 0.85rem; color: #737373;'>Executive Workspace</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="new-chat-btn">', unsafe_allow_html=True)
    if st.button("New Chat", key="new_chat_btn"):
        st.session_state.chat_history = []
        st.session_state.current_chat_index = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Search box
    search_query = st.text_input("Search", placeholder="Search conversations...", label_visibility="collapsed", key="search_chats")
    
    st.markdown("---")
    st.markdown("**Recent Searches**")
    
    # Only show results if user has typed something in search
    if search_query and len(st.session_state.saved_chats) > 0:
        # Filter chats based on search query
        filtered_chats = [
            (i, chat) for i, chat in enumerate(st.session_state.saved_chats)
            if search_query.lower() in chat.get("title", "").lower()
        ]
        
        if filtered_chats:
            for i, chat in filtered_chats:
                title = chat["title"]
                if st.button(title, key=f"chat_{i}"):
                    st.session_state.current_chat_index = i
                    st.session_state.chat_history = chat["messages"].copy()
                    st.rerun()
        else:
            st.caption("No results found")
    else:
        # Show empty state - no data displayed
        st.caption("Type to search recent conversations")

    st.markdown("---")
    with st.expander("Settings"):
        new_name = st.text_input("Your Name", value=st.session_state.user_name)
        st.session_state.user_name = new_name

    st.markdown("---")
    if st.button("Clear Current Chat"):
        st.session_state.chat_history = []
        st.session_state.current_chat_index = None
        st.rerun()

# =========================
# TOP BAR (UNCHANGED)
# =========================
header_left, header_right = st.columns([7, 3])
with header_left:
    st.markdown("## CEO Executive Workspace")
    st.caption("Strategic insights and HR analysis powered by AI.")
with header_right:
    col_chat_btn, col_dash_btn = st.columns(2)
    with col_chat_btn:
        st.markdown('<div class="top-btn">', unsafe_allow_html=True)
        if st.button("Chat", key="chat_mode_btn"):
            st.session_state.mode = "chat"
        st.markdown("</div>", unsafe_allow_html=True)
    with col_dash_btn:
        st.markdown('<div class="top-btn">', unsafe_allow_html=True)
        if st.button("Dashboard", key="dashboard_mode_btn"):
            st.session_state.mode = "dashboard"
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# =========================
# MAIN CONTENT: CHAT OR DASHBOARD (UNCHANGED LOGIC)
# =========================
if st.session_state.mode == "chat":
    if len(st.session_state.chat_history) == 0:
        st.markdown(
            f"""
            <div class="welcome-container">
                <div class="welcome-orb"></div>
                <h1 style="margin-bottom: 0.5rem;">{get_greeting()}</h1>
                <p style="max-width: 520px; color: #525252; font-size: 0.95rem;">
                    I'm your CEO AI Assistant. Ask about headcount, attrition, cost, or performance trends.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)
        user_q = None
        with col1:
            if st.button("Show me a summary of our workforce and key risks", key="s1"):
                user_q = "Give me an executive summary of workforce and key HR risks."
        with col2:
            if st.button("Which departments have the highest turnover?", key="s2"):
                user_q = "Which departments have the highest turnover and why?"
        with col3:
            if st.button("How are new joiners performing in probation?", key="s3"):
                user_q = "How are new joiners performing and how many are at risk in probation?"

        if user_q:
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.chat_message("user"):
                st.markdown(user_q)
            answer = answer_ceo_question(user_q)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            with st.chat_message("assistant"):
                st.markdown(answer)

    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_input = st.chat_input("Type a question to your CEO Assistant...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        answer = answer_ceo_question(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

else:
    render_dashboard(
        employee=employee,
        employees_df=employees_df,
        new_joiners_df=new_joiners_df,
        instructor_df=instructor_df,
        employee_trend_df=employee_trend_df,
        former_df=former_df,
    )