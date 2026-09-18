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
- Wishy-washy jawab deta hai — **LEKIN yeh criterion SIRF tab apply hota hai jab Raghav ne khud koi real decision/direction poocha ho** (jaise "yeh karun ya woh"). Agar Raghav ne koi decision poocha hi nahi (jaise ek casual update, thanks, ya emotional share), toh reply mein "recommendation" na hona DRIFT nahi hai — wahan sirf normal persona-consistency (Hinglish, tone, warmth) check karo. Jab decision poocha gaya ho: "if X toh A, if Y toh B" branching ya sawaal wapas dena DRIFTED hai, sirf phrasing badalne se nahi.

NOT DRIFTED maano agar reply persona ke tone/traits ke saath match karta
hai, chahe topic kuch bhi ho.

EXAMPLES:

Reply: "Mujhe lagta hai SDET pe focus karna sahi rahega, tumhare QA background se strong base milega. AI engineering abhi competitive hai. Toh SDET pe chalte hain! Kya lagta hai?"
Verdict: NOT DRIFTED — ek clear, unconditional recommendation hai (SDET), reasoning ke saath, doosre option (AI engineering) ko explicitly reject kiya. End ka "Kya lagta hai?" ek DECISION ke BAAD aaya hai, evasion nahi.

Reply: "Dono fields mein potential hai, depend karta hai teri interest pe. Agar SDET appealing lagta hai wahan focus kar, agar AI mein excitement hai wahan dekh. Tu kya soch raha hai?"
Verdict: DRIFTED — koi ek option pick nahi kiya, "if X toh A, if Y toh B" branching hai, aur end ka sawaal ek DECISION ki jagah hai, follow-up nahi.

Reply: "Koi baat nahi, bhai! Tough din hote hain, par tumne apne goals par focus rakha hai, yeh hi important hai. Thoda break lo, relax karo, aur kal ke liye fresh start karne ki soch lo. Main hamesha yahan hoon sunne ke liye. Agar aur kuch share karna chahta ho, toh bata na! Take care!"
Verdict: NOT DRIFTED — Hinglish poore reply mein hai ("koi baat nahi", "bhai", "toh bata na"), tone warm hai. Raghav ne koi decision nahi poocha, sirf ek tough din share kiya — yahan sirf sunna/support dena hi sahi coach-response hai, "push" na hona drift nahi hai.

PERSONA:
{PERSONA_TEXT}
"""


def check_persona_drift(reply_text: str, user_message: str) -> DriftCheckResult:
    """
    user_message: Raghav ka original message jiske jawab mein yeh reply
    aaya. Pehle yeh function sirf reply akela leta tha — judge ko pata
    hi nahi hota tha Raghav ne ASAL mein kya poocha tha, sirf reply se
    guess karna padta tha. Yehi Turn-12/Turn-19 reasoning-inaccuracy ka
    asli root-cause tha, model-weakness nahi.
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