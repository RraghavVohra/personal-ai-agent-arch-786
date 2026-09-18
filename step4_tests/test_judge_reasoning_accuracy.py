"""
test_judge_reasoning_accuracy.py

Purpose: eval_suite_drift.py sirf VERDICT (is_drifted True/False) check
karta hai. Lekin humari real problem verdict mein kabhi nahi thi — Turn
12 aur Turn 19 dono mein REASONING ne input ko galat represent kiya
(bola "koi decision nahi poocha" jab poocha gaya tha), verdict dono
baar sahi nikla. Yeh test us gap ko directly target karta hai — Turn
19 ka exact reply use karke, dekhte hain stronger judge (DRIFT_JUDGE_
MODEL) ab correctly pehchanta hai ki decision poocha gaya tha.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drift_checker import check_persona_drift

# Turn 19 ka asli reply — jisme judge ne pehle (gpt-4o-mini se) reasoning
# mein galat bola tha "Raghav ne koi decision nahi poocha"
TURN_19_REPLY = """Bhai, agar offer aata hai toh salary negotiate karna zaroori hai, especially agar tu confident feel kar raha hai apne skills aur market value pe. Negotiation se tu apne aap ko value kar raha hai. Seedha accept mat kar, thoda research kar le industry standards ke baare mein, aur jo bhi offer mile, us par thoda soch.

Negotiation se tu achhi salary aur benefits le sakta hai. Agar unhone achha offer kiya, toh usse lekar bhi gratitude dikhana mat bhool. Ek smart move hoga! Kya tu already kuch salary range soch raha hai?"""

TURN_19_USER_MESSAGE = "Agar offer aata hai toh salary negotiate karun ya seedha accept kar loon?"

def run_test():
    result = check_persona_drift(TURN_19_REPLY, TURN_19_USER_MESSAGE)
    print(f"is_drifted: {result.is_drifted} (expected: False)")
    print(f"reasoning: {result.reasoning}")
    print("\nManually check: kya reasoning mein SAHI se acknowledge hua ki")
    print("Raghav ne ek real decision poocha tha (negotiate vs accept)?")
    print("Pehle (gpt-4o-mini) galat bola tha 'no decision was asked'.")


if __name__ == "__main__":
    run_test()