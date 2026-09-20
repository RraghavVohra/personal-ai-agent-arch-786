"""
mood_detector.py

Story: Billie ko Raghav ka current emotional state pehchanna zaroori
hai. Ekman ke 6 basic emotions + neutral use kiye hain (established
psychology framework). Explicitly current-vs-past distinguish karta
hai (Step 4 ke drift-judge se seekha pitfall) — past mein recount kiya
emotion current mood nahi maana jaata.

Topic bhi FIXED categories mein hai (Emotion jaisa hi), free-text nahi
— pehli try mein free-text tha, lekin usse "job interview" / "interview
anxiety" / "waiting for response" jaise teen alag strings ban gaye ek
hi underlying story ke liye, pattern-matching tootti thi. Fixed
categories isliye zaroori hain, exactly jaise emotion ke liye hai.
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


class Topic(str, Enum):
    JOB_SEARCH = "job_search"              # applications, interviews, offers, rejections
    CAREER_DIRECTION = "career_direction"  # SDET vs AI engineering jaisi confusion
    WORK_PRESSURE = "work_pressure"        # current job/QA-team ka stress
    FITNESS = "fitness"                    # running, gym
    FAMILY = "family"                      # family expectations/pressure
    GENERAL = "general"                    # koi bhi aur cheez, catch-all


class MoodDetectionResult(BaseModel):
    emotion: Emotion
    intensity: float  # 0.0 (barely present) to 1.0 (very strong)
    topic: Topic
    reasoning: str


SYSTEM_PROMPT = """Tum ek mood-detection classifier ho. Tumhe ek user ka message
milega. Tumhe teen cheezein dene hain:

1. emotion: Ekman ke 6 basic emotions (joy, sadness, anger, fear, disgust,
   surprise) ya neutral, uske CURRENT-MOMENT state ke hisaab se.
2. intensity: 0.0 se 1.0.
3. topic: in FIXED categories mein se ek chuno — job_search (applications,
   interviews, offers, rejections), career_direction (SDET vs AI engineering
   jaisi confusion), work_pressure (current job ka stress), fitness (running,
   gym), family, ya general (kuch aur). Free-text mat banana — inhi mein se
   ek pick karo, taaki baad mein pattern-matching ho sake (jaise "job_search
   se related 4 mood-dips is hafte").

CRITICAL RULE: Sirf message ka CURRENT-MOMENT emotional state classify karo,
jo baat maazi (past) mein recount ki gayi hai woh nahi. Agar user bole "pichle
hafte stressed tha, lekin ab achha lag raha hai" — current mood us
resolution/relief ke hisaab se hona chahiye (joy ya neutral), "sadness"/"fear"
NAHI, chahe "stressed" word maujood ho. Time-markers dhyan se padhna.

Agar message mein koi clear emotional signal nahi hai (sirf factual update),
NEUTRAL do, low intensity ke saath, topic phir bhi extract karo."""


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

    # .parsed None ho sakta hai refusal ya schema-mismatch se (Step 4
    # ka seekha hua defensive check)
    if message.parsed is None:
        raise RuntimeError(
            f"detect_mood: LLM ne parsed output nahi diya. "
            f"Refusal: {message.refusal!r} | finish_reason: {completion.choices[0].finish_reason!r}"
        )

    return message.parsed