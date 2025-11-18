import streamlit as st
import requests
import json
from datetime import datetime

# ----------------------------
# CONFIGURATION
# ----------------------------
OPUS_API_KEY = st.secrets["OPUS_API_KEY"]
WORKFLOW_ID = st.secrets["WORKFLOW_ID"]

HEADERS = {
    "Authorization": f"Bearer {OPUS_API_KEY}",
    "Content-Type": "application/json"
}

# ----------------------------
# PAGE SETTINGS
# ----------------------------
st.set_page_config(
    page_title="AegisID Dashboard",
    layout="wide",
    page_icon="🔐"
)

st.title("🔐 AegisID — Identity Risk Analysis System")
st.subheader("AI-powered detection of risky API Keys & IAM Roles\n")


# ----------------------------
# SECTION: Workflow Overview
# ----------------------------
st.markdown("### 📘 What This Workflow Does")

st.info("""
AegisID analyzes API Keys and IAM Roles to detect potential security risks.
Your Opus workflow performs these steps:

1️⃣ **Parse API Keys**  
2️⃣ **AI Risk Scoring (Custom Agent)**  
3️⃣ **Parse Scored Identities**  
4️⃣ **Split High/Low Risk**  
5️⃣ **Generate Audit File**  
6️⃣ **Return final audit JSON**

This dashboard lets you **trigger the workflow and view results live**.
""")


# ----------------------------
# INPUT SECTION
# ----------------------------
st.markdown("### 📥 Upload API Keys JSON")

api_file = st.file_uploader("Upload API Keys JSON file", type=["json"])

st.markdown("### 🔗 IAM Roles API Endpoint")

iam_endpoint = st.text_input(
    "Enter IAM Roles API URL",
    placeholder="https://example.com/iam_roles"
)

if st.button("▶️ Run AegisID Workflow", use_container_width=True):

    if api_file is None:
        st.error("Please upload your API keys JSON file.")
        st.stop()

    if iam_endpoint.strip() == "":
        st.error("Please enter a valid IAM Roles API endpoint.")
        st.stop()

    with st.spinner("Running Opus Workflow... Please wait ⏳"):
        
        # Read uploaded API keys JSON
        api_json = json.load(api_file)

        # Build workflow input payload
        payload = {
            "inputs": {
                "api_keys_json_file": api_json,
                "iam_roles_api_endpoint": [iam_endpoint]   # Opus expects a list
            }
        }

        # Call Opus workflow
        url = f"https://api.opus.ai/workflows/{WORKFLOW_ID}/run"
        response = requests.post(url, headers=HEADERS, json=payload)

        if response.status_code != 200:
            st.error("Workflow failed ❌")
            st.json(response.json())
            st.stop()

        result = response.json()

    st.success("Workflow completed successfully! 🎉")

    # ----------------------------
    # OUTPUT SECTION
    # ----------------------------
    st.markdown("## 📊 AegisID Results")

    # Extract outputs
    outputs = result.get("outputs", {})

    # High & Low Risk results
    high_risk = outputs.get("high_risk", [])
    low_risk = outputs.get("low_risk", [])
    audit_json = outputs.get("audit_json", "")

    # Show high risk
    with st.expander("🔥 High Risk Identities", expanded=True):
        if high_risk:
            st.json(high_risk)
        else:
            st.info("No high-risk identities detected")

    # Show low risk
    with st.expander("🟢 Low Risk Identities"):
        st.json(low_risk)

    # Show audit file
    with st.expander("📁 Audit JSON File"):
        st.code(audit_json, language="json")

    # Download audit file
    st.download_button(
        "⬇️ Download Audit JSON",
        data=audit_json,
        file_name=f"aegisid_audit_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json"
    )


# ----------------------------
# FOOTER
# ----------------------------
st.markdown("---")
st.caption("Built using Opus + Streamlit · AegisID Security System")
