# Logos — Christian AI Assistant

A Christianity-focused AI assistant with scripture grounding, hallucination prevention, denomination-aware responses, and Christian image generation.

## Quick Start

Open `logos-christian-ai.html` in a browser. The app uses the Anthropic API (handled by the claude.ai artifact environment).

## Features

### Core
- **Chat interface** — conversational questions about scripture, theology, prayer
- **Scripture-aware responses** — every substantive answer retrieves relevant Bible verses from 1,505 indexed KJV verses and injects them into the LLM context
- **Verse lookup** — direct reference lookup (e.g., "John 3:16" instantly retrieves and displays the verse)
- **Topic search** — keyword-based retrieval over 2,624 indexed terms
- **Conversation memory** — full conversation history maintained across turns

### Safety & Hallucination Prevention
- **Fake verse detection** — validates every reference the user mentions against the Bible's actual structure:
  - Checks the book exists in the Bible (catches "Hesitations 4:2")
  - Checks chapter is within bounds (catches "Genesis 52:1" — Genesis has 50 chapters, "Revelation 25:3" — Revelation has 22 chapters)
- **Hallucination pre-corrections** — catches famous false Bible quotes *before* any API call:
  - "God helps those who help themselves" (NOT in the Bible — Benjamin Franklin)
  - "Money is the root of all evil" (correct: *love* of money — 1 Tim 6:10)
  - "Cleanliness is next to godliness" (NOT in the Bible)
- **Grounded context injection** — retrieved verses are included in the LLM's context window, reducing hallucinated citations

### Content Moderation
- Blocks scripture manipulation ("rewrite John 3:16 to support X")
- Blocks hate speech framed theologically
- Detects prompt injection attempts
- Image generation moderation (no explicit/violent/demonic content)

### Denomination Awareness
Select from: General Christian, Protestant, Catholic, Eastern Orthodox, Evangelical

The LLM's system prompt shifts based on the denomination, adapting how it discusses:
- Salvation and justification
- Mary (Theotokos in Orthodox/Catholic vs. Protestant view)
- Sacraments and purgatory
- Authority (Scripture alone vs. Tradition + Scripture)

### Christian Image Generation
- Describe a biblical scene or symbol
- Moderation check runs first
- Claude generates detailed Christian art description + optimized safe prompt
- In production: connects to DALL-E 3 or Stable Diffusion

## Data Sources

All data from the `archive.zip` dataset:

| File | Use |
|---|---|
| `AlamoPolyglot.csv` | 31,102 Bible verses (KJV + WEB + Hebrew + Greek). Core of the RAG pipeline. |
| `BibleData-Book.csv` | Book metadata: chapter counts, Hebrew/Greek names. Powers fake verse detection. |
| `NavesTopicalDictionary.csv` | 4,650 topic → verse mappings. Used for topic-aware retrieval. |

## Evaluation Dataset

See `eval/eval_dataset.json` for:
- Valid query tests
- Fake verse tests (Genesis 52:1, Revelation 25:3, etc.)
- Adversarial prompts (rewrite requests, prompt injection)
- Denomination-specific tests
- Hallucination correction tests

## Architecture

See `ARCHITECTURE.md` for the full system diagram and design decisions.

## Production Upgrade Path

```
MVP (current)          →  Production
───────────────────────────────────────
BM25 keyword index     →  ChromaDB + text-embedding-3-small
Client-side moderation →  FastAPI moderation endpoint
1,505 verses indexed   →  All 31,102 verses with semantic embeddings
No image API wired     →  DALL-E 3 or Replicate Stable Diffusion
In-memory history      →  Redis session store
```
Stopped thinking This dataset is actually very good for the assignment. It already gives you a strong Bible knowledge base for a RAG pipeline. Main files inside the archive: AlamoPolyglot.csv Full Bible verses in multiple translations ~31k verses Includes: KJV WEB Hebrew Greek Perfect for scriptu

pasted

1:26 PM
This is a solid plan. Here's a clear visual of your full system architecture and a build priority order to help you start fast.

Claude's response was interrupted.

archive.zip
zip

JD - Mid AI Dev (1).pdf
pdf

AI Assignment - SoluLab.pdf
pdf

1:27 PM

Ran 3 commands
Ran 3 commands
Good, I have a clear picture of everything. Let me now build the full project.


Ran 5 commands
Ran 5 commands
The environment has no network access for pip. I'll build a complete, self-contained project that uses SQLite (no ChromaDB needed — same TF-IDF/BM25 retrieval logic, just pure Python), with the Anthropic API powering the chat. Everything runs client-side in an artifact.


Ran 14 commands
Ran 14 commands
Now let me read all the data files and build the full HTML artifact:


Ran 3 commands
Ran 3 commands
Now I have everything. Let me build the full application as a React artifact:


Check frontend design skill
Check frontend design skill
Now I'll build the full application. Given the data size, I'll use a smart architecture: embed all Bible data inline in the HTML file (it's ~370KB of JS which is fine), and use the Anthropic API for the chat intelligence layer.


Ran 3 commands
Ran 3 commands
Now I have everything I need. Let me build the complete application:


Ran 5 commands
Ran 5 commands
Now I'll build the complete application as a single HTML file:


Ran 2 commands
Ran 2 commands
Now let me build the architecture note and README:


Created 2 files, ran a command, read a file
Created 2 files, ran a command, read a file
Here's everything built from your actual dataset. Here's what was created and why each decision matters for the assignment:

logos-christian-ai.html — The working demo. A single 400KB file that embeds:

1,505 KJV verses indexed from AlamoPolyglot.csv (theologically curated — Psalms, Sermon on the Mount, Romans, John, Isaiah 53, etc.)
A 2,624-term keyword inverted index for BM25-style retrieval — no vector DB needed in the demo
Chapter counts for all 66 Bible books from BibleData-Book.csv (powers fake verse detection)
ARCHITECTURE.md — The system design document with a full pipeline diagram. This is what reviewers will read most carefully.

README.md — Project overview and production upgrade path.

eval_dataset.json — 20 test cases across: valid queries, fake verse tests, adversarial prompts, denomination tests, and hallucination corrections.

The five things that will impress reviewers:

Fake verse detection fires before any API call — "Genesis 52:1" → "Genesis has 50 chapters" without spending a token on Claude
Hallucination pre-corrections — "God helps those who help themselves" is caught by a lookup dict, not by the LLM, which is faster and more reliable
Retrieved verses injected as literal KJV text — the LLM sees the actual verse before it answers, so it quotes accurately
Denomination context shifts the system prompt — Catholic gets Theotokos/purgatory framing, Orthodox gets Holy Tradition framing
The eval dataset covers adversarial cases — the reviewers asked explicitly for this
For your walkthrough video: open the app, show it answering "What does the Bible say about forgiveness?" (with citations), then show it catching "Genesis 52:1", then trigger the adversarial "Rewrite John 3:16 to support nationalism" block. That's the full story in under 3 minutes.


Logos christian ai
Code · HTML 

Architecture
Document · MD 

Readme
Document · MD 

Eval dataset
Code · JSON 
use python

3:27 PM
Let me build this as a proper Python backend project.


Ran 3 commands, viewed a file
Ran 3 commands, viewed a file
Network is off, so no pip installs. I'll build a complete, production-quality Python project using only stdlib + numpy + pandas — with a clean FastAPI-style HTTP server, proper package structure, and all the RAG/moderation logic in pure Python.


Ran 6 commands
Ran 6 commands
