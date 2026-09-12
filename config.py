"""
config.py - Central configuration for the personal AI agent.

Story: Har jagah collection ka naam, model names, paths hardcode
karne ke bajaye, sab yahan ek jagah define karte hain. Kal agar
kuch badalna pade, sirf yahan badlega, har file mein nahi dhundhna
padega.
"""

from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"

QDRANT_PATH = STORAGE_DIR / "qdrant_data"

# Mem0 ka apna audit-log — humare Step 1 wale test_history.db se
# ALAG rakha hai jaan-boojh kar, taaki dummy test data aur real
# Mem0 history kabhi mix na ho
MEM0_HISTORY_DB_PATH = STORAGE_DIR / "mem0_history.db"

# --- Vector store ---
# Naya collection name isliye diya — Step 1 ke "plumbing_test"
# collection mein humara dummy data pada hai jiska payload shape
# alag hai. Mem0 apna khud ka schema banata hai, dono ko kabhi
# mix nahi karna
MEM0_COLLECTION_NAME = "agent_memory"
EMBEDDING_DIMS = 1536  # text-embedding-3-small ka fixed output size

# --- Models ---
# Dono explicitly likhe hain — Mem0 ke apne docs mein hi defaults
# ko lekar confusion hai (alag-alag jagah alag model bataya gaya
# hai), isliye kabhi default pe bharosa nahi karna, hamesha yahan
# explicitly define karna
LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# --- Mem0 ka config dict ---
# Yeh exact structure hai jo Memory.from_config() expect karta hai
MEM0_CONFIG = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": MEM0_COLLECTION_NAME,
            "path": str(QDRANT_PATH),
            "embedding_model_dims": EMBEDDING_DIMS,
        },
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": LLM_MODEL,
            # gpt-4o-mini (non-reasoning family) hai — temperature
            # jaise sab standard sampling params support karta hai,
            # isliye yahan override ki zaroorat nahi. Mem0 ka apna
            # internal default (0.1) consistent extraction ke liye
            # theek hai
            
        },
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": EMBEDDING_MODEL,
        },
    },
    "history_db_path": str(MEM0_HISTORY_DB_PATH),
}