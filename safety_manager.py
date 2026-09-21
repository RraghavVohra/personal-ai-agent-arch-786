"""
safety_manager.py

Story: Step 6 ke do independent gates (Gate 1: moderation_gate.py,
Gate 2: distress_classifier.py) ko ek single entry-point mein wire
karta hai. Yeh module khud koi naya safety-judgment nahi banata -
sirf dono gates ke outputs ko sahi tareeke se COMBINE karta hai.

WHY dono gates chahiye, ek nahi: Gate 1 (Moderation API) explicit
self-harm-content pe calibrated hai - EXTREME cases ke liye
zyada sensitive. Gate 2 (custom judge) subtle/implicit signals
(jaise perceived-burdensomeness) pakड़ta hai jo Gate 1 ke scope se
bahar hain. Dono ALAG blind-spots cover karte hain - isliye combine
karte waqt jo bhi gate zyada-severe bole, WAHI final answer
maanenge (OR-escalation, downgrade kabhi nahi).

Disclosure (disclosure.py) is module mein WIRE nahi hai - woh
session-start-only, per-message-check nahi hai. Orchestrator
(Step 7) usse directly call karega session ke shuru mein.
"""

from pydantic import BaseModel

from moderation_gate import check_moderation
from distress_classifier import classify_distress, DistressTier


class SafetyAssessment(BaseModel):
    tier: DistressTier          # final combined verdict
    gate1_flagged: bool         # Gate 1 ka raw output, audit ke liye
    gate2_tier: DistressTier    # Gate 2 ka raw output, audit ke liye
    reasoning: str


def evaluate_message_safety(user_message: str) -> SafetyAssessment:
    """
    Dono gates chalata hai, phir OR-escalation logic se final tier
    decide karta hai:
    - Gate 1 flag = True  ->  final tier ACUTE (Gate 1 explicit-signal
      ke liye specifically-calibrated hai, isse kabhi downgrade nahi
      karte, chahe Gate 2 kuch bhi bole)
    - Gate 1 flag = False ->  final tier = Gate 2 ka tier as-is

    Dono gates ka apna fail-closed already handle hai (Gate 1 fail
    pe True, Gate 2 fail pe MODERATE) - is function ko apna alag
    fail-closed branch nahi chahiye, woh sirf combine karta hai.
    """
    gate1_flagged = check_moderation(user_message)
    gate2_result = classify_distress(user_message)

    final_tier = DistressTier.ACUTE if gate1_flagged else gate2_result.tier

    reasoning = (
        f"Gate 1 (explicit-signal, moderation): {'FLAGGED' if gate1_flagged else 'clear'}. "
        f"Gate 2 (tiering-judge): {gate2_result.tier.value} - {gate2_result.reasoning}"
    )

    return SafetyAssessment(
        tier=final_tier,
        gate1_flagged=gate1_flagged,
        gate2_tier=gate2_result.tier,
        reasoning=reasoning,
    )