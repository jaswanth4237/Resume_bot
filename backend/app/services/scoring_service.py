from typing import Dict, Any
from app.config.settings import settings


class ScoringService:
    @classmethod
    def calculate_scores(
        cls,
        mandatory_skills_score: float,
        preferred_skills_score: float,
        experience_score: float,
        responsibilities_score: float,
        education_score: float
    ) -> Dict[str, Any]:
        weights = settings.WEIGHTS

        # Combine mandatory (80%) and preferred (20%) into overall skills score or use category weights
        skills_category_score = round((mandatory_skills_score * 0.8) + (preferred_skills_score * 0.2), 2)
        exp_category_score = round(experience_score, 2)
        resp_category_score = round(responsibilities_score, 2)
        edu_category_score = round(education_score, 2)
        pref_category_score = round(preferred_skills_score, 2)

        weighted_skills = weights.get("skills", 0.50) * skills_category_score
        weighted_exp = weights.get("experience", 0.20) * exp_category_score
        weighted_resp = weights.get("responsibilities", 0.15) * resp_category_score
        weighted_edu = weights.get("education", 0.05) * edu_category_score
        weighted_pref = weights.get("preferred", 0.10) * pref_category_score

        overall_score = round(weighted_skills + weighted_exp + weighted_resp + weighted_edu + weighted_pref, 2)
        overall_score = min(100.0, max(0.0, overall_score))

        return {
            "overall_score": overall_score,
            "category_scores": {
                "skills": skills_category_score,
                "experience": exp_category_score,
                "responsibilities": resp_category_score,
                "education": edu_category_score,
                "preferred": pref_category_score
            }
        }
