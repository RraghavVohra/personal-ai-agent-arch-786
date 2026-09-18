"""
test_multiturn_simulation.py

Purpose: Original goal — 20-30 turn conversation, dekhna hai drift kahan
emerge hoti hai lambi, real conversation mein. Extended version — pichle
12-turn wale se continue karta hai, aur do stress-tests add karta hai:
ek decision-question bahut baad mein (turn 19), aur ek closing/gratitude
message end mein (turn 24) — dono known-tricky patterns hain jo humne
eval-suite mein fix kiye the.

Note: 24 turns x 2 calls (reply + drift-check) = ~48 LLM calls, chalne
mein 1-2 minute lag sakta hai — normal hai.
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
    "Ek aur interview call aayi hai, is baar thoda zyada confident feel ho raha hai.",
    "DSA practice continue kar raha hoon roz, thoda improve hua hai.",
    "Ek networking event tha, miss ho gaya kaam ki wajah se. Peers aage nikal rahe hain aisa lagta hai.",
    "Mock interview diya aaj, feedback kaafi achha mila.",
    "Ghar pe sabne poocha kab tak naya job milega, thoda pressure feel ho raha hai.",
    "Aaj phir gym skip kar diya, yeh pattern ban raha hai lagta hai.",
    "Agar offer aata hai toh salary negotiate karun ya seedha accept kar loon?",
    "Offer aa gaya bhai!! Excited hoon bahut.",
    "Ab current job resign karne ka soch raha hoon, thoda nervous hoon apni QA team ke liye jo miss karenge.",
    "Peeche mudke dekhta hoon toh pura yeh journey kaafi tough tha, lekin proud feel ho raha hai.",
    "Resume bhi update karna padega naye role ke hisaab se, bhool hi gaya tha.",
    "Bhai is poore stretch mein tumne bahut support kiya, thanks yaar.",
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