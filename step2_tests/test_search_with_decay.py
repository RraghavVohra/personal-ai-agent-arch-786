"""
test_search_with_decay.py

Purpose: search_memory_with_decay() test karta hai — superseded facts
default se hidden hone chahiye, confidence/reinforcement kaam karna
chahiye, aur include_superseded=True se poori history dikhni chahiye.

Pichli integration-test wala user_id reuse kiya hai (QA-engineer
superseded -> DevOps engineer active).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from memory_manager import search_memory_with_decay

USER_ID = "integration_test_user_v2"


def run_test():
    print("[1/2] Default search (superseded hidden):")
    results = search_memory_with_decay("What is the user's job?", user_id=USER_ID)
    for r in results:
        print(f"    {r}")
    qa_leaked = any(r["status"] == "superseded" for r in results)
    print("    PASS" if not qa_leaked else "    FAIL (superseded QA fact leaked through)")

    print("\n[2/2] With include_superseded=True (full history):")
    results_with_history = search_memory_with_decay(
        "What is the user's job?", user_id=USER_ID, include_superseded=True
    )
    for r in results_with_history:
        print(f"    {r}")
    has_superseded = any(r["status"] == "superseded" for r in results_with_history)
    print("    PASS" if has_superseded else "    FAIL (expected superseded history to appear)")


if __name__ == "__main__":
    run_test()