"""
mood_log.py

Story: mood_detector.py sirf ek single message ka mood detect karta
hai — yeh module us detection ko TIME ke saath store karta hai, taaki
Billie trends dekh sake, sirf ek isolated snapshot nahi.

Design choice: Step 2 ka Confidence/Decay yahan reuse NAHI kiya —
mood ek time-series event hai (fact nahi), poori history chahiye
trend dekhne ke liye, kisi ek decayed number mein summarize nahi
karna. Same DB file (APP_DB_PATH) reuse kiya hai, proven plumbing.
"""

import sqlite3
from datetime import datetime, timezone, timedelta
from config import APP_DB_PATH

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS mood_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT NOT NULL,
    emotion         TEXT NOT NULL,
    intensity       REAL NOT NULL,
    source_message  TEXT
);
"""


def _get_connection():
    conn = sqlite3.connect(APP_DB_PATH)
    conn.execute(CREATE_TABLE_SQL)
    return conn


def log_mood(emotion: str, intensity: float, source_message: str, timestamp: str = None) -> int:
    """
    timestamp: optional override — testing ke liye (decay.py mein bhi
    yehi pattern tha), taaki purani entries simulate ho sakein bina
    actually wait kiye.
    """
    conn = _get_connection()
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        "INSERT INTO mood_log (timestamp, emotion, intensity, source_message) VALUES (?, ?, ?, ?)",
        (ts, emotion, intensity, source_message),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_mood_trend(days: int = 7) -> list[dict]:
    """
    Pichle N din ke saare entries, newest pehle. Raw data deta hai —
    pattern-summarization (jaise "3 baar anxious") Orchestrator ka
    kaam hoga, yeh module sirf data provide karta hai.
    """
    conn = _get_connection()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT timestamp, emotion, intensity, source_message FROM mood_log WHERE timestamp >= ? ORDER BY timestamp DESC",
        (cutoff,),
    ).fetchall()
    conn.close()

    return [
        {"timestamp": r[0], "emotion": r[1], "intensity": r[2], "source_message": r[3]}
        for r in rows
    ]