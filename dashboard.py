import streamlit as st
import json
import requests
import base64
import pandas as pd
import plotly.express as px

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="AegisID — API Key Risk Analyzer",
    page_icon="🛡",
    layout="wide"
)

# ----------------------------
# Custom CSS (Enterprise UI)
# ----------------------------
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
.bad {  border-left: 6px solid #ef4444 !important; }

.step {
    font-size: 16px;
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 5px;
    background: #111827;
    border: 1px solid #1f2937;
}

.step-active {
    background: #2563eb !important;
    border-color: #1d4ed8 !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------
# Sidebar Navigation
# -----------------------------------
st.sidebar.title("🔎 Navigation")
page = st.sidebar.radio(
    "",
    ["🏠 Home", "📤 Upload", "📊 Results", "📁 Audit File"]
)

st.sidebar.markdown("---")
st.sidebar.caption("AegisID™ — Secure • Intelligent • Automated")

# -----------------------------------
# Home Page
# -----------------------------------
if page == "🏠 Home":
    st.markdown("<div class='big-title'>🛡 AegisID — API Key Risk Analysis System</div>", unsafe_allow_html=True)
    st.subheader("Enterprise-grade detection of risky API Keys")

    st.markdown("""
    AegisID analyzes **API Keys** to detect potential security risks, abnormal usage,
    exposure patterns, and missing safeguards like IP restrictions.

    ### 🔍 What This Workflow Does  
    """)

    with st.expander("📘 Workflow Explanation (Click to expand)"):
        st.markdown("""
        The workflow runs through the following steps:

        1️⃣ **Parse API Keys JSON**  
        2️⃣ **Risk Scoring using LLM**  
        3️⃣ **Parse & clean the LLM output**  
        4️⃣ **Split High/Low Risk keys**  
        5️⃣ **Generate Audit JSON**  
        6️⃣ **Return final risk results**

        This dashboard provides a clean user-friendly interface to run that workflow and analyze results.
        """)

    st.markdown("### 🚦 System Overview")
    col1, col2, col3 = st.columns(3)

    col1.metric("Analysis Speed", "Fast", "+ Real-time")
    col2.metric("Supported Keys", "Unlimited", "Batch mode")
    col3.metric("Security Level", "High", "LLM-driven")

# -----------------------------------
# Upload Page
# -----------------------------------
elif page == "📤 Upload":
    st.markdown("<div class='section-title'>📤 Upload API Keys JSON</div>", unsafe_allow_html=True)
    api_file = st.file_uploader("Upload your API Keys file", type=["json"])

    if api_file:
        st.success("API Keys file successfully uploaded. Ready to analyze.")

    run = st.button("⚡ Run AegisID Workflow")

    if run:
        if not api_file:
            st.error("Please upload a file first.")
        else:
            st.info("Running workflow... please wait.")

            OPUS_KEY = st.secrets["OPUS_API_KEY"]
            WORKFLOW_ID = st.secrets["WORKFLOW_ID"]

            api_keys_json = json.loads(api_file.read())
            payload = {"api_keys_json_file": api_keys_json}

            headers = {"Authorization": f"Bearer {OPUS_KEY}", "Content-Type": "application/json"}
            url = f"https://workflow.opus.ai/api/workflows/{WORKFLOW_ID}/run"

            response = requests.post(url, headers=headers, json={"inputs": payload})

            if response.status_code != 200:
                st.error(f"Workflow error: {response.text}")
            else:
                st.success("Workflow completed successfully!")
                st.session_state.run_output = response.json()

# -----------------------------------
# Results Page
# -----------------------------------
elif page == "📊 Results":
    st.markdown("<div class='section-title'>📊 API Key Risk Results</div>", unsafe_allow_html=True)

    if "run_output" not in st.session_state:
        st.warning("⚠ Please run the workflow first (Upload page).")
        st.stop()

    results = st.session_state.run_output["outputs"]["audit_json"]
    parsed = json.loads(results)

    # Build DataFrame for charts
    df = pd.DataFrame(parsed)

    # ----------------.- Risk Distribution Chart ----------------
    st.markdown("### 📈 Risk Score Distribution")
    fig = px.histogram(df, x="risk_score", nbins=10, title="Risk Score Histogram", color_discrete_sequence=["#3b82f6"])
    st.plotly_chart(fig, use_container_width=True)

    # ----------------.- Individual Results ----------------
    for item in parsed:
        risk = item["risk_score"]
        key_id = item["identity_id"]
        decision = item["decision"]

        css = "good" if risk < 30 else "warn" if risk < 60 else "bad"

        st.markdown(f"<div class='card {css}'>", unsafe_allow_html=True)
        st.markdown(f"### 🔑 `{key_id}`")
        st.write(f"**Risk Score:** {risk}")
        st.write(f"**Decision:** {decision}")
        st.write(f"**Usage Count:** {item['usage_count']}")
        st.write(f"**IP Restriction:** {item.get('ip_restriction')}")

        st.markdown("### 🛡 Security Recommendations")

        if risk >= 60:
            st.error("🚨 Immediate Rotation Required")
            st.markdown("""
            - This key is likely exposed or unsafe.
            - High volume usage without IP restrictions is dangerous.
            - Keys with names like *live* or *prod* attract attackers.
            - Rotate immediately and enable IP restriction.
            """)
        elif risk >= 30:
            st.warning("⚠ Key Should Be Reviewed")
            st.markdown("""
            - Monitor usage trends.
            - Add IP restriction.
            - Validate service integrations.
            """)
        else:
            st.success("🟢 Low Risk — No immediate vulnerabilities detected")

        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------
# Audit JSON Page
# -----------------------------------
elif page == "📁 Audit File":
    st.markdown("<div class='section-title'>📁 Download Audit File</div>", unsafe_allow_html=True)

    if "run_output" not in st.session_state:
        st.warning("⚠ Run workflow first.")
    else:
        results = st.session_state.run_output["outputs"]["audit_json"]
        b64 = base64.b64encode(results.encode()).decode()

        st.download_button(
            "📥 Download Full Audit JSON",
            data=b64,
            file_name="aegisid_audit.json",
            mime="application/json"
        )
