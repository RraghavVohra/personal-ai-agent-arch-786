"""
test_chat_loop.py

Purpose: Loop crash na kare, greet + exit sahi chalein - mocked input
se. Yeh REAL-CONVERSATION-FEEL test nahi hai (woh manually chalana
hai) - sirf mechanics verify karta hai.
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chat_loop import run_chat_loop


def run_test():
    scripted_inputs = ["Hi Billie", "exit"]
    with patch("builtins.input", side_effect=scripted_inputs):
        run_chat_loop(user_id="chat_loop_test_user")
    print("\n[Mechanical test] Loop crash nahi hua, greet + exit chale - PASS")


if __name__ == "__main__":
    run_test()