# 🤖 AI Incident Root Cause Analyzer

An advanced **AI-powered DevOps tool** that automatically analyzes server error logs to determine root causes, assess severity, and suggest immediate fixes. It uses **Google Gemini** and **Groq (Llama)** models for analysis and creates an audit trail in a **SQLite database**.

---

## 🚀 Features

- **Automated Root Cause Analysis**: Uses LLMs to understand complex error logs.
- **Severity Assessment**: Automatically categorizes incidents (Low, Medium, High, Critical).
- **Actionable Fixes**: Provides both immediate mitigation and long-term prevention strategies.
- **Audit Logging**: Saves every analysis into a local SQLite database (`incident_audit.db`) for future reference.
- **Dual AI Models**: 
  - **Gemini 2.5 Flash** (via Google Generative AI)
  - **Llama 3.1** (via Groq)
- **FastAPI & LangServe Audit**: Built on modern, high-performance web frameworks.

---

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **AI Orchestration**: LangChain, LangServe
- **Models**: Google Gemini, Groq (Llama 3)
- **Database**: SQLite
- **Language**: Python 3.10+

---

## 📂 Project Structure

| File | Description |
| :--- | :--- |
| **`first.py`** | **The Backend (Server)**. Defines the API, prompts, AI chains, and database connection. |
| **`second.py`** | **The Client (User)**. Simulates an incident by sending logs to the server and printing the report. |
| **`incident_audit.db`** | **The Database**. Stores the history of all analyzed incidents. |
| **`.env`** | **Configuration**. secure file for storing `GOOGLE_API_KEY` and `GROQ_API_KEY`. |
| **`requirements.txt`** | **Dependencies**. List of all Python packages required to run the project. |
| **`a.py` / `b.py`** | *Legacy/Alternative versions (without database integration).* |

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd AI_Incident_Analyzer_(Project)
```

### 2. Create a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory and add your API keys:
```ini
GOOGLE_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🚀 Usage

### 1. Start the Server (Backend)
Run the FastAPI server using `uvicorn`:
```bash
uvicorn first:app --reload
```
*The server will start at `http://localhost:8000`*

### 2. Run the Client (Trigger Analysis)
Open a new terminal (keep the server running) and execute the client script:
```bash
python second.py
```

### 3. View the Output
You will see a structured report in your console:
```text
🧠 INCIDENT ANALYSIS REPORT
============================================================
Incident ID       : 550e8400-e29b-41d4-a716-446655440000
Root Cause        : Connection Timeout to Redis
Severity          : High
Affected Services : payment-service
Immediate Fix     : Restart Redis service and check network rules.
Analysis Time     : 2025-02-06T10:30:00
============================================================
```

---

## 🔌 API Endpoints

The system exposes the following endpoints (via LangServe):

- **Gemini Analysis**: `POST /gemini/incident/invoke`
- **Groq Analysis**: `POST /groq/incident/invoke`

You can also access the interactive API docs (Swagger UI) at:
`http://localhost:8000/docs`