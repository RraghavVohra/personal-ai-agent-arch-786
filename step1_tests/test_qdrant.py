"""
Step 1 - Piece 2: Qdrant plumbing test (local mode, no Docker).

Story: QdrantClient ko ek disk path dete hain — koi server nahi
chal raha. Ek dummy vector daal ke, similarity search se wapas
nikaal ke dikhate hain.

IMPORTANT dhyan rakhne wali baat: local mode ek waqt mein sirf
EK process se access ho sakta hai (file lock ki wajah se). Agar
yeh script khula chhod diya aur dusra script isi path pe chalane
ki koshish ki, "storage folder already accessed" wala error
aayega. client.close() isliye zaroori hai.
"""

from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

QDRANT_PATH = Path(__file__).parent.parent / "storage" / "qdrant_data"
COLLECTION_NAME = "plumbing_test"
VECTOR_SIZE = 1536  # text-embedding-3-small ka output size


def run_test():
    client = QdrantClient(path=str(QDRANT_PATH))

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

    dummy_vector = [0.001] * VECTOR_SIZE
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=1, vector=dummy_vector, payload={"text": "plumbing_test_ok"})],
    )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=dummy_vector,
        limit=1,
    ).points

    assert len(results) == 1, "Qdrant se point wapas nahi mila."
    print(f"[Qdrant OK] id={results[0].id}, payload={results[0].payload}")
    print(f"Storage: {QDRANT_PATH}")

    client.close()


if __name__ == "__main__":
    run_test()