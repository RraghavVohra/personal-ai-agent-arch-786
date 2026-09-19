"""
test_mood_log.py

Purpose: Isolated test — mood_log.py ka schema, insert, aur trend-
retrieval. Koi LLM call nahi. Ek "purani" entry (8 din, 7-day window
se BAHAR) deliberately daali hai, taaki verify ho ki get_mood_trend()
sahi se filter karta hai, sab kuch return nahi kar deta.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timezone, timedelta
from mood_log import log_mood, get_mood_trend

TEST_TAG = "TEST-mood-log-check"


def run_test():
    now = datetime.now(timezone.utc)

    log_mood("joy", 0.8, f"{TEST_TAG}: got the offer!", timestamp=now.isoformat())
    log_mood("fear", 0.5, f"{TEST_TAG}: waiting on interview result", timestamp=(now - timedelta(days=2)).isoformat())

    old_timestamp = (now - timedelta(days=8)).isoformat()
    log_mood("sadness", 0.6, f"{TEST_TAG}: old entry, should be filtered out", timestamp=old_timestamp)

    print("[1/2] 3 entries logged (2 recent, 1 old-outside-window).")

    trend = get_mood_trend(days=7)
    tagged_entries = [e for e in trend if TEST_TAG in e["source_message"]]

    print(f"[2/2] get_mood_trend(days=7) returned {len(tagged_entries)} tagged entries (expected: 2).")
    for e in tagged_entries:
        print(f"    {e}")

    old_entry_leaked = any("old entry" in e["source_message"] for e in tagged_entries)
    print("\nPASS" if len(tagged_entries) == 2 and not old_entry_leaked else "FAIL")


if __name__ == "__main__":
    run_test()