# SarvamProject

A full-stack Indic AI Chat application powered by **Sarvam AI** (`sarvam-105b-conversations`).

## Architecture

- **`frontend/`**: Modern React + Vite application ready for **Vercel** deployment.
- **`backend/`**: Python FastAPI backend service ready for **Render** deployment.

```text
SarvamProject/
│
├── frontend/             # Vercel Root Directory
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── .env.example
│
├── backend/              # Render Root Directory
│   ├── main.py
│   ├── requirements.txt
│   ├── package.json
│   └── .env.example
│
├── .gitignore
├── .env                  # Secret API keys (never committed)
├── main.py               # Quick standalone test script
└── README.md
```

---

## Deployment

### 1. Backend on Render
1. Create a new **Web Service** on [Render](https://render.com).
2. Connect your GitHub repository `https://github.com/gitdev-007/SarvamProject.git`.
3. Set **Root Directory** to `backend`.
4. Set **Runtime** to `Python 3`.
5. Set **Build Command**: `pip install -r requirements.txt`
6. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. In **Environment Variables**, add:
   - `SARVAM_API_KEY`: Your Sarvam AI API subscription key.

### 2. Frontend on Vercel
1. Create a new Project on [Vercel](https://vercel.com).
2. Connect your GitHub repository `https://github.com/gitdev-007/SarvamProject.git`.
3. In Project Settings, set **Root Directory** to `frontend`.
4. Framework Preset: **Vite** (auto-detected).
5. In **Environment Variables**, add:
   - `VITE_API_URL`: The URL of your deployed Render backend (e.g. `https://your-service.onrender.com`).
6. Click **Deploy**.

---

## Local Development

### 1. Backend
```bash
cd backend
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
# Ensure SARVAM_API_KEY is in your environment or .env
uvicorn main:app --reload --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.
