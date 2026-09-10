from typing import Dict, Any, List
from app.schemas.resume_schema import ExperienceItem


class ExperienceMatcher:
    @classmethod
    def match_experience(
        cls,
        candidate_experience: List[ExperienceItem],
        total_candidate_years: float,
        required_minimum_years: float
    ) -> Dict[str, Any]:
        # Sum total candidate experience
        total_years = max(total_candidate_years, sum(e.years for e in candidate_experience))
        relevant_years = total_years  # If explicit evidence exists, use total or filtered relevant years

        gap_years = max(0.0, round(required_minimum_years - relevant_years, 2))
        is_satisfied = relevant_years >= required_minimum_years

        if required_minimum_years == 0:
            score = 100.0
        else:
            score = min(100.0, max(0.0, (relevant_years / required_minimum_years) * 100.0))

        return {
            "required_years": required_minimum_years,
            "candidate_years": round(relevant_years, 2),
            "total_candidate_years": round(total_years, 2),
            "gap_years": gap_years,
            "is_satisfied": is_satisfied,
            "score": round(score, 2)
        }
