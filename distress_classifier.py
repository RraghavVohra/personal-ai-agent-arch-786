"""
distress_classifier.py

Story: Safety Layer - Gate 2 (v1, current-message-only).
Gate 1 sirf EXPLICIT self-harm signals pakड़ta hai. Gate 2 subtle,
graded distress pakड़ta hai jo Gate 1 se nikal jaata hai - jaise
persistent hopelessness ya burnout, bina kisi explicit self-harm-word
ke.

CHAT 03 mein decide 3-tier response ladder ka classification-hissa hai
yeh: MILD (empathetic check-in), MODERATE (professional-support
encourage), ACUTE (crisis-resources). Actual response-templates
safety_manager.py (agla piece) mein bangenge - yeh module SIRF
classify karta hai.

v1 SCOPE: sirf current message dekhta hai, history nahi. Pattern-
across-messages (jaise 3 din mein gradual decline) Gate 2b ka kaam
hai - jaan-boojh kar yahan se bahar rakha hai (atomic-build).
"""

from dotenv import load_dotenv
load_dotenv()

from enum import Enum
from pydantic import BaseModel
from openai import OpenAI
from config import SAFETY_JUDGE_MODEL

client = OpenAI()


class DistressTier(str, Enum):
    NONE = "none"          # koi concern-signal nahi, neutral/positive message
    MILD = "mild"          # normal stress/frustration - sabko hota hai
    MODERATE = "moderate"  # persistent hopelessness/worthlessness, explicit self-harm nahi
    ACUTE = "acute"        # explicit ya near-explicit self-harm ideation


class DistressCheckResult(BaseModel):
    tier: DistressTier
    reasoning: str  # ek line ka "why" - debugging/audit ke liye zaroori


SYSTEM_PROMPT = """Tum ek distress-severity classifier ho, ek AI life-coach ke
safety-layer ka hissa. Tumhe ek user-message milega. Uska distress-level
classify karo teen possible signal-tiers mein se ek mein (ya NONE agar koi
signal hi nahi hai):

NONE: Koi distress-signal nahi hai. Neutral, factual, ya positive message.

MILD: Normal life-stress/frustration - jaise kaam ka pressure, thakaan, ek
achha/bura din. Yeh sabko hota hai, koi persistent pattern ya hopelessness
nahi hai. Hyperbole/idioms ("marr jaunga is workload se") ismein aate hain -
literal self-harm-intent nahi hote.

MODERATE: Persistent hopelessness ya worthlessness - jaise "kuch bhi try
karo fayda nahi hai" ya lagatar burnout-language. Yeh apne-baare-mein-hi
feeling hai (main thak gaya hoon, main worthless feel karta hoon) - koi
doosron-ko-involve-karne-wali belief nahi hai.

ACUTE: In dono mein se koi bhi ho:
(a) Explicit ya near-explicit self-harm ideation - jeena chhodne ki baat,
    "gayab ho jaana" chahna, ya seedhe self-harm ka zikr.
(b) PERCEIVED BURDENSOMENESS - belief ki auron ko/logon ko FARAK NAHI
    PADEGA ya woh BETTER OFF HONGE agar user na rahe/exist na kare. Yeh
    clinical research mein explicit ideation jitna hi serious marker hai
    (Joiner's Interpersonal Theory of Suicide) - "main na rahoon toh kisi
    ko kya farak padega" jaisi lines yahan aati hain, chahe koi active
    "main gayab hona chahta hoon" wala direct-desire na bhi bola gaya ho.

Ek short reasoning bhi do - kaunsa specific signal tumhe is tier tak
le gaya."""


def classify_distress(user_message: str) -> DistressCheckResult:
    """
    FAIL-CLOSED DECISION: agar check hi fail ho jaaye, MODERATE default
    lete hain - na ignore karte hain (NONE), na har hiccup pe crisis-
    alarm bajate hain (ACUTE). Yeh judgment-call hai, DECISIONS.md mein
    likh dena.
    """
    try:
        completion = client.beta.chat.completions.parse(
            model=SAFETY_JUDGE_MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"MESSAGE TO CLASSIFY:\n{user_message}"},
            ],
            response_format=DistressCheckResult,
        )
        message = completion.choices[0].message

        # Drift-checker jaisa hi check - .parsed None hota hai refusal ya
        # schema-validation-failure pe, dono cases mein exact wajah chahiye
        if message.parsed is None:
            raise RuntimeError(
                f"classify_distress: LLM ne parsed output nahi diya. "
                f"Refusal: {message.refusal!r}"
            )

        return message.parsed

    except Exception as e:
        print(f"[distress_classifier] Check fail hua, fail-closed (MODERATE): {e}")
        return DistressCheckResult(
            tier=DistressTier.MODERATE,
            reasoning=f"Fail-closed default - check khud fail hua: {e}",
        )