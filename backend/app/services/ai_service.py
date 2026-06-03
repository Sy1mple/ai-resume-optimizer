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
        "Respect the requested output language. Sort skills from more important/difficult to easier/supporting skills. "
        "Group related skills together, and write one skill per bullet line."
    ),
    TaskType.resume_optimize: (
        "You are a resume editor. Improve the given resume text for clarity, impact, ATS readability, and professional wording. "
        "Return an optimized version plus a short skills suggestion section. "
        "Respect the requested output language. Convert skill keywords into standard resume wording instead of leaving bare keywords. "
        "Sort skills by importance and difficulty, group related skills, and write one skill per bullet line."
    ),
    TaskType.resume_beautify: (
        "You are a senior resume designer and editor. Transform the resume into a visually organized, high-impact Markdown resume. "
        "Use clean sections, strong verbs, quantified bullets, and ATS-friendly wording. Keep it honest and concise. "
        "If the resume contains a Skills keyword list, rewrite it as polished skill bullets in the requested output language. "
        "Sort skills by importance and difficulty, group related skills, and write one skill per bullet line."
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
                "- Respect output_language exactly: zh uses Chinese wording; en uses English wording.\n"
                "- Convert keyword input into standard resume skill bullets.\n"
                "- Sort skills from more important/difficult to easier/supporting skills.\n"
                "- Group related skills together, but write each individual skill as its own bullet line.\n"
                "- For zh, use wording like 熟练掌握 X, 熟悉 Y, 了解 Z, 具备 W 能力.\n"
                "- For en, use wording like Proficient in X, Experienced with Y, Familiar with Z, Strong W capability.\n"
            )
        if task_type in {TaskType.resume_generate, TaskType.resume_beautify}:
            style_note += (
                "\n\nProject section rules:\n"
                "- If project_intro, project_architecture, technical_architecture, and personal_responsibilities are available, structure project experience with these four subsections.\n"
                "- Keep the four subsection titles in the requested output language.\n"
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
            language = self._output_language(model)
            skills_section = self._format_skills_section(model.skills, language)
            projects_section = self._format_project_section(model, language)
            summary_title = "Professional Summary" if language == "en" else "职业概述"
            education_title = "Education" if language == "en" else "教育经历"
            projects_title = "Projects" if language == "en" else "项目经历"
            skills_title = "Skills" if language == "en" else "专业技能"
            summary = (
                f"Motivated candidate targeting {model.target_role or 'an entry-level role'}, with hands-on project experience, strong learning ability, and a practical skill set."
                if language == "en"
                else f"目标岗位为{model.target_role or '相关岗位'}，具备项目实践经验、较强学习能力和清晰的技术能力结构。"
            )
            return self._clean_markdown(
                f"""
                # {model.name}

                **Email:** {model.email} | **Phone:** {model.phone}

                ## {summary_title}
                {summary}

                ## {education_title}
                {model.education}

                ## {projects_title}
                {projects_section}

                ## {skills_title}
                {skills_section}
                """
            ).strip()

        if task_type == TaskType.resume_optimize:
            target = f" for {model.target_role}" if model.target_role else ""
            language = self._output_language(model)
            extracted_skills = self._extract_skills_from_resume_text(model.resume_text)
            revised_content = self._remove_skills_from_resume_text(model.resume_text) if extracted_skills else model.resume_text
            skills_section = self._format_skills_section(extracted_skills, language) if extracted_skills else (
                "- Proficient in role-relevant core tools, with the ability to apply them in project delivery.\n"
                "- Experienced with requirement breakdown, issue diagnosis, and result review."
                if language == "en"
                else "- 熟练掌握目标岗位所需的核心工具与方法，能够结合项目场景完成实际交付。\n"
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
            language = self._output_language(model)
            extracted_skills = self._extract_skills_from_resume_text(model.resume_text)
            refined_content = self._remove_skills_from_resume_text(model.resume_text) if extracted_skills else model.resume_text
            skills_section = self._format_skills_section(extracted_skills, language) if extracted_skills else (
                "- Proficient in the target role's core toolchain, with the ability to complete development, debugging, and delivery independently.\n"
                "- Experienced with team collaboration workflows and project review practices."
                if language == "en"
                else "- 熟练掌握目标岗位相关工具链，能够独立完成基础功能开发、调试和交付。\n"
                "- 熟悉团队协作流程和项目复盘方法，具备清晰沟通与快速学习能力。"
            )
            skills_title = "Skills" if language == "en" else "专业技能"
            refined_title = "Refined Resume Content" if language == "en" else "优化后的简历内容"
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

                ## {skills_title}
                {skills_section}

                ## {refined_title}
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

    def _output_language(self, model: Any) -> str:
        return "en" if getattr(model, "output_language", "zh") == "en" else "zh"

    def _format_project_section(self, model: Any, language: str) -> str:
        structured = [
            ("Project introduction", "项目介绍", getattr(model, "project_intro", None)),
            ("Project architecture", "项目架构", getattr(model, "project_architecture", None)),
            ("Technical architecture", "技术架构", getattr(model, "technical_architecture", None)),
            ("Personal responsibilities", "个人职责", getattr(model, "personal_responsibilities", None)),
        ]
        if any(value for _, _, value in structured):
            lines: list[str] = []
            for en_title, zh_title, value in structured:
                if value:
                    title = en_title if language == "en" else zh_title
                    lines.append(f"### {title}\n{value}")
            return "\n\n".join(lines)
        return getattr(model, "projects", "")

    def _format_skills_section(self, raw_skills: str, language: str = "zh") -> str:
        skills = self._sort_skill_keywords(self._split_skill_keywords(raw_skills))
        if not skills:
            return (
                "- Proficient in role-relevant core skills, with the ability to apply them in project delivery."
                if language == "en"
                else "- 熟练掌握岗位相关核心技能，能够结合项目需求完成落地交付。"
            )

        bullets: list[str] = []
        for skill in skills:
            category = self._skill_category(skill)
            if language == "en":
                if category in {"language", "frontend"}:
                    bullets.append(f"- Proficient in {skill}, with practical experience applying it to feature development and delivery.")
                elif category in {"backend", "database"}:
                    bullets.append(f"- Experienced with {skill}, including API integration, data interaction, or backend collaboration scenarios.")
                elif category in {"devops", "tool"}:
                    bullets.append(f"- Familiar with {skill}, and able to use it effectively in development, debugging, and team workflows.")
                else:
                    bullets.append(f"- Strong {skill} capability, with solid learning, collaboration, and delivery awareness.")
            else:
                if category in {"language", "frontend"}:
                    bullets.append(f"- 熟练掌握 {skill}，能够结合业务需求完成页面开发、功能实现和交付优化。")
                elif category in {"backend", "database"}:
                    bullets.append(f"- 熟悉 {skill}，理解接口协作、数据处理和后端联调等常见项目场景。")
                elif category in {"devops", "tool"}:
                    bullets.append(f"- 了解 {skill}，能够在开发调试、版本管理和团队协作流程中高效使用。")
                else:
                    bullets.append(f"- 具备 {skill} 相关能力，能够根据项目需要快速学习并落地应用。")
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

    def _sort_skill_keywords(self, skills: list[str]) -> list[str]:
        return sorted(skills, key=lambda skill: (self._category_rank(self._skill_category(skill)), self._skill_rank(skill), skill.lower()))

    def _skill_category(self, skill: str) -> str:
        key = self._skill_key(skill)
        categories = {
            "language": {"javascript", "typescript", "python", "java", "go", "golang", "c++", "c#", "php", "swift", "kotlin"},
            "frontend": {"vue", "vue.js", "vue3", "react", "react.js", "angular", "html", "css", "sass", "less", "tailwind", "element plus", "element-plus", "vite", "webpack"},
            "backend": {"fastapi", "django", "flask", "node", "node.js", "express", "spring", "spring boot", "rest api", "restful api", "graphql"},
            "database": {"sql", "mysql", "postgresql", "postgres", "mongodb", "redis", "sqlite", "elasticsearch"},
            "devops": {"docker", "kubernetes", "k8s", "linux", "nginx", "ci/cd", "github actions", "jenkins"},
            "tool": {"git", "github", "gitlab", "figma", "postman", "jira", "notion", "excel"},
        }
        for category, values in categories.items():
            if key in values:
                return category
        return "other"

    def _category_rank(self, category: str) -> int:
        ranks = {
            "language": 0,
            "frontend": 1,
            "backend": 2,
            "database": 3,
            "devops": 4,
            "tool": 5,
            "other": 6,
        }
        return ranks.get(category, 9)

    def _skill_rank(self, skill: str) -> int:
        key = self._skill_key(skill)
        ranks = {
            "javascript": 0,
            "typescript": 1,
            "python": 2,
            "java": 3,
            "vue": 0,
            "vue.js": 0,
            "vue3": 0,
            "react": 1,
            "react.js": 1,
            "html": 8,
            "css": 9,
            "fastapi": 0,
            "node.js": 1,
            "node": 1,
            "sql": 0,
            "mysql": 1,
            "postgresql": 2,
            "redis": 3,
            "git": 0,
        }
        return ranks.get(key, 20)

    def _skill_key(self, skill: str) -> str:
        return re.sub(r"\s+", " ", skill.strip().lower())
