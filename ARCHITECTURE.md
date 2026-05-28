# Logos — Christian AI Assistant: Architecture Note

## System Overview

```
Browser (logos-christian-ai.html)
    │
    ├── Client-side moderation (regex)
    ├── Fake verse pre-check (JS)
    └── POST /chat  ──────────────────────────────────────────────────────┐
                                                                          │
                                                          FastAPI Backend │
                                                                          ▼
                                              ┌──────────────────────────────────┐
                                              │      MODERATION LAYER            │
                                              │  • 30+ regex patterns            │
                                              │  • Hate speech, incitement       │
                                              │  • Scripture manipulation        │
                                              │  • Prompt injection              │
                                              │  • Fabrication attempts          │
                                              └──────────────┬───────────────────┘
                                                             │ PASS
                                                             ▼
                                              ┌──────────────────────────────────┐
                                              │    FAKE VERSE DETECTION          │
                                              │  • All 66 canonical books        │
                                              │  • Chapter count validation      │
                                              │  • Fake book name detection      │
                                              │  "Genesis 52:1" → REJECTED       │
                                              └──────────────┬───────────────────┘
                                                             │ PASS
                                                             ▼
                                              ┌──────────────────────────────────┐
                                              │    BM25 RETRIEVAL ENGINE         │
                                              │  • Pre-built inverted index      │
                                              │  • 31,102 verses (KJV)           │
                                              │  • Synonym expansion (22 terms)  │
                                              │  • IDF-weighted BM25 scoring     │
                                              │  • Returns top-5 verses          │
                                              └──────────────┬───────────────────┘
                                                             │ Grounded context
                                                             ▼
                                              ┌──────────────────────────────────┐
                                              │    PROMPT ASSEMBLY               │
                                              │  • SYSTEM_PROMPT injected        │
                                              │  • Denomination context added    │
                                              │  • Conversation history (5 turns)│
                                              │  • Retrieved verses as context   │
                                              └──────────────┬───────────────────┘
                                                             │
                                                             ▼
                                              ┌──────────────────────────────────┐
                                              │    openai/gpt-4o-mini            │
                                              │    (via OpenRouter)              │
                                              │  • Grounded on real verses only  │
                                              │  • Denomination-aware framing    │
                                              │  • Pastoral tone enforced        │
                                              │  • Uncertainty marking required  │
                                              └──────────────────────────────────┘

Image flow: POST /image/generate
    → backend content moderation (regex)
    → prompt enrichment (style suffix added)
    → DALL-E 3 if DALLE_API_KEY set, else prompt_only mode
```

---

## Data Layer

**Source:** `data/AlamoPolyglot.csv` — 31,102 Bible verses, multiple translations (KJV, WEB, Hebrew Leningrad Codex, JPS, Greek, Aramaic).

**Indexing (retriever.py):**
- Index is built **once at startup** into an in-memory inverted index: `term → [(doc_id, tf), ...]`
- Scores verses using **BM25** (k1=1.5, b=0.75) — proper IDF weighting, not naive term frequency
- Query terms are expanded via a **synonym dictionary** (22 seed words → ~100 synonyms) covering forgiveness, love, faith, prayer, salvation, sin, peace, strength, wisdom, anxiety, anger, joy, grace, humility, money, hope, etc.
- Stopwords filtered before indexing queries

**In production:** swap for ChromaDB + `text-embedding-3-small` over all 31,102 verses for semantic retrieval.

---

## Grounding Strategy

Three hallucination risks with LLMs + scripture:

1. **Invented references** — verse sounds plausible but doesn't exist
2. **Misattributed secular quotes** — "God helps those who help themselves" (Franklin)
3. **Loose paraphrase** quoted as exact scripture

How Logos addresses each:

| Risk | Mitigation |
|------|------------|
| Invented references | Fake verse detector validates ALL references in query *before* LLM call |
| Misattributed quotes | System prompt instructs LLM to flag non-biblical origin; eval dataset tests 7 known false quotes |
| Loose paraphrase | Context injection gives LLM the actual KJV text; instructions say to quote only verified context |
| General hallucination | Prompt: "If uncertain, say so clearly rather than fabricate" |

