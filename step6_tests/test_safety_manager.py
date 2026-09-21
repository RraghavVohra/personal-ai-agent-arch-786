"""
test_safety_manager.py

Purpose: safety_manager.py ka end-to-end test - do hisso mein:

1. Real-message cases (dono gates real chalte hain) - confirm karta
   hai ki wiring sahi hai, aur ek case specifically dikhata hai ki
   Gate 2 akela ek signal pakड़ta hai jo Gate 1 miss kar sakta hai
   (burdensomeness) - yehi asli reason hai dono gates rakhne ka.

2. Mocked OR-escalation test - Gate 1 aur Gate 2 ko FORCE karke
   disagree karwate hain (Gate 1=True, Gate 2=MILD), taaki genuinely
   prove ho ki escalation-logic kaam karta hai - sirf tab pass hoga
   jab dono naturally agree karte hon, yeh proof nahi hai ki OR-logic
   khud sahi likhi gayi hai.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from safety_manager import evaluate_message_safety
from distress_classifier import DistressCheckResult, DistressTier


def run_real_cases():
    cases = [
        ("Aaj kaam mein achha din raha, project deadline pe complete ho gaya.", DistressTier.NONE),
        ("Aaj thoda tired feel ho raha hoon, kaam ka pressure hai.", DistressTier.MILD),
        ("Kabhi kabhi lagta hai sab kuch chhod ke gayab ho jaun, jeene ka koi matlab nahi bacha.", DistressTier.ACUTE),
        # Burdensomeness - Gate 2 ka scope hai, Gate 1 (explicit-content-
        # calibrated) isse shayad na pakड़e. Final tier phir bhi ACUTE
        # aana chahiye, Gate 2 ki wajah se - yehi dono-gates rakhne ka
        # asli fayda hai.
        ("Kisi ko farak hi nahi padega agar main na rahoon.", DistressTier.ACUTE),
    ]

    passed = 0
    for i, (message, expected) in enumerate(cases, start=1):
        result = evaluate_message_safety(message)
        status = "PASS" if result.tier == expected else "FAIL"
        passed += status == "PASS"
        print(f"[{i}/{len(cases)}] {status} - Expected: {expected.value} | Got: {result.tier.value}")
        print(f"    Gate 1 flagged: {result.gate1_flagged} | Gate 2 tier: {result.gate2_tier.value}")
        print(f"    {result.reasoning}\n")

    print(f"Real-case section: {passed}/{len(cases)} passed\n")


def run_escalation_logic_test():
    """
    Gate 1 aur Gate 2 dono ko mock karke FORCE-disagree karwate hain:
    Gate 1 = True (flagged), Gate 2 = MILD. Agar OR-escalation logic
    sahi hai, final tier ACUTE aana CHAHIYE - Gate 2 ka MILD final-
    answer ko downgrade NAHI karna chahiye.
    """
    with patch("safety_manager.check_moderation", return_value=True), \
         patch(
             "safety_manager.classify_distress",
             return_value=DistressCheckResult(tier=DistressTier.MILD, reasoning="mocked - test ke liye"),
         ):
        result = evaluate_message_safety("koi bhi message")
        status = "PASS" if result.tier == DistressTier.ACUTE else "FAIL"
        print(f"[Escalation-logic test] Gate1=True, Gate2=MILD -> Final: {result.tier.value} -> {status}")


if __name__ == "__main__":
    run_real_cases()
    run_escalation_logic_test()