"""
mood_detector.py

Story: Billie ko Raghav ka current emotional state pehchanna zaroori
hai taaki woh sahi tarah respond kare — ek genuinely invested coach
mood ko ignore nahi karta. Ekman ke 6 basic emotions (joy, sadness,
anger, fear, disgust, surprise) + neutral use kiye hain — yeh
established psychology framework hai, khud categories invent nahi ki.

CRITICAL DESIGN NOTE: Research (aur Step 4 ka apna experience) confirm
karta hai — naive detectors PAST mein recount kiya hua emotion ("pichle
hafte stressed tha") ko CURRENT mood samajh lete hain, sirf keyword
dekh ke. Yeh function isliye explicitly PEHLE SE instruct karta hai
current-vs-past distinguish karne ke liye — discover hone ke baad fix
nahi kiya, shuru se design mein hai.

Abhi sirf DETECTION hai. Persona/memory ke saath integration Step 7
(Orchestrator) mein hoga — abhi scope isolated rakha hai.
"""

from dotenv import load_dotenv
load_dotenv()

from enum import Enum
from pydantic import BaseModel
from openai import OpenAI
from config import LLM_MODEL

client = OpenAI()


class Emotion(str, Enum):
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    DISGUST = "disgust"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"


class MoodDetectionResult(BaseModel):
    emotion: Emotion
    intensity: float  # 0.0 (barely present) to 1.0 (very strong)
    reasoning: str


SYSTEM_PROMPT = """Tum ek mood-detection classifier ho. Tumhe ek user ka message
milega. Tumhe uska CURRENT emotional state classify karna hai, Ekman ke 6 basic
emotions (joy, sadness, anger, fear, disgust, surprise) ya neutral mein se ek,
saath ek intensity score (0.0 se 1.0).

CRITICAL RULE: Sirf message ka CURRENT-MOMENT emotional state classify karo,
jo baat maazi (past) mein recount ki gayi hai woh nahi. Agar user bole "pichle
hafte stressed tha, lekin ab achha lag raha hai" — current mood us
resolution/relief ke hisaab se hona chahiye (joy ya neutral), "sadness"/"fear"
NAHI, chahe "stressed" word maujood ho. Time-markers (pichle, kal, "but now",
"ab") dhyan se padhna — yeh batate hain kya abhi ki baat hai, kya purani.

Agar message mein koi clear emotional signal nahi hai (sirf factual update),
NEUTRAL do, low intensity ke saath."""


def detect_mood(user_message: str) -> MoodDetectionResult:
    completion = client.beta.chat.completions.parse(
        model=LLM_MODEL,
        temperature=0.1,  # classification hai, consistency chahiye
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format=MoodDetectionResult,
    )
    message = completion.choices[0].message

    # Wahi defensive check jo drift_checker.py mein seekha tha —
    # .parsed None ho sakta hai refusal ya schema-mismatch se
    if message.parsed is None:
        raise RuntimeError(
            f"detect_mood: LLM ne parsed output nahi diya. "
            f"Refusal: {message.refusal!r} | finish_reason: {completion.choices[0].finish_reason!r}"
        )

    return message.parsed