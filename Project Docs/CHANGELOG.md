# Changelog

All notable changes to the Cipher project are recorded here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/); versions correspond to the milestones in `ROADMAP.md`.

## [Unreleased]

v0.1 — Basic AI Assistant is in progress (see `PHASES.md`).

### Added
- Phase 1: OpenRouter account confirmed, API key generated, stored in `.env` (gitignored).
- Phase 2: Python project scaffolding — `pyproject.toml` (hatchling backend, no runtime dependencies yet), `src/cipher/` package, venv, editable install. Terminal CLI shell (`python -m cipher` / `cipher` command): async input loop (`asyncio.run` + `asyncio.to_thread`), stdlib logging to stderr, clean exit on `exit`/`quit`/Ctrl+C/Ctrl+D. Responses are a placeholder echo — no OpenRouter wiring yet (Phase 3).
- Phase 3: CLI wired to a real OpenRouter model call (single-turn, no history yet — Phase 4). Added `config.py` (stdlib `.env` loader + Pydantic `Settings`), `llm_client.py` (model-agnostic `LLMClient` interface), `openrouter_client.py` (`OpenRouterClient`, real error handling for timeouts/network errors/rate limits/malformed responses/embedded errors in HTTP 200 bodies). First runtime dependencies: `httpx`, `pydantic`.
- Phase 4: real multi-turn conversation — a running in-memory history (with a minimal system prompt) is threaded through each model call, so Cipher now remembers earlier turns within a session. A failed turn is popped back off history to avoid corrupting later context.

### Fixed
- `thinkingmachines/inkling-small:free` (originally documented v0.1 primary model) turned out to 403 outside recognized "agentic harness" integrations — not usable from Cipher's CLI. First replacement, `nvidia/nemotron-3-ultra-550b-a55b:free`, worked but timed out ~30-40% of the time under free-tier load. Settled on `nvidia/nemotron-3-super-120b-a12b:free` as default model — 5/5 successful test calls, faster and more reliable (see `LLM.md`).
- `OpenRouterClient` now retries up to 3 total attempts (2s delay) for clearly-transient failures — HTTP 429/5xx and embedded provider errors with a 5xx-style code (e.g. observed "Upstream error from Nvidia: Service temporarily overloaded") — before surfacing an error. Retries the same configured model only; not auto-fallback across models (`LLM.md`: "fallbacks are manual, not routed").

### Notes
- Next milestone: Phase 5 — polishing and end-to-end testing of v0.1.

## [0.0.0] - 2026-08-31 - Planning

### Added
- Full project documentation set: `README.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `SECURITY.md`, `TOOLS.md`, `MEMORY.md`, `DEVELOPMENT.md`.
- Version roadmap defined, v0.1 through v1.0, with post-v1.0 directions.
- Security model defined (risk tiers, required mechanisms) ahead of any tool implementation.
- Personalized learning path mapped to each version, based on current background (Python/Django/Channels/ASGI, Java/Spring, prior CV/hardware projects) and identified gaps (ML/DL fundamentals, math for ML, agent architecture, OS automation, voice pipelines, vector DBs).

### Notes
- No code written. This release exists purely to lock down concept, architecture, and security posture before implementation begins.
- Next milestone: define and implement Cipher v0.1 (`User -> LLM -> Response`).
