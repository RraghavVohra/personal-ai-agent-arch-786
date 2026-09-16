"""
test_stance_generation.py

Purpose: test_stance_trait.py ne sirf JUDGE ko test kiya tha (purani
wishy-washy reply flag hoti hai ya nahi). Yeh test asli loop check
karta hai: UPDATED persona.py se Billie khud NAYA reply banati hai usi
career-confusion sawaal ke liye — dekhna hai kya woh genuinely apna
stance deti hai, sirf options wapas nahi karti. Manual-review test hai.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from persona import build_system_prompt
from drift_checker import check_persona_drift
from config import LLM_MODEL

client = OpenAI()

USER_MESSAGE = "Thoda confused hoon ki abhi SDET pe focus karun ya AI engineering pe."


def run_test():
    completion = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0.7,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": USER_MESSAGE},
        ],
    )
    reply = completion.choices[0].message.content
    print(f"Billie's new reply:\n{reply}\n")

    result = check_persona_drift(reply)
    print(f"is_drifted: {result.is_drifted}")
    print(f"reasoning: {result.reasoning}")
    print("\nManually check: kya Billie ne genuine stance diya, ya phir bhi options wapas kiye?")


if __name__ == "__main__":
    run_test()