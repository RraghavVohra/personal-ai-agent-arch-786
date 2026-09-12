"""
Step 1 - Piece 1: SQLite plumbing test.

Story: Hum sirf yeh prove kar rahe hain ki is machine par ek
SQLite file ban sakti hai, likhi ja sakti hai, aur wapas padhi
ja sakti hai. Yeh Mem0 ka apna history.db NAHI hai — woh Step 2
mein Mem0 khud banayega, apni jagah, apne schema ke saath. Yeh
sirf ek isolated sanity check hai.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "storage" / "test_history.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def run_test():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dummy_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("INSERT INTO dummy_log (event) VALUES (?)", ("plumbing_test_ok",))
    conn.commit()

    cursor.execute("SELECT id, event, created_at FROM dummy_log ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "SQLite se record wapas nahi mila."
    print(f"[SQLite OK] id={row[0]}, event={row[1]}, at={row[2]}")
    print(f"DB file: {DB_PATH}")


if __name__ == "__main__":
    run_test()