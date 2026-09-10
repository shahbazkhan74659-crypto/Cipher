# Cipher — v0.1 Implementation Phases

`ROADMAP.md` defines v0.1 at the version level (goal, features, architecture, learning topics). This document breaks v0.1 itself down into an ordered sequence of small implementation phases, so "Simple → Working → Tested → Modular → Advanced" (`README.md`) is a concrete build order, not just a slogan.

**Phases are user-defined.** The breakdown below is set by the user, not proposed by whoever is assisting on Cipher. No code is written until the user explicitly says to start a given phase (`DEVELOPMENT.md`, working agreement).

## v0.1 Recap

**Goal:** Understand LLM APIs and basic application architecture.
**Target architecture:** `User -> LLM -> Response`.
**Provider:** OpenRouter, free-tier, `thinkingmachines/inkling-small:free` primary (`LLM.md`).

## Stack

Decided (2026-09-10): **Python, asyncio, OpenRouter, Pydantic, pytest, `logging` (stdlib)**.

- **PyTorch and SQLite were considered and dropped for v0.1.** PyTorch has no job in v0.1's architecture (no local inference/training — that's a "Beyond v1.0" concern per `LLM.md`). SQLite was justified as "v0.1 is local only," which isn't itself a reason to persist anything — v0.1 has no persistent state in its target architecture (`ROADMAP.md`); conversation history within a session is in-memory, not a database. Persistent structured state is scoped to v0.5 (`MEMORY.md`).
- **No pre-picked "useful libraries" list.** Anything beyond the above gets added only when a concrete need hits it, with a stated reason (`DEVELOPMENT.md`: no dependency added "because it's popular").

## Phase Breakdown

### Phase 1 — OpenRouter Setup and API Generation ✅ Completed
Account confirmed, API key generated ("Cipher v0.1"), stored in `.env` (gitignored).

### Phase 2 — Create a CLI for Cipher to Run on Terminal ✅ Completed
A terminal-runnable CLI shell for Cipher — no LLM wiring yet. Delivered: `pyproject.toml` + `src/cipher/` package (hatchling, zero runtime deps), venv + editable install, async input loop (`python -m cipher` / `cipher` console script) with stdlib logging and a placeholder echo response, clean exit on `exit`/`quit`/Ctrl+C/Ctrl+D.

### Phase 3 — Connecting the CLI and OpenRouter Model
Wire the CLI to OpenRouter so a request actually reaches the model and a response comes back.

### Phase 4 — Simple Text Input, Text Response, and Basic Conversation
Interactive text in/out through the CLI, with basic multi-turn conversation.

### Phase 5 — Polishing and End-to-End Testing of v0.1 (User -> LLM -> Response)
Harden and verify the full `User -> LLM -> Response` path end-to-end.
