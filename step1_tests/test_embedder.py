"""
Step 1 - Piece 3: OpenAI embedder plumbing test.

Story: Sirf itna prove karna hai — API key kaam kar raha hai,
aur text-embedding-3-small model expected 1536-dim vector deta
hai (jis size ka Qdrant collection bana hai).
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

load_dotenv()
EXPECTED_DIMS = 1536
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding


def run_test():
    vector = get_embedding("plumbing test sentence")
    assert len(vector) == EXPECTED_DIMS, f"Expected {EXPECTED_DIMS} dims, got {len(vector)}."
    print(f"[Embedder OK] {len(vector)}-dim vector. First 5: {vector[:5]}")


if __name__ == "__main__":
    run_test()