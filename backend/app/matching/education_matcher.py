from typing import List, Dict, Any
from app.schemas.resume_schema import EducationItem
from app.schemas.jd_schema import EducationRequirement


class EducationMatcher:
    @classmethod
    def match_education(
        cls,
        candidate_education: List[EducationItem],
        jd_education_requirements: List[EducationRequirement]
    ) -> Dict[str, Any]:
        if not jd_education_requirements:
            return {"score": 100.0, "is_satisfied": True, "details": "No explicit education requirements specified"}

        for req in jd_education_requirements:
            req_degree_lower = req.degree.lower()
            req_field_lower = (req.field or "").lower()

            matched = False
            for cand in candidate_education:
                cand_degree_lower = cand.degree.lower()
                cand_field_lower = (cand.field or "").lower()

                # Degree match
                degree_ok = ("bachelor" in req_degree_lower and ("bachelor" in cand_degree_lower or "b.tech" in cand_degree_lower or "bs" in cand_degree_lower or "degree" in cand_degree_lower)) or \
                            ("master" in req_degree_lower and ("master" in cand_degree_lower or "m.tech" in cand_degree_lower or "ms" in cand_degree_lower)) or \
                            (req_degree_lower in cand_degree_lower)

                field_ok = not req_field_lower or any(word in cand_field_lower for word in ["computer", "science", "engineering", "technology", "related"]) or (req_field_lower in cand_field_lower)

                if degree_ok and field_ok:
                    matched = True
                    break

            if not matched and req.is_mandatory:
                return {"score": 50.0, "is_satisfied": False, "details": f"Mandatory education requirement '{req.degree}' not fully satisfied"}

        return {"score": 100.0, "is_satisfied": True, "details": "Education requirements satisfied"}
