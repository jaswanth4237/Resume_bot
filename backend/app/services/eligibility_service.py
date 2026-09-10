from typing import Dict, Any, List
from app.config.settings import settings


class EligibilityService:
    @classmethod
    def evaluate_eligibility(
        cls,
        overall_score: float,
        missing_mandatory_skills: List[str],
        experience_gap_satisfied: bool,
        experience_gap_years: float,
        education_satisfied: bool
    ) -> Dict[str, Any]:
        mandatory_failures = []
        decision_reasons = []

        if missing_mandatory_skills:
            for skill in missing_mandatory_skills:
                mandatory_failures.append(f"Missing mandatory skill: {skill}")
                decision_reasons.append(f"Candidate lacks mandatory required skill '{skill}'.")

        if not experience_gap_satisfied and experience_gap_years > 0:
            mandatory_failures.append(f"Experience gap: lacks {experience_gap_years} years required minimum experience")
            decision_reasons.append(f"Candidate falls short of minimum required experience by {experience_gap_years} years.")

        if not education_satisfied:
            mandatory_failures.append("Mandatory education requirement not satisfied")
            decision_reasons.append("Candidate does not meet mandatory education criteria.")

        suitable_thresh = settings.SUITABLE_THRESHOLD
        borderline_thresh = settings.BORDERLINE_THRESHOLD

        if mandatory_failures:
            decision = "REJECT"
            reason_summary = "Candidate does not satisfy mandatory job requirements: " + "; ".join(mandatory_failures)
        elif overall_score >= suitable_thresh:
            decision = "SUITABLE"
            reason_summary = f"Candidate satisfies all mandatory requirements and meets high match score threshold ({overall_score}% >= {suitable_thresh}%)."
        elif overall_score >= borderline_thresh:
            decision = "BORDERLINE"
            reason_summary = f"Candidate satisfies mandatory requirements but match score is borderline ({overall_score}%)."
        else:
            decision = "REJECT"
            reason_summary = f"Candidate match score ({overall_score}%) falls below minimum threshold ({borderline_thresh}%)."
            decision_reasons.append(f"Overall match score {overall_score}% is below required cutoff of {borderline_thresh}%.")

        return {
            "decision": decision,
            "decision_reasons": decision_reasons if decision_reasons else [reason_summary],
            "mandatory_failures": mandatory_failures,
            "reason_summary": reason_summary
        }
