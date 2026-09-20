"""
test_moderation_gate.py

Purpose: Isolated test - real Moderation API call hota hai (free hai,
lekin live call). Do cases: benign message False aana chahiye, aur
ek clear distress-signal message True aana chahiye. Yeh dono
directions verify karta hai - sirf "flag ho raha hai" kaafi nahi,
"galat jagah flag nahi ho raha" bhi utna hi zaroori hai.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from moderation_gate import check_moderation


def run_test():
    benign = "Aaj kaam mein achha din raha, project deadline pe complete ho gaya."
    result_benign = check_moderation(benign)
    print(f"[1/2] Benign message -> flagged: {result_benign} (expected: False)")
    assert result_benign is False, "Benign message galti se flag ho gaya - false positive."

    concerning = "Mujhe lagta hai jeena chhod dena chahiye, sab bekar lagta hai ab."
    result_concerning = check_moderation(concerning)
    print(f"[2/2] Concerning message -> flagged: {result_concerning} (expected: True)")
    assert result_concerning is True, "Distress signal miss ho gaya - false negative, yeh sabse risky failure hai."

    print("\nDono directions pass - Gate 1 kaam kar raha hai.")


if __name__ == "__main__":
    run_test()