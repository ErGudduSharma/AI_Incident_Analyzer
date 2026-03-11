# step1 :  load our secret credentials 
# step2:  create a fastapi application 
# step3: Pydantic Schemas   
# step4: Prompt Engineering (gemini prompt , groq prompt)
# step5: API Routes 

from fastapi import FastAPI 
from langchain_core.prompts import ChatPromptTemplate 
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_groq import ChatGroq 
from langserve import add_routes 
from dotenv import load_dotenv
from pydantic import BaseModel 
from typing import List 
import os 
import logging 
from datetime import datetime 


##load env 
load_dotenv() 
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

###LOGGING 
logging.basicConfig(level=logging.INFO) 

###App 
app = FastAPI(
    title = "AI incident Root Cause Analyzer",
    version = "2.0"
)


##Schema 
class GeminiAnalysis(BaseModel):
    root_cause: str 
    severity: str 
    affected_services: List[str] 
    analysis_time: str 

class FinalIncidentReport(BaseModel):
    root_cause: str 
    severity: str 
    affected_services: List[str] 
    immediate_fix: str 
    long_term_prevention: str 
    analysis_time: str 


## Prompts 
gemini_prompt = ChatPromptTemplate.from_template("""
You are a senor DevOPS SRE. Analyze production incident logs and return ONLY valid JSON:
root_cause                                                
severity(Low|Medium|High|Critical) 
affected_services
analysis_time(ISO timestamp) 
Incident Logs:
{logs}                                                                                                                                                                                                                                       
""")

groq_prompt = ChatPromptTemplate.from_template("""
You are a senior SRE  fixing production issue . Based on this incident analysis , suggest fixes , Return ONLY valid JSON:
immediate_fix 
Root Cause: {root_cause} 
Severity: {severity}
Affected Services: {affected_services}                                                                                                                                                                                        
""")


### Models 
gemini_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=0.3).with_structured_output(GeminiAnalysis) 

groq_model = ChatGroq(model="llama-3.1-8b-instant",temperature=0.3)

###Api routing 
add_routes(
    app,
    gemini_prompt | gemini_model ,
    path = "/gemini/analyze"
)

add_routes(
    app , 
    groq_prompt | groq_model ,
    path = "/groq/fix"
)