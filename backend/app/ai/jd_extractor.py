import re
import logging
from app.schemas.jd_schema import (
    JDSchema, MandatoryRequirements, PreferredRequirements, EducationRequirement, RequirementClassification
)
from app.ai.llm_client import LLMClient
from app.ai.prompts import JD_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class JDExtractor:
    @classmethod
    async def extract(cls, text: str) -> JDSchema:
        if not text or not text.strip():
            raise ValueError("Job description text is empty")

        llm_result = await LLMClient.extract_structured_json(
            prompt=JD_EXTRACTION_PROMPT,
            document_text=text,
            schema_cls=JDSchema
        )
        if llm_result:
            return llm_result

        return cls._rule_based_extract(text)

    @classmethod
    def _rule_based_extract(cls, text: str) -> JDSchema:
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        job_title = "Software Engineer"
        for line in lines[:5]:
            if any(term in line.lower() for term in ["developer", "engineer", "architect", "lead", "manager", "specialist"]):
                job_title = line[:60]
                break

        known_techs = [
            "Spring Boot", "Spring", "Java", "Python", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust",
            "Django", "FastAPI", "Express", "React", "Angular", "Vue",
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes",
            "AWS", "Azure", "GCP", "Microservices", "REST API", "Git", "Linux", "CI/CD", "SQL"
        ]

        mandatory_skills = []
        preferred_skills = []
        classified = []

        preferred_section = False

        for line in lines:
            line_lower = line.lower()

            if any(w in line_lower for w in ["preferred", "nice to have", "plus", "optional", "desired"]):
                preferred_section = True
            elif any(w in line_lower for w in ["required", "must have", "mandatory", "qualifications", "responsibilities", "requirements"]):
                preferred_section = False

            for tech in known_techs:
                pattern = r"\b" + re.escape(tech) + r"\b"
                if re.search(pattern, line, re.IGNORECASE):
                    # Avoid adding generic "Spring" if "Spring Boot" is present
                    if tech == "Spring" and "Spring Boot" in line:
                        continue

                    if preferred_section or any(p in line_lower for p in ["preferred", "nice to have", "plus"]):
                        if tech not in preferred_skills and tech not in mandatory_skills:
                            preferred_skills.append(tech)
                            classified.append(
                                RequirementClassification(
                                    requirement_text=line[:100],
                                    category="SKILL",
                                    classification="PREFERRED"
                                )
                            )
                    else:
                        if tech not in mandatory_skills:
                            mandatory_skills.append(tech)
                            classified.append(
                                RequirementClassification(
                                    requirement_text=line[:100],
                                    category="SKILL",
                                    classification="MANDATORY"
                                )
                            )

        min_years = 0.0
        exp_match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?(?:\s+of)?\s+experience", text, re.IGNORECASE)
        if exp_match:
            try:
                min_years = float(exp_match.group(1))
            except Exception:
                min_years = 0.0

        if min_years > 0:
            classified.append(
                RequirementClassification(
                    requirement_text=f"Minimum {min_years} years experience required",
                    category="EXPERIENCE",
                    classification="MANDATORY"
                )
            )

        responsibilities = []
        resp_section = False
        for line in lines:
            if "responsibilities" in line.lower() or "duties" in line.lower() or "what you'll do" in line.lower():
                resp_section = True
                continue
            if resp_section:
                if any(h in line.lower() for h in ["requirements", "skills", "qualifications", "preferred"]):
                    resp_section = False
                elif len(line) > 10:
                    responsibilities.append(line[:150])

        if not responsibilities:
            responsibilities = ["Develop and maintain software applications", "Collaborate with cross-functional teams"]

        return JDSchema(
            job_title=job_title,
            mandatory_requirements=MandatoryRequirements(
                skills=mandatory_skills if mandatory_skills else ["Java"],
                minimum_experience_years=min_years
            ),
            preferred_requirements=PreferredRequirements(
                skills=preferred_skills
            ),
            education_requirements=[
                EducationRequirement(degree="Bachelor's degree", field="Computer Science or related", is_mandatory=False)
            ],
            responsibilities=responsibilities[:5],
            classified_requirements=classified
        )
