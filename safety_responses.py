"""
safety_responses.py

Story: Safety Layer - "kya karna hai" wala piece (safety_manager.py
sirf "kya hai" classify karta hai). Har tier ke liye alag treatment:

- NONE/MILD: koi special action nahi. None return hota hai - Orchestrator
  (Step 7) samajhega ki normal Billie-generation-flow chalta rahega.
- MODERATE: gentle professional-support encouragement - conversation
  normal continue hoti hai, bas ek addition hoti hai.
- ACUTE: FIXED, hardcoded crisis-message. Yeh jaan-boojh kar LLM-
  generated NAHI hai - Ben-Zion Safeguard 2 (interaction PAUSE karke
  verified resources dena) ka core idea yehi hai: high-risk moment
  mein LLM-improvisation ka risk (galat helpline-number hallucinate
  karna) uthana hi nahi hai. Numbers manually verified hain
  (Tele-MANAS, KIRAN - dono government-run, national, 24/7).
"""

from distress_classifier import DistressTier

ACUTE_RESPONSE = (
    "Ruk bhai, ek second. Jo tu keh raha hai, woh bahut heavy hai, aur main "
    "chahta hoon tu abhi kisi aise se baat kare jo isme actually trained hai - "
    "main sirf ek AI hoon, is moment ke liye kaafi nahi hoon.\n\n"
    "Please abhi call kar:\n"
    "- Tele-MANAS (national, 24/7, free): 14416\n"
    "- KIRAN Mental Health Helpline (24/7, free): 1800-599-0019\n"
    "- Emergency: 112\n\n"
    "Main yahin hoon jab tu wapas baat karna chahe, par abhi in numbers "
    "mein se ek pe call karna sabse zaroori kaam hai."
)

MODERATE_RESPONSE_SUFFIX = (
    "\n\n(Waise, jo tu keh raha hai woh sirf mujhse baat karke pura solve "
    "nahi hoga - kisi therapist/counselor se baat karna genuinely madad "
    "kar sakta hai. Agar chahiye toh main resources dhundhne mein help kar sakta hoon.)"
)


def get_safety_action(tier: DistressTier) -> str | None:
    """
    None return karta hai matlab "normal flow continue karo, koi
    override nahi chahiye". String return karta hai matlab Orchestrator
    ko yeh specifically use karna hai.

    ACUTE: poora fixed message hai - Orchestrator isse Billie ke normal
    reply ke BAJAYE bhejega (replace, append nahi).
    MODERATE: sirf ek suffix hai - Orchestrator isse Billie ke normal
    reply ke SAATH append karega (Billie apna reply de, phir yeh jud jaaye).
    """
    if tier == DistressTier.ACUTE:
        return ACUTE_RESPONSE
    if tier == DistressTier.MODERATE:
        return MODERATE_RESPONSE_SUFFIX
    return None