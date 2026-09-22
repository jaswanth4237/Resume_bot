# EVALUATION.md — ResumeMatch AI Evaluation Methodology

## Overview

Accuracy is measured against a manually labeled evaluation dataset.
No universal accuracy percentages are claimed without evidence.

---

## Evaluation Dataset Location

`backend/tests/evaluation_dataset/`

Each case contains:
- `resume.txt` — candidate resume text
- `jd.txt` — job description text
- `expected.json` — manually labeled ground truth

---

## Ground Truth Schema

```json
{
  "case_id": "case_001",
  "description": "Strong Java developer, all mandatory skills met",
  "expected_decision": "SUITABLE",
  "expected_score_range": [80, 95],
  "expected_mandatory_requirements": ["Java", "Spring Boot", "Microservices"],
  "expected_missing_skills": [],
  "expected_partial_skills": ["Docker"]
}
```

---

## Metrics Measured

| Metric                          | Definition                                                          |
|---------------------------------|---------------------------------------------------------------------|
| Decision Accuracy               | % cases where predicted decision matches expected decision          |
| False Acceptance Rate (FAR)     | % REJECT cases incorrectly classified as SUITABLE                  |
| False Rejection Rate (FRR)      | % SUITABLE cases incorrectly classified as REJECT                  |
| Mandatory Skill Detection       | % mandatory skills correctly identified from JD text               |
| Missing Skill Detection Recall  | % truly missing skills correctly flagged as MISSING                |
| Missing Skill Precision         | % flagged MISSING skills that are genuinely missing                |
| F1 Score (Missing Skill)        | Harmonic mean of missing skill precision and recall                |

---

## Evaluation Cases

### case_001 — Fully Qualified Candidate
- Decision: SUITABLE
- Score range: 80–95%
- Notes: All mandatory skills present, experience met

### case_002 — Missing Critical Mandatory Skill
- Decision: REJECT
- Score range: any
- Notes: Must reject regardless of high score on other categories

### case_003 — Borderline Experience Gap
- Decision: BORDERLINE or REJECT
- Score range: 60–74%
- Notes: Partial experience shortfall, no mandatory skill failures

### case_004 — Preferred Only Gaps
- Decision: SUITABLE or BORDERLINE
- Notes: Mandatory met, some preferred skills absent

### case_005 — No Skills Match
- Decision: REJECT
- Notes: Complete mandatory skill mismatch

---

## Running the Evaluation

```bash
cd backend
node tests/evaluation_dataset/run_evaluation.js
```

Output will print per-case results and aggregate metrics.

---

## Limitations

- The evaluation dataset is small and manually curated.
- Rule-based extraction does not use an LLM, so complex resume layouts may produce lower recall.
- Accuracy metrics apply to the labeled dataset only.
- This system is a recruitment **assistance tool** and should not replace human review.
- Protected characteristics (age, gender, race, disability, religion) are never used as scoring factors.
