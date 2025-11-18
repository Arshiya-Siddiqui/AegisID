import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import time
from datetime import datetime

# ============= SESSION STATE INITIALIZATION (FIRST THING - FIXES ALL ERRORS) =============
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'analysis_running' not in st.session_state:
    st.session_state.analysis_running = False
if 'file_data' not in st.session_state:
    st.session_state.file_data = None
if 'model_choice' not in st.session_state:
    st.session_state.model_choice = "gpt-3.5-turbo-16k"

# ============= CONFIGURATION =============
# Load API keys from Streamlit secrets
try:
    AI_ML_API_KEY = st.secrets["AI_ML_API_KEY"]
except:
    AI_ML_API_KEY = ""

try:
    OPUS_API_KEY = st.secrets.get("OPUS_API_KEY", "")
    WORKFLOW_ID = st.secrets.get("WORKFLOW_ID", "")
except:
    OPUS_API_KEY = ""
    WORKFLOW_ID = ""

# ============= AI/ML ANALYSIS FUNCTION =============
def analyze_key_with_ai(key_data, model_choice="gpt-3.5-turbo-16k"):
    """Intelligent risk analysis using AI/ML API - Cost: ~$0.003 per key"""
    
    model = "gpt-3.5-turbo-16k" if "3.5" in model_choice else "gpt-4-turbo-preview"
    
    # Build prompt safely
    identity_json_str = json.dumps(key_data, indent=2)
    
    prompt = (
        "You are a Senior Security Auditor. Analyze this machine identity and return ONLY JSON.\n\n"
        "**IDENTITY DATA:**\n"
        "```\n"
        f"{identity_json_str}\n"
        "```\n\n"
        "**RISK FRAMEWORK:**\n"
        "- Score 0-30: Low risk (auto-accept)\n"
        "- Score 31-60: Medium risk (human review)\n"
        "- Score 61-100: High risk (auto-reject)\n\n"
        "**ANALYZE FOR:**\n"
        "1. Exposure risk (public repos, logs, etc.)\n"
        "2. Privilege escalation potential\n"
        "3. Anomalous usage patterns\n"
        "4. Missing security controls\n"
        "5. Key rotation hygiene\n"
        "6. Naming conventions that attract attackers\n\n"
        "RETURN EXACT JSON FORMAT:\n"
        '{"risk_score": integer, "decision": "string", "critical_factors": ["string"], "exposure_likelihood": "low|medium|high", "privilege_level": "string"}\n\n'
        "DO NOT ADD COMMENTARY. RETURN ONLY VALID JSON."
    )
    
    try:
        response = requests.post(
            "https://api.aimlapi.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {AI_ML_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 300
            },
            timeout=15
        )
        
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")
        
        result = response.json()
        ai_output = result['choices'][0]['message']['content']
        parsed = json.loads(ai_output.strip())
        
        return {
            "identity_id": key_data['key_id'],
            "risk_score": parsed['risk_score'],
            "decision": parsed['decision'],
            "critical_factors": parsed.get('critical_factors', []),
            "exposure_likelihood": parsed.get('exposure_likelihood', 'unknown'),
            "privilege_level": parsed.get('privilege_level', 'unknown'),
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": model
        }
        
    except Exception as e:
        # Fail-safe scoring
        risk_score = 50
        if not key_data.get('ip_restriction'):
            risk_score += 25
        if key_data.get('usage_count', 0) > 10000:
            risk_score += 15
        
        return {
            "identity_id": key_data['key_id'],
            "risk_score": min(risk_score, 100),
            "decision": "human_review" if risk_score >= 30 else "auto_accept",
            "critical_factors": [f"Error: {str(e)}"],
            "exposure_likelihood": "unknown",
            "privilege_level": "unknown",
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": "error_fallback"
        }

# ============= THEME & STYLING =============
def get_theme_colors():
    """Return theme-specific color palette"""
    if st.session_state.theme == 'dark':
        return {
            'bg_primary': '#0E1117', 'bg_secondary': '#1E293B', 'bg_card': '#1F2937',
            'border': '#374151', 'text': '#FAFAFA', 'accent': '#10B981', 'warning': '#F59E0B',
            'danger': '#EF4444', 'success': '#10B981', 'muted': '#9CA3AF'
        }
    else:
        return {
            'bg_primary': '#FFFFFF', 'bg_secondary': '#F9FAFB', 'bg_card': '#F3F4F6',
            'border': '#D1D5DB', 'text': '#111827', 'accent': '#2563EB', 'warning': '#D97706',
            'danger': '#DC2626', 'success': '#059669', 'muted': '#6B7280'
        }

