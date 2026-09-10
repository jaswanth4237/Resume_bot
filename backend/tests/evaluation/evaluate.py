import asyncio
import json
import os
import sys
from typing import List, Dict, Any

# Ensure backend path is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from app.services.matching_service import MatchingService


async def run_evaluation():
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../tests/evaluation_dataset"))
    if not os.path.exists(dataset_dir):
        print(f"Evaluation dataset directory not found: {dataset_dir}")
        return

    test_files = [f for f in os.listdir(dataset_dir) if f.endswith(".json")]
    print(f"Found {len(test_files)} evaluation test cases in {dataset_dir}\n")

    correct_decisions = 0
    total_cases = len(test_files)
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    true_negatives = 0

    for file_name in test_files:
        file_path = os.path.join(dataset_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            case = json.load(f)

        print(f"--- Evaluating {case['id']}: {case['name']} ---")
        result = await MatchingService.analyze_candidate_against_jd(
            resume_filename="resume.txt",
            resume_bytes=case["resume_text"].encode("utf-8"),
            jd_filename="jd.txt",
            jd_bytes=case["jd_text"].encode("utf-8")
        )

        actual_decision = result["decision"]
        expected_decision = case["expected_decision"]
        score = result["overall_score"]

        is_correct = (actual_decision == expected_decision)
        if is_correct:
            correct_decisions += 1

        if expected_decision in ["SUITABLE", "BORDERLINE"]:
            if actual_decision in ["SUITABLE", "BORDERLINE"]:
                true_positives += 1
            else:
                false_negatives += 1
        else:
            if actual_decision == "REJECT":
                true_negatives += 1
            else:
                false_positives += 1

        print(f"Expected Decision: {expected_decision} | Actual: {actual_decision} | Score: {score}% | Status: {'[PASS]' if is_correct else '[FAIL]'}")
        print(f"Mandatory Failures: {result['mandatory_failures']}")
        print(f"Explanation: {result['explanation']}\n")

    accuracy = (correct_decisions / total_cases * 100.0) if total_cases > 0 else 0.0
    precision = (true_positives / (true_positives + false_positives)) * 100.0 if (true_positives + false_positives) > 0 else 100.0
    recall = (true_positives / (true_positives + false_negatives)) * 100.0 if (true_positives + false_negatives) > 0 else 100.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    print("==================================================")
    print("EVALUATION METRICS REPORT")
    print("==================================================")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Precision: {precision:.2f}%")
    print(f"Recall: {recall:.2f}%")
    print(f"F1 Score: {f1:.2f}%")
    print(f"Total Evaluated Cases: {total_cases}")
    print("==================================================")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
