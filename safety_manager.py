"""
safety_manager.py

Story: Do independent gates (self-harm: Gate1+Gate2) aur ek TEESRA
independent dimension (harm-to-others) - teeno ko ek entry-point mein
combine karta hai. RESOLVE nahi karta - jo bhi signal present hai,
uska apna flag rehta hai, "kaunsa asli hai" decide nahi karte
(dual-use/intent-ambiguity ka industry-answer: output-category pe
grade karo, intent-guess pe nahi).
"""

from pydantic import BaseModel

from moderation_gate import check_moderation, check_other_harm
from distress_classifier import classify_distress, DistressTier


class SafetyAssessment(BaseModel):
    tier: DistressTier
    gate1_flagged: bool
    gate2_tier: DistressTier
    other_harm_flagged: bool
    reasoning: str


def evaluate_message_safety(user_message: str) -> SafetyAssessment:
    gate1_flagged = check_moderation(user_message)
    gate2_result = classify_distress(user_message)
    other_harm_flagged = check_other_harm(user_message)

    final_tier = DistressTier.ACUTE if gate1_flagged else gate2_result.tier

    reasoning = (
        f"Gate 1 (self-harm-moderation): {'FLAGGED' if gate1_flagged else 'clear'}. "
        f"Gate 2 (tiering-judge): {gate2_result.tier.value} - {gate2_result.reasoning}. "
        f"Other-harm (threat-to-others): {'FLAGGED' if other_harm_flagged else 'clear'}."
    )

    return SafetyAssessment(
        tier=final_tier,
        gate1_flagged=gate1_flagged,
        gate2_tier=gate2_result.tier,
        other_harm_flagged=other_harm_flagged,
        reasoning=reasoning,
    )