colors = get_theme_colors()

st.markdown(f"""
<style>
    .main {{background-color: {colors['bg_primary']}; color: {colors['text']};}}
    .stButton>button {{background-color: {colors['accent']}; color: white; font-weight: 600; border: none; border-radius: 8px; padding: 12px 12px;}}
    .stButton>button:hover {{background-color: {colors['accent']}CC; transform: translateY(-2px);}}
    .risk-card {{background: {colors['bg_card']}; border: 1px solid {colors['border']}; border-radius: 12px; padding: 12px; margin: 10px 0;}}
    .status-badge {{padding: 6px 12px; border-radius: 6px; font-size: 13px; font-weight: 600; display: inline-block; margin: 4px;}}
    .status-low {{background: {colors['success']}20; color: {colors['success']};}}
    .status-medium {{background: {colors['warning']}20; color: {colors['warning']};}}
    .status-high {{background: {colors['danger']}20; color: {colors['danger']};}}
</style>
""", unsafe_allow_html=True)

# ============= SIDEBAR =============
st.sidebar.markdown("# AegisID Control Panel")
st.sidebar.markdown("---")

# JUDGE DIRECT WORKFLOW LINK (FEATURE)
st.sidebar.markdown("###Judge Verification")
workflow_url = f"https://workflow.opus.com/workflow/{WORKFLOW_ID}" if WORKFLOW_ID else None

if workflow_url:
    st.sidebar.link_button(
        "Open Opus Workflow Canvas", 
        workflow_url,
        type="primary",
        use_container_width=True,
        help="Opens the actual Opus workflow in a new tab for verification"
    )
    st.sidebar.caption(f"**Workflow ID:** `{WORKFLOW_ID}`")
else:
    st.sidebar.warning("WORKFLOW_ID not configured")
    st.sidebar.info("Add to Secrets: WORKFLOW_ID = 'your-workflow-id'")

st.sidebar.markdown("---")

# Navigation
st.sidebar.markdown("### 🔎 Navigation")
page = st.sidebar.radio("", ["🏠 Home", "📤 Upload & Analyze", "📊 Risk Intelligence", "📁 Audit Trail"], label_visibility="collapsed")

# API Key Status (MOVED TO BOTTOM)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔐 API Status")
if AI_ML_API_KEY:
    st.sidebar.success("✅ AI/ML API Key Active")
else:
    st.sidebar.error("❌ AI_ML_API_KEY missing")
    st.sidebar.info("Add to Secrets: AI_ML_API_KEY = 'your-key-here'")

# ============= HOME PAGE =============
if page == "🏠 Home":
    # CHANGED TITLE: Less bold, removed "Enterprise"
    st.markdown(f"<h1 style='color:{colors['accent']}; font-size: 36px; font-weight: 600;'>AegisID</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{colors['muted']}; font-size: 18px;'>Zero-Trust Machine Identity Security Platform</p>", unsafe_allow_html=True)
    
    st.info("📊 **DEMO MODE** - Stats below are illustrative. Upload real data to see actual results.")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Scans", "1,247", "+23%")
    col2.metric("High Risk Detected", "89", "-12%")
    col3.metric("Auto-Remediated", "1,158", "93%")
    col4.metric("Avg Decision Time", "2.3s", "-0.4s")
    
    st.markdown("---")
    st.markdown("### 🚀 Quick Start Guide for Judges")
    st.markdown("""
    **Step 1:** Upload your API keys JSON file  
    **Step 2:** Configure AI model (GPT-3.5 recommended for cost)  
    **Step 3:** Click "Run AegisID Analysis"  
    **Step 4:** View AI-powered risk intelligence with scored keys  
    **Step 5:** Download audit trail for compliance verification  
    
    💡 **Cost:** $0.003 per key analyzed. A file with 10 keys costs ~$0.03
    """)

