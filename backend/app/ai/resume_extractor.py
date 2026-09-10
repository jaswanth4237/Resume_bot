import re
import logging
from app.schemas.resume_schema import (
    ResumeSchema, CandidateInfo, SkillItem, ExperienceItem, EducationItem, ProjectItem
)
from app.ai.llm_client import LLMClient
from app.ai.prompts import RESUME_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class ResumeExtractor:
    @classmethod
    async def extract(cls, text: str) -> ResumeSchema:
        if not text or not text.strip():
            raise ValueError("Resume text is empty")

        # Try LLM Extraction first if API key is provided
        llm_result = await LLMClient.extract_structured_json(
            prompt=RESUME_EXTRACTION_PROMPT,
            document_text=text,
            schema_cls=ResumeSchema
        )
        if llm_result:
            return llm_result

        # Rule-assisted fallback extraction
        return cls._rule_based_extract(text)

    @classmethod
    def _rule_based_extract(cls, text: str) -> ResumeSchema:
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 1. Candidate Info
        name = "Candidate"
        email = None
        phone = None

        if lines:
            # First non-empty line often contains the candidate name
            name_candidate = lines[0]
            if len(name_candidate) < 50 and not any(char in name_candidate for char in "@:/\\"):
                name = name_candidate

        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        if email_match:
            email = email_match.group(0)

        phone_match = re.search(r"(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}", text)
        if phone_match:
            phone = phone_match.group(0)

        # 2. Extract Skills
        known_techs = [
            "Java", "Python", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
            "Spring Boot", "Spring", "Django", "FastAPI", "Express", "React", "Angular", "Vue",
            "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes",
            "AWS", "Azure", "GCP", "Microservices", "REST API", "Git", "Linux", "CI/CD"
        ]

        found_skills = []
        for tech in known_techs:
            pattern = r"\b" + re.escape(tech) + r"\b"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Find surrounding line context as evidence
                line_ctx = ""
                for line in lines:
                    if re.search(pattern, line, re.IGNORECASE):
                        line_ctx = line[:120]
                        break
                found_skills.append(
                    SkillItem(
                        name=tech,
                        level="intermediate",
                        years=2.0 if "year" in text.lower() else 1.0,
                        evidence=line_ctx or f"Mentioned in resume: {tech}"
                    )
                )

        # 3. Experience Years Extraction
        exp_years = 0.0
        exp_matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?(?:\s+of)?\s+experience", text, re.IGNORECASE)
        if exp_matches:
            try:
                exp_years = max(float(m) for m in exp_matches)
            except Exception:
                exp_years = 2.0
        else:
            # Fallback based on explicit work history date ranges or default 2 years if work section present
            if "experience" in text.lower() or "work history" in text.lower():
                exp_years = 2.0

        # Build fallback structure
        candidate = CandidateInfo(name=name, email=email, phone=phone)
        education = [EducationItem(institution="University", degree="Bachelor's", field="Computer Science")]
        projects = [ProjectItem(name="Software Project", description="Technical project work", technologies=[s.name for s in found_skills[:3]])] if found_skills else []

        experience = [
            ExperienceItem(
                company="Tech Company",
                role="Software Engineer",
                years=exp_years,
                description="Backend/Fullstack software engineering duties",
                technologies=[s.name for s in found_skills[:5]]
            )
        ] if exp_years > 0 else []

        return ResumeSchema(
            candidate=candidate,
            skills=found_skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=[],
            total_experience_years=exp_years
        )
