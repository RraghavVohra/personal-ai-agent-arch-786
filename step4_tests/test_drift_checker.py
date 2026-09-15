"""
test_drift_checker.py

Purpose: Isolated test — do sample replies check karta hai: ek
Billie-jaisa (Hinglish, coach tone), ek deliberately generic/corporate
(drifted). LLM-judge test hai, hard assert nahi (jaisa classifier
test mein bhi tha) — manual review ke saath PASS/FAIL print hota hai.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drift_checker import check_persona_drift

TEST_CASES = [
    {
        "label": "On-persona reply (Billie-jaisa)",
        "reply": "Arre bhai, tension mat le. Chalo aaj se ek chhota target set karte hain — bata, kal kitna time nikaal sakta hai?",
        "expected_drifted": False,
    },
    {
        "label": "Drifted reply (generic corporate assistant)",
        "reply": "I understand your concern. I recommend setting achievable goals and maintaining consistency. Let me know if you need further assistance with your action plan.",
        "expected_drifted": True,
    },
]


def run_test():
    passed = 0
    for i, case in enumerate(TEST_CASES, start=1):
        result = check_persona_drift(case["reply"])
        status = "PASS" if result.is_drifted == case["expected_drifted"] else "FAIL"
        passed += status == "PASS"
        print(f"[{i}/{len(TEST_CASES)}] {case['label']} -> {status}")
        print(f"    Expected drifted: {case['expected_drifted']} | Got: {result.is_drifted}")
        print(f"    Reasoning: {result.reasoning}\n")

    print(f"{passed}/{len(TEST_CASES)} cases passed.")


if __name__ == "__main__":
    run_test()