from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
import os
import sqlite3
from datetime import datetime
import logging

# -------------------------------------------------
# Load env
# -------------------------------------------------
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)

# -------------------------------------------------
# App
# -------------------------------------------------
app = FastAPI(
    title="AI Incident Root Cause Analyzer",
    version="3.1"
)

# -------------------------------------------------
# DB
# -------------------------------------------------
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

init_db()

# -------------------------------------------------
# Schema
# -------------------------------------------------
class IncidentAnalysis(BaseModel):
    root_cause: str
    severity: str
    affected_services: List[str]
    immediate_fix: str
    long_term_prevention: str
    analysis_time: str

# -------------------------------------------------
# Prompt
# -------------------------------------------------
incident_prompt = ChatPromptTemplate.from_template("""
You are a senior DevOps SRE.

Analyze the incident and return ONLY valid JSON:

root_cause
severity (Low | Medium | High | Critical)
affected_services
immediate_fix
long_term_prevention
analysis_time (ISO)

Incident Logs:
{logs}
""")

# -------------------------------------------------
# Models
# -------------------------------------------------
gemini = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3
).with_structured_output(IncidentAnalysis)

groq = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.3
).with_structured_output(IncidentAnalysis)

# -------------------------------------------------
# Persistence
# -------------------------------------------------
def save_incident(model: str, result: IncidentAnalysis):
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

# -------------------------------------------------
# Runnable pipelines (THIS IS THE FIX)
# -------------------------------------------------
gemini_chain = (
    incident_prompt
    | gemini
    | RunnableLambda(lambda result: (save_incident("gemini", result), result)[1])
)

groq_chain = (
    incident_prompt
    | groq
    | RunnableLambda(lambda result: (save_incident("groq", result), result)[1])
)

# -------------------------------------------------
# Routes
# -------------------------------------------------
add_routes(app, gemini_chain, path="/gemini/incident")
add_routes(app, groq_chain, path="/groq/incident")