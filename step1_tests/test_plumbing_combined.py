"""
Step 1 - Combined plumbing test.

Story: Real sentence -> OpenAI embed -> Qdrant insert -> Qdrant
retrieve -> SQLite audit-style log. Agar yeh 4 lines print hokar
"Step 1 done" tak pahunch jaaye, matlab foundation ready hai.
"""

import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from tenacity import retry, wait_random_exponential, stop_after_attempt

load_dotenv()

BASE_DIR = Path(__file__).parent.parent / "storage"
DB_PATH = BASE_DIR / "test_history.db"
QDRANT_PATH = BASE_DIR / "qdrant_data"
COLLECTION_NAME = "plumbing_test"
VECTOR_SIZE = 1536

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def embed(text: str) -> list[float]:
    return openai_client.embeddings.create(input=text, model="text-embedding-3-small").data[0].embedding


def log_to_sqlite(event: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dummy_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("INSERT INTO dummy_log (event) VALUES (?)", (event,))
    conn.commit()
    conn.close()


def run_test():
    sentence = "I like running on weekends near Shalimar Bagh."

    vector = embed(sentence)
    print(f"[1/4] Embedded into {len(vector)}-dim vector")

    qdrant = QdrantClient(path=str(QDRANT_PATH))
    if not qdrant.collection_exists(COLLECTION_NAME):
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=1, vector=vector, payload={"text": sentence})],
    )
    print("[2/4] Inserted into Qdrant")

    results = qdrant.query_points(collection_name=COLLECTION_NAME, query=vector, limit=1).points
    assert results[0].payload["text"] == sentence
    print(f"[3/4] Retrieved: '{results[0].payload['text']}' (score={results[0].score:.4f})")
    qdrant.close()

    log_to_sqlite("full_plumbing_test_passed")
    print("[4/4] Logged to SQLite")

    print("\nStep 1 done bhai — teeno pieces ek saath kaam kar rahe hain.")


if __name__ == "__main__":
    run_test()