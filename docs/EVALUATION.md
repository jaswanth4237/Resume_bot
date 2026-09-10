# EVALUATION.md — Evaluation Framework & Metrics

## 1. Overview
The evaluation framework validates the accuracy, precision, recall, and suitability decisions of ResumeMatch AI against a manually labeled ground-truth dataset.

## 2. Evaluation Metrics
- **Accuracy**: Overall proportion of correct suitability decisions (SUITABLE, BORDERLINE, REJECT).
- **Precision**: Ratio of true suitable candidates among all candidates flagged suitable.
- **Recall**: Ratio of correctly identified suitable candidates out of total actual suitable candidates.
- **F1 Score**: Harmonic mean of Precision and Recall.
- **False Acceptance Rate (FAR)**: Rate at which unqualified/rejected candidates are falsely accepted.
- **False Rejection Rate (FRR)**: Rate at which qualified candidates are falsely rejected.
- **Skill Matching Accuracy**: Percentage of skills correctly classified as MATCHED, PARTIAL, or MISSING.
- **Mandatory Requirement Detection Accuracy**: Precision/Recall of identifying mandatory constraints in JDs.

## 3. Dataset Structure
Evaluation test cases are located in `tests/evaluation_dataset/`.
Each case contains a candidate resume, job description, expected decision, and ground-truth breakdown.
