from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models import GenerateRequest, GenerateResponse, HistoryRecord
from app.services.ai_service import AIService
from app.services.history_store import HistoryStore

load_dotenv()

app = FastAPI(title="AI Resume Optimizer API", version="0.1.0")

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = AIService()
history_store = HistoryStore()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    content, source = await ai_service.generate(request.task_type, request.payload)
    record = await history_store.add(
        task_type=request.task_type,
        content=content,
        user_id=str(request.user_id) if request.user_id else None,
    )
    return GenerateResponse(
        task_type=request.task_type,
        content=content,
        history_id=record.id,
        source=source,
    )


@app.get("/api/history", response_model=list[HistoryRecord])
async def list_history(user_id: str | None = Query(default=None)) -> list[HistoryRecord]:
    return await history_store.list(user_id=user_id)


@app.delete("/api/history/{record_id}")
async def delete_history(record_id: str) -> dict[str, bool]:
    deleted = await history_store.delete(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History record not found")
    return {"deleted": True}
