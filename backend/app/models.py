from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TaskType(str, Enum):
    resume_generate = "resume_generate"
    resume_optimize = "resume_optimize"
    resume_beautify = "resume_beautify"
    cover_letter = "cover_letter"
    interview_questions = "interview_questions"


class ResumeGenerateInput(BaseModel):
    name: str = Field(..., max_length=80)
    email: EmailStr
    phone: str = Field(..., max_length=40)
    education: str = Field(..., max_length=3000)
    projects: str = Field(..., max_length=5000)
    skills: str = Field(..., max_length=2000)
    target_role: str | None = Field(default=None, max_length=120)
    photo_data_url: str | None = Field(default=None, max_length=1_500_000)


class ResumeOptimizeInput(BaseModel):
    resume_text: str = Field(..., min_length=20, max_length=12000)
    target_role: str | None = Field(default=None, max_length=120)


class ResumeBeautifyInput(BaseModel):
    resume_text: str = Field(..., min_length=20, max_length=16000)
    target_role: str | None = Field(default=None, max_length=120)
    style: str | None = Field(default="modern", max_length=80)
    photo_included: bool = False


class CoverLetterInput(BaseModel):
    company_name: str = Field(..., max_length=120)
    job_title: str = Field(..., max_length=120)
    personal_experience: str = Field(..., min_length=20, max_length=8000)


class InterviewInput(BaseModel):
    job_title: str = Field(..., max_length=120)
    technical_direction: str = Field(..., max_length=160)
    experience_level: str | None = Field(default="Entry level", max_length=80)


class GenerateRequest(BaseModel):
    task_type: TaskType
    payload: dict[str, Any]
    user_id: UUID | None = None


class GenerateResponse(BaseModel):
    task_type: TaskType
    content: str
    history_id: str | None = None
    source: str


class HistoryRecord(BaseModel):
    id: str
    user_id: str | None = None
    task_type: TaskType
    content: str
    created_at: str


class ExportFormat(str, Enum):
    pdf = "pdf"
    docx = "docx"
    md = "md"
    txt = "txt"


class ExportRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=30000)
    format: ExportFormat
    file_name: str = Field(default="resume", max_length=80)
    candidate_name: str | None = Field(default=None, max_length=80)
    photo_data_url: str | None = Field(default=None, max_length=1_500_000)
    style: str | None = Field(default="modern", max_length=80)


class EmailCodeRequest(BaseModel):
    email: EmailStr


class EmailCodeResponse(BaseModel):
    email: EmailStr
    message: str
    dev_code: str


class VerifyEmailCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=8)


class QrLoginRequest(BaseModel):
    provider: str = Field(..., pattern="^(wechat|alipay)$")


class AuthResponse(BaseModel):
    user_id: str
    email: str | None = None
    provider: str
    display_name: str


class QrSessionRequest(BaseModel):
    provider: str = Field(..., pattern="^(wechat|alipay)$")


class QrSessionResponse(BaseModel):
    session_id: str
    provider: str
    qr_url: str
    expires_at: str
    status: str


class QrSessionStatus(BaseModel):
    session_id: str
    provider: str
    status: str
    user: AuthResponse | None = None