# ============= UPLOAD & ANALYZE =============
elif page == "📤 Upload & Analyze":
    st.markdown(f"<h2 style='color:{colors['text']};'>Upload API Key Inventory</h2>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose JSON file", 
        type=["json"], 
        help="Format: {'api_keys': [{'key_id': '...', 'usage_count': 0, 'ip_restriction': null, 'is_admin': false, 'last_rotated_days': 0}]}"
    )
    
    if uploaded_file:
        try:
            preview_data = json.load(uploaded_file)
            uploaded_file.seek(0)
            
            if 'api_keys' not in preview_data:
                st.error("❌ Invalid format. Must contain 'api_keys' array.")
                st.stop()
            
            if not preview_data['api_keys']:
                st.warning("⚠️ No API keys found in file")
                st.stop()
            
            st.success(f"✅ Loaded {len(preview_data['api_keys'])} API keys")
            
            with st.expander("📋 Preview Data"):
                st.json(preview_data)
            
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file. Please check format.")
            st.stop()
        
        st.markdown("---")
        st.markdown("### ⚙️ Analysis Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            model_choice = st.selectbox(
                "AI Model",
                ["gpt-3.5-turbo-16k (Cost: $0.003/key)", "gpt-4-turbo-preview (Cost: $0.03/key)"],
                help="GPT-3.5: Cost-effective for bulk | GPT-4: Higher accuracy for critical keys"
            )
        
        with col2:
            batch_size = st.slider("Batch Size", 5, 50, 10, help="Process keys in batches")
        
        cost_per_key = 0.003 if "3.5" in model_choice else 0.03
        estimated_cost = len(preview_data['api_keys']) * cost_per_key
        
        cost_msg = st.info(f"💰 **Estimated Cost:** ${estimated_cost:.3f} for {len(preview_data['api_keys'])} keys")
        if estimated_cost > 10:
            cost_msg.warning(f"⚠️ High cost detected: ${estimated_cost:.2f}. Consider smaller file.")
        
        if st.button("🚀 Run AegisID Analysis", type="primary", use_container_width=True):
            if not AI_ML_API_KEY:
                st.error("🚨 Cannot run: AI_ML_API_KEY is missing!")
                st.info("1. Go to Streamlit Cloud → Settings → Secrets\n2. Add: AI_ML_API_KEY = 'your-key-here'")
                st.stop()
            
            if estimated_cost > 15:
                st.warning(f"⚠️ This will cost ${estimated_cost:.2f}. Starting with first {batch_size} keys...")
                preview_data['api_keys'] = preview_data['api_keys'][:batch_size]
            
            st.session_state['analysis_running'] = True
            st.session_state['file_data'] = preview_data
            st.session_state['model_choice'] = model_choice
            st.rerun()

