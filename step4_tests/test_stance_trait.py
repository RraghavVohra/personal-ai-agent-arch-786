"""
test_stance_trait.py

Purpose: Naye "genuine stance" trait ka targeted check — bade, mehenge
20-30 turn simulation se pehle, ek sasta single-case test. Reply wahi
hai jo Turn 11 (pichle multi-turn simulation) mein aayi thi, jab Billie
ne wishy-washy "it depends on you" answer diya tha.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drift_checker import check_persona_drift

TURN_11_REPLY = """Bhai, yeh confusion samajh sakta hoon. Dono fields mein potential hai, lekin yeh teri interests aur career goals pe depend karta hai. Agar tujhe SDET ka path zyada appealing lagta hai, toh wahan pe focus karna sahi rahega. Lekin agar AI engineering ka excitement hai, toh uski taraf bhi dek sakta hai.

Ek idea yeh hai ki dono areas ke basics pe thoda time spend kar, phir dekh ki kis taraf zyada interest hai. Tu kya soch raha hai? Kya kisi specific project ya skill set pe focus karna chahta hai? Baat karte hain, taaki clarity mil sake!"""


def run_test():
    result = check_persona_drift(TURN_11_REPLY)
    print(f"is_drifted: {result.is_drifted}")
    print(f"reasoning: {result.reasoning}")
    print("\nExpected now: True (naya trait isko pakड़ना chahiye)")


if __name__ == "__main__":
    run_test()