# Client Script | Calls Gemini ---> send groq 

import requests 
import uuid 
from datetime import datetime 

BASE_URL = "http://localhost:8000" 

## Sample log 
INCIDENT_LOGS = """"
2025-01-18 10:21:45 ERROR ConnectionTimeoutError
Service: payment-service 
Dependency: Redis Cache 
Timeout while connecting to redis-cluster:6379
"""

def pretty_print(report , incident_id):
    print("\n INCIDENT ANALYSIS REPORT")
    print("=" * 60)
    print(f"Incident ID : {incident_id}")
    print(f"Root Cause: {report['root_cause']}")
    print(f"Severity: {report['severity']}")
    print(f"Affected Services: {', '.join(report['affected_services'])}")
    print(f"Immediate Fix : {report['immediate_fix']}") 
    print(f"Long-Term Fix: {report['long_term_prevention']}")
    print(f"Analysis Time : {report['analysis_time']}") 
    print("="*60) 

## Auto Alert 

def auto_alert(severity):
    if severity == "Critical":
        print("CRITICAL INCIDENT - Escalation triggered!!!")
    elif severity == "High":
        print("HIGH SEVERITY - Immediate attention required.") 

### Run pipeline 
def run():
    incident_id = str(uuid.uuid4()) 

    ## Gemini Analysis 
    gemini_resp = requests.post(
        f"{BASE_URL}/gemini/analyze/invoke",
        json={"input": {"logs": INCIDENT_LOGS}},
        timeout = 60
    )
    if gemini_resp.status_code != 200:
        print("Gemini Error: " , gemini_resp.text) 
        return 
    analysis = gemini_resp.json()["output"] 

    ## GROQ FIX Suggestions
    groq_resp = requests.post(
        f"{BASE_URL}/groq/fix/invoke",
        json = {
            "input": {
                "root_cause": analysis["root_cause"],
                "severity": analysis["severity"],
                "affected_services":analysis["affected_services"]
            }
        },
        timeout = 60
    )

    if groq_resp.status_code != 200:
        print("Groq Error :" , groq_resp.text) 
        return 
    fixes = groq_resp.json()["output"] 

    ### Final Report 
    final_report = {
    "root_cause": analysis["root_cause"],
    "severity": analysis["severity"],
    "affected_services": analysis["affected_services"],
    "immediate_fix": fixes["immediate_fix"],
    "long_term_prevention": fixes["long_term_prevention"],
    "analysis_time": analysis["analysis_time"]
    }

    pretty_print(final_report , incident_id)
    auto_alert(final_report["severity"])


if __name__ == "__main__":
    run() 

