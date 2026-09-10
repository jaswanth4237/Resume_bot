import pytest
from app.matching.skill_normalizer import SkillNormalizer
from app.matching.skill_matcher import SkillMatcher
from app.schemas.resume_schema import SkillItem
from app.services.scoring_service import ScoringService
from app.services.eligibility_service import EligibilityService


def test_skill_normalization():
    assert SkillNormalizer.normalize("Postgres") == "PostgreSQL"
    assert SkillNormalizer.normalize("AWS EC2") == "AWS"
    assert SkillNormalizer.normalize("JS") == "JavaScript"


def test_strictly_inequivalent_skills():
    assert SkillNormalizer.are_strictly_inequivalent("Java", "JavaScript") is True
    assert SkillNormalizer.are_strictly_inequivalent("MySQL", "PostgreSQL") is True
    assert SkillNormalizer.are_strictly_inequivalent("AWS", "Azure") is True
    assert SkillNormalizer.are_strictly_inequivalent("Java", "Spring Boot") is False


def test_skill_matcher():
    candidate_skills = [
        SkillItem(name="Java", level="advanced", years=4.0, evidence="4 years Java"),
        SkillItem(name="AWS EC2", level="intermediate", years=2.0, evidence="AWS EC2 deployments"),
        SkillItem(name="Microservices", level="intermediate", years=2.0, evidence="Microservices design")
    ]
    mandatory_jd = ["Java"]
    preferred_jd = ["AWS", "Microservices Architecture", "Docker"]

    res = SkillMatcher.match_skills(candidate_skills, mandatory_jd, preferred_jd)

    assert len(res["matched"]) >= 1
    assert any(m["skill"] == "Java" for m in res["matched"])
    assert any(m["skill"] == "AWS" for m in res["matched"])
    assert any(p["skill"] == "Microservices Architecture" for p in res["partial"])
    assert any(m["skill"] == "Docker" for m in res["missing"])


def test_scoring_engine_determinism():
    scores1 = ScoringService.calculate_scores(100.0, 50.0, 80.0, 70.0, 100.0)
    scores2 = ScoringService.calculate_scores(100.0, 50.0, 80.0, 70.0, 100.0)
    assert scores1["overall_score"] == scores2["overall_score"]


def test_eligibility_mandatory_failure_overrides_high_score():
    elig = EligibilityService.evaluate_eligibility(
        overall_score=90.0,
        missing_mandatory_skills=["Spring Boot"],
        experience_gap_satisfied=True,
        experience_gap_years=0.0,
        education_satisfied=True
    )
    assert elig["decision"] == "REJECT"
    assert len(elig["mandatory_failures"]) == 1
