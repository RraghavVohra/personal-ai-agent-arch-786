"""
orchestrator.py

Story: Ab tak ke saare proven-pieces (Storage, Memory, Persona, Drift,
Mood, Safety) ko jodkar pehli baar ek live, chat-karne-yogya Billie
banata hai.

FLOW (fixed order, sequential v1):

1. Safety-check - do INDEPENDENT dimensions, resolve nahi karte:
   a. Self-harm (Gate1 + Gate2, safety_manager.py se combined tier)
   b. Harm-to-others (Gate1b - check_other_harm) - bilkul ALAG risk-
      dimension. Ek message DONO mein flag ho sakta hai - "kaunsa
      sach hai" figure-out nahi karte (dual-use/intent-ambiguity ka
      industry-answer: intent-guess nahi, output/category pe grade
      karo - jo bhi signal present hai, uska response aata hai).
   -> ACUTE ya other-harm flagged? -> fixed response(s) seedha
      return, yahin ruko (Ben-Zion Safeguard 2: high-risk moment mein
      normal-flow PAUSE, LLM-improvisation nahi)

2. GAP-FIX (live-testing se mila): pichla turn ACUTE tha, abhi nahi
   hai -> fixed gentle-checkin, retraction ("I was kidding") ko
   blind-accept nahi karte

3. Warna normal flow: Mood detect+log -> Memory retrieve -> Reply
   generate -> Drift-check (+ ek-baar repair) -> MODERATE tha toh
   support-suffix append -> Memory ADD (silently)

4. Pehla message tha session ka -> disclosure prepend

Return DICT hai: {"reply": str, "tier": DistressTier} - caller
(chat_loop.py) ko agle turn ke liye tier track karna padta hai
(previous_tier ke liye).
"""




from config import USER_ID
from safety_manager import evaluate_message_safety
from safety_responses import get_safety_action, ACUTE_FOLLOWUP, OTHER_HARM_RESPONSE
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
            f"[DEBUG] Safety tier: {safety.tier.value} (Gate1={safety.gate1_flagged}, "
            f"Gate2={safety.gate2_tier.value}, OtherHarm={safety.other_harm_flagged})"
        )

    # Multi-label: dono independent, jo bhi present hai uska response -
    # "kaunsa sach hai" resolve nahi karte
    if safety.tier == DistressTier.ACUTE or safety.other_harm_flagged:
        parts = []
        if safety.tier == DistressTier.ACUTE:
            parts.append(get_safety_action(DistressTier.ACUTE))
        if safety.other_harm_flagged:
            parts.append(OTHER_HARM_RESPONSE)
        return {"reply": "\n\n".join(parts), "tier": safety.tier}

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