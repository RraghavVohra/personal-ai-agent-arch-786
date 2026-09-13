"""
test_classifier.py

Purpose: Isolated test for classifier.py. Real LLM call hota hai (koi
DB, koi Mem0 nahi). LLM thoda non-deterministic ho sakta hai, isliye
hard assert() ki jagah PASS/FAIL print karte hain per case — taaki ek
borderline case pura test crash na kare, aur hum prompt tune kar sakein.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from classifier import classify_relationship

TEST_CASES = [
    {
        "label": "CONFIRMS case",
        "existing": "User is a QA engineer.",
        "new": "User works as a QA engineer.",
        "expected": "CONFIRMS",
    },
    {
        "label": "CONTRADICTS case (real scenario from Step 2 test)",
        "existing": "User is a QA engineer.",
        "new": "User recently switched from QA engineer to SDET.",
        "expected": "CONTRADICTS",
    },
    {
        "label": "UNRELATED case",
        "existing": "User loves running on weekends.",
        "new": "User is a QA engineer.",
        "expected": "UNRELATED",
    },
]


def run_test():
    passed = 0
    for i, case in enumerate(TEST_CASES, start=1):
        result = classify_relationship(case["existing"], case["new"])
        status = "PASS" if result.relationship.value == case["expected"] else "FAIL"
        passed += status == "PASS"
        print(f"[{i}/{len(TEST_CASES)}] {case['label']} -> {status}")
        print(f"    Expected: {case['expected']} | Got: {result.relationship.value}")
        print(f"    Reasoning: {result.reasoning}\n")

    print(f"{passed}/{len(TEST_CASES)} cases passed.")


if __name__ == "__main__":
    run_test()