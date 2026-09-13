"""
classifier.py

Story: Do facts (existing + new) ka relationship decide karta hai —
CONFIRMS (same baat dobara), CONTRADICTS (mutually exclusive), ya
UNRELATED (similarity search ka false-positive). Sirf ek LLM call hai,
koi DB/Mem0 nahi. Yeh module KAB call hona hai woh decide nahi karta —
woh add-pipeline ka kaam hoga (sirf close-similarity matches pe, token-
minimization ke liye).

load_dotenv() yahin top pe hai — Step 2 mein humein ek baar bhool ke
crash mil chuka hai, isliye ab har LLM-calling module apni khud ki
.env loading khud handle karta hai, kisi caller pe depend nahi karta.
"""

from dotenv import load_dotenv
load_dotenv()

from enum import Enum
from pydantic import BaseModel
from openai import OpenAI
from config import LLM_MODEL

client = OpenAI()


class Relationship(str, Enum):
    CONFIRMS = "CONFIRMS"
    CONTRADICTS = "CONTRADICTS"
    UNRELATED = "UNRELATED"


class ClassificationResult(BaseModel):
    relationship: Relationship
    reasoning: str  # ek line ka "why" — debugging/audit ke liye


SYSTEM_PROMPT = """Tum ek fact-comparison classifier ho. Tumhe do facts diye jaayenge
— ek EXISTING (pehle se stored) aur ek NEW (abhi extract hua). Decide karo:

- CONFIRMS: NEW fact EXISTING fact ko dobara bata raha hai (same underlying
  truth, chahe alag words mein ho).
- CONTRADICTS: NEW fact EXISTING fact ko directly contradict karta hai — dono
  ek saath sach nahi ho sakte (jaise job title change, location change).
- UNRELATED: Dono facts alag cheezon ke baare mein hain — semantic similarity
  ne galti se close bataya, lekin inka koi confirm/contradict relation nahi hai.

Ek short reasoning bhi do."""


def classify_relationship(existing_fact: str, new_fact: str) -> ClassificationResult:
    completion = client.beta.chat.completions.parse(
        model=LLM_MODEL,
        temperature=0.1,  # consistent classification chahiye, creative nahi — explicit, Mem0 ke internal default pe bharosa nahi (yeh humara apna standalone call hai)
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"EXISTING: {existing_fact}\nNEW: {new_fact}"},
        ],
        response_format=ClassificationResult,
    )
    return completion.choices[0].message.parsed