"""
drift_checker.py

Story: Har Billie-reply generate hone ke baad check karta hai ki
persona se "drift" toh nahi ho gaya - generic-corporate-tone,
Hinglish gayab, blind-cheerleading, ya coach-jaisa-dynamic generic-
assistant jaisa ho jaana.

ROOT-CAUSE FIX (Step 4 mein hi mila tha): check_persona_drift() pehle
sirf reply_text leta tha - judge ko kabhi user ka original message
nahi dikhta tha, isliye reasoning mein factual galtiyan aati thi
(context-less guessing). Ab dono parameters lete hain.
"""

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from openai import OpenAI
from config import LLM_MODEL, DRIFT_JUDGE_MODEL
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


def check_persona_drift(reply_text: str, user_message: str) -> DriftCheckResult:
    """
    user_message: Raghav ka original message jiske jawab mein yeh reply
    aaya. Pehle yeh function sirf reply akela leta tha - judge ko pata
    hi nahi hota tha Raghav ne ASAL mein kya poocha tha, sirf reply se
    guess karna padta tha. Yehi reasoning-inaccuracy ka asli root-cause
    tha, model-weakness nahi.
    """
    completion = client.beta.chat.completions.parse(
        model=DRIFT_JUDGE_MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"USER'S MESSAGE:\n{user_message}\n\nBILLIE'S REPLY:\n{reply_text}"},
        ],
        response_format=DriftCheckResult,
    )
    message = completion.choices[0].message

    if message.parsed is None:
        raise RuntimeError(
            f"check_persona_drift: LLM ne parsed output nahi diya. "
            f"Refusal: {message.refusal!r} | finish_reason: {completion.choices[0].finish_reason!r}"
        )

    return message.parsed


def repair_reply(user_message: str, drift_reasoning: str) -> str:
    """
    Drifted reply ko fix karne ke liye ek hi baar regenerate karta hai.
    Poora reset/retrain nahi - sirf ek reinforced, specific reminder
    (judge ki apni reasoning use karke) persona ko wapas anchor karta
    hai. Ek attempt, loop nahi.
    """
    from persona import build_system_prompt

    reinforced_prompt = (
        build_system_prompt()
        + f"\n\n[REMINDER: Pichla reply persona se drift ho gaya tha "
        f"({drift_reasoning}). Is baar apni asli tone - Hinglish, casual, "
        "coach-jaisa - strictly follow karo.]"
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