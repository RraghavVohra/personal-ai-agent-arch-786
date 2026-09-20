"""
test_disclosure.py

Purpose: Isolated structure test - disclosure message khaali nahi hai,
aur clear "AI"-disclosure keyword contain karta hai. Koi LLM call nahi.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from disclosure import get_disclosure_message


def run_test():
    message = get_disclosure_message()

    assert isinstance(message, str) and len(message) > 0, "Message khaali ya string nahi hai."
    print(f"[1/2] Message generate hua, length: {len(message)} chars.")

    assert "AI" in message, "Disclosure keyword 'AI' message mein nahi mila."
    print("[2/2] Disclosure keyword present hai.")

    print("\nAll disclosure structure tests passed.")
    print("\n--- Message ---")
    print(message)


if __name__ == "__main__":
    run_test()