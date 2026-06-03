from __future__ import annotations

import os
from textwrap import dedent
from typing import Any

from openai import OpenAI

from app.models import (
    CoverLetterInput,
    InterviewInput,
    ResumeGenerateInput,
    ResumeOptimizeInput,
    TaskType,
)


PROMPTS: dict[TaskType, str] = {
    TaskType.resume_generate: (
        "You are a senior career coach. Create a polished professional resume in Markdown. "
        "Use concise bullet points, quantify impact when possible, and keep the tone suitable for early-career candidates."
    ),
    TaskType.resume_optimize: (
        "You are a resume editor. Improve the given resume text for clarity, impact, ATS readability, and professional wording. "
        "Return an optimized version plus a short skills suggestion section."
    ),
    TaskType.cover_letter: (
        "You are a career writing assistant. Write a tailored cover letter with a confident, specific, and professional tone."
    ),
    TaskType.interview_questions: (
        "You are an interview coach. Generate likely technical and behavioral interview questions with concise reference answers."
    ),
}


class AIService:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    async def generate(self, task_type: TaskType, payload: dict[str, Any]) -> tuple[str, str]:
        model = self._validate_payload(task_type, payload)
        prompt = self._build_user_prompt(task_type, model)

        if not self.client:
            return self._mock_response(task_type, model), "mock"

        response = self.client.responses.create(
            model=self.model,
            instructions=PROMPTS[task_type],
            input=prompt,
            max_output_tokens=1400,
        )
        return response.output_text.strip(), "openai"

    def _validate_payload(self, task_type: TaskType, payload: dict[str, Any]) -> Any:
        validators = {
            TaskType.resume_generate: ResumeGenerateInput,
            TaskType.resume_optimize: ResumeOptimizeInput,
            TaskType.cover_letter: CoverLetterInput,
            TaskType.interview_questions: InterviewInput,
        }
        return validators[task_type](**payload)

    def _build_user_prompt(self, task_type: TaskType, model: Any) -> str:
        fields = "\n".join(f"- {key}: {value}" for key, value in model.model_dump().items() if value)
        return f"Task: {task_type.value}\n\nInput:\n{fields}\n\nReturn Markdown only."

    def _mock_response(self, task_type: TaskType, model: Any) -> str:
        if task_type == TaskType.resume_generate:
            return dedent(
                f"""
                # {model.name}

                **Email:** {model.email} | **Phone:** {model.phone}

                ## Professional Summary
                Motivated candidate targeting {model.target_role or "an entry-level role"}, with hands-on project experience, strong learning ability, and a practical skill set.

                ## Education
                {model.education}

                ## Projects
                - Reframed project experience around business value, technical ownership, and measurable outcomes.
                - Highlighted collaboration, problem solving, and delivery quality.

                {model.projects}

                ## Skills
                {model.skills}
                """
            ).strip()

        if task_type == TaskType.resume_optimize:
            target = f" for {model.target_role}" if model.target_role else ""
            return dedent(
                f"""
                # Optimized Resume Draft{target}

                ## Improved Positioning
                - Strengthened action verbs and clarified ownership.
                - Converted generic responsibilities into outcome-focused bullet points.
                - Added ATS-friendly keywords based on the target direction.

                ## Revised Content
                {model.resume_text}

                ## Skills Suggestions
                Add concrete tools, frameworks, metrics, and project scale wherever possible.
                """
            ).strip()

        if task_type == TaskType.cover_letter:
            return dedent(
                f"""
                Dear Hiring Manager,

                I am excited to apply for the {model.job_title} role at {model.company_name}. My background has prepared me to contribute quickly, communicate clearly, and keep improving through hands-on work.

                In my recent experience, I have developed practical strengths that align with this role:

                {model.personal_experience}

                I would welcome the opportunity to discuss how my skills and motivation can support {model.company_name}'s goals.

                Sincerely,
                Your Candidate
                """
            ).strip()

        return dedent(
            f"""
            # Interview Prep: {model.job_title}

            ## Technical Questions
            1. Explain a core concept in {model.technical_direction} and how you used it in a project.
               - Reference answer: Define the concept, describe the project context, and explain the trade-off you made.
            2. How would you debug a production issue related to {model.technical_direction}?
               - Reference answer: Reproduce, inspect logs and metrics, isolate the cause, fix, test, and monitor.

            ## Behavioral Questions
            1. Tell me about a time you learned a new technology quickly.
               - Reference answer: Use STAR: situation, task, action, result.
            2. Describe a conflict or disagreement in a team project.
               - Reference answer: Focus on communication, evidence, and a constructive outcome.
            """
        ).strip()
