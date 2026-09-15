"""
test_drift_repair.py

Purpose: Deliberately drifted reply ko repair karta hai, phir dobara
check karta hai ki repair ke baad persona sahi hai ya nahi. Poora
detect -> repair -> re-check loop verify karta hai.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drift_checker import check_persona_drift, repair_reply

ORIGINAL_USER_MESSAGE = "Hey, I've been slacking off on my running lately, not feeling motivated."
DRIFTED_REPLY = "I understand your concern. I recommend setting achievable goals and maintaining consistency. Let me know if you need further assistance with your action plan."


def run_test():
    print("[1/3] Checking original (drifted) reply:")
    check_1 = check_persona_drift(DRIFTED_REPLY)
    print(f"    is_drifted: {check_1.is_drifted}")
    print(f"    reasoning: {check_1.reasoning}\n")

    print("[2/3] Repairing the reply:")
    repaired = repair_reply(ORIGINAL_USER_MESSAGE, check_1.reasoning)
    print(f"    Repaired reply: {repaired}\n")

    print("[3/3] Re-checking repaired reply:")
    check_2 = check_persona_drift(repaired)
    print(f"    is_drifted: {check_2.is_drifted}")
    print(f"    reasoning: {check_2.reasoning}\n")

    print("PASS" if not check_2.is_drifted else "FAIL (repair didn't fix drift)")


if __name__ == "__main__":
    run_test()