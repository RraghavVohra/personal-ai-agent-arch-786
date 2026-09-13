"""
test_memory_manager_integration.py

Purpose: End-to-end test — real Mem0 add() + resolution pipeline
(memory_manager.py) saath mein. Alag user_id use kiya hai taaki
raw test_mem0_basic.py wale data se collide na kare.

Teen scenarios: (1) pehla fact -> NEW, (2) contradicting fact ->
purana superseded, (3) confirming fact -> naya khud superseded, purana
reinforce.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import sqlite3
from memory_manager import add_memory_with_resolution
from config import APP_DB_PATH

USER_ID = "integration_test_user_v2"


def get_status(memory_id):
    conn = sqlite3.connect(APP_DB_PATH)
    row = conn.execute(
        "SELECT status, superseded_by, confidence FROM memory_meta WHERE memory_id = ?",
        (memory_id,),
    ).fetchone()
    conn.close()
    return row


def run_test():
    result_1 = add_memory_with_resolution("I am a QA engineer.", user_id=USER_ID)
    print("[1/3] First add:")
    for r in result_1:
        print(f"    {r}")
    qa_fact_id = result_1[0]["memory_id"] if result_1 else None

    result_2 = add_memory_with_resolution(
        "I recently switched from QA engineer to being a DevOps engineer.", user_id=USER_ID
    )
    print("\n[2/3] Contradicting add:")
    for r in result_2:
        print(f"    {r}")

    if qa_fact_id:
        status = get_status(qa_fact_id)
        print(f"    Old QA-engineer fact status: {status}")
        print("    PASS" if status and status[0] == "superseded" else "    FAIL")

    devops_fact_id = next((r["memory_id"] for r in result_2 if r["resolution"] == "CONTRADICTS"), None)

    result_3 = add_memory_with_resolution("I am still working as a DevOps engineer.", user_id=USER_ID)
    print("\n[3/3] Confirming add:")
    for r in result_3:
        print(f"    {r}")

    if devops_fact_id:
        status = get_status(devops_fact_id)
        print(f"    DevOps fact status after confirmation: {status}")
        print("    PASS" if status and status[0] == "active" and status[2] == 1.0 else "    FAIL")


if __name__ == "__main__":
    run_test()