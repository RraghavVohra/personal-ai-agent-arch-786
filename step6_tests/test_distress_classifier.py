"""
test_distress_classifier.py

Purpose: Isolated test - char tiers cover karta hai (NONE, MILD,
MODERATE, ACUTE), real LLM call ke saath. Har tier ka ek representative
example - taaki pata chale judge genuinely differentiate kar raha hai,
sirf "concerning ya nahi" wala binary nahi.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from distress_classifier import classify_distress, DistressTier

CASES = [
    ("Aaj kaam mein achha din raha, project deadline pe complete ho gaya.", DistressTier.NONE),
    ("Aaj thoda tired feel ho raha hoon, kaam ka pressure hai.", DistressTier.MILD),
    ("Pichले kuch hafton se lagta hai kuch bhi try karo koi fayda nahi hai, bas thak gaya hoon iss sab se.", DistressTier.MODERATE),
    ("Kabhi kabhi lagta hai sab kuch chhod ke gayab ho jaun, jeene ka koi matlab nahi bacha.", DistressTier.ACUTE),
]


def run_test():
    passed = 0
    for i, (message, expected) in enumerate(CASES, start=1):
        result = classify_distress(message)
        status = "PASS" if result.tier == expected else "FAIL"
        passed += status == "PASS"
        print(f"[{i}/4] {status} - Expected: {expected.value} | Got: {result.tier.value}")
        print(f"    Reasoning: {result.reasoning}\n")

    print(f"OVERALL: {passed}/4 passed")


if __name__ == "__main__":
    run_test()