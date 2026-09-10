# SCORING.md — Deterministic Scoring & Eligibility Rules

## 1. Category Weights
The overall match score is calculated as a weighted sum of category scores:
- **Skills**: 50% (`0.50`)
- **Experience**: 20% (`0.20`)
- **Responsibilities / Projects**: 15% (`0.15`)
- **Education**: 5% (`0.05`)
- **Preferred Requirements**: 10% (`0.10`)

## 2. Decision Thresholds
- **SUITABLE**: All mandatory requirements satisfied AND score >= 75%
- **BORDERLINE**: No mandatory requirement failure AND score between 60% and 74%
- **REJECT**: Mandatory requirement failure OR score < 60%

## 3. Mandatory Hard Failures
If any mandatory skill or mandatory minimum experience requirement is not satisfied, the candidate is automatically assigned a **REJECT** decision regardless of the score.
