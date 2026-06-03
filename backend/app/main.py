from __future__ import annotations

import os
import random
import socket
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response

from app.models import (
    AuthResponse,
    EmailCodeRequest,
    EmailCodeResponse,
    ExportRequest,
    GenerateRequest,
    GenerateResponse,
    HistoryRecord,
    QrLoginRequest,
    QrSessionRequest,
    QrSessionResponse,
    QrSessionStatus,
    VerifyEmailCodeRequest,
)
from app.services.ai_service import AIService
from app.services.export_service import export_document
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
email_codes: dict[str, str] = {}
qr_sessions: dict[str, dict[str, object]] = {}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/auth/email-code", response_model=EmailCodeResponse)
async def send_email_code(request: EmailCodeRequest) -> EmailCodeResponse:
    code = f"{random.randint(100000, 999999)}"
    email_codes[str(request.email).lower()] = code
    return EmailCodeResponse(
        email=request.email,
        message="Verification code generated for local demo.",
        dev_code=code,
    )


@app.post("/api/auth/verify-code", response_model=AuthResponse)
async def verify_email_code(request: VerifyEmailCodeRequest) -> AuthResponse:
    email = str(request.email).lower()
    if email_codes.get(email) != request.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    email_codes.pop(email, None)
    return AuthResponse(
        user_id=str(uuid4()),
        email=email,
        provider="email",
        display_name=email.split("@", 1)[0],
    )


@app.post("/api/auth/qr-login", response_model=AuthResponse)
async def qr_login(request: QrLoginRequest) -> AuthResponse:
    provider_name = "WeChat" if request.provider == "wechat" else "Alipay"
    return AuthResponse(
        user_id=str(uuid4()),
        provider=request.provider,
        display_name=f"{provider_name} Demo User",
    )


@app.post("/api/auth/qr-session", response_model=QrSessionResponse)
async def create_qr_session(payload: QrSessionRequest, request: Request) -> QrSessionResponse:
    session_id = str(uuid4())
    expires_at = datetime.now(UTC) + timedelta(minutes=5)
    qr_sessions[session_id] = {
        "provider": payload.provider,
        "status": "pending",
        "expires_at": expires_at,
        "user": None,
    }
    qr_url = f"{_public_base_url(request)}/api/auth/qr-session/{session_id}/confirm-page"
    return QrSessionResponse(
        session_id=session_id,
        provider=payload.provider,
        qr_url=qr_url,
        expires_at=expires_at.isoformat(),
        status="pending",
    )


@app.get("/api/auth/qr-session/{session_id}", response_model=QrSessionStatus)
async def get_qr_session(session_id: str) -> QrSessionStatus:
    session = _get_valid_qr_session(session_id)
    return QrSessionStatus(
        session_id=session_id,
        provider=str(session["provider"]),
        status=str(session["status"]),
        user=session["user"],
    )


@app.get("/api/auth/qr-session/{session_id}/confirm-page", response_class=HTMLResponse)
async def qr_confirm_page(session_id: str) -> str:
    session = _get_valid_qr_session(session_id)
    provider = "WeChat" if session["provider"] == "wechat" else "Alipay"
    return f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{provider} Login Confirm</title>
        <style>
          body {{ margin: 0; font-family: Arial, sans-serif; background: #eef2f6; color: #17212b; }}
          main {{ min-height: 100vh; display: grid; place-items: center; padding: 24px; }}
          section {{ width: min(420px, 100%); background: #fff; border: 1px solid #d8e1e8; border-radius: 12px; padding: 24px; box-shadow: 0 20px 60px rgba(23, 33, 43, .12); }}
          h1 {{ margin: 0 0 10px; font-size: 24px; }}
          p {{ color: #637383; line-height: 1.6; }}
          button {{ width: 100%; height: 46px; border: 0; border-radius: 8px; background: #216869; color: #fff; font-weight: 800; font-size: 16px; }}
        </style>
      </head>
      <body>
        <main>
          <section>
            <h1>{provider} scan login</h1>
            <p>Confirm this login request for AI Resume Optimizer. This local demo does not read your real {provider} identity.</p>
            <form method="post" action="/api/auth/qr-session/{session_id}/confirm">
              <button type="submit">Confirm login</button>
            </form>
          </section>
        </main>
      </body>
    </html>
    """


@app.post("/api/auth/qr-session/{session_id}/confirm", response_class=HTMLResponse)
async def confirm_qr_session(session_id: str) -> str:
    session = _get_valid_qr_session(session_id)
    provider_name = "WeChat" if session["provider"] == "wechat" else "Alipay"
    session["status"] = "confirmed"
    session["user"] = AuthResponse(
        user_id=str(uuid4()),
        provider=str(session["provider"]),
        display_name=f"{provider_name} Scan User",
    )
    return """
    <!doctype html>
    <html>
      <head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /></head>
      <body style="font-family: Arial, sans-serif; display: grid; min-height: 100vh; place-items: center; margin: 0; background: #eef2f6;">
        <main style="background: white; padding: 24px; border-radius: 12px; text-align: center;">
          <h1>Login confirmed</h1>
          <p>You can return to the desktop page now.</p>
        </main>
      </body>
    </html>
    """


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    content, source = await ai_service.generate(
        request.task_type,
        request.payload,
        provider=request.ai_provider,
    )
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


@app.post("/api/export")
async def export_resume(request: ExportRequest) -> Response:
    content, filename, media_type = export_document(request)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _get_valid_qr_session(session_id: str) -> dict[str, object]:
    session = qr_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="QR session not found")
    if datetime.now(UTC) > session["expires_at"]:
        session["status"] = "expired"
    return session


def _public_base_url(request: Request) -> str:
    configured = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")
    if configured:
        return configured
    port = request.url.port or 8000
    return f"http://{_local_ip()}:{port}"


def _local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
