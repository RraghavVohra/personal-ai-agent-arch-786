"""
Step 2 - Piece 1: Mem0 basic plumbing test (standalone).

Story: Yeh Mem0 ka apna add()/search() pehli baar real tareeke se
chalana hai — humare config.py wale settings ke saath (gpt-5-mini
extraction ke liye, text-embedding-3-small embedding ke liye,
Qdrant local-mode humari apni storage folder mein).

Abhi tak koi custom confidence/decay layer nahi hai — sirf Mem0
jo khud-ba-khud karta hai, wahi dekhna hai.
"""

import sys
from dotenv import load_dotenv
from pathlib import Path

# config.py project root mein hai, yeh script step2_tests ke andar.
# Seedha "from config import ..." isliye fail karega kyunki Python
# sirf isi folder (step2_tests) ko dekhta hai jab file directly
# chalayi jaati hai — root ko manually path mein add karna padta hai
sys.path.insert(0, str(Path(__file__).parent.parent))

from mem0 import Memory
from config import MEM0_CONFIG
# .env file se OPENAI_API_KEY environment mein load karta hai
load_dotenv()

# from_config isliye use kiya, Memory() nahi — taaki humara apna
# collection name, path, aur explicit models use hon, kisi
# ambiguous default pe nahi (Mem0 ke apne docs mein hi defaults
# ko lekar confusion hai — humne pehle discuss kiya tha)
memory = Memory.from_config(MEM0_CONFIG)

USER_ID = "raghav_test"


def run_test():
    conversation = [
        {"role": "user", "content": "I am a QA engineer and I love running on weekends."},
        {"role": "assistant", "content": "Got it, noted!"},
    ]

    add_result = memory.add(conversation, user_id=USER_ID)
    print("[1/3] Added conversation to memory:")
    print(add_result)

    # Naye mem0ai version mein search() ab user_id ko top-level
    # argument ki tarah accept nahi karta — filters dict mein
    # dena padta hai (add() mein abhi bhi purana tareeka chalta hai)
    search_result = memory.search("What does the user do for work?", filters={"user_id": USER_ID})
    print("\n[2/3] Search result:")
    print(search_result)

    # Ab ek CONTRADICTING fact daal rahe hain — dekhna hai Mem0
    # purane fact ko update/delete karta hai, ya dono ko side-by-side
    # rakh deta hai (jo humari research ke hisaab se hona chahiye)
    contradiction = [
        {"role": "user", "content": "Actually, I recently switched from QA to being a full-time SDET."},
        {"role": "assistant", "content": "Congrats on the switch!"},
    ]
    contradiction_result = memory.add(contradiction, user_id=USER_ID)
    print("\n[3/3] Added contradicting fact:")
    print(contradiction_result)

    all_memories = memory.get_all(filters={"user_id": USER_ID})
    print("\n[Check] All memories for this user now:")
    for m in all_memories["results"]:
        print(f"  - {m['memory']}")


if __name__ == "__main__":
    run_test()