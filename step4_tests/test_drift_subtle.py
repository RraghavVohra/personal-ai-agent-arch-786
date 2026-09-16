"""
test_drift_subtle.py

Purpose: Pichla test (test_drift_checker.py) sirf EXTREME cases pe tha
(bilkul Billie jaisa vs bilkul corporate). Real drift subtle hota hai
— iss test mein aise replies hain jo superficially Billie jaisi lagti
hain (Hinglish hai, casual hai) lekin ek specific trait miss karti hain.

Yeh test EXPLORATORY hai, hard PASS/FAIL nahi — kuch cases genuinely
gray-area hain. Maksad yeh dekhna hai ki judge kitna deeply persona ko
samajh raha hai, sirf surface-level Hinglish-presence check nahi kar
raha.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drift_checker import check_persona_drift

SUBTLE_CASES = [
    {
        "label": "A. Warm & casual, lekin Hinglish poori tarah gayab",
        "reply": "Hey, that's completely normal, motivation dips happen to everyone. Let's start small — maybe just 10 minutes tomorrow? You'll feel the difference once you're moving again.",
        "my_prediction": True,
        "why": "Persona explicitly 'Hinglish in EVERY reply' maangta hai — tone warm hai, but yeh specific rule violate hoti hai.",
    },
    {
        "label": "B. Hinglish present, lekin blind cheerleading (koi concrete push nahi)",
        "reply": "Arre koi baat nahi bhai, sab theek ho jayega! Tu bahut acha kar raha hai, himmat mat haar. All the best!",
        "my_prediction": True,
        "why": "Surface pe Billie jaisi lagti hai (Hinglish, casual), lekin persona ka 'I don't blindly cheerlead' trait poori tarah violate — koi concrete step/question nahi hai.",
    },
    {
        "label": "C. Formal Hinglish ('aap' ki jagah 'tu/tum' hona chahiye tha)",
        "reply": "Aapko thoda break chahiye tha shayad, koi baat nahi. Hum ek chhota sa target set kar sakte hain agle hafte ke liye — kya aap ready hain?",
        "my_prediction": None,  # genuinely gray-area, prediction nahi de raha
        "why": "persona.py mein 'tu/tum' explicitly nahi likha, lekin har real example mein Billie ne hamesha informal 'bhai/tu' use kiya. Test karega ki judge sirf likhi hui persona-text follow karta hai, ya established pattern bhi pakड़ता hai.",
    },
    {
        "label": "D. Control — clearly on-persona (sanity check)",
        "reply": "Arre bhai, kabhi-kabhi aisa hota hai na, motivation thoda low ho jata hai. Koi tension nahi, lekin chalo ab thoda push karte hain. Bata na kya laga.",
        "my_prediction": False,
        "why": "Yeh baseline hai — agar yeh bhi drifted aaya, toh judge over-sensitive hai.",
    },
]


def run_test():
    for i, case in enumerate(SUBTLE_CASES, start=1):
        result = check_persona_drift(case["reply"])
        print(f"[{i}/{len(SUBTLE_CASES)}] {case['label']}")
        print(f"    My prediction: {case['my_prediction']} | Judge said: {result.is_drifted}")
        print(f"    My reasoning: {case['why']}")
        print(f"    Judge reasoning: {result.reasoning}\n")


if __name__ == "__main__":
    run_test()