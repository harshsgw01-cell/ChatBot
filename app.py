import streamlit as st
import pandas as pd
import plotly.express as px

# ✅ OpenAI API (new SDK)
from openai import OpenAI

from data import (
    get_financial_data,
    get_revenue_trend_data,
    get_employee_data,
    get_ceo_summary,
)

from lang import LANGUAGES, get_text

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="CEO Analytic Dashboard", layout="wide")

# =========================
# API KEY (Streamlit Secrets ONLY)
# =========================
st.session_state.openai_api_key = st.secrets["OPENAI_API_KEY"]

# =========================
# Initialize OpenAI client
# =========================
client = OpenAI(api_key=st.session_state.openai_api_key)

# Choose OpenAI model
GEN_AI_MODEL = "gpt-4o"  # or "gpt-4o-mini"

# =========================
# LANGUAGE TOGGLE
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "English"

lang = st.radio(
    "Select Language / اختر اللغة",
    options=LANGUAGES,
    index=0 if st.session_state.lang == "English" else 1,
    horizontal=True,
)
st.session_state.lang = lang
txt = get_text(lang)

# =========================
# LOAD DATA
# =========================
finance = get_financial_data()
trend = get_revenue_trend_data()
employee = get_employee_data()

# =========================
# HEADER
# =========================
st.title(txt["dashboard_title"])
st.caption(txt["dashboard_caption"])

# =========================
# FINANCIAL OVERVIEW
# =========================
st.subheader(txt["financial_overview"])
c1, c2, c3, c4 = st.columns(4)
c1.metric(f"{txt['revenue_label']} (M QAR)", finance["revenue"])
c2.metric("Profit Margin %", finance["profit_margin"])
c3.metric(f"{txt['expenses_label']} (M QAR)", finance["expenses"])
c4.metric("Profit (M QAR)", finance["profit"])

fig_finance = px.bar(
    x=[txt["revenue_label"], txt["expenses_label"]],
    y=[finance["revenue"], finance["expenses"]],
    text=[
        f"{finance['revenue']}M" if lang == "English" else f"{finance['revenue']} مليون",
        f"{finance['expenses']}M" if lang == "English" else f"{finance['expenses']} مليون",
    ],
    color=[txt["revenue_label"], txt["expenses_label"]],
    title=txt["revenue_vs_expenses"],
)
fig_finance.update_traces(textposition="outside")
fig_finance.update_layout(
    yaxis_title=txt["yaxis_millions"],
    xaxis_title="",
    title_x=0.5,
    showlegend=False,
)
st.plotly_chart(fig_finance, use_container_width=True)

# =========================
# REVENUE TREND
# =========================
st.subheader(txt["revenue_trend"])
st.line_chart(trend.set_index("Month"))

# =========================
# EMPLOYEE OVERVIEW
# =========================
st.subheader(txt["workforce_overview"])
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Employees", employee["total_employees"])
c2.metric("Active Employees", employee["active_employees"])
c3.metric("Attrition Rate %", employee["attrition_rate"])
c4.metric("Engagement Score", employee["engagement_score"])
c5.metric("Avg Tenure", employee["avg_tenure"])

inactive_employees = employee["total_employees"] - employee["active_employees"]

fig_employee = px.pie(
    names=["Active", "Inactive"] if lang == "English" else ["نشط", "غير نشط"],
    values=[employee["active_employees"], inactive_employees],
    hole=0.5,
    title=txt["active_inactive"],
)
st.plotly_chart(fig_employee, use_container_width=True)

# =========================
# CEO INSIGHT
# =========================
st.subheader(txt["ceo_insight"])
st.info(get_ceo_summary())

# =========================
# AI EXECUTIVE ASSISTANT
# =========================
def ai_analyze(messages, max_history=5):
    history = messages[-max_history:]

    conversation_messages = [
        {
            "role": "system",
            "content": f"""You are a CEO Executive Assistant.
Provide business insights, risks, and actionable recommendations.
Respond in {st.session_state.lang}.
Financial Data: {finance}
Employee Data: {employee}
Revenue Trend: {trend.to_dict()}"""
        }
    ]

    for msg in history:
        conversation_messages.append(
            {"role": msg["role"], "content": msg["content"]}
        )

    try:
        response = client.chat.completions.create(
            model=GEN_AI_MODEL,
            messages=conversation_messages,
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI Error: {e}"

# =========================
# SIDEBAR – AI CHAT
# =========================
st.sidebar.title(txt["ai_sidebar_title"])
st.sidebar.caption(txt["ai_sidebar_caption"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Quick Questions
st.sidebar.markdown("### Quick Questions")
for q in txt["quick_questions"]:
    if st.sidebar.button(q, key=f"quick_{q}"):
        st.session_state.chat_history.append({"role": "user", "content": q})
        reply = ai_analyze(st.session_state.chat_history)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )

# Clear chat
if st.sidebar.button(txt["clear_chat"]):
    st.session_state.chat_history = []

# Display chat history
for msg in st.session_state.chat_history:
    with st.sidebar.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.sidebar.chat_input(txt["chat_input"])
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.sidebar.chat_message("assistant"):
        with st.spinner(txt["analyzing"]):
            reply = ai_analyze(st.session_state.chat_history)
            st.markdown(reply)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": reply}
            )

# =========================
# FOOTER
# =========================
st.caption(txt["footer"])
