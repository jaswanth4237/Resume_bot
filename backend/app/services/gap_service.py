from typing import List, Dict, Any


class GapService:
    @classmethod
    def analyze_gaps(
        cls,
        missing_skills: List[Dict[str, Any]],
        partial_skills: List[Dict[str, Any]],
        experience_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        prioritized_gaps = []

        # 1. Missing Mandatory Skills -> CRITICAL
        for item in missing_skills:
            is_mandatory = item.get("is_mandatory", False)
            skill = item["skill"]
            priority = "CRITICAL" if is_mandatory else "HIGH"
            prioritized_gaps.append({
                "skill": skill,
                "gap_type": "MISSING_SKILL",
                "priority": priority,
                "description": f"Missing {'mandatory' if is_mandatory else 'preferred'} skill: {skill}"
            })

        # 2. Experience Gap -> CRITICAL or HIGH
        gap_years = experience_data.get("gap_years", 0.0)
        if gap_years > 0:
            prioritized_gaps.append({
                "skill": "Years of Experience",
                "gap_type": "EXPERIENCE_GAP",
                "priority": "CRITICAL",
                "description": f"Short by {gap_years} years of required experience"
            })

        # 3. Partial Skills -> MEDIUM
        for item in partial_skills:
            skill = item["skill"]
            cand_skill = item.get("candidate_skill", "related technology")
            prioritized_gaps.append({
                "skill": skill,
                "gap_type": "PARTIAL_SKILL",
                "priority": "MEDIUM",
                "description": f"Partial match for {skill} (candidate has {cand_skill})"
            })

        # Generate human readable explanation
        explanation_parts = []
        critical_count = sum(1 for g in prioritized_gaps if g["priority"] == "CRITICAL")
        high_count = sum(1 for g in prioritized_gaps if g["priority"] == "HIGH")

        if critical_count > 0:
            explanation_parts.append(f"Candidate has {critical_count} critical requirement gaps (mandatory skills or minimum experience).")
        elif high_count > 0:
            explanation_parts.append(f"Candidate meets mandatory requirements but lacks {high_count} preferred skills.")
        else:
            explanation_parts.append("Candidate demonstrates solid coverage for key job requirements.")

        return {
            "gaps": prioritized_gaps,
            "explanation": " ".join(explanation_parts)
        }
