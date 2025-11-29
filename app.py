import streamlit as st
import google.generativeai as genai
import json
import os
import pandas as pd
from PIL import Image
from datetime import datetime

# ==========================================
# 🎨 UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="CivicSight Auditor", page_icon="👁️", layout="wide")

# ==========================================
# 🔑 SECURITY & SETUP
# ==========================================
# Try getting key from Cloud Secrets (Hugging Face) first
try:
    API_KEY = os.environ.get("GOOGLE_API_KEY")
except:
    API_KEY = None

# If running locally, you can set it here for testing (DO NOT COMMIT KEY TO GITHUB)
if not API_KEY:
    # API_KEY = "AIzaSy..." 
    pass

if not API_KEY:
    st.error("🚨 API Key is missing! Please set GOOGLE_API_KEY in Hugging Face Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# ==========================================
# 🧠 AGENT LOGIC
# ==========================================

# 1. OBSERVABILITY (Scoring: Observability)
def log_trace(agent_name, action):
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"**[{timestamp}] {agent_name}:** {action}"

# 2. CUSTOM TOOL (Scoring: Custom Tools)
def risk_assessment_tool(damage_type, severity, metadata):
    """
    Deterministic Python Tool to calculate safety scores.
    """
    risk_score = int(severity) * 10
    
    # Safety Rules
    if metadata.get("near_school"): risk_score += 20
    if metadata.get("heavy_traffic"): risk_score += 15
    if metadata.get("water_leak"): risk_score += 10
    
    risk_score = min(100, risk_score)
    
    if risk_score >= 80: urgency = "CRITICAL"
    elif risk_score >= 50: urgency = "HIGH"
    else: urgency = "MODERATE"
    
    return {"risk_index": risk_score, "urgency": urgency}

# 3. MEMORY SYSTEM (Scoring: Long Term Memory)
MEMORY_FILE = "civic_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_memory(record):
    history = load_memory()
    history.append(record)
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# 4. CONTEXT ENGINEERING (Scoring: Context Compaction)
def get_context_summary(location):
    history = load_memory()
    relevant = [r for r in history if r['location'].lower() == location.lower()]
    if not relevant: return "No prior incidents at this site."
    return f"Found {len(relevant)} prior reports. Last reported severity: {relevant[-1]['vision_data']['severity']}/10."

# 5. ORCHESTRATOR (Scoring: Multi-Agent)
def run_audit_pipeline(image, location):
    logs = []
    
    # PHASE 1: VISION AGENT (Gemini 2.0)
    logs.append(log_trace("Agent-V", "Scanning image with Gemini 2.0 Vision..."))
    vision_model = genai.GenerativeModel('gemini-2.0-flash')
    vision_prompt = """
    Analyze this infrastructure image. Return strictly valid JSON:
    {
        "damage_type": "string (e.g. pothole, crack, garbage, streetlight)",
        "severity": integer (1-10),
        "metadata": {
            "near_school": boolean,
            "heavy_traffic": boolean,
            "water_leak": boolean
        },
        "description": "Short summary of the visual hazard"
    }
    """
    try:
        response = vision_model.generate_content([vision_prompt, image], generation_config={"response_mime_type": "application/json"})
        vision_data = json.loads(response.text)
        logs.append(log_trace("Agent-V", f"Identified {vision_data['damage_type']} (Sev: {vision_data['severity']})"))
    except Exception as e:
        return None, [f"Vision Error: {e}"]

    # PHASE 2: TOOL USE
    logs.append(log_trace("Risk-Tool", "Calculating safety metrics..."))
    risk_data = risk_assessment_tool(vision_data['damage_type'], vision_data['severity'], vision_data['metadata'])
    
    # PHASE 3: PLANNING & MEMORY
    logs.append(log_trace("Agent-M", f"Querying Memory Bank for '{location}'..."))
    context = get_context_summary(location)
    logs.append(log_trace("Agent-M", f"Context Retrieved: {context}"))
    
    logs.append(log_trace("Agent-P", "Drafting technical repair plan..."))
    planner_model = genai.GenerativeModel('gemini-2.0-flash')
    plan_prompt = f"""
    Act as City Engineer. 
    Issue: {vision_data['damage_type']}
    Risk Score: {risk_data['risk_index']}
    History Context: {context}
    
    Task: Provide 3 bullet points for immediate technical remediation.
    """
    plan_response = planner_model.generate_content(plan_prompt)
    
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "location": location,
        "vision_data": vision_data,
        "risk_data": risk_data,
        "plan": plan_response.text,
        "context": context
    }
    save_memory(record)
    return record, logs

