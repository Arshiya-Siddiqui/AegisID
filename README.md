# AegisID - Machine Identity Zero-Trust

Zero-trust security for machine identities (API keys, IAM roles, service accounts). Built for AppliedAI Opus Challenge.

## Features
- Multi-format intake (JSON, CSV, REST API)
- AI-powered risk scoring (AI/ML API)
- Human-in-the-loop review simulation
- Tamper-evident audit trail
- Real-time observability

## Demo
Live dashboard: [streamlit.app/your-link](https://streamlit.app)

## Workflow Structure
See `workflow.json` for full Opus workflow.

## Quick Start
1. Deploy workflow to Opus
2. Add API keys to `config/api_keys.json`
3. Run dashboard
4. Upload file → Click RUN → Download audit

## Architecture
Supports 500+ identities with batching, parallel processing, and sub-workflows.
