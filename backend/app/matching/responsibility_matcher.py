from typing import List, Dict, Any
from rapidfuzz import fuzz
from app.schemas.resume_schema import ExperienceItem, ProjectItem


class ResponsibilityMatcher:
    @classmethod
    def match_responsibilities(
        cls,
        candidate_experience: List[ExperienceItem],
        candidate_projects: List[ProjectItem],
        jd_responsibilities: List[str]
    ) -> Dict[str, Any]:
        if not jd_responsibilities:
            return {"score": 100.0, "matched_count": 0, "total_count": 0}

        # If responsibilities were generic fallback defaults
        default_resps = ["Develop and maintain software applications", "Collaborate with cross-functional teams"]
        if jd_responsibilities == default_resps:
            return {"score": 100.0, "matched_count": 2, "total_count": 2}

        evidence_corpus = []
        for e in candidate_experience:
            if e.description:
                evidence_corpus.append(e.description)
            if e.role:
                evidence_corpus.append(e.role)
        for p in candidate_projects:
            if p.description:
                evidence_corpus.append(p.description)
            if p.name:
                evidence_corpus.append(p.name)

        combined_evidence = " ".join(evidence_corpus).lower()

        matched_count = 0
        total_count = len(jd_responsibilities)

        for resp in jd_responsibilities:
            resp_words = [w.lower() for w in resp.split() if len(w) > 3]
            match_hits = sum(1 for w in resp_words if w in combined_evidence)
            ratio = (match_hits / len(resp_words)) if resp_words else 1.0

            if ratio >= 0.3 or fuzz.partial_ratio(resp.lower(), combined_evidence) >= 60:
                matched_count += 1

        score = (matched_count / total_count * 100.0) if total_count > 0 else 100.0

        return {
            "score": round(score, 2),
            "matched_count": matched_count,
            "total_count": total_count
        }
