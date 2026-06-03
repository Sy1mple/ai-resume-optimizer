# Product Notes

## Positioning

AI Resume Optimizer helps students and job seekers produce better job application material with less friction.

## MVP Scope

- Generate a resume from structured profile input.
- Optimize existing resume text.
- Generate a cover letter from company, role, and personal experience.
- Generate interview questions and reference answers.
- Show recent generation history.

## User Flow

1. User selects a task from the workspace tabs.
2. User fills in the task-specific form.
3. Backend validates the input and calls the AI service.
4. Result is returned as Markdown.
5. Result is saved into history.
6. User can copy, review, or delete history records.

## Non-Functional Notes

- API keys stay on the backend.
- Input length is limited by Pydantic validation.
- The app is responsive for desktop and mobile.
- Mock generation keeps demos usable without external services.
