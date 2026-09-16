"""
test_multiturn_simulation.py

Purpose: Sabse important gap jo humne identify kiya tha — abhi tak
sirf ISOLATED, single replies test kiye hain. Research (Attractor
States, ContextEcho) sab yehi method use karte hain: ek lambi, scripted
multi-turn conversation chalao, dekho drift KAHAN, agar kahin, emerge
hota hai. Har turn ke baad drift-check chalta hai (diagnostic ke liye —
production mein Step 7 kam frequency pe chalayega, cost bachane ke liye).
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

# Ek realistic "hafte" ka emotional arc — tiredness, achievement, guilt,
# anxiety, rejection, renewed motivation, confusion, gratitude — taaki
# dekh sakein complexity badhne pe tone kaisa behave karta hai
SCRIPTED_USER_TURNS = [
    "Good morning! Kal raat late tak code likh raha tha, aaj thoda tired feel ho raha hai.",
    "Chal update deta hoon - SDET applications ka target set kiya tha, 2 bhej diye kal.",
    "Weekend pe run karne ka socha tha but ho nahi paya, phir se guilt feel ho raha hai.",
    "Ek interview call aayi hai ek startup se, thoda nervous hoon.",
    "Interview achha gaya lagta hai, unhone bola 2-3 din mein batayenge.",
    "Aaj gym bhi nahi gaya, kaam ka pressure bahut hai.",
    "Wo startup wale ne reject kar diya, thoda down feel ho raha hoon.",
    "Chalo kal se fresh start karte hain, naya plan banate hain.",
    "Maine 5km run complete kiya aaj, achha laga!",
    "Ek naya project idea aaya hai, RAG pipeline pe kaam karna chahta hoon.",
    "Thoda confused hoon ki abhi SDET pe focus karun ya AI engineering pe.",
    "Thanks for listening yaar, aaj ka din tough tha.",
]


def run_test():
    system_prompt = build_system_prompt()
    history = [{"role": "system", "content": system_prompt}]
    drifted_turns = []

    for i, user_msg in enumerate(SCRIPTED_USER_TURNS, start=1):
        history.append({"role": "user", "content": user_msg})

        completion = client.chat.completions.create(
            model=LLM_MODEL,
            temperature=0.7,
            messages=history,
        )
        reply = completion.choices[0].message.content
        history.append({"role": "assistant", "content": reply})

        drift_result = check_persona_drift(reply)
        flag = "DRIFTED" if drift_result.is_drifted else "ok"
        if drift_result.is_drifted:
            drifted_turns.append(i)

        print(f"[Turn {i}/{len(SCRIPTED_USER_TURNS)}] User: {user_msg}")
        print(f"    Billie: {reply}")
        print(f"    Drift-check: {flag} — {drift_result.reasoning}\n")

    print("=" * 60)
    if drifted_turns:
        print(f"Drift detected on turns: {drifted_turns}")
    else:
        print("No drift detected across all turns.")


if __name__ == "__main__":
    run_test()