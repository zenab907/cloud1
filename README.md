# AI Career Match

A university demo project that compares a CV (PDF) with a Job Description.
- Frontend: React + Vite
- Backend: Python + FastAPI
- PDF text extraction: PyMuPDF
- Matching: lightweight skill extraction and transparent scoring (no paid APIs)

## Run locally

### 1) Backend
Open PowerShell in the project folder:

```powershell
cd E:\AI_Career_Match\backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend runs at http://127.0.0.1:8000

If PowerShell blocks activation, run this once in that terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2) Frontend
Open a SECOND PowerShell terminal:

```powershell
cd E:\AI_Career_Match\frontend
npm.cmd install
npm.cmd run dev
```

Open the URL shown by Vite (usually http://localhost:5173).

## Notes
- This is an educational prototype, not an employment decision system.
- The score is an explainable keyword/skill overlap estimate, not a validated hiring score.
- No accounts, paid APIs, or database are required for the core demo.
- For deployment, the frontend and backend are hosted separately. Configure `VITE_API_URL` to the deployed backend URL.