# ==========================================
# 🎨 MAIN UI LAYOUT
# ==========================================

# Custom CSS for "Cards"
st.markdown("""
<style>
    .risk-card {
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .metric-value { font-size: 32px; font-weight: bold; }
    .metric-label { font-size: 14px; color: #555; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ System Status")
    st.success("✅ Agents Online")
    st.info("🧠 Memory Bank Active")
    st.divider()
    st.markdown("**Architecture:**")
    st.caption("1. Agent-V (Vision)")
    st.caption("2. Risk Tool (Logic)")
    st.caption("3. Agent-P (Planner)")

# Main Header
st.title("👁️ CivicSight: Infrastructure Auditor")
st.markdown("*Autonomous Risk Assessment for Smart Cities*")

# Step 1: Input
st.markdown("### 1️⃣ Incident Context")
col_a, col_b = st.columns([2, 1])
with col_a:
    loc_input = st.text_input("📍 Location Address", placeholder="e.g. Ward 12, Main St")
with col_b:
    st.write("")
    st.caption("Enter a specific address to activate the Memory Agent.")

if not loc_input:
    st.warning("⚠️ Please enter a location to enable the Audit Agents.")
    st.stop()

# Step 2: Upload
st.markdown("### 2️⃣ Site Inspection")
col1, col2 = st.columns([1, 1.2])

with col1:
    img_file = st.file_uploader("Upload Inspection Image", type=['jpg', 'png'])
    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="Live Site Feed", use_container_width=True)

with col2:
    if img_file:
        if st.button("🚀 Run Audit Pipeline", type="primary", use_container_width=True):
            with st.spinner("🤖 Agents are orchestrating..."):
                record, logs = run_audit_pipeline(img, loc_input)
                
                if record:
                    # --- DASHBOARD ---
                    r_score = record['risk_data']['risk_index']
                    urgency = record['risk_data']['urgency']
                    bg_color = '#ffe6e6' if r_score > 75 else '#fff5e6' if r_score > 50 else '#e6ffe6'
                    text_color = '#cc0000' if r_score > 75 else '#cc6600' if r_score > 50 else '#006600'

                    st.markdown(f"""
                    <div class="risk-card" style="background-color: {bg_color};">
                        <div class="metric-label">CALCULATED RISK INDEX</div>
                        <div class="metric-value" style="color: {text_color}">{r_score} / 100</div>
                        <div style="font-weight: bold; margin-top:5px;">STATUS: {urgency}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("") 

                    # Tabs
                    tab1, tab2, tab3 = st.tabs(["👁️ Vision Data", "🛠️ Repair Plan", "🧠 History Log"])
                    
                    with tab1:
                        v = record['vision_data']
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("Damage Type", v['damage_type'].upper())
                            st.metric("Severity", f"{v['severity']}/10")
                        with c2:
                            st.caption("Detected Hazards")
                            st.checkbox("Near School", value=v['metadata']['near_school'], disabled=True)
                            st.checkbox("Heavy Traffic", value=v['metadata']['heavy_traffic'], disabled=True)
                            st.checkbox("Water Leak", value=v['metadata']['water_leak'], disabled=True)
                        st.progress(v['severity'] / 10, text="Severity Level")

                    with tab2:
                        st.info("Engineering Solution:")
                        st.markdown(record['plan'])
                    
                    with tab3:
                        st.warning(f"Memory Context: {record['context']}")
                        full_history = load_memory()
                        if full_history:
                            df = pd.DataFrame(full_history)
                            # Create clean table for display
                            display_df = pd.DataFrame({
                                "Time": df['timestamp'],
                                "Location": df['location'],
                                "Issue": df['vision_data'].apply(lambda x: x['damage_type']),
                                "Risk": df['risk_data'].apply(lambda x: x['risk_index'])
                            })
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                    
                    # Logs
                    with st.expander("🕵️ Live Agent Trace (Observability)"):
                        for log in logs: st.markdown(log)