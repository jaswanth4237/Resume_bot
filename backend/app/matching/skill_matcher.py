from typing import List, Dict, Any
from rapidfuzz import fuzz
from app.matching.skill_normalizer import SkillNormalizer
from app.schemas.resume_schema import SkillItem


class SkillMatcher:
    @classmethod
    def match_skills(
        cls,
        candidate_skills: List[SkillItem],
        mandatory_jd_skills: List[str],
        preferred_jd_skills: List[str]
    ) -> Dict[str, Any]:
        matched = []
        partial = []
        missing = []

        candidate_map = {}
        for s in candidate_skills:
            norm_name = SkillNormalizer.normalize(s.name)
            candidate_map[norm_name.lower()] = s

        all_jd_skills = []
        for s in mandatory_jd_skills:
            all_jd_skills.append((s, True))
        for s in preferred_jd_skills:
            if s not in mandatory_jd_skills:
                all_jd_skills.append((s, False))

        for jd_skill, is_mandatory in all_jd_skills:
            norm_jd = SkillNormalizer.normalize(jd_skill)
            norm_jd_lower = norm_jd.lower()

            # 1. Exact / Normalized Match
            if norm_jd_lower in candidate_map:
                cand_skill = candidate_map[norm_jd_lower]
                matched.append({
                    "skill": jd_skill,
                    "normalized_skill": norm_jd,
                    "evidence": cand_skill.evidence or f"Found in resume as {cand_skill.name}",
                    "match_type": "EXACT",
                    "confidence": 1.0,
                    "is_mandatory": is_mandatory
                })
                continue

            # 2. Semantic / Related Match (Fuzzy ratio & substring containment)
            best_partial_match = None
            best_score = 0.0

            for cand_norm_lower, cand_skill in candidate_map.items():
                if SkillNormalizer.are_strictly_inequivalent(jd_skill, cand_skill.name):
                    continue

                # Substring inclusion (e.g. AWS EC2 -> AWS, Spring Boot -> Spring)
                if norm_jd_lower in cand_norm_lower or cand_norm_lower in norm_jd_lower:
                    score = 0.85
                else:
                    ratio = fuzz.ratio(norm_jd_lower, cand_norm_lower)
                    score = ratio / 100.0 if ratio >= 75 else 0.0

                if score > best_score and score >= 0.70:
                    best_score = score
                    best_partial_match = {
                        "skill": jd_skill,
                        "normalized_skill": norm_jd,
                        "candidate_skill": cand_skill.name,
                        "evidence": cand_skill.evidence or f"Related skill found: {cand_skill.name}",
                        "match_type": "PARTIAL",
                        "confidence": round(best_score, 2),
                        "is_mandatory": is_mandatory
                    }

            if best_partial_match:
                partial.append(best_partial_match)
            else:
                missing.append({
                    "skill": jd_skill,
                    "normalized_skill": norm_jd,
                    "evidence": "No evidence found in candidate resume",
                    "match_type": "MISSING",
                    "confidence": 0.0,
                    "is_mandatory": is_mandatory
                })

        # Calculate scores
        total_mandatory = len(mandatory_jd_skills)
        mandatory_matched_count = sum(1 for m in matched if m["is_mandatory"])
        mandatory_partial_count = sum(1 for p in partial if p["is_mandatory"])
        mandatory_score = ((mandatory_matched_count + (0.5 * mandatory_partial_count)) / total_mandatory * 100.0) if total_mandatory > 0 else 100.0

        total_preferred = len(preferred_jd_skills)
        pref_matched_count = sum(1 for m in matched if not m["is_mandatory"])
        pref_partial_count = sum(1 for p in partial if not p["is_mandatory"])
        preferred_score = ((pref_matched_count + (0.5 * pref_partial_count)) / total_preferred * 100.0) if total_preferred > 0 else 100.0

        return {
            "matched": matched,
            "partial": partial,
            "missing": missing,
            "mandatory_score": min(100.0, max(0.0, round(mandatory_score, 2))),
            "preferred_score": min(100.0, max(0.0, round(preferred_score, 2)))
        }
