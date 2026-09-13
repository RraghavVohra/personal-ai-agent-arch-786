"""
test_persona_llm_response.py

Purpose: Behavioral check — persona.py ka system prompt use karke real
LLM call karta hai, dekhna hai tone Billie jaisi aa rahi hai ya nahi.
Manual-review test hai, hard assert nahi.

Yeh sirf verification ke liye — actual "chat with Billie" function
Step 7 (Orchestrator) mein banega, jab memory + persona dono combine
honge.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from persona import build_system_prompt
from config import LLM_MODEL

client = OpenAI()

SAMPLE_MESSAGES = [
    "Hey, I've been slacking off on my running lately, not feeling motivated.",
    "I finally cleared my SDET mock interview today!",
    "I've been saying I'll start applying for AI engineer jobs for 3 weeks now, but I still haven't sent a single application.",
]


def run_test():
    system_prompt = build_system_prompt()

    for i, user_message in enumerate(SAMPLE_MESSAGES, start=1):
        # temperature=0.7 yahan jaan-boojh kar — classifier.py mein 0.1
        # tha kyunki wahan consistency chahiye thi, yahan conversational
        # natural-ness chahiye
        completion = client.chat.completions.create(
            model=LLM_MODEL,
            temperature=0.7,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        reply = completion.choices[0].message.content
        print(f"[{i}/{len(SAMPLE_MESSAGES)}] User: {user_message}")
        print(f"    Billie: {reply}\n")


if __name__ == "__main__":
    run_test()