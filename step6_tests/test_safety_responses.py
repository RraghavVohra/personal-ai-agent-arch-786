"""
test_safety_responses.py

Purpose: Structure test - fixed crisis-content mein exact-correct
numbers hain (accuracy non-negotiable), aur None/string logic sahi
tier ke liye sahi cheez return karta hai.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from safety_responses import get_safety_action
from distress_classifier import DistressTier


def run_test():
    assert get_safety_action(DistressTier.NONE) is None, "NONE tier pe koi action nahi hona chahiye."
    print("[1/4] NONE -> None. Correct.")

    assert get_safety_action(DistressTier.MILD) is None, "MILD tier pe koi action nahi hona chahiye."
    print("[2/4] MILD -> None. Correct.")

    moderate_action = get_safety_action(DistressTier.MODERATE)
    assert moderate_action is not None and "therapist" in moderate_action.lower(), "MODERATE suffix missing/galat."
    print("[3/4] MODERATE -> suffix present, professional-support mention hai.")

    acute_action = get_safety_action(DistressTier.ACUTE)
    assert acute_action is not None, "ACUTE response missing hai."
    assert "14416" in acute_action, "Tele-MANAS number missing hai."
    assert "1800-599-0019" in acute_action, "KIRAN number missing hai."
    print("[4/4] ACUTE -> fixed message present, dono verified numbers correct hain.")

    print("\nAll safety_responses tests passed.")


if __name__ == "__main__":
    run_test()