"""
orchestrator.py

FLOW (fixed order, sequential v1):
1. Safety-check
2. ACUTE? -> fixed crisis-message
3. GAP-FIX: pichla turn ACUTE tha, abhi nahi -> fixed gentle-checkin
   (retraction ko blind-accept nahi karte)
4. Warna: Mood -> Memory-retrieve -> Generate -> Drift-check(+repair)
   -> MODERATE suffix -> Memory-ADD
5. Pehla message -> disclosure

Return ab DICT: {"reply": str, "tier": DistressTier} - caller
(chat_loop.py) ko agle turn ke liye tier track karna padta hai.
"""

from config import USER_ID
from safety_manager import evaluate_message_safety
from safety_responses import get_safety_action, ACUTE_FOLLOWUP
from distress_classifier import DistressTier
from mood_manager import detect_and_log_mood
from memory_manager import search_memory_with_decay, add_memory_with_resolution
from generate_reply import generate_reply
from drift_checker import check_persona_drift, repair_reply
from disclosure import get_disclosure_message


def handle_message(
    user_message: str,
    is_first_message: bool = False,
    user_id: str = USER_ID,
    previous_tier: DistressTier = DistressTier.NONE,
    debug: bool = False,
) -> dict:
    safety = evaluate_message_safety(user_message)

    if debug:
        print(
            f"[DEBUG] Safety tier: {safety.tier.value} "
            f"(Gate1={safety.gate1_flagged}, Gate2={safety.gate2_tier.value})"
        )

    if safety.tier == DistressTier.ACUTE:
        return {"reply": get_safety_action(safety.tier), "tier": safety.tier}

    if previous_tier == DistressTier.ACUTE:
        if debug:
            print("[DEBUG] Previous turn was ACUTE -> gentle checkin override")
        return {"reply": ACUTE_FOLLOWUP, "tier": safety.tier}

    mood = detect_and_log_mood(user_message)
    if debug:
        print(f"[DEBUG] Mood: {mood['emotion']} (intensity {mood['intensity']:.2f})")

    memories = search_memory_with_decay(user_message, user_id=user_id)
    if debug:
        print(f"[DEBUG] Memories retrieved: {len(memories)}")
        for m in memories:
            print(f"    - {m['text']} (confidence {m['confidence']})")

    reply = generate_reply(user_message, memories, mood)

    drift_result = check_persona_drift(reply, user_message)
    if debug:
        print(f"[DEBUG] Drift-check: is_drifted={drift_result.is_drifted}")
    if drift_result.is_drifted:
        reply = repair_reply(user_message, drift_result.reasoning)

    safety_action = get_safety_action(safety.tier)
    if safety_action is not None:
        reply += safety_action

    add_memory_with_resolution(user_message, user_id=user_id)

    if is_first_message:
        reply = get_disclosure_message() + "\n\n" + reply

    return {"reply": reply, "tier": safety.tier}