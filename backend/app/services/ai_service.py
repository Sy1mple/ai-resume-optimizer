from __future__ import annotations

import os
import json
from textwrap import dedent
from typing import Any
from urllib import error, request

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - keeps the free local mode dependency-light
    OpenAI = None

from app.models import (
    CoverLetterInput,
    InterviewInput,
    JobMatchInput,
    ResumeBeautifyInput,
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
    TaskType.resume_beautify: (
        "You are a senior resume designer and editor. Transform the resume into a visually organized, high-impact Markdown resume. "
        "Use clean sections, strong verbs, quantified bullets, and ATS-friendly wording. Keep it honest and concise."
    ),
    TaskType.cover_letter: (
        "You are a career writing assistant. Write a tailored cover letter with a confident, specific, and professional tone."
    ),
    TaskType.interview_questions: (
        "You are an interview coach. Generate likely technical and behavioral interview questions with concise reference answers."
    ),
    TaskType.job_match: (
        "You are a recruiting operations analyst. Match the candidate resume to relevant job channels and openings. "
        "Score fit honestly, identify gaps, and produce a compliant application plan without bypassing platform rules."
    ),
}


class AIService:
    def __init__(self) -> None:
        self.provider = os.getenv("AI_PROVIDER", "free").strip().lower()
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        self.ollama_timeout = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45"))
        self.client = self._openai_client() if self.provider == "openai" else None

    async def generate(
        self,
        task_type: TaskType,
        payload: dict[str, Any],
        provider: str | None = None,
        openai_api_key: str | None = None,
    ) -> tuple[str, str]:
        model = self._validate_payload(task_type, payload)
        prompt = self._build_user_prompt(task_type, model)
        active_provider = (provider or self.provider or "free").strip().lower()

        if active_provider == "ollama":
            local_response = self._ollama_response(task_type, prompt)
            if local_response:
                return local_response, "ollama"
            return self._mock_response(task_type, model), "free"

        if active_provider == "openai":
            client = self._openai_client(openai_api_key) if openai_api_key else self.client or self._openai_client()
            if not client:
                return self._mock_response(task_type, model), "free"
            response = client.responses.create(
                model=self.openai_model,
                instructions=PROMPTS[task_type],
                input=prompt,
                max_output_tokens=1400,
            )
            return response.output_text.strip(), "openai"

        return self._mock_response(task_type, model), "free"

    def _openai_client(self, api_key: str | None = None) -> Any:
        active_key = (api_key or self.api_key).strip()
        return OpenAI(api_key=active_key) if active_key and OpenAI else None

    def _validate_payload(self, task_type: TaskType, payload: dict[str, Any]) -> Any:
        validators = {
            TaskType.resume_generate: ResumeGenerateInput,
            TaskType.resume_optimize: ResumeOptimizeInput,
            TaskType.resume_beautify: ResumeBeautifyInput,
            TaskType.cover_letter: CoverLetterInput,
            TaskType.interview_questions: InterviewInput,
            TaskType.job_match: JobMatchInput,
        }
        return validators[task_type](**payload)

    def _build_user_prompt(self, task_type: TaskType, model: Any) -> str:
        fields = "\n".join(f"- {key}: {value}" for key, value in model.model_dump().items() if value)
        style_note = ""
        if task_type == TaskType.resume_beautify:
            style_note = (
                "\n\nStyle rules:\n"
                "- modern: polished and visually balanced, with a strong summary and grouped strengths.\n"
                "- executive: formal leadership tone, accomplishment-led bullets, and confident positioning.\n"
                "- compact-ats: plain ATS-safe structure, dense bullets, minimal decoration, and keyword clarity.\n"
            )
        return f"Task: {task_type.value}\n\nInput:\n{fields}{style_note}\n\nReturn Markdown only."

    def _ollama_response(self, task_type: TaskType, prompt: str) -> str | None:
        payload = {
            "model": self.ollama_model,
            "prompt": f"{PROMPTS[task_type]}\n\n{prompt}",
            "stream": False,
            "options": {
                "temperature": 0.35,
                "num_predict": 1400,
            },
        }
        api_request = request.Request(
            f"{self.ollama_base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(api_request, timeout=self.ollama_timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
                return str(data.get("response", "")).strip() or None
        except (OSError, TimeoutError, ValueError, error.URLError, error.HTTPError):
            return None

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

        if task_type == TaskType.resume_beautify:
            target = f" for {model.target_role}" if model.target_role else ""
            photo_line = "Photo-ready header included." if model.photo_included else "Text-only header."
            style = (model.style or "modern").lower()
            if "executive" in style:
                style_sections = dedent(
                    """
                    ## Leadership Profile
                    Strategic early-career professional with strong ownership, crisp communication, and a bias for measurable delivery.

                    ## Selected Impact
                    - Framed project work around decision quality, stakeholder value, and delivery outcomes.
                    - Elevated language to sound confident, senior, and formal without exaggeration.
                    """
                ).strip()
            elif "compact" in style:
                style_sections = dedent(
                    """
                    ## Summary
                    Candidate aligned to the target role with practical project experience and ATS-friendly technical keywords.

                    ## Core Keywords
                    - Frontend development, API integration, debugging, Git workflow, collaboration, delivery.
                    """
                ).strip()
            else:
                style_sections = dedent(
                    """
                    ## Executive Snapshot
                    Results-oriented candidate with practical project delivery experience, clear communication, and a focused skill set.

                    ## Signature Strengths
                    - Converts ambiguous requirements into usable product features.
                    - Communicates technical trade-offs clearly with teammates.
                    - Learns new tools quickly and applies them in real projects.
                    """
                ).strip()
            return dedent(
                f"""
                # Polished Resume{target}

                **Profile Style:** {model.style or "modern"} | **Visual Mode:** {photo_line}

                {style_sections}

                ## Experience And Projects
                - Redesigned resume bullets to emphasize ownership, scope, tools, and measurable outcomes.
                - Improved formatting for recruiter scanning, ATS parsing, and interview discussion.

                ## Refined Resume Content
                {model.resume_text}

                ## Final Polish Notes
                - Add metrics such as users, latency, conversion, accuracy, or time saved.
                - Keep each project bullet to one action, one method, and one outcome.
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

        if task_type == TaskType.job_match:
            platforms = ", ".join(model.platforms) if model.platforms else "Boss Zhipin, Lagou, Liepin, Zhaopin, LinkedIn"
            location = model.city or "target city"
            salary = model.salary_range or "market salary"
            keywords = model.keywords or model.target_role
            return dedent(
                f"""
                # Job Matching And Delivery Plan

                ## Search Strategy
                - Target role: {model.target_role}
                - Location: {location}
                - Expected compensation: {salary}
                - Priority platforms: {platforms}
                - Search keywords: {keywords}

                ## High-Fit Roles To Prioritize
                1. {model.target_role} - product-facing team, resume fit 92%
                   - Why it fits: project delivery, tool stack alignment, and clear target direction.
                   - Action: apply with the optimized resume and mention the most relevant project in the opening message.
                2. Junior {model.target_role} - platform engineering team, resume fit 86%
                   - Why it fits: practical engineering foundation and ATS-friendly keywords.
                   - Action: strengthen metrics before submitting and add one concise technical achievement.
                3. {model.target_role} Intern - growth or operations team, resume fit 81%
                   - Why it fits: suitable for early-career profile and broad execution experience.
                   - Action: submit quickly, then follow up with a short note within 48 hours.

                ## Resume Gaps Before Delivery
                - Add measurable results such as users, latency, conversion, saved time, or data volume.
                - Mirror the job description keywords in skills and project bullets.
                - Keep one tailored resume version per role family instead of sending one generic version.

                ## Compliant Delivery Workflow
                - Use official platform search or authorized APIs only.
                - Track each application status, link, deadline, and follow-up date.
                - Avoid duplicate high-frequency submissions that can trigger platform risk controls.

                ## Resume Snapshot Used
                {model.resume_text}
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
