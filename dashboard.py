import streamlit as st
import json
import requests
import base64
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="AegisID — Machine Identity Intelligence",
    page_icon="🛡",
    layout="wide"
)

# ==========================================
# 2. CUSTOM CSS (Enterprise Theme)
# ==========================================
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Title */
.big-title {
    font-size: 40px !important;
    font-weight: 800 !important;
    padding-bottom: 5px;
}

/* Section Title */
.section-title {
    font-size: 24px !important;
    font-weight: 600 !important;
    margin-top: 25px;
    margin-bottom: 10px;
}

/* Cards */
.card {
    padding: 20px;
    border-radius: 12px;
    background: #1e293b;
    border: 1px solid #334155;
    margin-bottom: 15px;
}

.good { border-left: 6px solid #10b981 !important; }
.warn { border-left: 6px solid #f59e0b !important; }
.bad  { border-left: 6px solid #ef4444 !important; }

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. LOAD SECRETS
# ==========================================
OPUS_KEY = st.secrets["OPUS_API_KEY"]
WORKFLOW_ID = st.secrets["WORKFLOW_ID"]
AI_ML_API_KEY = st.secrets.get("AIML_API_KEY", None)


# ==========================================
# 4. AI ANALYSIS FUNCTION  (MUST BE BEFORE PAGE ROUTING)
# ==========================================
def analyze_key_with_ai(key_data):
    """Risk analysis using AI/ML — Extremely lightweight."""

    if not AI_ML_API_KEY:
        return {
            "ai_summary": "AI/ML API Key not configured.",
            "risk_factors": [],
            "recommendations": []
        }

    identity_json_str = json.dumps(key_data, indent=2)

    # --- SAFE PROMPT BUILDING ---
    prompt_template = """
You are a Senior Security Auditor. Analyze this machine identity and return ONLY JSON.

### IDENTITY DATA ###
{identity_json}

### REQUIRED OUTPUT FORMAT ###
{{
    "why_risky": "string",
    "what_attackers_can_do": "string",
    "business_impact": "string",
    "recommended_fix": ["string", "..."]
}}

Return ONLY valid JSON.
"""
    prompt = prompt_template.format(identity_json=identity_json_str)

    try:
        response = requests.post(
            "https://api.aimlapi.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {AI_ML_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )

        ai_data = response.json()
        content = ai_data["choices"][0]["message"]["content"]
        parsed = json.loads(content)

        return parsed

    except Exception as e:
        return {
            "why_risky": "AI analysis failed.",
            "what_attackers_can_do": str(e),
            "business_impact": "Unknown",
            "recommended_fix": ["Rotate key", "Add IP restrictions"]
        }


# ==========================================
# 5. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "",
    ["Home", "Upload", "Results", "Audit File"]
)

# ==========================================
# 6. PAGE ROUTING STARTS
# ==========================================

# ---------------- HOME PAGE ----------------
if page == "Home":

    st.markdown("<div class='big-title'>🛡 AegisID — API Key Risk Analysis</div>", unsafe_allow_html=True)
    st.subheader("Enterprise-grade exposure detection for API Keys")

    st.markdown("""
AegisID analyzes API Keys for:
- Exposure risks  
- Abnormal usage  
- Missing IP restrictions  
- Naming conventions that attract attackers  
- Potential compromise indicators  

The system runs an Opus workflow and adds AI insights for deep analysis.
    """)

    st.divider()
    st.markdown("### Pipeline Overview")
    st.markdown("""
1️⃣ Parse API Keys (JSON)  
2️⃣ Risk Scoring (Opus LLM)  
3️⃣ Parse Scored Output  
4️⃣ Split High / Low Risk  
5️⃣ Generate Audit JSON  
6️⃣ Add AI Explanation (Real-time)  
    """)


# ---------------- UPLOAD PAGE ----------------
elif page == "Upload":

    st.markdown("<div class='section-title'>📤 Upload API Keys JSON</div>", unsafe_allow_html=True)
    api_file = st.file_uploader("Upload your API Keys JSON", type=["json"])

    run = st.button("⚡ Run AegisID Workflow")

    if run:
        if not api_file:
            st.error("Upload a file first.")
            st.stop()

        st.info("Running workflow... ⏳")

        api_data = json.loads(api_file.read())

        url = f"https://workflow.opus.ai/api/workflows/{WORKFLOW_ID}/run"
        headers = {"Authorization": f"Bearer {OPUS_KEY}", "Content-Type": "application/json"}

        resp = requests.post(url, headers=headers, json={"inputs": {"api_keys_json_file": api_data}})

        if resp.status_code != 200:
            st.error(resp.text)
        else:
            st.success("Workflow completed!")
            st.session_state.workflow_data = resp.json()


# ---------------- RESULTS PAGE ----------------
elif page == "Results":

    if "workflow_data" not in st.session_state:
        st.warning("Run the workflow first.")
        st.stop()

    results = st.session_state.workflow_data["outputs"]["audit_json"]
    parsed = json.loads(results)

    st.markdown("<div class='section-title'> Risk Analysis Results</div>", unsafe_allow_html=True)

    df = pd.DataFrame(parsed)

    # Histogram
    fig = px.histogram(df, x="risk_score", nbins=10)
    st.plotly_chart(fig, use_container_width=True)

    # Per-key cards
    for item in parsed:

        key_id = item["identity_id"]
        risk = item["risk_score"]
        decision = item["decision"]

        css = "good" if risk < 30 else "warn" if risk < 60 else "bad"

        st.markdown(f"<div class='card {css}'>", unsafe_allow_html=True)
        st.markdown(f"### 🔑 {key_id}")
        st.write(f"**Risk Score:** {risk}")
        st.write(f"**Decision:** {decision}")
        st.write(f"**Usage Count:** {item['usage_count']}")
        st.write(f"**IP Restriction:** {item.get('ip_restriction')}")

        # 🔥 AI DEEP ANALYSIS
        st.markdown("### AI Security Insight")
        ai_info = analyze_key_with_ai(item)
        st.json(ai_info)

        st.markdown("</div>", unsafe_allow_html=True)


# ---------------- AUDIT FILE PAGE ----------------
elif page == "Audit File":

    if "workflow_data" not in st.session_state:
        st.warning("Run the workflow first.")
        st.stop()

    results = st.session_state.workflow_data["outputs"]["audit_json"]

    st.markdown("<div class='section-title'>📁 Download Audit JSON</div>", unsafe_allow_html=True)

    st.code(results, language="json")

    st.download_button(
        "⬇️ Download JSON",
        results,
        file_name="aegisid_audit.json",
        mime="application/json"
    )
