"""
mood_log.py

Story: mood_detector.py ke result ko TIME ke saath store karta hai,
taaki Billie trends dekh sake, sirf ek isolated snapshot nahi.

Design choice: Step 2 ka Confidence/Decay yahan reuse NAHI kiya — mood
ek time-series event hai (fact nahi), poori history chahiye trend ke
liye, kisi ek decayed number mein summarize nahi karna. Same DB file
(APP_DB_PATH) reuse kiya hai, proven plumbing.

topic column: production mood-tracking apps ka standard practice hai
(work/sleep/family jaise tags) — warna trend sirf "kitni baar" batata
hai, "kis wajah se" nahi bata sakta.
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
    topic           TEXT,
    source_message  TEXT
);
"""


def _get_connection():
    conn = sqlite3.connect(APP_DB_PATH)
    conn.execute(CREATE_TABLE_SQL)
    # Migration guard: agar table PEHLE se (topic-column se pehle) ban
    # chuki thi, CREATE TABLE IF NOT EXISTS usse skip kar dega — yeh
    # try/except purane DB pe bhi safely naya column add karta hai,
    # bina data loss ke
    try:
        conn.execute("ALTER TABLE mood_log ADD COLUMN topic TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # column already exists — normal case
    return conn


def log_mood(emotion: str, intensity: float, source_message: str, topic: str = None, timestamp: str = None) -> int:
    """
    timestamp: optional override — testing ke liye, taaki purani
    entries simulate ho sakein bina actually wait kiye.
    """
    conn = _get_connection()
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        "INSERT INTO mood_log (timestamp, emotion, intensity, topic, source_message) VALUES (?, ?, ?, ?, ?)",
        (ts, emotion, intensity, topic, source_message),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_mood_trend(days: int = 7) -> list[dict]:
    """
    Pichle N din ke saare entries, newest pehle. Raw data deta hai —
    pattern-summarization Orchestrator ka kaam hoga.
    """
    conn = _get_connection()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT timestamp, emotion, intensity, topic, source_message FROM mood_log WHERE timestamp >= ? ORDER BY timestamp DESC",
        (cutoff,),
    ).fetchall()
    conn.close()

    return [
        {"timestamp": r[0], "emotion": r[1], "intensity": r[2], "topic": r[3], "source_message": r[4]}
        for r in rows
    ]


def clear_mood_log(tag: str = None) -> int:
    """
    Test-data cleanup ke liye. tag diya toh sirf usse-matching entries
    delete hoti hain, warna poori table clear hoti hai.

    NOTE (revisit before real usage): abhi blanket-wipe safe hai,
    kyunki koi real conversation-data nahi hai. Jab Billie real
    conversations se mood collect karna shuru karegi, isse tagged/
    scoped cleanup mein badalna hoga.
    """
    conn = _get_connection()
    if tag:
        cursor = conn.execute("DELETE FROM mood_log WHERE source_message LIKE ?", (f"%{tag}%",))
    else:
        cursor = conn.execute("DELETE FROM mood_log")
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted