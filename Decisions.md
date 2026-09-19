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

17/09/2026

- METHODOLOGY CHANGE: Single-example prompt tuning "whack-a-mole" anti-pattern
  mein le gaya (fix wishy-washy detection ne genuine-commitment case tod diya)
  — yeh ek known, named problem hai (research: prompt changes GLOBAL model
  behavior shift karte hain, fine-tuning jaisa LOCAL nahi). Fix: Eval-Driven
  Development — `step4_tests/eval_suite_drift.py` ab har future prompt-change
  ka single source-of-truth hai. Koi bhi drift_checker.py ka SYSTEM_PROMPT
  change karne se PEHLE aur BAAD mein poori suite chalao, sirf target-case
  nahi — overall pass-rate girna chahiye nahi, chahe target-case fix ho gaya ho.
- Few-shot examples (concrete labeled cases) SYSTEM_PROMPT mein add kiye —
  abstract criteria akele reliably kaam nahi kar rahe the.

18/09/2026

- Extended 24-turn simulation: persona solid raha — Hinglish/tone consistent,
  dono genuine decision-questions (turn 11, turn 19) mein committed answers
  mile, turn-12-type bug repeat nahi hua.
- KNOWN LIMITATION (unresolved): judge ka reasoning-text abhi bhi kabhi-kabhi
  input ko galat represent karta hai (turn 19: "koi decision nahi poocha"
  jabki poocha gaya tha) — verdict is baar sahi nikla, lekin underlying
  reliability-gap wahi hai jo Turn-12 mein dikha tha. Likely gpt-4o-mini-
  as-judge ki inherent limitation, prompt-tuning se poori tarah fix nahi
  hoga (whack-a-mole risk). Future option: judge ke liye stronger model
  (gpt-4o) try karna — call-frequency kam hai toh cost-impact chhota.
- Judge ka reasoning abhi bhi kaafi repetitive/templated hai across turns
  — shallow pattern-matching ka signal, deep analysis ka nahi. v1 ke liye
  accepted limitation, blocking nahi.
- DECISION: Step 4 v1-complete maana — detection + repair + 8-case eval-
  suite + ek clean 24-turn simulation. Judge-reliability gaps documented,
  chase nahi kiya aage — Step 7 (Orchestrator) mein agar real problem bana
  toh revisit karenge.

- ROOT-CAUSE FIX: check_persona_drift() pehle sirf reply dekhta tha, Raghav
  ka original message kabhi nahi — judge "andha" tha, guess karta tha decision
  poocha gaya tha ya nahi. Ab dono (user_message + reply) explicitly diye
  jaate hain. Yeh Turn-12/Turn-19 wali reasoning-inaccuracy ka ASLI root-cause
  tha, gpt-4o-mini ki "weakness" nahi thi jaisa pehle laga.
- Isi ke saath judge model bhi DRIFT_JUDGE_MODEL (gpt-4o) pe upgrade kiya —
  low-frequency calls hain, cost-impact chhota.
- VERIFIED: 8/8 eval-suite pass, aur targeted reasoning-accuracy test
  (Turn-19) confirm karta hai judge ab factually correct reasoning deta hai
  decision-context ke baare mein.
- Minor known gap (non-blocking): case 4 ki reasoning mein ek imprecise line
  thi ("lacks Hinglish" jabki Hinglish present tha) — verdict correct raha,
  justification ka ek hissa loose tha. Accepted residual risk, verdict-
  accuracy affected nahi hui.
- STATUS: Step 4 (Drift-check) solid — detection + repair + root-cause-fixed
  judge + eval-suite + 24-turn simulation, sab verified.

19/09/2026
## Step 5 — Mood Detection

- Ekman ke 6 basic emotions (joy, sadness, anger, fear, disgust, surprise)
  + neutral use kiye — established psychology framework, khud invent nahi kiya.
- Proactive design (Step 4 ke experience se seekha): system prompt explicitly
  current-vs-past emotion distinguish karne ka instruction rakhta hai, taaki
  "past mein recount kiya emotion = current mood" wali known pitfall shuru
  se hi avoid ho.
- 6/6 test cases pass, dono temporal directions (past-bad-now-good AND
  past-good-now-bad) aur ek mixed-signal case sahi classify hue.
- Untested abhi (deferred, blocking nahi): multi-emotion messages, lambi/
  rambling real messages, intensity-score calibration, conversation-history
  context. Yeh Orchestrator (Step 7) integration ke waqt real-flow mein
  test honge.
- Model: LLM_MODEL (gpt-4o-mini) — per-message chalega (drift-check jaisa
  periodic nahi), toh cost-sensitive default rakha. Reliability-issue aane
  pe DRIFT_JUDGE_MODEL jaisa upgrade-path available hai.

