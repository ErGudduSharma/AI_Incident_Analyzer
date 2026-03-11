import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from pydantic import BaseModel
from typing import List

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="AI Incident Root Cause Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    .report-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #1e2130;
        border: 1px solid #3e4259;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------
# Environment & Logic
# -------------------------------------------------
load_dotenv()

# DB Helper
DB_NAME = "incident_audit.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT,
            model TEXT,
            root_cause TEXT,
            severity TEXT,
            affected_services TEXT,
            immediate_fix TEXT,
            long_term_prevention TEXT,
            analysis_time TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(model: str, result):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO incidents VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        model,
        result.root_cause,
        result.severity,
        ", ".join(result.affected_services),
        result.immediate_fix,
        result.long_term_prevention,
        result.analysis_time
    ))
    conn.commit()
    conn.close()

init_db()

# Schema for Structured Output
class IncidentAnalysis(BaseModel):
    root_cause: str
    severity: str
    affected_services: List[str]
    immediate_fix: str
    long_term_prevention: str
    analysis_time: str

# -------------------------------------------------
# Sidebar - Configuration
# -------------------------------------------------
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("---")
    selected_model = st.selectbox(
        "Choose AI Model",
        ["Google Gemini", "Groq (Llama 3)"],
        index=0
    )
    
    st.info("Ensure your API Keys are set in `.env` or Streamlit Secrets.")
    
    if st.button("Clear History"):
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
            init_db()
            st.success("History cleared!")
            st.rerun()

# -------------------------------------------------
# Main UI
# -------------------------------------------------
st.title("🧠 AI Incident Root Cause Analyzer")
st.markdown("Automate DevOps debugging and root cause analysis using Generative AI.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Input Incident Logs")
    logs_input = st.text_area(
        "Paste your production error logs here...",
        height=300,
        placeholder="Example:\n2025-01-18 10:21:45 ERROR ConnectionTimeoutError\nService: payment-service..."
    )
    
    analyze_btn = st.button("🚀 Run Analysis")

with col2:
    st.subheader("📊 Recent Incidents")
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT model, severity, analysis_time FROM incidents ORDER BY analysis_time DESC LIMIT 5", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.write("No history available yet.")
    except Exception as e:
        st.error("Could not load history.")

# -------------------------------------------------
# Execution Logic
# -------------------------------------------------
if analyze_btn:
    if not logs_input.strip():
        st.warning("Please paste some logs first!")
    else:
        with st.spinner(f"Analyzing with {selected_model}..."):
            try:
                # Prompt Template
                incident_prompt = ChatPromptTemplate.from_template("""
                You are a senior DevOps SRE.
                Analyze the incident and return ONLY valid JSON:
                root_cause, severity (Low|Medium|High|Critical), affected_services, immediate_fix, long_term_prevention, analysis_time (ISO).
                
                Logs:
                {logs}
                """)

                # Initialize LLM
                if selected_model == "Google Gemini":
                    # Using the model name as per your project settings (gemini-2.5-flash as used in first.py)
                    llm = ChatGoogleGenerativeAI(
                        model="gemini-2.5-flash", 
                        temperature=0.3
                    ).with_structured_output(IncidentAnalysis)
                    model_id = "gemini"
                else:
                    llm = ChatGroq(
                        model_name="llama-3.1-8b-instant",
                        temperature=0.3
                    ).with_structured_output(IncidentAnalysis)
                    model_id = "groq"

                # Run Chain
                chain = incident_prompt | llm
                result = chain.invoke({"logs": logs_input})

                # Save to DB
                save_to_db(model_id, result)

                # Show Results
                st.success("Analysis Complete!")
                
                # Report Layout
                st.markdown("---")
                st.header("📋 Analysis Report")
                
                res_col1, res_col2 = st.columns(2)
                
                severity_color = {
                    "Critical": "🔴",
                    "High": "🟠",
                    "Medium": "🟡",
                    "Low": "🟢"
                }.get(result.severity, "⚪")

                with res_col1:
                    st.markdown(f"**Severity:** {severity_color} {result.severity}")
                    st.markdown(f"**Root Cause:**\n{result.root_cause}")
                    st.markdown(f"**Affected Services:**")
                    for service in result.affected_services:
                        st.markdown(f"- `{service}`")

                with res_col2:
                    st.markdown(f"**Immediate Fix:**\n{result.immediate_fix}")
                    st.markdown(f"**Prevention Strategy:**\n{result.long_term_prevention}")
                    st.caption(f"Analysis generated at: {result.analysis_time}")

                if result.severity in ["Critical", "High"]:
                    st.error(f"🚨 {result.severity} incident detected! Alerts would be sent to on-call engineers.")

            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.info("Check if your API keys are correct and you have enough quota.")

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("---")
st.caption("AI Incident Analyzer v1.0 | Built with Streamlit and LangChain")
