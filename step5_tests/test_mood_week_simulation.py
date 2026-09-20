"""
test_mood_week_simulation.py

Purpose: End-to-end validation — ek simulated hafte ke messages
detect+log karta hai, phir trend retrieve karke readable summary
banata hai. Poora loop (detect -> store -> retrieve -> summarize)
test karta hai.

Self-cleaning: yeh galti teen baar ho chuki hai (Mem0/Step 2, mood_log
do baar) — script purana data APPEND karta tha, "yaad rakhna clear
karna" insaan pe depend karta tha. Ab script khud shuru mein apna
purana data clear karke chalta hai.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collections import Counter
from datetime import datetime, timezone, timedelta
from mood_manager import detect_and_log_mood
from mood_log import get_mood_trend, clear_mood_log

now = datetime.now(timezone.utc)

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
    # NOTE (revisit before real usage): blanket-wipe abhi safe hai,
    # koi real conversation-data nahi hai. Real usage shuru hone pe
    # scoped/tagged cleanup mein badalna hoga.
    deleted = clear_mood_log()
    print(f"[0/2] Cleared {deleted} old entries before running simulation.\n")

    print("[1/2] Logging simulated week...")
    for days_ago, message in SIMULATED_WEEK:
        ts = (now - timedelta(days=days_ago)).isoformat()
        result = detect_and_log_mood(message, timestamp=ts)
        print(f"    Day -{days_ago}: '{message}' -> {result['emotion']} ({result['intensity']}) | topic: {result['topic']}")

    print("\n[2/2] Retrieving 7-day trend:")
    trend = get_mood_trend(days=7)
    print(f"    Total entries in window: {len(trend)}")
    print("    Topics captured:")
    for e in trend:
        print(f"      {e['emotion']} — {e['topic']}")

    counts = Counter(e["emotion"] for e in trend)
    print(f"    Emotion breakdown: {dict(counts)}")

    print("\nManually review: kya job_search wali teeno entries (interview,")
    print("wait, rejection) ab EK hi topic ke taur pe group ho rahi hain?")


if __name__ == "__main__":
    run_test()