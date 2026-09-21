"""
generate_reply.py

Story: Yeh Step 7 ka core piece hai - ab tak koi bhi function Billie
ka ACTUAL conversational-reply nahi banata tha. Persona (Step 3),
relevant memories (Step 2 ka search_memory_with_decay), aur current
mood (Step 5) - teeno ko system-prompt mein fold karke ek LLM call
se reply generate karta hai.

Isolated rakha hai (jaisa har piece) - Safety-tier ka koi awareness
nahi is function ko, woh Orchestrator ki responsibility hai (agar
ACUTE hai toh yeh function CALL hi nahi hoga, safety_responses ka
fixed-message seedha return hoga).
"""

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from config import LLM_MODEL, GENERATION_TEMPERATURE
from persona import build_system_prompt

client = OpenAI()


def generate_reply(user_message: str, memories: list[dict], mood: dict) -> str:
    """
    memories: search_memory_with_decay() ka output (empty list chalega
    agar kuch relevant nahi mila).
    mood: detect_and_log_mood() ka output dict (emotion, intensity, ...).
    """
    system_prompt = build_system_prompt()

    # Why memories ko system-prompt mein fold karte hain, user-message
    # mein nahi: taaki Billie ko yeh "apna hi pata hua context" lage,
    # user ne khud nahi bataya abhi - persona ki continuity isi se
    # maintain hoti hai
    if memories:
        memory_lines = "\n".join(f"- {m['text']}" for m in memories)
        system_prompt += f"\n\n[TUJHE YEH PEHLE SE PATA HAI USER KE BAARE MEIN:\n{memory_lines}]"

    system_prompt += (
        f"\n\n[USER KA ABHI KA MOOD: {mood['emotion']}, "
        f"intensity {mood['intensity']:.1f}/1.0 - apna response isi ke hisaab se tune karo.]"
    )

    completion = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=GENERATION_TEMPERATURE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return completion.choices[0].message.content