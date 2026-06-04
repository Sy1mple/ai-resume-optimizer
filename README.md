# AI Resume Optimizer

AI Resume Optimizer is a full-stack resume generation and optimization app for job seekers. It can generate polished resumes from structured input, refine existing resume drafts, upload a profile photo, export documents in multiple formats, and provide job-matching suggestions.

## Live Demo

Production deployment:

https://ai-resume-optimizer-coral.vercel.app/

## Features

- Resume generation: Create a professional resume from name, target role, education, project experience, and skill keywords.
- Integrated optimization workflow: Generate a resume from form input or continue polishing an existing resume draft in the same workspace.
- Smart skills formatting: Convert raw skill keywords into resume-ready skill bullets, sorted by priority such as frameworks, middleware/databases, languages, and engineering tools.
- Structured project input: Each project can include project introduction, project architecture, technical architecture, and personal responsibilities.
- Multiple projects: Add or remove project entries for realistic resume building.
- Bilingual UI: Switch between Chinese and English across the login screen, main interface, status panels, placeholders, and generated content.
- Profile photo upload: Upload a candidate photo for preview and exported documents.
- Multi-format export: Export resumes as PDF, Word DOCX, Markdown, or TXT.
- Login demo: Email verification-code login, plus WeChat and Alipay QR-code login demos.
- Job matching plan: Generate compliant job-board matching and resume delivery suggestions based on role, city, salary range, keywords, and platforms.
- AI mode selection: Free local generation by default; paid OpenAI mode only runs when the user enters their own API key.
- History records: Keep recent generation history for review and reuse.

## Important Notes

The project does not spend OpenAI credits by default. Free mode uses local rule-based generation and templates. OpenAI is called only when the user selects the paid OpenAI API mode and enters their own API key.

The WeChat and Alipay QR-code login flows are demo flows. The QR codes are real scannable URLs that open a confirmation page and update login status, but they are not connected to official WeChat Open Platform or Alipay Open Platform OAuth production authentication.

The job matching feature generates compliant recommendations and application plans. It does not bypass job-board rules and does not perform automated bulk applications.

## Tech Stack

- Frontend: Vue 3, Vite, Element Plus, Axios, QRCode
- Backend: FastAPI, Python, Pydantic
- Export: python-docx, ReportLab, Pillow
- AI: local free rule-based generation, optional Ollama, optional OpenAI API
- Deployment: Vercel
- Data: in-memory history records, with optional Supabase integration reserved

## Project Structure

```text
.
├── api/
│   └── index.py                  # Vercel Python Function entry
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI routes
│   │   ├── models.py             # Request and response models
│   │   └── services/
│   │       ├── ai_service.py     # Resume generation, optimization, and job matching
│   │       ├── export_service.py # PDF, Word, and text export
│   │       └── history_store.py  # History storage
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.vue               # Main application UI
│   │   ├── api.js                # Frontend API wrapper
│   │   ├── main.js
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── docs/
├── pyproject.toml
├── requirements.txt
├── vercel.json
└── README.md
```

## Local Development

### 1. Start the Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Default backend URL:

```text
http://localhost:8000
```

### 2. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Default frontend URL:

```text
http://127.0.0.1:5173
```

## Environment Variables

Backend environment variables:

```text
AI_PROVIDER=free
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_TIMEOUT_SECONDS=45
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
PUBLIC_BASE_URL=
```

Frontend environment variables:

```text
VITE_API_BASE_URL=http://localhost:8000
```

On Vercel, the frontend uses same-origin relative API paths by default, so `VITE_API_BASE_URL` is not required for production.

## API Overview

Main endpoints:

- `POST /api/generate`: Generate or optimize resume content, or generate a job matching plan.
- `GET /api/history`: Fetch generation history.
- `DELETE /api/history/{record_id}`: Delete a history record.
- `POST /api/export`: Export PDF, DOCX, Markdown, or TXT.
- `POST /api/auth/email-code`: Generate a demo email verification code.
- `POST /api/auth/verify-code`: Verify an email code.
- `POST /api/auth/qr-session`: Create a QR login session.
- `GET /api/auth/qr-session/{session_id}`: Check QR login status.
- `GET /api/auth/qr-session/{session_id}/confirm-page`: Open the QR confirmation page.

## Deployment

The project is deployed on Vercel:

https://ai-resume-optimizer-coral.vercel.app/

Vercel configuration is stored in `vercel.json`:

- Build command: `cd frontend && npm ci && npm run build`
- Output directory: `frontend/dist`
- API rewrite: `/api/(.*)` routes to `api/index.py`
- SPA rewrite: all other routes return `index.html`

The backend dependencies were updated for Vercel's current Python build environment. The build environment also sets `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` for Python package compatibility.

## GitHub Repository

Remote repository:

https://github.com/Sy1mple/ai-resume-optimizer

Main branch:

```text
main
```

## Future Improvements

- Connect real WeChat Open Platform and Alipay Open Platform authentication.
- Integrate authorized job-board APIs for role search and application tracking.
- Add user accounts and cloud-based resume version management.
- Add more resume templates for different roles and industries.
- Add ATS scoring, job description matching, and keyword gap analysis.
- Add more model providers such as OpenAI, DeepSeek, Qwen, and Zhipu AI.
