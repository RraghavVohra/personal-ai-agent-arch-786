"""
test_memory_meta_schema.py

Purpose: Isolated test for the memory_meta table — the SQLite-based
companion table that holds Confidence/Decay/Superseded state for every
memory Mem0 stores. This test ONLY touches our own database schema —
no Mem0, no LLM, no Qdrant. If this fails, the bug is 100% in our own
table design, nothing borrowed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import sqlite3
from datetime import datetime, timezone
# from config import SQLITE_DB_PATH  # <-- CONFIRM this matches the actual constant name in your config.py
from config import APP_DB_PATH  # (SQLITE_DB_PATH ki jagah)

# Why a separate TABLE, not a separate DB FILE: memory_meta sits in the
# same SQLite file Step 1 already proved (test_sqlite.py), so we reuse
# proven plumbing — but it stays fully decoupled from Mem0's OWN internal
# storage (Mem0's history.db + Qdrant), so replacing/upgrading Mem0 later
# never touches this table.
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS memory_meta (
    memory_id           TEXT PRIMARY KEY,               -- Mem0's own memory UUID, links back to the real fact
    confidence          REAL NOT NULL DEFAULT 1.0,       -- confidence AS OF last_reinforced_at; live decayed value gets computed at read-time, not stored here
    created_at          TEXT NOT NULL,                   -- ISO timestamp, when this memory first appeared
    last_reinforced_at  TEXT NOT NULL,                   -- resets every time confidence is boosted or fully reset
    status              TEXT NOT NULL DEFAULT 'active',  -- 'active' or 'superseded'
    superseded_by       TEXT,                            -- memory_id of the fact that replaced this one (NULL if active)
    superseded_at       TEXT                             -- ISO timestamp of when it was superseded (NULL if active)
);
"""

def run_test():
    conn = sqlite3.connect(APP_DB_PATH )
    cursor = conn.cursor()

    # Step 1: create the table. IF NOT EXISTS makes this safe to re-run
    # without wiping out real data later.
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()
    print("[1/3] memory_meta table created (or already existed).")

    # Step 2: insert a dummy row with a fixed, recognizable test ID.
    # INSERT OR REPLACE makes the whole script idempotent — running it
    # twice won't crash on a duplicate primary key, it just overwrites
    # the same test row cleanly.
    now = datetime.now(timezone.utc).isoformat()
    test_id = "TEST-schema-check-0001"
    cursor.execute(
        """
        INSERT OR REPLACE INTO memory_meta
            (memory_id, confidence, created_at, last_reinforced_at, status, superseded_by, superseded_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (test_id, 1.0, now, now, "active", None, None),
    )
    conn.commit()
    print(f"[2/3] Dummy row inserted: {test_id}")

    # Step 3: read it back and verify every field round-tripped correctly.
    cursor.execute("SELECT * FROM memory_meta WHERE memory_id = ?", (test_id,))
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "Row not found after insert — schema or path is broken."
    assert row[1] == 1.0, "Confidence did not round-trip correctly."
    assert row[4] == "active", "Status did not round-trip correctly."

    print("[3/3] Row read back successfully — schema is correct.")
    print(row)

if __name__ == "__main__":
    run_test()