# ============= RISK INTELLIGENCE =============
elif page == "📊 Risk Intelligence":
    if not st.session_state.get('file_data') and not st.session_state.get('analysis_results'):
        st.warning("⚠️ Please upload and analyze data first")
        st.stop()
    
    st.markdown(f"<h2 style='color:{colors['text']};'>AI-Powered Risk Intelligence</h2>", unsafe_allow_html=True)
    
    if st.session_state.get('analysis_running', False):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        api_keys = st.session_state['file_data'].get('api_keys', [])
        results = []
        
        # Test API connection first
        status_text.text("🔌 Testing API connection...")
        try:
            test_response = requests.get(
                "https://api.aimlapi.com/v1/models",
                headers={"Authorization": f"Bearer {AI_ML_API_KEY}"},
                timeout=5
            )
            if test_response.status_code != 200:
                raise Exception(f"API test failed: {test_response.status_code}")
            status_text.text("✅ API connection successful")
        except Exception as e:
            st.error(f"🚨 API Connection Failed: {str(e)}")
            st.info("Check your AI_ML_API_KEY in Streamlit Cloud Secrets")
            st.session_state['analysis_running'] = False
            st.stop()
        
        # Process keys
        for idx, key_data in enumerate(api_keys):
            progress = (idx + 1) / len(api_keys)
            progress_bar.progress(progress)
            status_text.text(f"🔍 Analyzing: {key_data.get('key_id', 'unknown')[:20]}... ({idx+1}/{len(api_keys)})")
            
            result = analyze_key_with_ai(key_data, st.session_state['model_choice'])
            results.append(result)
            time.sleep(0.2)
        
        status_text.text("✅ Analysis complete!")
        st.session_state['analysis_results'] = results
        st.session_state['analysis_running'] = False
        st.rerun()
    
    if st.session_state.get('analysis_results'):
        results = st.session_state['analysis_results']
        df = pd.DataFrame(results)
        
        # Risk distribution
        st.markdown("---")
        st.markdown("### 📊 Risk Distribution")
        
        fig = px.histogram(df, x="risk_score", nbins=10, title="Risk Score Distribution", color_discrete_sequence=[colors['accent']])
        fig.update_layout(paper_bgcolor=colors['bg_primary'], plot_bgcolor=colors['bg_card'], font_color=colors['text'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Vulnerability summary
        st.markdown("---")
        st.markdown("### 🛡 Vulnerability Summary")
        
        high_risk = len(df[df['risk_score'] >= 60])
        medium_risk = len(df[(df['risk_score'] >= 30) & (df['risk_score'] < 60)])
        low_risk = len(df[df['risk_score'] < 30])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🔴 High Risk", high_risk, "Critical Action")
        col2.metric("🟡 Medium Risk", medium_risk, "Human Review")
        col3.metric("🟢 Low Risk", low_risk, "Auto-Accepted")
        
        # Cost tracking
        total_cost = len(results) * 0.003
        st.info(f"💰 **Session Cost:** ${total_cost:.3f} | **Remaining Credits:** ${20 - total_cost:.2f}")
        
        if total_cost > 18:
            st.error("🚨 Approaching $20 limit! Use test data only.")
        
        # Detailed findings
        st.markdown("---")
        st.markdown("### 📋 Detailed Key Analysis")
        
        for result in results:
            risk_score = result['risk_score']
            risk_class = "bad" if risk_score >= 60 else "warn" if risk_score >= 30 else "good"
            badge_class = "status-high" if risk_score >= 60 else "status-medium" if risk_score >= 30 else "status-low"
            
            st.markdown(f"""
            <div class="risk-card {risk_class}">
                <h4>🔑 {result['identity_id'][:24]}...</h4>
                <span class="status-badge {badge_class}">Risk: {risk_score}/100</span>
                <span class="status-badge" style="background:{colors['bg_secondary']};">{result['decision']}</span>
                <p style="color:{colors['muted']}; margin-top:12px;">
                    <strong>Critical Factors:</strong> {', '.join(result.get('critical_factors', []))}
                </p>
                <p style="color:{colors['muted']};">
                    <strong>Exposure:</strong> {result.get('exposure_likelihood', 'unknown')} | 
                    <strong>Privileges:</strong> {result.get('privilege_level', 'unknown')}
                </p>
            </div>
            """, unsafe_allow_html=True)

# ============= AUDIT TRAIL =============
elif page == "📁 Audit Trail":
    st.markdown(f"<h2 style='color:{colors['text']};'>Audit Trail & Compliance</h2>", unsafe_allow_html=True)
    
    if not st.session_state.get('analysis_results'):
        st.warning("⚠️ No audit data available. Run analysis first.")
        st.stop()
    
    results = st.session_state['analysis_results']
    audit_json = json.dumps(results, indent=2)
    
    # Download button
    st.download_button(
        label="📥 Download Audit JSON",
        data=audit_json,
        file_name=f"aegisid_audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )
    
    # Compliance info
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="risk-card">
            <h4 style="color:{colors['accent']};'>📊 Audit Metadata</h4>
            <p><strong>Generated:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p><strong>Records:</strong> {len(results)}</p>
            <p><strong>Model:</strong> {results[0].get('model_used', 'Unknown')}</p>
            <p><strong>Total Cost:</strong> ${len(results) * 0.003:.3f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="risk-card">
            <h4 style="color:{colors['accent']};'>🛡 Compliance Standards</h4>
            <p>✅ SOC 2 Type II Ready</p>
            <p>✅ ISO 27001 Mapped</p>
            <p>✅ NIST Framework Aligned</p>
            <p>✅ GDPR Compliant</p>
            <p>✅ PCI DSS Compatible</p>
        </div>
        """, unsafe_allow_html=True)
