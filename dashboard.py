import streamlit as st
import requests
import json
import base64
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
import os

# ============= ENTERPRISE CONFIGURATION =============
# API Keys (loaded from Streamlit secrets)
OPUS_API_KEY = st.secrets.get("OPUS_API_KEY", "")
AI_ML_API_KEY = st.secrets.get("AI_ML_API_KEY", "")
WORKFLOW_ID = st.secrets.get("WORKFLOW_ID", "")

# ============= THEME MANAGER (Dark/Light Mode) =============
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def get_theme_colors():
    """Return theme-specific color palette"""
    if st.session_state.theme == 'dark':
        return {
            'bg_primary': '#0E1117',
            'bg_secondary': '#1E293B',
            'bg_card': '#1F2937',
            'border': '#374151',
            'text': '#FAFAFA',
            'accent': '#10B981',
            'warning': '#F59E0B',
            'danger': '#EF4444',
            'success': '#10B981',
            'muted': '#9CA3AF'
        }
    else:
        return {
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#F9FAFB',
            'bg_card': '#F3F4F6',
            'border': '#D1D5DB',
            'text': '#111827',
            'accent': '#2563EB',
            'warning': '#D97706',
            'danger': '#DC2626',
            'success': '#059669',
            'muted': '#6B7280'
        }

colors = get_theme_colors()

# ============= ENTERPRISE CSS =============
st.markdown(f"""
<style>
    .main {{background-color: {colors['bg_primary']}; color: {colors['text']};}}
    .stButton>button {{
        background-color: {colors['accent']};
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: {colors['accent']}CC;
        transform: translateY(-2px);
    }}
    
    .risk-card {{
        background: {colors['bg_card']};
        border: 1px solid {colors['border']};
        border-radius: 12px;
        padding: 24px;
        margin: 12px 0;
        transition: all 0.3s ease;
    }}
    .risk-card:hover {{transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.2);}}
    
    .status-badge {{
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
        margin: 4px;
    }}
    .status-low {{background: {colors['success']}20; color: {colors['success']};}}
    .status-medium {{background: {colors['warning']}20; color: {colors['warning']};}}
    .status-high {{background: {colors['danger']}20; color: {colors['danger']};}}
    
    .stepper-container {{display: flex; justify-content: space-between; margin: 32px 0;}}
    .step {{
        flex: 1;
        text-align: center;
        padding: 16px;
        position: relative;
    }}
    .step::after {{
        content: '';
        position: absolute;
        top: 24px;
        right: -50%;
        width: 100%;
        height: 2px;
        background: {colors['border']};
        z-index: 0;
    }}
    .step:last-child::after {{display: none;}}
    .step-circle {{
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: {colors['bg_secondary']};
        border: 2px solid {colors['border']};
        color: {colors['muted']};
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 12px;
        font-weight: bold;
        position: relative;
        z-index: 1;
        transition: all 0.3s ease;
    }}
    .step.active .step-circle {{
        background: {colors['accent']};
        border-color: {colors['accent']};
        color: white;
        transform: scale(1.1);
    }}
    .step.completed .step-circle {{
        background: {colors['success']};
        border-color: {colors['success']};
        color: white;
    }}
</style>
""", unsafe_allow_html=True)

# ============= THEME TOGGLE =============
col1, col2 = st.sidebar.columns([1, 1])
with col1:
    st.sidebar.markdown("### 🎨 Appearance")
with col2:
    if st.sidebar.button("🌓 Toggle Theme"):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.experimental_rerun()

# ============= NAVIGATION =============
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔎 Navigation")
page = st.sidebar.radio(
    "",
    ["🏠 Home", "📤 Upload & Analyze", "📊 Risk Intelligence", "📁 Audit Trail", "⚙️ Configuration"],
    label_visibility="collapsed"
)

