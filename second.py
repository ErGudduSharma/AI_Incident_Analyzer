import requests
import uuid

BASE_URL = "http://localhost:8000"

# -------------------------------------------------
# Sample logs
# -------------------------------------------------
INCIDENT_LOGS = """
2025-01-18 10:21:45 ERROR ConnectionTimeoutError
Service: payment-service
Dependency: Redis Cache
Timeout while connecting to redis-cluster:6379
"""

# -------------------------------------------------
# Pretty print
# -------------------------------------------------
def pretty_print(result, incident_id):
    print("\n🧠 INCIDENT ANALYSIS REPORT")
    print("=" * 60)
    print(f"Incident ID       : {incident_id}")
    print(f"Root Cause        : {result['root_cause']}")
    print(f"Severity          : {result['severity']}")
    print(f"Affected Services : {', '.join(result['affected_services'])}")
    print(f"Immediate Fix     : {result['immediate_fix']}")
    print(f"Long-Term Fix     : {result['long_term_prevention']}")
    print(f"Analysis Time     : {result['analysis_time']}")
    print("=" * 60)

# -------------------------------------------------
# Auto alert
# -------------------------------------------------
def auto_alert(severity):
    if severity == "Critical":
        print("🚨 CRITICAL INCIDENT – Escalation triggered!")
    elif severity == "High":
        print("⚠️ HIGH SEVERITY – Immediate attention required.")

# -------------------------------------------------
# Run analysis
# -------------------------------------------------
def run():
    incident_id = str(uuid.uuid4())

    response = requests.post(
        f"{BASE_URL}/gemini/incident/invoke",
        json={"input": {"logs": INCIDENT_LOGS}},
        timeout=60
    )

    if response.status_code != 200:
        print("❌ ERROR:", response.text)
        return

    output = response.json()["output"]
    pretty_print(output, incident_id)
    auto_alert(output["severity"])

if __name__ == "__main__":
    run()