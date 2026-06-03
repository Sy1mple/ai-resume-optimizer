from __future__ import annotations

import os
import json
import re
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
        "Use concise bullet points, quantify impact when possible, and keep the tone suitable for early-career candidates. "
        "When skills are provided as keywords, rewrite them into a formal resume Skills section. "
        "For Chinese resumes, use phrases like 熟练掌握, 熟悉, 了解, and 具备; never return a raw comma-separated keyword list."
    ),
    TaskType.resume_optimize: (
        "You are a resume editor. Improve the given resume text for clarity, impact, ATS readability, and professional wording. "
        "Return an optimized version plus a short skills suggestion section. "
        "Convert skill keywords into standard resume wording such as 熟练掌握..., 熟悉..., 具备..., instead of leaving bare keywords."
    ),
    TaskType.resume_beautify: (
        "You are a senior resume designer and editor. Transform the resume into a visually organized, high-impact Markdown resume. "
        "Use clean sections, strong verbs, quantified bullets, and ATS-friendly wording. Keep it honest and concise. "
        "If the resume contains a Skills keyword list, rewrite it as polished skill bullets using 熟练掌握, 熟悉, 了解, and 具备 where suitable."
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
        if task_type in {TaskType.resume_generate, TaskType.resume_optimize, TaskType.resume_beautify}:
            style_note += (
                "\n\nSkill section rules:\n"
                "- Do not output skills as a bare keyword list.\n"
                "- Convert keyword input into standard resume skill bullets.\n"
                "- For Chinese output, use wording like 熟练掌握 X，熟悉 Y，了解 Z，具备 W 项目协作能力。\n"
                "- Group related tools naturally and keep each bullet specific, concise, and recruiter-friendly.\n"
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
            skills_section = self._format_skills_section(model.skills)
            return self._clean_markdown(
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
                {skills_section}
                """
            ).strip()

        if task_type == TaskType.resume_optimize:
            target = f" for {model.target_role}" if model.target_role else ""
            extracted_skills = self._extract_skills_from_resume_text(model.resume_text)
            revised_content = self._remove_skills_from_resume_text(model.resume_text) if extracted_skills else model.resume_text
            skills_section = self._format_skills_section(extracted_skills) if extracted_skills else (
                "- 熟练掌握目标岗位所需的核心工具与方法，能够结合项目场景完成实际交付。\n"
                "- 熟悉业务需求拆解、问题定位和结果复盘，具备持续优化简历表达的能力。"
            )
            return self._clean_markdown(
                f"""
                # Optimized Resume Draft{target}

                ## Improved Positioning
                - Strengthened action verbs and clarified ownership.
                - Converted generic responsibilities into outcome-focused bullet points.
                - Added ATS-friendly keywords based on the target direction.

                ## Revised Content
                {revised_content}

                ## Skills Suggestions
                {skills_section}
                """
            ).strip()

        if task_type == TaskType.resume_beautify:
            target = f" for {model.target_role}" if model.target_role else ""
            photo_line = "Photo-ready header included." if model.photo_included else "Text-only header."
            style = (model.style or "modern").lower()
            extracted_skills = self._extract_skills_from_resume_text(model.resume_text)
            refined_content = self._remove_skills_from_resume_text(model.resume_text) if extracted_skills else model.resume_text
            skills_section = self._format_skills_section(extracted_skills) if extracted_skills else (
                "- 熟练掌握目标岗位相关工具链，能够独立完成基础功能开发、调试和交付。\n"
                "- 熟悉团队协作流程和项目复盘方法，具备清晰沟通与快速学习能力。"
            )
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
            return self._clean_markdown(
                f"""
                # Polished Resume{target}

                **Profile Style:** {model.style or "modern"} | **Visual Mode:** {photo_line}

                {style_sections}

                ## Experience And Projects
                - Redesigned resume bullets to emphasize ownership, scope, tools, and measurable outcomes.
                - Improved formatting for recruiter scanning, ATS parsing, and interview discussion.

                ## Skills
                {skills_section}

                ## Refined Resume Content
                {refined_content}

                ## Final Polish Notes
                - Add metrics such as users, latency, conversion, accuracy, or time saved.
                - Keep each project bullet to one action, one method, and one outcome.
                """
            ).strip()

        if task_type == TaskType.cover_letter:
            return self._clean_markdown(
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
            return self._clean_markdown(
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

        return self._clean_markdown(
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

    def _clean_markdown(self, markdown: str) -> str:
        return "\n".join(line.strip() for line in dedent(markdown).strip().splitlines())

    def _extract_skills_from_resume_text(self, resume_text: str) -> str:
        patterns = [
            r"(?:^|\n)\s*(?:Skills|技能|专业技能|核心技能)\s*[:：]\s*(.+?)(?=\n\s*(?:Education|Projects|Experience|Work|项目|经历|教育|工作|##|#)\b|\Z)",
            r"(?:^|\n)\s*##\s*(?:Skills|技能|专业技能|核心技能)\s*\n(.+?)(?=\n\s*##\s+|\Z)",
        ]
        for pattern in patterns:
            match = re.search(pattern, resume_text, flags=re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""

    def _remove_skills_from_resume_text(self, resume_text: str) -> str:
        patterns = [
            r"(?:^|\n)\s*(?:Skills|技能|专业技能|核心技能)\s*[:：]\s*.+?(?=\n\s*(?:Education|Projects|Experience|Work|项目|经历|教育|工作|##|#)\b|\Z)",
            r"(?:^|\n)\s*##\s*(?:Skills|技能|专业技能|核心技能)\s*\n.+?(?=\n\s*##\s+|\Z)",
        ]
        cleaned = resume_text
        for pattern in patterns:
            cleaned = re.sub(pattern, "\n", cleaned, flags=re.IGNORECASE | re.DOTALL)
        return re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    def _format_skills_section(self, raw_skills: str) -> str:
        skills = self._split_skill_keywords(raw_skills)
        if not skills:
            return "- 熟练掌握岗位相关核心技能，能够结合项目需求完成落地交付。"

        primary = "、".join(skills[:3])
        secondary = "、".join(skills[3:6])
        extra = "、".join(skills[6:10])
        bullets = [
            f"- 熟练掌握 {primary}，能够在实际项目中完成需求开发、问题定位和功能交付。"
        ]
        if secondary:
            bullets.append(f"- 熟悉 {secondary}，理解常见工程流程、接口协作和数据处理场景。")
        if extra:
            bullets.append(f"- 了解 {extra} 等相关工具或技术，能够根据项目需要快速学习并应用。")
        bullets.append("- 具备良好的 Git 协作、调试排查、文档整理和跨角色沟通能力。")
        return "\n".join(bullets)

    def _split_skill_keywords(self, raw_skills: str) -> list[str]:
        cleaned = re.sub(r"[*#`>-]", " ", raw_skills)
        parts = re.split(r"[,，、/|;；\n]+", cleaned)
        skills: list[str] = []
        for part in parts:
            skill = re.sub(r"\s+", " ", part).strip(" .。:：")
            if not skill:
                continue
            if len(skill) > 40:
                continue
            if skill.lower() not in {item.lower() for item in skills}:
                skills.append(skill)
        return skills[:12]
