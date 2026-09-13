# Architecture Decisions Log

Yeh document project ke saare architectural decisions aur unke "why" track karta hai. Har naya major decision yahin add hoga.

## Step 1 — Foundation Storage Layer

- Qdrant local-mode (embedded, no Docker) use kiya gaya hai, deployment simplicity ke liye.
- Python 3.13.12 environment mein build ho raha hai.
- Qdrant ka naya `query_points()` API use hota hai, deprecated `search()` nahi.
- Har storage component (SQLite, Qdrant, Embedder) pehle isolation mein test hua, phir combined plumbing test likha gaya.

## Step 2 — Mem0 Core Wiring

- - `gpt-4o-mini` extraction ke liye, `text-embedding-3-small` embeddings ke liye use ho raha hai.
- `mem0ai[nlp]`/spaCy extras Python 3.13 pe support nahi karte, isliye retrieval abhi semantic-only hai — BM25/entity-matching baad mein add hoga.
- `agent_memory` collection Qdrant mein `plumbing_test` collection se alag rakha gaya hai, schema conflict avoid karne ke liye.
- Mem0 ka naya ADD-only pipeline contradictions khud resolve nahi karta — yeh empirically prove ho chuka hai (QA engineer vs SDET test case). Isi wajah se custom Confidence/Decay/Superseded layer zaroori hai.

## Step 2 — Confidence, Decay & Superseded Layer

- Confidence/decay/superseded state ek alag SQLite table (`memory_meta`) mein store hoga, Mem0 ke apne storage se decoupled — taaki Mem0 replace/upgrade hone pe yeh logic untouched rahe, aur SQL queries aasan rahein.
- Confidence decay Ebbinghaus forgetting-curve formula follow karta hai: `confidence(t) = e^(-t/S)`.
- Reinforcement do tareeke se hota hai: (1) search mein retrieve hone pe chhota boost (+0.05, max 0.95 tak cap), (2) explicit re-confirmation (CONFIRMS classification) pe full reset (confidence = 1.0).
- Contradiction detection do-step hai: pehle cheap vector-similarity search, phir sirf close matches pe ek LLM classification call (CONFIRMS / CONTRADICTS / UNRELATED) — taaki token usage minimize ho.
- Superseded facts delete nahi hote, sirf `status=superseded` mark hote hain aur naye fact se link (`superseded_by`) ho jaate hain — Zep/Graphiti ke temporal-invalidation pattern se inspired, taaki full history audit ke liye preserve rahe.
- Bug fix: `_is_active()` missing memory_meta row ko "inactive" ki jagah "active" treat karta hai — kyunki missing row ka matlab fact invalid nahi, sirf untracked hai (crash-recovery ke liye zaroori).
- Bug fix: per-fact commit (loop ke andar), poore batch ke end mein ek commit nahi — taaki ek fact ka crash pichle facts ka data orphan na kare.
- CAUTION: Mem0 OSS `Memory.delete_all()` mein confirmed bug tha (GitHub #3928) jahan yeh poori collection wipe kar deta hai, sirf filtered user ka nahi. Test data cleanup ke liye fresh user_id use karna, delete_all() nahi.

## Step 2 — STATUS: COMPLETE

- Add-side (`add_memory_with_resolution`) aur search-side (`search_memory_with_decay`)
  dono end-to-end tested — contradiction detection, confirmation-reinforcement,
  superseded-hiding, aur live decay, sab integration tests mein PASS.
- Mem0 ka apna add()/search() API mein inconsistency hai: `add()` top-level
  `user_id` accept karta hai, `search()`/`get_all()` `filters={"user_id": ...}`
  maangte hain (top-level dena `ValueError` deta hai).
- Mem0 OSS `delete_all()` mein confirmed bug hai (GitHub #3928) — poori
  collection wipe kar deta hai, sirf filtered user ka nahi. Kabhi use nahi
  karna; test-isolation ke liye fresh `user_id` use karna.