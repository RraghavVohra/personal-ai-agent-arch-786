"""
test_generate_reply.py

Purpose: Teen scenarios test karta hai - memory-context, mood-context,
aur dono ke saath. "Achha reply hai ya nahi" subjective hai, isliye
naya judge nahi likha - Step 4 ka check_persona_drift() reuse kiya
hai verify karne ke liye ki generated reply persona se drift toh
nahi kar gayi.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generate_reply import generate_reply
from drift_checker import check_persona_drift

CASES = [
    {
        "label": "Plain message, no memory, neutral mood",
        "user_message": "Aaj kaam kaisa raha poochna chahta tha.",
        "memories": [],
        "mood": {"emotion": "neutral", "intensity": 0.2},
    },
    {
        "label": "Memory-context present",
        "user_message": "Kya lag raha hai, interview ke liye ready hoon?",
        "memories": [{"text": "User SDET role ke liye interview-prep kar raha hai"}],
        "mood": {"emotion": "fear", "intensity": 0.5},
    },
    {
        "label": "Strong mood signal",
        "user_message": "Aaj bahut achha din tha, ek achha news mila.",
        "memories": [],
        "mood": {"emotion": "joy", "intensity": 0.9},
    },
]


def run_test():
    for i, case in enumerate(CASES, start=1):
        reply = generate_reply(case["user_message"], case["memories"], case["mood"])
        drift_result = check_persona_drift(reply, case["user_message"])

        status = "PASS" if not drift_result.is_drifted else "FAIL"
        print(f"[{i}/{len(CASES)}] {case['label']} -> {status}")
        print(f"    Reply: {reply}")
        print(f"    Drift-check reasoning: {drift_result.reasoning}\n")


if __name__ == "__main__":
    run_test()