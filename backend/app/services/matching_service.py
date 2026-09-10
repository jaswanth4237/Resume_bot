import logging
import uuid
from typing import Dict, Any, List
from app.services.document_service import DocumentService
from app.ai.resume_extractor import ResumeExtractor
from app.ai.jd_extractor import JDExtractor
from app.matching.skill_matcher import SkillMatcher
from app.matching.experience_matcher import ExperienceMatcher
from app.matching.education_matcher import EducationMatcher
from app.matching.responsibility_matcher import ResponsibilityMatcher
from app.services.scoring_service import ScoringService
from app.services.eligibility_service import EligibilityService
from app.services.gap_service import GapService
from app.services.course_service import CourseService

logger = logging.getLogger(__name__)


class MatchingService:
    @classmethod
    async def analyze_candidate_against_jd(
        cls,
        resume_filename: str,
        resume_bytes: bytes,
        jd_filename: str,
        jd_bytes: bytes
    ) -> Dict[str, Any]:
        # 1. Document Extraction
        resume_raw_text = DocumentService.extract_text(resume_filename, resume_bytes)
        jd_raw_text = DocumentService.extract_text(jd_filename, jd_bytes)

        # 2. AI Structured Extraction
        resume_schema = await ResumeExtractor.extract(resume_raw_text)
        jd_schema = await JDExtractor.extract(jd_raw_text)

        # 3. Matching Engine Calculations
        skill_match_result = SkillMatcher.match_skills(
            candidate_skills=resume_schema.skills,
            mandatory_jd_skills=jd_schema.mandatory_requirements.skills,
            preferred_jd_skills=jd_schema.preferred_requirements.skills
        )

        exp_match_result = ExperienceMatcher.match_experience(
            candidate_experience=resume_schema.experience,
            total_candidate_years=resume_schema.total_experience_years,
            required_minimum_years=jd_schema.mandatory_requirements.minimum_experience_years
        )

        edu_match_result = EducationMatcher.match_education(
            candidate_education=resume_schema.education,
            jd_education_requirements=jd_schema.education_requirements
        )

        resp_match_result = ResponsibilityMatcher.match_responsibilities(
            candidate_experience=resume_schema.experience,
            candidate_projects=resume_schema.projects,
            jd_responsibilities=jd_schema.responsibilities
        )

        # 4. Deterministic Scoring
        scoring_result = ScoringService.calculate_scores(
            mandatory_skills_score=skill_match_result["mandatory_score"],
            preferred_skills_score=skill_match_result["preferred_score"],
            experience_score=exp_match_result["score"],
            responsibilities_score=resp_match_result["score"],
            education_score=edu_match_result["score"]
        )

        # 5. Eligibility Decision Engine
        missing_mandatory = [m["skill"] for m in skill_match_result["missing"] if m["is_mandatory"]]
        eligibility_result = EligibilityService.evaluate_eligibility(
            overall_score=scoring_result["overall_score"],
            missing_mandatory_skills=missing_mandatory,
            experience_gap_satisfied=exp_match_result["is_satisfied"],
            experience_gap_years=exp_match_result["gap_years"],
            education_satisfied=edu_match_result["is_satisfied"]
        )

        # 6. Gap Analysis Engine
        gap_result = GapService.analyze_gaps(
            missing_skills=skill_match_result["missing"],
            partial_skills=skill_match_result["partial"],
            experience_data=exp_match_result
        )

        # 7. Course Recommendation Engine
        course_recommendations = CourseService.get_recommendations_for_gaps(gap_result["gaps"])

        analysis_id = str(uuid.uuid4())

        return {
            "analysis_id": analysis_id,
            "candidate": resume_schema.candidate.model_dump(),
            "job_title": jd_schema.job_title,
            "overall_score": scoring_result["overall_score"],
            "decision": eligibility_result["decision"],
            "decision_reasons": eligibility_result["decision_reasons"],
            "category_scores": scoring_result["category_scores"],
            "matched_requirements": [m["skill"] for m in skill_match_result["matched"]],
            "partial_requirements": [p["skill"] for p in skill_match_result["partial"]],
            "missing_requirements": [m["skill"] for m in skill_match_result["missing"]],
            "mandatory_failures": eligibility_result["mandatory_failures"],
            "experience_gap": {
                "required_years": exp_match_result["required_years"],
                "candidate_years": exp_match_result["candidate_years"],
                "gap_years": exp_match_result["gap_years"]
            },
            "gaps": gap_result["gaps"],
            "explanation": gap_result["explanation"],
            "course_recommendations": course_recommendations
        }
