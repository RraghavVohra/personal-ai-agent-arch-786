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

# Humara apna app-level state ke liye SQLite db — Mem0 ke history db se
# jaan-boojh kar alag (jo upar already separate rakha hai). Confidence/
# Decay/Superseded jaisi custom layers isi file mein apni tables
# banayengi, taaki Mem0 ke internal storage ko kabhi touch na karna pade
APP_DB_PATH = STORAGE_DIR / "agent_state.db"

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

# Drift-judge ke liye alag, stronger model — Billie ki generation aur
# classifier.py dono gpt-4o-mini pe rehte hain (sasta, high-frequency
# calls), lekin judge ki reasoning mein 3 baar input-misrepresentation
# dekha gaya hai (Turn 12, Turn 19). Judge calls kam-frequency (periodic)
# hain, toh stronger model yahan cost-effective hai
DRIFT_JUDGE_MODEL = "gpt-4o"

# Gate 2 (distress-tiering) ke liye alag constant - DRIFT_JUDGE_MODEL se
# jaan-boojh kar alag rakha hai, taaki dono independently tune ho sakein.
# Stakes drift-judge se bhi zyada hai yahan, isliye stronger model.
SAFETY_JUDGE_MODEL = "gpt-4o"

# --- Decay ---
# Ebbinghaus forgetting-curve stability constant — kitne hours mein
# confidence apne 1/e (~37%) tak gir jaata hai agar memory reinforce na
# ho. 720 hours = 30 din. MVP ke liye single global rate hai — baad mein
# fact-type ke hisaab se alag rates ban sakte hain (jaise "naam" slow
# decay, "current job" fast decay), lekin abhi simplicity ke liye ek hi
DECAY_STABILITY_HOURS = 720

# --- Persona ---
# Letta/MemGPT ke persona-block pattern se — persona ka text hamesha
# context mein rahega har LLM call mein, isliye character-capped rakhna
# zaroori hai warna token cost badhta jaayega
PERSONA_CHAR_LIMIT = 2000

# --- Contradiction Resolution ---
# Vector-similarity score jisse upar wale candidates hi classifier.py
# ko LLM-classify karne ke liye bheje jaate hain. Humare khud ke real
# test mein genuine contradiction (QA engineer -> SDET) ka score 0.4557
# tha — isse thoda neeche rakha hai starting gate ke taur pe. Zyada
# real data aane ke baad tune karna aasan hoga, kyunki yeh ek hi jagah
# define hai
CONTRADICTION_SIMILARITY_THRESHOLD = 0.35

# --- Generation ---
# Classifiers/judges 0.1 pe hain (consistency chahiye). Conversational
# reply ke liye zyada rakha hai - Billie ko har baar bilkul same-words
# mein nahi bolna chahiye, thoda natural-variation chahiye
GENERATION_TEMPERATURE = 0.8

# --- User ---
# Single-user personal agent hai - ek hi real production user_id.
# Test-files apna alag test-specific user_id use karenge (jaise Step 2
# mein), taaki testing se asli Billie-memory kabhi pollute na ho
USER_ID = "raghav"


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