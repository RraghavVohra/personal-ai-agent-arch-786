"""
test_decay_formula.py

Purpose: Isolated test for the Ebbinghaus decay formula in decay.py.
Pure math only — no DB, no LLM, no Mem0. `now` har call mein explicitly
pass kiya jaata hai, taaki time-beetna simulate ho bina actually wait
kiye.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import math
from datetime import datetime, timedelta, timezone
from decay import calculate_decayed_confidence
from config import DECAY_STABILITY_HOURS


def run_test():
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    # [1/4] Zero time elapsed — confidence unchanged honi chahiye (e^0 = 1)
    result_1 = calculate_decayed_confidence(1.0, base_time, now=base_time)
    assert math.isclose(result_1, 1.0, rel_tol=1e-9), f"Expected 1.0, got {result_1}"
    print(f"[1/4] t=0 -> confidence={result_1:.4f} (expected 1.0000)")

    # [2/4] Exactly ek stability period beeta — ~1/e (~0.3679) tak decay hona chahiye
    now_2 = base_time + timedelta(hours=DECAY_STABILITY_HOURS)
    result_2 = calculate_decayed_confidence(1.0, base_time, now=now_2)
    assert math.isclose(result_2, 1 / math.e, rel_tol=1e-6), f"Expected ~0.3679, got {result_2}"
    print(f"[2/4] t=1 stability period -> confidence={result_2:.4f} (expected ~0.3679)")

    # [3/4] Das stability periods beete — near-zero hona chahiye
    now_3 = base_time + timedelta(hours=DECAY_STABILITY_HOURS * 10)
    result_3 = calculate_decayed_confidence(1.0, base_time, now=now_3)
    assert result_3 < 0.01, f"Expected near-zero, got {result_3}"
    print(f"[3/4] t=10 stability periods -> confidence={result_3:.6f} (expected < 0.01)")

    # [4/4] Non-1.0 base confidence (jaise partial retrieval-boost ke baad)
    # proportionally scale hona chahiye, hamesha 1.0 se shuru nahi
    result_4 = calculate_decayed_confidence(0.5, base_time, now=base_time)
    assert math.isclose(result_4, 0.5, rel_tol=1e-9), f"Expected 0.5, got {result_4}"
    print(f"[4/4] base=0.5, t=0 -> confidence={result_4:.4f} (expected 0.5000)")

    print("\nAll decay formula tests passed.")


if __name__ == "__main__":
    run_test()