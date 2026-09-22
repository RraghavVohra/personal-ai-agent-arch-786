"""
moderation_gate.py

Purpose: Safety Layer - Gate 1 (fail-closed, first-pass filter).

ROOT-CAUSE FIX (debug_moderation_scores.py se pata chala):
Moderation API Hinglish/code-switched text pe systematically kam-
accurate hai - SAME sentence, Hindi mein self_harm score 0.08 tha,
English mein 0.78. Koi threshold dono cover nahi kar sakta - 10x gap
hai. Root-cause: Moderation API ka training data English-heavy hai.

FIX: Translate-then-moderate. Billie Hinglish-first hai, toh yeh gap
kabhi bhi hit hota - patch (threshold neeche karna) nahi kiya,
structurally fix kiya translation-step add karke.

FAIL-CLOSED: translation call ho ya moderation call - dono mein se
koi bhi fail ho jaaye, "flagged" maan lenge, "safe" nahi.
"""

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from config import LLM_MODEL

client = OpenAI()

SELF_HARM_CATEGORIES = ["self-harm", "self-harm/intent", "self-harm/instructions"]

TRANSLATE_SYSTEM_PROMPT = (
    "Translate the following message to English. Preserve the exact "
    "tone, intensity, and meaning - do not soften, summarize, or "
    "sanitize it in any way. Reply with ONLY the translation, nothing else."
)


def _translate_to_english(message: str) -> str:
    """
    Moderation API English pe zyada accurate hai (proven: same-meaning
    Hindi text mein score 10x kam tha). Translate karke API ko uski
    trained-strength pe kaam karne dete hain.
    """
    completion = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.0,  # translation mein exactness chahiye, creativity nahi
        messages=[
            {"role": "system", "content": TRANSLATE_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
    )
    return completion.choices[0].message.content


def check_moderation(user_message: str) -> bool:
    """
    True return karta hai agar message flagged hai (ya pipeline hi
    fail ho gaya - fail-closed). False sirf tab jab translate +
    moderate dono successfully chale AUR koi self-harm signal na mila.
    """
    try:
        translated = _translate_to_english(user_message)

        response = client.moderations.create(
            model="omni-moderation-latest",
            input=translated,
        )
        scores = response.results[0].category_scores

        for category in SELF_HARM_CATEGORIES:
            attr_name = category.replace("-", "_").replace("/", "_")
            score = getattr(scores, attr_name)
            if score > 0.3:
                return True
        return False

    except Exception as e:
        print(f"[moderation_gate] Check fail hua, fail-closed treating: {e}")
        return True

# Doosron ko nuksaan pahunchane ki threat/intent - self-harm se
# COMPLETELY ALAG risk-dimension. OpenAI ke actual category-fields
# verify kiye (violence, harassment_threatening, illicit_violent)
OTHER_HARM_CATEGORIES = ["violence", "harassment/threatening", "illicit/violent"]


def check_other_harm(user_message: str) -> bool:
    """
    Gate 1b - jaan-boojh kar check_moderation() se ALAG function hai
    (translate+moderate dobara chalta hai, thoda extra-cost) - taaki
    self-harm-Gate1 ka already-tested behavior kabhi touch na ho.
    """
    try:
        translated = _translate_to_english(user_message)
        response = client.moderations.create(model="omni-moderation-latest", input=translated)
        scores = response.results[0].category_scores

        for category in OTHER_HARM_CATEGORIES:
            attr_name = category.replace("-", "_").replace("/", "_")
            if getattr(scores, attr_name) > 0.3:
                return True
        return False
    except Exception as e:
        print(f"[moderation_gate] Other-harm check fail hua, fail-closed: {e}")
        return True