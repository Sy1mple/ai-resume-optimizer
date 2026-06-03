# AI Resume Optimizer

AI Resume Optimizer is a full-stack MVP for generating and improving job application materials with AI.

It includes:

- Resume generation
- Resume optimization
- Cover letter generation
- Interview question generation
- Local history records, with optional Supabase integration

## Tech Stack

- Frontend: Vue 3, JavaScript, Vite, Element Plus, Axios
- Backend: FastAPI, Python
- AI: OpenAI API, with deterministic mock output when no API key is configured
- Database: Supabase optional, in-memory fallback for local demos

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   └── services/
│   │       ├── ai_service.py
│   │       └── history_store.py
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   ├── api.md
│   └── product.md
└── frontend/
    ├── src/
    │   ├── App.vue
    │   ├── main.js
    │   ├── api.js
    │   └── styles.css
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Run Locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

The backend works without an OpenAI key by returning mock content. To enable real AI generation, set `OPENAI_API_KEY` in `backend/.env`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal. The default API base URL is `http://localhost:8000`.

## Environment Variables

Backend:

- `OPENAI_API_KEY`: optional OpenAI API key
- `OPENAI_MODEL`: optional model name, defaults to `gpt-4.1-mini`
- `SUPABASE_URL`: optional Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: optional Supabase service role key

Frontend:

- `VITE_API_BASE_URL`: optional backend base URL

## MVP Demo Flow

1. Fill in resume details and generate a resume.
2. Paste an existing resume and optimize it.
3. Generate a cover letter for a target company and role.
4. Generate interview questions for a role and technical direction.
5. Review recent generation history.
