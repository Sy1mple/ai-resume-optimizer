# API

Base URL: `http://localhost:8000`

## GET `/health`

Returns service health.

```json
{
  "status": "ok"
}
```

## POST `/api/generate`

Generates AI content for one task.

Supported `task_type` values:

- `resume_generate`
- `resume_optimize`
- `cover_letter`
- `interview_questions`

Example:

```json
{
  "task_type": "cover_letter",
  "payload": {
    "company_name": "Example Inc.",
    "job_title": "Frontend Developer",
    "personal_experience": "Built Vue applications and collaborated with designers."
  }
}
```

Response:

```json
{
  "task_type": "cover_letter",
  "content": "Markdown content",
  "history_id": "uuid",
  "source": "free"
}
```

`source` can be:

- `free`: no-cost local rule-based generation
- `ollama`: no-cost local model through Ollama
- `openai`: OpenAI API generation, used only when `AI_PROVIDER=openai`

## GET `/api/history`

Returns up to 50 recent history records. Optional query: `user_id`.

## DELETE `/api/history/{record_id}`

Deletes a history record.
