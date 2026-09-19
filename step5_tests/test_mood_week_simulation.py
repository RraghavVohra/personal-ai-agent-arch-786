"""
test_mood_week_simulation.py

Purpose: End-to-end validation — ek simulated hafte ke messages
(alag din, alag moods) detect+log karta hai, phir trend retrieve karke
readable summary banata hai. Yeh poora loop (detect -> store -> retrieve
-> summarize) test karta hai, sirf isolated pieces nahi — bilkul jaisa
24-turn simulation Persona/Drift ke liye tha.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collections import Counter
from datetime import datetime, timezone, timedelta
from mood_manager import detect_and_log_mood
from mood_log import get_mood_trend

now = datetime.now(timezone.utc)

# Din 6 (sabse purana) se din 0 (aaj) tak — ek realistic emotional arc
SIMULATED_WEEK = [
    (6, "Interview ke liye bahut nervous hoon, pata nahi kaisa jayega."),
    (5, "Interview toh theek gaya, ab result ka wait hai, thoda anxious hoon."),
    (4, "Koi response nahi aaya abhi tak unka, tension badhta ja raha hai."),
    (3, "Aaj gym bhi nahi gaya, sab kuch overwhelming lag raha hai."),
    (2, "Unhone reject kar diya, bahut down feel ho raha hoon."),
    (1, "Chalo kal se fresh start karte hain, naya plan banate hain."),
    (0, "Aaj 5km run complete kiya, bahut achha laga!"),
]


def run_test():
    print("[1/2] Logging simulated week...")
    for days_ago, message in SIMULATED_WEEK:
        ts = (now - timedelta(days=days_ago)).isoformat()
        result = detect_and_log_mood(message, timestamp=ts)
        print(f"    Day -{days_ago}: '{message}' -> {result['emotion']} ({result['intensity']})")

    print("\n[2/2] Retrieving 7-day trend:")
    trend = get_mood_trend(days=7)
    print(f"    Total entries in window: {len(trend)}")

    counts = Counter(e["emotion"] for e in trend)
    print(f"    Emotion breakdown: {dict(counts)}")

    print("\nManually review: kya yeh breakdown asli hafte ki story batata hai —")
    print("shuru mein fear/anxiety, beech mein sadness, end mein recovery/joy?")


if __name__ == "__main__":
    run_test()