# ============= HOME PAGE =============
if page == "🏠 Home":
    st.markdown(f"<h1 style='color:{colors['accent']}; font-size: 42px; font-weight: 800;'>AegisID Enterprise</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{colors['muted']}; font-size: 18px;'>Zero-Trust Machine Identity Security Platform</p>", unsafe_allow_html=True)
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Scans", "1,247", "+23%", delta_color="normal")
    col2.metric("High Risk Detected", "89", "-12%", delta_color="inverse")
    col3.metric("Auto-Remediated", "1,158", "93%", delta_color="normal")
    col4.metric("Avg Decision Time", "2.3s", "-0.4s", delta_color="normal")
    
    # Animated stepper
    st.markdown("---")
    st.markdown(f"<h3 style='color:{colors['text']};'>Workflow Pipeline</h3>", unsafe_allow_html=True)
    
    stepper_html = f"""
    <div class="stepper-container">
        <div class="step completed">
            <div class="step-circle">1</div>
            <div>Ingest</div>
        </div>
        <div class="step completed">
            <div class="step-circle">2</div>
            <div>AI Analysis</div>
        </div>
        <div class="step active">
            <div class="step-circle">3</div>
            <div>Risk Scoring</div>
        </div>
        <div class="step">
            <div class="step-circle">4</div>
            <div>Enforce</div>
        </div>
    </div>
    """
    st.markdown(stepper_html, unsafe_allow_html=True)
    
    # Vulnerability summary panel
    st.markdown("---")
    st.markdown(f"<h3 style='color:{colors['text']};'>Critical Vulnerabilities</h3>", unsafe_allow_html=True)
    vuln_col1, vuln_col2 = st.columns(2)
    
    with vuln_col1:
        st.markdown(f"""
        <div class="risk-card" style="border-left: 4px solid {colors['danger']};">
            <h4 style="color:{colors['danger']};'>🔴 12 Keys Exposed in Public Repos</h4>
            <p style="color:{colors['muted']};'>GitHub scanning detected hardcoded credentials in commits</p>
            <span class="status-badge status-high">IMMEDIATE ACTION</span>
        </div>
        """, unsafe_allow_html=True)
    
    with vuln_col2:
        st.markdown(f"""
        <div class="risk-card" style="border-left: 4px solid {colors['warning']};">
            <h4 style="color:{colors['warning']};'>🟡 89 Keys Without IP Restrictions</h4>
            <p style="color:{colors['muted']};'>High-privilege keys lack network-level controls</p>
            <span class="status-badge status-medium">REVIEW REQUIRED</span>
        </div>
        """, unsafe_allow_html=True)

# ============= UPLOAD & ANALYZE =============
elif page == "📤 Upload & Analyze":
    st.markdown(f"<h2 style='color:{colors['text']};'>Upload API Key Inventory</h2>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose JSON file with API keys",
        type=["json"],
        help="Expected format: {'api_keys': [{'key_id': '...', 'ip_restriction': '...', ...}]}"
    )
    
    if uploaded_file:
        st.success("✅ File uploaded successfully")
        
        preview_data = json.load(uploaded_file)
        uploaded_file.seek(0)
        
        with st.expander("📋 Preview Data"):
            st.json(preview_data)
        
        st.markdown("---")
        st.markdown("### Analysis Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            model_choice = st.selectbox(
                "AI Model",
                ["gpt-3.5-turbo-16k (Cost-Optimized)", "gpt-4-turbo-preview (Premium)"],
                help="GPT-3.5-turbo: $0.003/scan | GPT-4: $0.03/scan"
            )
        
        with col2:
            batch_size = st.slider("Batch Size", 5, 50, 10, help="Number of keys to analyze per batch")
        
        cost_per_key = 0.003 if "3.5" in model_choice else 0.03
        estimated_cost = batch_size * cost_per_key
        st.info(f"💰 **Estimated Cost:** ${estimated_cost:.3f} for {batch_size} keys")
        
        if st.button("🚀 Run AegisID Analysis", type="primary", use_container_width=True):
            st.session_state['analysis_running'] = True
            st.session_state['file_data'] = preview_data
            st.session_state['model_choice'] = model_choice
            st.experimental_rerun()

