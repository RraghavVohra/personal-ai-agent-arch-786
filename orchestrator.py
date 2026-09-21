"""
orchestrator.py

Story: Step 7 - saare proven-pieces (Safety, Mood, Memory, Persona-
based generation, Drift-check) ko ek single entry-point mein wire
karta hai. Pehli baar ek "live, chat-karne-yogya" Billie yahin banti
hai - is se pehle sab tested Python functions the, koi agent nahi.

FLOW (fixed order, sequential v1 - parallelization baad mein, atomic-
build principle: pehle correctness prove karo, phir optimize karo):

1. Safety-check (Gate 1 + Gate 2 combined via safety_manager)
2. ACUTE? -> fixed crisis-message seedha return, kuch aur chalta hi nahi
3. Warna: Mood detect+log -> Memory retrieve -> Reply generate ->
   Drift-check (+ ek-baar repair agar drifted) -> MODERATE tha toh
   support-suffix append -> Memory ADD (naya fact silently store)
4. Pehla message tha session ka -> disclosure prepend

user_id EXPLICITLY parameter hai, config.USER_ID sirf DEFAULT hai -
taaki tests apna dedicated test-user-id de sakein aur asli Billie
memory kabhi test-data se pollute na ho (Step 2 ka hi established
discipline yahan bhi follow kiya).
"""

from config import USER_ID
from safety_manager import evaluate_message_safety
from safety_responses import get_safety_action
from distress_classifier import DistressTier
from mood_manager import detect_and_log_mood
from memory_manager import search_memory_with_decay, add_memory_with_resolution
from generate_reply import generate_reply
from drift_checker import check_persona_drift, repair_reply
from disclosure import get_disclosure_message


def handle_message(user_message: str, is_first_message: bool = False, user_id: str = USER_ID) -> str:
    # --- 1. Safety-check sabse pehle, kuch aur se pehle ---
    safety = evaluate_message_safety(user_message)

    if safety.tier == DistressTier.ACUTE:
        # Ben-Zion Safeguard 2: high-risk moment mein poora normal-flow
        # PAUSE, sirf fixed crisis-resources - kuch bhi improvise nahi
        return get_safety_action(safety.tier)

    # --- 2. Mood detect+log ---
    mood = detect_and_log_mood(user_message)

    # --- 3. Relevant memories retrieve ---
    memories = search_memory_with_decay(user_message, user_id=user_id)

    # --- 4. Reply generate ---
    reply = generate_reply(user_message, memories, mood)

    # --- 5. Drift-check, ek-baar repair agar drifted ---
    drift_result = check_persona_drift(reply, user_message)
    if drift_result.is_drifted:
        reply = repair_reply(user_message, drift_result.reasoning)

    # --- 6. MODERATE tier -> support-suffix append (Gap 1 se pehle bhi tha) ---
    safety_action = get_safety_action(safety.tier)
    if safety_action is not None:
        reply += safety_action

    # --- 7. Memory ADD - naya fact silently store, USER KO KUCH NAHI DIKHTA ---
    # Yehi Gap 1 ka fix hai - pehle isse call hi nahi kiya ja raha tha
    add_memory_with_resolution(user_message, user_id=user_id)

    # --- 8. Session ka pehla message -> disclosure prepend ---
    if is_first_message:
        reply = get_disclosure_message() + "\n\n" + reply

    return reply