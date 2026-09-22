# SCORING.md — ResumeMatch AI Scoring & Decision Engine

## Core Principle

**The LLM extracts. Application code scores.**

An LLM is never asked "what percentage does this candidate score?" 
The score is always calculated by `scoring.js` from structured extracted data.

---

## Category Weights

```
Skills:             50%  (mandatory 80% + preferred 20% blend)
Experience:         20%
Responsibilities:   15%
Education:           5%
Preferred Skills:   10%
```

These are defined in `scoring.js` and are configurable as constants. The sum equals 1.0.

---

## Skills Score (50%)

The skills category score is a **weighted blend** of:

- **Mandatory skill coverage** (80% weight within skills)
- **Preferred skill coverage** (20% weight within skills)

**Mandatory skill coverage:**
```
mandatory_score = (exact_mandatory_matches + 0.5 × partial_mandatory_matches) / total_mandatory_skills × 100
```

**Preferred skill coverage:**
```
preferred_score = (exact_preferred_matches + 0.5 × partial_preferred_matches) / total_preferred_skills × 100
```

**Combined skills score:**
```
skills_score = (mandatory_score × 0.8) + (preferred_score × 0.2)
```

---

## Experience Score (20%)

```
experience_score = min(100, (candidate_years / required_years) × 100)
```

If no minimum experience is specified in the JD, the experience score is 100.

---

## Responsibilities Score (15%)

Currently: 100 if resume text is non-empty AND JD has listed responsibilities. 0 if resume is empty.

This is a simplification—future versions will use semantic similarity between resume experience descriptions and JD responsibilities.

---

## Education Score (5%)

100 if the resume contains at least one degree matching the JD education requirement keyword (bachelor, master, phd, etc.), or if no requirement is specified.

0 if the JD specifies a mandatory education requirement and no matching degree is found.

---

## Preferred Score (10%)

Equal to `preferred_score` from the skills calculation above.

---

## Overall Score Formula

```
overall_score = (skills_score × 0.50)
              + (experience_score × 0.20)
              + (responsibilities_score × 0.15)
              + (education_score × 0.05)
              + (preferred_score × 0.10)

overall_score = min(100, max(0, overall_score))
```

---

## Decision Rules

**Evaluated in order:**

1. If any mandatory skill is missing → **REJECT**
2. If experience gap > 0 against a mandatory minimum → **REJECT**
3. If mandatory education not satisfied → **REJECT**
4. If `overall_score >= SUITABLE_THRESHOLD` (default: 75) → **SUITABLE**
5. If `overall_score >= BORDERLINE_THRESHOLD` (default: 60) → **BORDERLINE**
6. Otherwise → **REJECT**

Thresholds are configurable via environment variables:
```
SUITABLE_THRESHOLD=75
BORDERLINE_THRESHOLD=60
```

**Critical rule:** A REJECT due to mandatory failures is NOT overridden by a high score.
A candidate with score=95% who is missing a mandatory skill is still **REJECT**.

---

## Skill Matching Levels

### Exact Match (confidence: 1.0)
Normalized skill names match exactly.
```
Resume: "Node.js"   JD: "Node.js"   → EXACT
Resume: "Node"      JD: "Node.js"   → EXACT (after alias normalization)
```

### Partial Match (confidence: 0.85)
Token overlap or alias hit, but not blocked by `strict_inequivalent`.
```
Resume: "AWS EC2"   JD: "AWS"       → PARTIAL
Resume: "Spring"    JD: "Spring Boot" → PARTIAL
```

Contributes 0.5× to the match score.

### Missing (confidence: 0.0)
No evidence found and not blocked by strict inequality.
```
Resume: has Java    JD: requires Docker  → Docker is MISSING
```

---

## Strict Non-Equivalents

The following pairs are explicitly blocked from partial matching:
- MySQL ≠ PostgreSQL
- Java ≠ JavaScript
- AWS ≠ Azure
- AWS ≠ GCP
- Azure ≠ GCP
- React ≠ React Native
- C ≠ C++
- C++ ≠ C#

---

## Gap Priority

| Priority | Condition                                  |
|----------|--------------------------------------------|
| CRITICAL | Mandatory skill missing or experience gap  |
| HIGH     | Important preferred skill missing          |
| MEDIUM   | Partial skill match                        |
| LOW      | Nice-to-have not present                   |

---

## Reproducibility

The same resume + JD inputs always produce the same result.
No randomness, no LLM-generated scores.
All intermediate values are returned in `category_scores`.
