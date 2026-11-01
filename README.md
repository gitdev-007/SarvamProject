# TenderGuard — AI-Powered Tender Intelligence & Compliance Platform

> **"Understand the tender. Verify your evidence. Find the gaps before submission."**

TenderGuard is an AI-powered bid-readiness platform built for Indian MSMEs, startups, and contractors. Powered by **Sarvam AI** (`sarvam-105b-conversations`), TenderGuard extracts RFP requirements, compares them against company evidence with deterministic arithmetic, identifies disqualification risks, generates traceable compliance matrices, and produces evidence-grounded proposals.

---

## 🌟 Key Features

1. **RFP & Tender Room**: Upload and manage RFPs, technical specifications, BOQs, and corrigenda.
2. **Requirement Extraction**: Structured requirement extraction with source document and page number references.
3. **Deterministic Compliance Engine**:
   - 3-Year Average Turnover calculation vs tender threshold (+₹2.67 Lakhs buffer check).
   - Past experience completed project count check (2 uploaded vs 3 required).
   - Certificate validity and expiration tracking against submission deadlines.
4. **Risk Auditor**: Disqualification gap analysis ranked by Critical, High, and Medium severity with actionable remediation steps.
5. **Proposal Studio**: Evidence-grounded drafting powered by Sarvam AI (`sarvam-105b-conversations`), preventing hallucinations by inserting `[USER INPUT REQUIRED]` placeholders for missing facts.
6. **Voice & Multilingual Assistant**: Natural language tender Q&A in English and Hindi with verifiable citations.
7. **Company Vault**: MSME Udyam details, GSTIN, PAN, audited turnover, and certificate management.

---

## 🏗️ Architecture

```text
SarvamProject/
│
├── frontend/             # Vercel Root Directory (React 18 + Vite)
│   ├── src/
│   │   ├── api/client.js
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── backend/              # Render Root Directory (Python FastAPI)
│   ├── app/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── seed_data.py
│   │   ├── services/
│   │   │   ├── sarvam_service.py
│   │   │   └── compliance_engine.py
│   │   └── routers/
│   │       ├── tenders.py
│   │       ├── documents.py
│   │       ├── requirements.py
│   │       ├── company.py
│   │       ├── risks.py
│   │       ├── proposal.py
│   │       └── voice.py
│   ├── main.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── package.json
│
├── .gitignore
└── README.md
```

---

## 🚀 Deployment

### 1. Backend on Render
1. Create a new **Web Service** on [Render](https://render.com).
2. Connect repository `https://github.com/gitdev-007/SarvamProject.git`.
3. Set **Root Directory**: `backend`
4. Set **Runtime**: `Python 3`
5. Set **Build Command**: `pip install -r requirements.txt`
6. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. In **Environment Variables**:
   - `SARVAM_API_KEY`: *(paste your Sarvam subscription key)*
8. Deploy and copy your backend URL (`https://your-service.onrender.com`).

### 2. Frontend on Vercel
1. Create a new Project on [Vercel](https://vercel.com).
2. Import repository `gitdev-007/SarvamProject`.
3. Set **Root Directory**: `frontend`
4. Framework Preset: **Vite** (auto-detected)
5. In **Environment Variables**:
   - `VITE_API_URL`: `https://your-service.onrender.com`
6. Deploy!

---

## 💻 Local Development

### Backend
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate  # On Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API Documentation will be live at `http://localhost:8000/docs`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.
