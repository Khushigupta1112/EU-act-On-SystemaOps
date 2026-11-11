# SystemaOps — Enterprise AI Compliance Control Plane

> **SystemaOps is the orchestration layer that connects AI systems, regulatory controls, evidence, assessments, security events, incidents, vendors, contracts, approvals and continuous reviews into one unified enterprise governance system.**

[![Backend CI](https://github.com/systemaops/systemaops/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/systemaops/systemaops/actions)
[![Frontend CI](https://github.com/systemaops/systemaops/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/systemaops/systemaops/actions)

---

## 🏛️ Architecture Overview

```text
                         SYSTEMAOPS
                 ENTERPRISE AI GOVERNANCE
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
        AI INVENTORY     CONTROLS          EVIDENCE
             |                |                |
             +----------------+----------------+
                              |
                              v
                       ASSESSMENT ENGINE
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
         PRIVACY         SECURITY         GOVERNANCE
             |                |                |
             +----------------+----------------+
                              |
                              v
                       GAP ANALYSIS
                              |
                              v
                       REMEDIATION
                              |
                              v
                        APPROVALS
                              |
                              v
                     CONTINUOUS REVIEW
                              |
                              v
                         AUDIT TRAIL
```

### Complete 12-Pillar Compliance Framework
1. **AI Systems Inventory** (Art. 49 & 71)
2. **Risk Classification Engine** (Art. 6 & Annex III)
3. **AI Literacy & Employee Training** (Art. 4)
4. **AI Transparency & Disclosure** (Art. 50)
5. **GDPR & Data-Processing Review** (Art. 10 & GDPR)
6. **Human Oversight Controls** (Art. 14)
7. **AI Accuracy, Robustness & Cybersecurity Testing** (Art. 15)
8. **Security & Incident Management** (Art. 73)
9. **AI Model/Vendor Assessment** (Art. 25 & 28)
10. **Technical Documentation & Audit Records** (Art. 11 & 12)
11. **Customer Contract Governance** (Art. 26)
12. **Regular Post-Market Compliance Review** (Art. 72)

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+ (Node 20+ recommended)
- PostgreSQL 16 (or SQLite for testing/standalone evaluation)

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Launch API server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access the Control Plane UI at: `http://localhost:3000`

---

## 🔒 Enterprise Security & Multi-Tenancy Guarantees
- **Strict Multi-Tenancy**: Organization tenant boundary (`organization_id`) enforced at DB, ORM, Repository and API layer.
- **Role-Based Access Control (RBAC)**: 11 enterprise roles (`SUPER_ADMIN`, `ORG_ADMIN`, `AI_GOVERNANCE`, `COMPLIANCE_MANAGER`, `PRIVACY_OFFICER`, etc.) and fine-grained permissions.
- **Tamper-Evident Audit Logging**: Append-only audit table recording all tenant state modifications and administrative actions.
- **Regulatory Integrity**: Transparent classification rules with human-in-the-loop approvals.

---

## ⚖️ Regulatory Disclaimer
*SystemaOps is a technical governance and compliance orchestration platform. It does not provide legal representation or legally certify compliance with the EU AI Act or any other regulation.*