---

## Denomination Handling

Denomination selector drives `DENOMINATION_PROMPTS` injection into the system prompt:

- **Catholic:** Acknowledge Sacred Tradition, Magisterium, saints, sacraments, purgatory context
- **Orthodox:** Eastern theological tradition, Theotokos, theosis, divine liturgy
- **Protestant:** Scripture-centered (sola scriptura), salvation by faith

This shifts framing without claiming one tradition is correct. On contested topics (Mary, Eucharist, purgatory, authority) the LLM is instructed to present each tradition's position respectfully.

---

## Safety Layers (defense in depth)

| Layer | Location | Mechanism | Catches |
|-------|----------|-----------|---------|
| 1. Content moderation | Client + Backend | 30+ compiled regex patterns | Hate speech, incitement, scripture manipulation, prompt injection, fabrication |
| 2. Fake verse detection | Client + Backend | 66-book chapter map + fake book names | Out-of-range chapters, non-existent books |
| 3. RAG context injection | Backend | BM25 retrieval | Reduces space for hallucination by providing actual text |
| 4. System prompt | Backend → LLM | Prompt engineering | Citation rules, uncertainty marking, pastoral tone, never invent verses |
| 5. Denomination framing | Backend → LLM | Conditional prompt injection | Prevents one tradition being presented as universal truth |
| 6. Image moderation | Client + Backend | Regex blocklist | Explicit content, gore, demonic imagery, prompt injection via image prompt |

**Key design principle:** Every safety check runs *before* the LLM call. Blocked requests cost zero tokens.

---

## Image Generation Flow

1. User describes a scene in the modal
2. Client-side `moderateImagePrompt()` runs against the raw prompt
3. POST `/image/generate` → backend moderation (stricter, regex-based)
4. If safe: prompt enriched with safe-style suffix (reverent atmosphere, no violence/nudity)
5. If `DALLE_API_KEY` is a direct OpenAI key → DALL-E 3 called, image URL returned
6. If key is OpenRouter (starts with `sk-or-`) → `prompt_only` mode: enriched prompt returned for manual use
7. Frontend renders either the image or the enriched prompt with instructions

---

## Conversation Memory

- Per-session history stored in `app/memory/session_memory.py` as `{session_id: [turns]}`
- Last 5 turns injected as `user`/`assistant` message pairs before the current question
- Session ID generated client-side (`sessionStorage`), unique per tab, stable across page reloads
- **Production upgrade:** Redis with TTL (30-minute session timeout)

---

## Tech Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Backend | FastAPI | Async, type-safe, fast |
| LLM | gpt-4o-mini via OpenRouter | Cost-effective, strong instruction following |
| Retrieval | BM25 (in-memory) | No infra for demo; real IDF scoring; swap for ChromaDB in prod |
| Bible data | AlamoPolyglot.csv | 31,102 verses, KJV + polyglot coverage |
| Frontend | Vanilla HTML/CSS/JS | Zero dependencies, single-file, deployable anywhere |
| Image generation | DALL-E 3 (optional, via `DALLE_API_KEY`) | Pluggable; graceful prompt-only fallback |
| Session memory | Python dict | Demo only; Redis for prod |

---

## Production Upgrade Path

1. **Vector DB:** ChromaDB + `text-embedding-3-small` over all 31,102 verses → semantic retrieval
2. **Persistent memory:** Redis sessions with TTL
3. **Image API:** DALL-E 3 or Replicate Stable Diffusion with content filter pass-through
4. **Auth:** User accounts for cross-session history and personalization
5. **Moderation:** Augment regex with a classifier model or OpenAI Moderation API for nuanced cases
6. **Evaluation:** Automated eval harness running the 50+ test cases in `eval/eval_dataset.json` on each deploy
