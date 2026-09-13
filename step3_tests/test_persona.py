"""
test_persona.py

Purpose: Isolated test — sirf persona.py ka structure/length check
karta hai. Koi LLM call nahi. Agla test (baad mein) actual LLM se
call karke dekhega ki tone sahi aa raha hai ya nahi.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from persona import build_system_prompt, PERSONA_NAME
from config import PERSONA_CHAR_LIMIT


def run_test():
    prompt = build_system_prompt()

    assert isinstance(prompt, str) and len(prompt) > 0, "Prompt khaali ya string nahi hai."
    print(f"[1/3] Prompt generate hua, length: {len(prompt)} chars.")

    assert len(prompt) <= PERSONA_CHAR_LIMIT, "Character limit cross ho gaya."
    print(f"[2/3] Limit ({PERSONA_CHAR_LIMIT}) ke andar hai.")

    assert PERSONA_NAME in prompt, "Naam prompt ke andar nahi mila."
    print(f"[3/3] Naam '{PERSONA_NAME}' prompt mein present hai.")

    print("\nAll persona structure tests passed.")
    print("\n--- Rendered prompt ---")
    print(prompt)


if __name__ == "__main__":
    run_test()