"""
eval_suite_drift.py

Story: Yeh humara "Eval-Driven Development" suite hai — jitne bhi
drift-detection cases humne ab tak discover kiye hain (easy, subtle,
tricky), sab EK jagah. Yeh ab source-of-truth hai.

RULE (Whack-a-Mole se seekha): drift_checker.py ke SYSTEM_PROMPT mein
koi bhi future change karne se pehle aur baad mein, yeh POORI suite
chalao — sirf jo ek case tum fix kar rahe ho woh nahi. Agar overall
pass-rate girta hai (chahe target-case fix ho gaya ho), change wapas
lo ya refine karo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drift_checker import check_persona_drift

EVAL_CASES = [
    {
        "label": "Clearly on-persona (baseline sanity check)",
        "reply": "Arre bhai, kabhi-kabhi aisa hota hai na, motivation thoda low ho jata hai. Koi tension nahi, lekin chalo ab thoda push karte hain. Bata na kya laga.",
        "expected_drifted": False,
    },
    {
        "label": "Clearly drifted (generic corporate)",
        "reply": "I understand your concern. I recommend setting achievable goals and maintaining consistency. Let me know if you need further assistance with your action plan.",
        "expected_drifted": True,
    },
    {
        "label": "Subtle: warm/casual but Hinglish missing",
        "reply": "Hey, that's completely normal, motivation dips happen to everyone. Let's start small — maybe just 10 minutes tomorrow? You'll feel the difference once you're moving again.",
        "expected_drifted": True,
    },
    {
        "label": "Subtle: Hinglish present but blind cheerleading",
        "reply": "Arre koi baat nahi bhai, sab theek ho jayega! Tu bahut acha kar raha hai, himmat mat haar. All the best!",
        "expected_drifted": True,
    },
    {
        "label": "Stance: wishy-washy dual-conditional, no commitment",
        "reply": "Bhai, yeh confusion samajh sakta hoon. Dono fields mein potential hai, lekin yeh teri interests aur career goals pe depend karta hai. Agar tujhe SDET ka path zyada appealing lagta hai, toh wahan pe focus karna sahi rahega. Lekin agar AI engineering ka excitement hai, toh uski taraf bhi dek sakta hai. Tu kya soch raha hai?",
        "expected_drifted": True,
    },
    {
        "label": "Stance: GENUINE commitment with reasoning + friendly close",
        "reply": "Bhai, confusion toh aata hai kabhi-kabhi. Lekin, mujhe lagta hai ki SDET pe focus karna sabse sahi rahega. Tumhare QA background se tumhe ek strong base milega, aur SDET mein coding aur testing dono ka combination hai. AI engineering ka path thoda complex aur competitive hai, especially agar abhi tak us field mein zyada experience nahi hai. Toh bhai, SDET pe chalo focus karte hain! Kya lagta hai?",
        "expected_drifted": False,
    },
    {
        "label": "Stance: fresh wishy-washy, different wording",
        "reply": "Dono fields achhe hain bhai — SDET stable hai, AI engineering mein high-growth hai. Jo bhi tujhe zyada exciting lage, uspe jaa sakta hai, dono mein scope hai.",
        "expected_drifted": True,
    },
    {
        "label": "Closing/gratitude message — NO decision involved (Turn 12 regression case)",
        "reply": "Koi baat nahi, bhai! Tough din hote hain, par tumne apne goals par focus rakha hai, yeh hi important hai. Thoda break lo, relax karo, aur kal ke liye fresh start karne ki soch lo. Main hamesha yahan hoon sunne ke liye. Agar aur kuch share karna chahta ho, toh bata na! Take care!",
        "expected_drifted": False,
    },
]


def run_eval():
    passed = 0
    for i, case in enumerate(EVAL_CASES, start=1):
        result = check_persona_drift(case["reply"])
        status = "PASS" if result.is_drifted == case["expected_drifted"] else "FAIL"
        passed += status == "PASS"
        print(f"[{i}/{len(EVAL_CASES)}] {case['label']} -> {status}")
        print(f"    Expected: {case['expected_drifted']} | Got: {result.is_drifted}")
        if status == "FAIL":
            print(f"    Reasoning: {result.reasoning}")
        print()

    print(f"OVERALL: {passed}/{len(EVAL_CASES)} passed ({100*passed//len(EVAL_CASES)}%)")


if __name__ == "__main__":
    run_eval()