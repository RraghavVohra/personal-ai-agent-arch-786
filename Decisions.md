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

  ## Step 3 — Persona Layer

- Design Letta/MemGPT ke "persona block" pattern se inspired — ek chhota,
  character-capped text (limit: 2000 chars) jo agent ki identity/tone/
  behavioral guidelines define karta hai, hamesha context mein rahega
  jab Orchestrator (Step 7) reply generate karega.
- Decided: agent ka naam **Billie**, tone **casual Hinglish**, relationship
  dynamic **blended life + career coach** (encouraging, invested — sirf
  task-completion-focused nahi).
- Abhi static hai; Step 4 (Drift-check) lambi conversations mein isko
  degrade hone se rokega.

- Learning: Abstract persona instructions ("mix Hindi and English") LLM
  se consistent behavior nahi nikalwate. Concrete example phrases
  ("bhai chalo push karte hain") aur explicit anti-patterns ("no generic
  phrases like 'reignite that spark'") deni padti hain — yeh principle
  aage Orchestrator (Step 7) ke prompts likhte waqt bhi yaad rakhna hai.

16/09/2026
- Subtle-drift test se pata chala: judge deep-trait violations (blind
  cheerleading) sahi pakड़ता hai, lekin sirf explicitly-written persona
  rules enforce karta hai — unwritten conventions (jaise formality
  level) judge nahi pakड़ega jab tak persona.py mein likhe na hon.

- Multi-turn simulation (12 turns): tone/Hinglish stable raha throughout,
  lekin do limitations mili: (1) judge ki reasoning repetitive/templated
  thi across varied replies — surface-pattern-matching ka signal, deep
  evaluation ka nahi; (2) Turn 11 mein Billie ne generic "it depends on
  you" non-committal answer diya (career-direction question pe) jo judge
  ne "ok" mark kiya — persona/judge dono mein "coach takes an actual
  stance" trait explicitly missing hai.



