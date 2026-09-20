"""
test_mood_detector.py

Purpose: Isolated test — mood_detector.py ka detection check karta hai.
Case 3, 5, 6 sabse zaroori hain: temporal-reasoning aur mixed-signal
pitfalls ko directly target karte hain.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mood_detector import detect_mood

TEST_CASES = [
    {
        "label": "Clear current negative emotion",
        "message": "I'm so frustrated right now, nothing is working today.",
        "expected_emotion": "anger",
    },
    {
        "label": "Clear current positive emotion",
        "message": "I'm so excited, I just got the job offer!!",
        "expected_emotion": "joy",
    },
    {
        "label": "CRITICAL: past emotion recounted, now resolved",
        "message": "Pichle hafte interview ko lekar bahut stressed tha, lekin ab bahut achha lag raha hai, sab sahi ho gaya.",
        "expected_emotion": "joy",
    },
    {
        "label": "Neutral factual update",
        "message": "I sent 2 job applications yesterday.",
        "expected_emotion": "neutral",
    },
    {
        "label": "REVERSE: past positive, now negative",
        "message": "Pehle running bahut pasand tha, lekin ab bilkul mann nahi karta uska, boring lagta hai.",
        "expected_emotion": "sadness",
    },
    {
        "label": "Mixed signal: good past event, current anxiety",
        "message": "Interview toh accha gaya tha, lekin ab tak koi response nahi aaya unka, thoda anxious feel ho raha hai wait karte karte.",
        "expected_emotion": "fear",
    },
]


def run_test():
    passed = 0
    for i, case in enumerate(TEST_CASES, start=1):
        result = detect_mood(case["message"])
        status = "PASS" if result.emotion.value == case["expected_emotion"] else "FAIL"
        passed += status == "PASS"
        print(f"[{i}/{len(TEST_CASES)}] {case['label']} -> {status}")
        print(f"    Expected: {case['expected_emotion']} | Got: {result.emotion.value} (intensity: {result.intensity}) | topic: {result.topic.value}")
        print(f"    Reasoning: {result.reasoning}\n")

    print(f"{passed}/{len(TEST_CASES)} passed.")


if __name__ == "__main__":
    run_test()