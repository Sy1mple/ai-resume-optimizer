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
                "- If project description, architecture, and responsibilities are provided, merge them into compact project bullets instead of separate subsections.\n"
                "- Project experience must appear above the Skills section in the final resume.\n"
                "- Do not output subsection titles such as Project description, Project architecture, Technical architecture, or Personal responsibilities.\n"
            )
        if task_type in {TaskType.resume_generate, TaskType.resume_optimize, TaskType.resume_beautify}:
            style_note += (
                "\n\nResume output rules:\n"
                "- Do not include internal UI or template metadata such as visual style, modern, executive, compact ATS, photo mode, scan mode, or output language.\n"
                "- The final resume must read like a real resume, not a system report or formatting explanation.\n"
                "- All section titles and visible labels must match output_language.\n"
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
            email_label = "Email" if language == "en" else "邮箱"
            phone_label = "Phone" if language == "en" else "电话"
            summary = (
                f"Motivated candidate targeting {model.target_role or 'an entry-level role'}, with hands-on project experience, strong learning ability, and a practical skill set."
                if language == "en"
                else f"目标岗位为{model.target_role or '相关岗位'}，具备项目实践经验、较强学习能力和清晰的技术能力结构。"
            )
            return self._clean_markdown(
                f"""
                # {model.name}

                **{email_label}:** {model.email} | **{phone_label}:** {model.phone}

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
            style = (model.style or "modern").lower()
            language = self._output_language(model)
            extracted_skills = self._extract_skills_from_resume_text(model.resume_text)
            refined_content = self._remove_skills_from_resume_text(model.resume_text) if extracted_skills else model.resume_text
            resume_parts = self._extract_resume_parts(model.resume_text)
            skills_section = self._format_skills_section(extracted_skills, language) if extracted_skills else (
                "- Proficient in the target role's core toolchain, with the ability to complete development, debugging, and delivery independently.\n"
                "- Experienced with team collaboration workflows and project review practices."
                if language == "en"
                else "- 熟练掌握目标岗位相关工具链，能够独立完成基础功能开发、调试和交付。\n"
                "- 熟悉团队协作流程和项目复盘方法，具备清晰沟通与快速学习能力。"
            )
            skills_title = "Skills" if language == "en" else "专业技能"
            education_title = "Education" if language == "en" else "教育经历"
            project_title = "Project Experience" if language == "en" else "项目经历"
            target_label = "Target role" if language == "en" else "目标岗位"
            email_label = "Email" if language == "en" else "邮箱"
            phone_label = "Phone" if language == "en" else "电话"
            if language == "en":
                resume_title = resume_parts["name"] or (f"{model.target_role} Resume" if model.target_role else "Resume")
            else:
                resume_title = resume_parts["name"] or (f"{model.target_role}简历" if model.target_role else "简历")
            contact_items = []
            if resume_parts["email"]:
                contact_items.append(f"**{email_label}:** {resume_parts['email']}")
            if resume_parts["phone"]:
                contact_items.append(f"**{phone_label}:** {resume_parts['phone']}")
            if model.target_role:
                contact_items.append(f"**{target_label}:** {model.target_role}")
            contact_line = " | ".join(contact_items)
            education_section = f"## {education_title}\n{resume_parts['education']}\n\n" if resume_parts["education"] else ""
            project_content = self._compact_project_content(resume_parts["projects"] or refined_content, language)
            if "executive" in style:
                style_sections = (
                    "## Professional Summary\nStrategic candidate with strong ownership, clear communication, and practical project delivery experience.\n\n"
                    "## Core Strengths\n- Demonstrates structured thinking, reliable execution, and outcome-oriented project delivery.\n"
                    "- Communicates technical trade-offs clearly and collaborates effectively across roles."
                    if language == "en"
                    else "## 职业概述\n具备较强责任心、清晰沟通能力和项目落地经验，能够围绕目标岗位完成稳定交付。\n\n"
                    "## 核心优势\n- 具备结构化思考、可靠执行和结果导向的项目交付能力。\n"
                    "- 能够清晰说明技术取舍，并与产品、后端等角色高效协作。"
                )
            elif "compact" in style:
                style_sections = (
                    "## Professional Summary\nCandidate aligned to the target role with practical project experience, clear technical keywords, and delivery awareness."
                    if language == "en"
                    else "## 职业概述\n目标岗位匹配度较高，具备项目实践经验、清晰技术关键词和交付意识。"
                )
            else:
                style_sections = (
                    "## Professional Summary\nResults-oriented candidate with practical project delivery experience, clear communication, and a focused technical skill set.\n\n"
                    "## Core Strengths\n- Converts requirements into usable product features and complete delivery outcomes.\n"
                    "- Learns new tools quickly and applies them in real project scenarios."
                    if language == "en"
                    else "## 职业概述\n具备项目交付经验、清晰沟通能力和聚焦的技术能力结构，能够围绕业务需求完成开发任务。\n\n"
                    "## 核心优势\n- 能够将需求转化为可用的产品功能和完整交付结果。\n"
                    "- 学习新工具速度快，能够结合真实项目场景落地应用。"
                )
            return self._clean_markdown(
                f"""
                # {resume_title}

                {contact_line}

                {style_sections}

                {education_section}

                ## {project_title}
                {project_content}

                ## {skills_title}
                {skills_section}
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

    def _extract_resume_parts(self, resume_text: str) -> dict[str, str]:
        return {
            "name": self._extract_single_line(resume_text, ["Name", "姓名"]),
            "email": self._extract_single_line(resume_text, ["Email", "邮箱"]),
            "phone": self._extract_single_line(resume_text, ["Phone", "电话"]),
            "education": self._extract_labeled_block(resume_text, ["Education", "教育经历"]),
            "projects": self._extract_project_block(resume_text),
        }

    def _extract_single_line(self, text: str, labels: list[str]) -> str:
        label_pattern = "|".join(re.escape(label) for label in labels)
        match = re.search(rf"(?:^|\n)\s*(?:{label_pattern})\s*[:：]\s*(.+)", text, flags=re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _extract_labeled_block(self, text: str, labels: list[str]) -> str:
        start_pattern = "|".join(re.escape(label) for label in labels)
        stop_labels = [
            "Name", "姓名", "Email", "邮箱", "Phone", "电话", "Target role", "目标岗位",
            "Education", "教育经历", "Projects", "Project Experience", "项目经历",
            "Project introduction", "项目介绍", "Project architecture", "项目架构",
            "Technical architecture", "技术架构", "Personal responsibilities", "个人职责",
            "Skills", "技能", "专业技能", "核心技能"
        ]
        stop_pattern = "|".join(re.escape(label) for label in stop_labels)
        match = re.search(
            rf"(?:^|\n)\s*(?:{start_pattern})\s*[:：]\s*(.+?)(?=\n\s*(?:{stop_pattern})\s*[:：]|\Z)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        return match.group(1).strip() if match else ""

    def _extract_project_block(self, text: str) -> str:
        start_pattern = "|".join(re.escape(label) for label in ["Projects", "Project Experience", "项目经历"])
        stop_pattern = "|".join(re.escape(label) for label in ["Skills", "技能", "专业技能", "核心技能"])
        match = re.search(
            rf"(?:^|\n)\s*(?:{start_pattern})\s*[:：]\s*(.+?)(?=\n\s*(?:{stop_pattern})\s*[:：]|\Z)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        return match.group(1).strip() if match else ""

    def _format_project_section(self, model: Any, language: str) -> str:
        parts = {
            "intro": getattr(model, "project_intro", None),
            "architecture": getattr(model, "project_architecture", None),
            "technical": getattr(model, "technical_architecture", None),
            "responsibilities": getattr(model, "personal_responsibilities", None),
        }
        if any(parts.values()):
            if language == "en":
                bullets = []
                if parts["intro"]:
                    bullets.append(f"- Built {parts['intro']}")
                if parts["architecture"] or parts["technical"]:
                    bullets.append(f"- Designed and implemented the solution using {self._join_sentence_parts([parts['architecture'], parts['technical']], language)}.")
                if parts["responsibilities"]:
                    bullets.append(f"- Owned {self._strip_leading_terms(parts['responsibilities'], ['Owned', 'Responsible for'])}")
            else:
                bullets = []
                if parts["intro"]:
                    bullets.append(f"- 参与建设{parts['intro']}")
                if parts["architecture"] or parts["technical"]:
                    bullets.append(f"- 基于{self._join_sentence_parts([parts['architecture'], parts['technical']], language)}，完成系统方案设计与落地。")
                if parts["responsibilities"]:
                    bullets.append(f"- 主要负责{self._strip_leading_terms(parts['responsibilities'], ['主要负责', '负责'])}")
            return "\n".join(bullets)
        return self._compact_project_content(getattr(model, "projects", ""), language)

    def _compact_project_content(self, project_text: str, language: str) -> str:
        clean = project_text.strip()
        if not clean:
            return ""
        fields = {
            "intro": self._extract_labeled_block(clean, ["Project introduction", "项目介绍"]),
            "architecture": self._extract_labeled_block(clean, ["Project architecture", "项目架构"]),
            "technical": self._extract_labeled_block(clean, ["Technical architecture", "技术架构"]),
            "responsibilities": self._extract_labeled_block(clean, ["Personal responsibilities", "个人职责"]),
        }
        if any(fields.values()):
            if language == "en":
                bullets = []
                if fields["intro"]:
                    bullets.append(f"- Delivered {fields['intro']}")
                if fields["architecture"] or fields["technical"]:
                    bullets.append(f"- Implemented the technical solution with {self._join_sentence_parts([fields['architecture'], fields['technical']], language)}.")
                if fields["responsibilities"]:
                    bullets.append(f"- Owned {self._strip_leading_terms(fields['responsibilities'], ['Owned', 'Responsible for'])}")
            else:
                bullets = []
                if fields["intro"]:
                    bullets.append(f"- 参与建设{fields['intro']}")
                if fields["architecture"] or fields["technical"]:
                    bullets.append(f"- 基于{self._join_sentence_parts([fields['architecture'], fields['technical']], language)}，完成前后端方案落地。")
                if fields["responsibilities"]:
                    bullets.append(f"- 主要负责{self._strip_leading_terms(fields['responsibilities'], ['主要负责', '负责'])}")
            return "\n".join(bullets)
        if "\n" in clean:
            lines = [line.strip(" -•\t") for line in clean.splitlines() if line.strip()]
            return "\n".join(self._format_project_line(line, language) for line in lines[:8])
        segments = [segment.strip() for segment in re.split(r"[；;]\s*", clean) if segment.strip()]
        if len(segments) > 1:
            return "\n".join(f"- {self._format_plain_project_segment(segment, language)}" for segment in segments[:4])
        return f"- {self._ensure_sentence_end(clean, language)}"

    def _format_project_line(self, text: str, language: str) -> str:
        clean = text.strip()
        if not clean:
            return ""
        name = ""
        detail = clean
        if ":" in clean or "：" in clean:
            name, detail = re.split(r"[:：]", clean, maxsplit=1)
            name = name.strip()
            detail = detail.strip()
        segments = [segment.strip() for segment in re.split(r"[；;]\s*", detail) if segment.strip()]
        if not segments:
            return f"- {self._ensure_sentence_end(clean, language)}"
        if name and len(segments) > 1:
            first_line = f"- **{name}:** {self._format_plain_project_segment(segments[0], language)}"
            detail_lines = [f"- {self._format_plain_project_segment(segment, language)}" for segment in segments[1:4]]
            return "\n".join([first_line, *detail_lines])
        if name:
            return f"- **{name}:** {self._format_plain_project_segment(segments[0], language)}"
        return "\n".join(f"- {self._format_plain_project_segment(segment, language)}" for segment in segments[:4])

    def _join_sentence_parts(self, parts: list[str | None], language: str) -> str:
        separator = ", " if language == "en" else "，"
        return separator.join(part.strip(" 。.；;") for part in parts if part and part.strip())

    def _format_plain_project_segment(self, text: str, language: str) -> str:
        clean = text.strip()
        if language == "en" and clean:
            clean = f"{clean[0].upper()}{clean[1:]}"
        if language == "zh":
            clean = re.sub(r"^个人负责", "负责", clean)
        return self._ensure_sentence_end(clean, language)

    def _ensure_sentence_end(self, text: str, language: str) -> str:
        clean = text.strip()
        if not clean:
            return clean
        if clean[-1] in ".。!！?？":
            return clean
        return f"{clean}." if language == "en" else f"{clean}。"

    def _strip_leading_terms(self, text: str, terms: list[str]) -> str:
        cleaned = text.strip()
        for term in terms:
            pattern = rf"^\s*{re.escape(term)}\s*[:：,，]?\s*"
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        return cleaned

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
