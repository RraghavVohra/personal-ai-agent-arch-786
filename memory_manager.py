"""
memory_manager.py

Story: Yeh file teeno proven pieces (memory_meta schema, decay.py,
classifier.py) ko Mem0 ke actual add() ke saath wire karta hai. Jab
bhi naya fact add hota hai, yeh pipeline decide karta hai ki woh
independent NEW hai, ya kisi existing fact ko CONFIRM/CONTRADICT karta
hai, aur uske hisaab se memory_meta table update karta hai.

Dono CONFIRMS aur CONTRADICTS mein sirf "superseded" mark hota hai,
delete kabhi nahi — Zep/Graphiti pattern, poori history audit ke liye
preserve rehti hai.

Search-side (search_memory_with_decay) is memory ko live-decay ke
saath retrieve karta hai — superseded facts hide, confidence
recalculate, aur retrieval khud ek chhota reinforcement deta hai.
"""

import sqlite3
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from config import MEM0_CONFIG, APP_DB_PATH, CONTRADICTION_SIMILARITY_THRESHOLD
from classifier import classify_relationship, Relationship
from decay import calculate_decayed_confidence
from mem0 import Memory

memory = Memory.from_config(MEM0_CONFIG)


def _get_connection():
    return sqlite3.connect(APP_DB_PATH)


def _insert_meta_row(conn, memory_id, confidence=1.0, status="active"):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT OR REPLACE INTO memory_meta
            (memory_id, confidence, created_at, last_reinforced_at, status, superseded_by, superseded_at)
        VALUES (?, ?, ?, ?, ?, NULL, NULL)
        """,
        (memory_id, confidence, now, now, status),
    )


def _mark_superseded(conn, memory_id, superseded_by):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        UPDATE memory_meta
        SET status = 'superseded', superseded_by = ?, superseded_at = ?
        WHERE memory_id = ?
        """,
        (superseded_by, now, memory_id),
    )


def _reinforce(conn, memory_id):
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE memory_meta SET confidence = 1.0, last_reinforced_at = ? WHERE memory_id = ?",
        (now, memory_id),
    )


def _update_confidence(conn, memory_id, confidence, now):
    conn.execute(
        "UPDATE memory_meta SET confidence = ?, last_reinforced_at = ? WHERE memory_id = ?",
        (confidence, now.isoformat(), memory_id),
    )


def _is_active(conn, memory_id):
    row = conn.execute(
        "SELECT status FROM memory_meta WHERE memory_id = ?", (memory_id,)
    ).fetchone()
    # Row missing = humari tracking se pehle ka fact ya crash se orphan
    # hua — dono cases mein Mem0 mein woh abhi bhi valid hai, isliye
    # "unknown" ko silently skip karne ke bajaye active maano
    if row is None:
        return True
    return row[0] == "active"


def add_memory_with_resolution(text, user_id):
    """
    Naya fact add karta hai aur contradiction/confirmation resolve
    karta hai. Returns: list of {"memory_id", "text", "resolution",
    "acted_on_id"} — har naye Mem0-added fact ke liye ek entry.
    """
    add_result = memory.add(text, user_id=user_id)
    new_facts = add_result.get("results", [])

    conn = _get_connection()
    outcomes = []

    try:
        for fact in new_facts:
            new_id = fact["id"]
            new_text = fact["memory"]

            # Default assume: yeh naya fact independent hai
            _insert_meta_row(conn, new_id, confidence=1.0, status="active")

            resolution = "NEW"
            acted_on_id = None

            # Mem0 ka apna embedding pipeline reuse — apna similarity
            # code dobara nahi likha
            search_result = memory.search(new_text, filters={"user_id": user_id}, limit=5)

            for candidate in search_result.get("results", []):
                cand_id = candidate["id"]
                cand_score = candidate.get("score", 0)

                if cand_id == new_id:
                    continue
                if cand_score < CONTRADICTION_SIMILARITY_THRESHOLD:
                    continue
                if not _is_active(conn, cand_id):
                    continue

                # Threshold cross hua — ab hi LLM classifier chalega
                classification = classify_relationship(candidate["memory"], new_text)

                if classification.relationship == Relationship.CONFIRMS:
                    _mark_superseded(conn, new_id, superseded_by=cand_id)
                    _reinforce(conn, cand_id)
                    resolution, acted_on_id = "CONFIRMS", cand_id
                    break

                elif classification.relationship == Relationship.CONTRADICTS:
                    _mark_superseded(conn, cand_id, superseded_by=new_id)
                    resolution, acted_on_id = "CONTRADICTS", cand_id
                    break
                # UNRELATED -> kuch mat karo, agla candidate check karo

            # Har fact process hone ke TURANT baad commit — pehle yeh
            # sirf poore loop ke end mein hota tha, isliye jab search()
            # crash hua tha pichli baar, is se pehle wale fact ka
            # memory_meta insert bhi rollback ho gaya tha (orphan ban
            # gaya). Ab har fact apna commit khud carry karta hai, ek
            # baad wale fact ka crash pehle wale ko touch nahi karega
            conn.commit()

            outcomes.append({
                "memory_id": new_id,
                "text": new_text,
                "resolution": resolution,
                "acted_on_id": acted_on_id,
            })
    finally:
        conn.close()

    return outcomes


def search_memory_with_decay(query, user_id, limit=5, include_superseded=False):
    """
    Mem0 se raw semantic search karta hai, phir memory_meta se join karke:
    - superseded facts hata deta hai (jab tak include_superseded=True na ho)
    - live decayed confidence calculate karta hai
    - retrieval ka reinforcement boost apply karta hai (+0.05, cap 0.95)
    Results confidence ke hisaab se sorted (highest pehle) return hote hain.
    """
    raw_results = memory.search(query, filters={"user_id": user_id}, limit=limit)
    now = datetime.now(timezone.utc)

    conn = _get_connection()
    results = []

    try:
        for item in raw_results.get("results", []):
            mem_id = item["id"]
            row = conn.execute(
                "SELECT confidence, last_reinforced_at, status FROM memory_meta WHERE memory_id = ?",
                (mem_id,),
            ).fetchone()

            if row is None:
                # Untracked — humari layer se pehle ka fact ya orphan.
                # Fresh baseline maan lo, active treat karo (same principle
                # jo _is_active() mein use kiya tha)
                status = "active"
                live_confidence = 1.0
            else:
                stored_confidence, last_reinforced_str, status = row
                if status == "superseded" and not include_superseded:
                    continue
                last_reinforced_at = datetime.fromisoformat(last_reinforced_str)
                live_confidence = calculate_decayed_confidence(
                    stored_confidence, last_reinforced_at, now=now
                )

            # Reinforcement: retrieval se chhota boost, decay-clock naye
            # boosted level se restart
            boosted_confidence = min(0.95, live_confidence + 0.05)

            if row is None:
                _insert_meta_row(conn, mem_id, confidence=boosted_confidence, status="active")
            else:
                _update_confidence(conn, mem_id, boosted_confidence, now)

            results.append({
                "memory_id": mem_id,
                "text": item["memory"],
                "score": item.get("score"),
                "confidence": round(boosted_confidence, 4),
                "status": status,
            })

        conn.commit()
    finally:
        conn.close()

    results.sort(key=lambda r: r["confidence"], reverse=True)
    return results