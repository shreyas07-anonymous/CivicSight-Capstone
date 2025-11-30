# 👁️ CivicSight: AI-Powered Infrastructure Auditor
### 🌍 Track: Agents for Good (Smart Cities & Governance)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://huggingface.co/spaces/ShreyasPatankar/CivicSight-Live)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini%202.0-blue)](https://deepmind.google/technologies/gemini/)

## 🎥 Project Demo
### [▶️ Click Here to Watch the Video Walkthrough](PASTE_YOUR_YOUTUBE_LINK_HERE)

---

## 1. The Problem: Cities are "Blind"
Urban infrastructure maintenance is currently **reactive** and **unstructured**.
* **No Standard:** A citizen reports a "bad pothole," but city officials have no objective way to measure severity remotely.
* **No Memory:** If a road is repaired and breaks again in two weeks, legacy systems treat it as a "new" issue, failing to detect the **trend** of poor workmanship.
* **Slow Response:** Manual inspection takes days.

## 2. The Solution: CivicSight
CivicSight is a Multi-Agent system that transforms a single photo into a **Quantified Risk Assessment**. It moves governance from "Reactive Repairs" to "Proactive Auditing."

### 💡 Why AI Agents?
A standard script can detect a pothole, but it cannot reason about budget constraints or remember context from two weeks ago. Multi-Agent orchestration allows us to separate Observation (Agent-V) from Logic (Risk Tool) and Reasoning (Agent-P), preventing hallucinations and ensuring safety-critical accuracy.

### 🚀 Key Capabilities
1.  **Quantifies Risk:** Uses Computer Vision to assign a specific `Risk Index` (0-100) based on severity and environmental context.
2.  **Long-Term Memory:** Remembers every audit. If you upload a photo of a location that has been reported before, it flags it as a **"Recurring Issue"**.
3.  **Action Planning:** Instantly generates a technical repair plan and budget estimate.

---

## 3. Agent Architecture
![CivicSight Architecture](civicsight_architecture.png)
I implemented a **Sequential Multi-Agent Pipeline** powered by **Google Gemini 2.0 Flash**:

* **👁️ Agent-V (Vision):** The Perception Layer. It analyzes images to extract structured metadata (Damage Type, Severity 1-10).
* **🧮 Tool (Risk Engine):** A deterministic Python function that calculates safety scores based on strict variables. *Example: If `heavy_traffic=True`, Risk Score += 15.*
* **🧠 Agent-M (Memory):** The Context Layer. It queries a persistent JSON database to retrieve history.
* **👷 Agent-P (Planner):** The Reasoning Layer. It uses **Context Compaction** to summarize history and generate a remediation plan.

---

## 4. Technical Implementation (Scoring Criteria)
This project demonstrates **5 Key Agent Concepts**:
1.  **Sequential Agents:** (Vision → Tool → Planner).
2.  **Custom Tools:** (`risk_assessment_tool` for deterministic logic).
3.  **Long-Term Memory:** Persistent database (JSON) vs. ephemeral chat history.
4.  **Context Engineering:** Summarizing historical logs to save tokens.
5.  **Observability:** Real-time "Trace Logs" in the UI to visualize agent thought processes.

## 5. How to Run Locally

### Prerequisites

Python 3.10+

A Google Gemini API Key (Free tier works)

Git installed

### Installation Steps

Clone the repository:
 ```bash
git clone [https://github.com/YOUR_USERNAME/CivicSight-Capstone.git](https://github.com/YOUR_USERNAME/CivicSight-Capstone.git)
```
Install dependencies:
 ```bash
pip install -r requirements.txt
```

### Set your API Key:

#### Linux/Mac
```bash
export GOOGLE_API_KEY="AIzaSy..."
```
#### Windows PowerShell
```bash
$env:GOOGLE_API_KEY="AIzaSy..."
```

### Run the app:
```bash
streamlit run app.py
```

