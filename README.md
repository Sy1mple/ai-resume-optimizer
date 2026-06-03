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
- AI: free local rule-based generation by default, optional local Ollama model, optional OpenAI API
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

The backend works without an OpenAI key and does not spend money by default. `AI_PROVIDER=free` returns local rule-based content. If you install Ollama locally, set `AI_PROVIDER=ollama` to use a local model. Only set `AI_PROVIDER=openai` when you intentionally want to call the paid OpenAI API.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal. The default API base URL is `http://localhost:8000`.

## Environment Variables

Backend:

- `AI_PROVIDER`: `free`, `ollama`, or `openai`; defaults to `free`
- `OPENAI_API_KEY`: optional OpenAI API key
- `OPENAI_MODEL`: optional model name, defaults to `gpt-4.1-mini`
- `OLLAMA_BASE_URL`: optional local Ollama URL, defaults to `http://127.0.0.1:11434`
- `OLLAMA_MODEL`: optional local Ollama model, defaults to `qwen2.5:3b`
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