# ============= RISK INTELLIGENCE =============
elif page == "📊 Risk Intelligence":
    if 'analysis_running' not in st.session_state:
        st.warning("⚠️ Please run analysis first")
        st.stop()
    
    st.markdown(f"<h2 style='color:{colors['text']};'>AI-Powered Risk Intelligence</h2>", unsafe_allow_html=True)
    
    if st.session_state.get('analysis_running', False):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        api_keys = st.session_state['file_data'].get('api_keys', [])
        results = []
        
        for idx, key_data in enumerate(api_keys):
            progress = (idx + 1) / len(api_keys)
            progress_bar.progress(progress)
            status_text.text(f"Analyzing: {key_data['key_id'][:16]}... ({idx+1}/{len(api_keys)})")
            
            result = analyze_key_with_ai(key_data, st.session_state.get('model_choice', 'gpt-3.5-turbo-16k'))
            results.append(result)
            time.sleep(0.3)
        
        status_text.text("✅ Analysis complete!")
        st.session_state['analysis_results'] = results
        st.session_state['analysis_running'] = False
        st.experimental_rerun()
    
    if 'analysis_results' in st.session_state:
        results = st.session_state['analysis_results']
        df = pd.DataFrame(results)
        
        st.markdown("---")
        st.markdown(f"<h3 style='color:{colors['text']};'>Risk Distribution</h3>", unsafe_allow_html=True)
        
        fig = px.histogram(df, x="risk_score", nbins=10, title="Risk Score Distribution", color_discrete_sequence=[colors['accent']])
        fig.update_layout(paper_bgcolor=colors['bg_primary'], plot_bgcolor=colors['bg_card'], font_color=colors['text'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown(f"<h3 style='color:{colors['text']};'>Vulnerability Summary</h3>", unsafe_allow_html=True)
        
        high_risk = len(df[df['risk_score'] >= 60])
        medium_risk = len(df[(df['risk_score'] >= 30) & (df['risk_score'] < 60)])
        low_risk = len(df[df['risk_score'] < 30])
        
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        summary_col1.metric("🔴 High Risk", high_risk, "Critical")
        summary_col2.metric("🟡 Medium Risk", medium_risk, "Review")
        summary_col3.metric("🟢 Low Risk", low_risk, "Accepted")
        
        st.markdown("---")
        st.markdown(f"<h3 style='color:{colors['text']};'>Detailed Findings</h3>", unsafe_allow_html=True)
        
        for result in results:
            risk_score = result['risk_score']
            risk_class = "bad" if risk_score >= 60 else "warn" if risk_score >= 30 else "good"
            badge_class = "status-high" if risk_score >= 60 else "status-medium" if risk_score >= 30 else "status-low"
            
            st.markdown(f"""
            <div class="risk-card {risk_class}">
                <h4 style="margin-bottom:8px;">🔑 {result['identity_id'][:24]}...</h4>
                <span class="status-badge {badge_class}">Risk: {risk_score}/100</span>
                <span class="status-badge" style="background:{colors['bg_secondary']};">{result['decision']}</span>
                <p style="color:{colors['muted']}; margin-top:12px;">
                    <strong>Critical Factors:</strong> {', '.join(result.get('critical_factors', []))}
                </p>
            </div>
            """, unsafe_allow_html=True)

# ============= AUDIT TRAIL =============
elif page == "📁 Audit Trail":
    st.markdown(f"<h2 style='color:{colors['text']};'>Audit Trail & Compliance</h2>", unsafe_allow_html=True)
    
    if 'analysis_results' not in st.session_state:
        st.warning("⚠️ No audit data available")
        st.stop()
    
    results = st.session_state['analysis_results']
    audit_json = json.dumps(results, indent=2)
    
    st.download_button(
        label="📥 Download Audit JSON",
        data=audit_json,
        file_name=f"aegisid_audit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )
    
    st.markdown("---")
    st.markdown(f"<h3 style='color:{colors['text']};'>Compliance Summary</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="risk-card">
            <h4 style="color:{colors['accent']};'>📊 Audit Metadata</h4>
            <p>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p>Records: {len(results)}</p>
            <p>Model: {results[0].get('model_used', 'Unknown')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="risk-card">
            <h4 style="color:{colors['accent']};'>🛡 Compliance Standards</h4>
            <p>✅ SOC 2 Type II Ready</p>
            <p>✅ ISO 27001 Mapped</p>
            <p>✅ NIST Framework Aligned</p>
        </div>
        """, unsafe_allow_html=True)

# ============= AI/ML ANALYSIS FUNCTION =============
def analyze_key_with_ai(key_data, model_choice="gpt-3.5-turbo-16k"):
    """Intelligent risk analysis using AI/ML API - Cost: ~$0.003 per key"""

    model = "gpt-3.5-turbo-16k" if "3.5" in model_choice else "gpt-4-turbo-preview"

    # Convert key data to JSON string
    identity_json_str = json.dumps(key_data, indent=2)

    # ===================== FIXED PROMPT (Correct Indentation) =====================
    prompt_template = """
You are a Senior Security Auditor. Analyze this machine identity and return ONLY JSON.

### IDENTITY DATA ###
{identity_json}

### RISK FRAMEWORK ###
- 0–30 = low risk (auto-accept)
- 31–60 = medium risk (human review)
- 61–100 = high risk (auto-reject)

### CHECK FOR ###
1. Exposure risk (public repos, logs, screenshots)
2. Over-privilege or unsafe permissions
3. High usage anomalies
4. Missing IP restrictions
5. Naming patterns like "prod", "live" that attract attackers
6. Rotation hygiene and lifespan

### OUTPUT STRICTLY AS JSON ###
{
  "risk_score": number,
  "decision": "auto_accept | human_review | auto_reject",
  "critical_factors": ["string", "..."],
  "exposure_likelihood": "low | medium | high",
  "privilege_level": "low | medium | high"
}

Return ONLY valid JSON.
"""

    prompt = prompt_template.format(identity_json=identity_json_str)
    # ===========================================================================

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

        ai_output = response.json()['choices'][0]['message']['content']
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
        # Fail-safe scoring in case of LLM failure
        fallback_score = 30

        if not key_data.get("ip_restriction"):
            fallback_score += 25
        if key_data.get("usage_count", 0) > 10000:
            fallback_score += 15

        return {
            "identity_id": key_data['key_id'],
            "risk_score": min(fallback_score, 100),
            "decision": "human_review" if fallback_score >= 30 else "auto_accept",
            "critical_factors": [f"Fallback: {str(e)}"],
            "exposure_likelihood": "unknown",
            "privilege_level": "unknown",
            "timestamp": datetime.utcnow().isoformat(),
            "model_used": "error_fallback"
        }

# ============= CONFIGURATION PAGE =============
elif page == "⚙️ Configuration":
    st.markdown(f"<h2 style='color:{colors['text']};'>Platform Configuration</h2>", unsafe_allow_html=True)
    
    st.markdown("### 🔐 API Keys Status")
    
    key_status = {
        "OPUS_API_KEY": "✅ Active" if OPUS_API_KEY else "❌ Missing",
        "AI_ML_API_KEY": "✅ Active" if AI_ML_API_KEY else "❌ Missing",
        "WORKFLOW_ID": "✅ Configured" if WORKFLOW_ID else "❌ Missing"
    }
    
    for key, status in key_status.items():
        badge_type = "status-low" if "✅" in status else "status-high"
        st.markdown(f"""
        <div class="risk-card">
            <h4>{key}</h4>
            <span class="status-badge {badge_type}">{status}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Cost tracking dashboard
    st.markdown("---")
    st.markdown("### 💰 Cost Tracking Dashboard")
    
    if 'analysis_results' in st.session_state:
        total_scans = len(st.session_state['analysis_results'])
        total_cost = total_scans * 0.003
        remaining = 20 - total_cost
        
        cost_col1, cost_col2, cost_col3 = st.columns(3)
        cost_col1.metric("Total Scans", total_scans)
        cost_col2.metric("Session Spend", f"${total_cost:.3f}")
        cost_col3.metric("Credits Remaining", f"${remaining:.2f}")
        
        # Progress bar to $20
        st.progress(min(total_cost / 20, 1.0))
        
        if total_cost > 15:
            st.warning("⚠️ Approaching $20 credit limit. Switch to smaller batches.")
        elif total_cost > 18:
            st.error("🚨 Stop! You are near the $20 limit. Use test keys only.")
    else:
        st.info("No analysis runs yet. Each key costs ~$0.003 to analyze.")
        st.metric("Estimated Max Scans", f"{int(20/0.003):,}", "with $20 credits")
