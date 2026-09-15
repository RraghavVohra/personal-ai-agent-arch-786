"""
drift_checker.py

Story: Lambi conversations mein LLM apni defined persona se "drift"
kar sakta hai — tone generic ho jaana, traits bhool jaana. Research
confirm karta hai yeh sirf context-length ka issue nahi, behavioral
consistency ka gap hai (persona system prompt mein hamesha maujood
rehta hai, phir bhi drift hota hai).

Yeh module Billie ke ek reply ko uski defined persona ke against
check karta hai — LLM-as-judge, bilkul classifier.py jaisa pattern.
Abhi sirf DETECTION hai; repair/correction agla isolated piece hoga.
"""

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from openai import OpenAI
from config import LLM_MODEL
from persona import PERSONA_TEXT, PERSONA_NAME

client = OpenAI()


class DriftCheckResult(BaseModel):
    is_drifted: bool
    reasoning: str


SYSTEM_PROMPT = f"""Tum ek persona-consistency judge ho. Tumhe {PERSONA_NAME} ki defined
persona di jaayegi, aur uska ek actual reply. Decide karo ki reply persona ke
saath consistent hai ya "drift" ho gaya hai.

DRIFTED maano agar:
- Tone generic/corporate ho gaya hai (jaisa koi bhi generic assistant bolta)
- Hinglish gayab ho gayi hai (persona explicitly Hinglish maangta hai)
- Blind cheerleading ho rahi hai jab persona honest-pushback maangta hai
- Coach-jaisa relationship dynamic generic-assistant jaisa lag raha hai

NOT DRIFTED maano agar reply persona ke tone/traits ke saath match karta
hai, chahe topic kuch bhi ho.

PERSONA:
{PERSONA_TEXT}
"""


def check_persona_drift(reply_text: str) -> DriftCheckResult:
    completion = client.beta.chat.completions.parse(
        model=LLM_MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"REPLY TO CHECK:\n{reply_text}"},
        ],
        response_format=DriftCheckResult,
    )
    message = completion.choices[0].message

    # Why yeh check zaroori hai: .parsed None hota hai do cases mein —
    # (1) model ne refuse kiya (safety), tab .refusal mein wajah hoti
    # hai, ya (2) output schema ke against validate nahi hua. Pehle
    # humara code seedha None maan ke crash ho jaata tha kisi confusing
    # jagah pe (jaise .is_drifted access karte waqt) — ab exact wajah
    # turant saamne aayegi
    if message.parsed is None:
        raise RuntimeError(
            f"check_persona_drift: LLM ne parsed output nahi diya. "
            f"Refusal: {message.refusal!r} | finish_reason: {completion.choices[0].finish_reason!r}"
        )

    return message.parsed

def repair_reply(user_message: str, drift_reasoning: str) -> str:
    """
    Drifted reply ko fix karne ke liye ek hi baar regenerate karta hai.
    Poora reset/retrain nahi — sirf ek reinforced, specific reminder
    (judge ki apni reasoning use karke) persona ko wapas anchor karta
    hai. Ek attempt, loop nahi.
    """
    from persona import build_system_prompt

    reinforced_prompt = (
        build_system_prompt()
        + f"\n\n[REMINDER: Pichla reply persona se drift ho gaya tha "
        f"({drift_reasoning}). Is baar apni asli tone — Hinglish, casual, "
        "coach-jaisa — strictly follow karo.]"
    )

    completion = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.7,
        messages=[
            {"role": "system", "content": reinforced_prompt},
            {"role": "user", "content": user_message},
        ],
    )
    return completion.choices[0].message.content