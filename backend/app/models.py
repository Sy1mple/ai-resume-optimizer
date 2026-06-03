from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TaskType(str, Enum):
    resume_generate = "resume_generate"
    resume_optimize = "resume_optimize"
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


class ResumeOptimizeInput(BaseModel):
    resume_text: str = Field(..., min_length=20, max_length=12000)
    target_role: str | None = Field(default=None, max_length=120)


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
