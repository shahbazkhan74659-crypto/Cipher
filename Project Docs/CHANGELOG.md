# Changelog

All notable changes to the Cipher project are recorded here. Format loosely follows [Keep a Changelog](https://keepachangelog.com/); versions correspond to the milestones in `ROADMAP.md`.

## [Unreleased]

v0.1 — Basic AI Assistant is in progress (see `PHASES.md`).

### Added
- Phase 1: OpenRouter account confirmed, API key generated, stored in `.env` (gitignored).
- Phase 2: Python project scaffolding — `pyproject.toml` (hatchling backend, no runtime dependencies yet), `src/cipher/` package, venv, editable install. Terminal CLI shell (`python -m cipher` / `cipher` command): async input loop (`asyncio.run` + `asyncio.to_thread`), stdlib logging to stderr, clean exit on `exit`/`quit`/Ctrl+C/Ctrl+D. Responses are a placeholder echo — no OpenRouter wiring yet (Phase 3).

### Notes
- Next milestone: Phase 3 — connect the CLI to the OpenRouter model.

## [0.0.0] - 2026-08-31 - Planning

### Added
- Full project documentation set: `README.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `SECURITY.md`, `TOOLS.md`, `MEMORY.md`, `DEVELOPMENT.md`.
- Version roadmap defined, v0.1 through v1.0, with post-v1.0 directions.
- Security model defined (risk tiers, required mechanisms) ahead of any tool implementation.
- Personalized learning path mapped to each version, based on current background (Python/Django/Channels/ASGI, Java/Spring, prior CV/hardware projects) and identified gaps (ML/DL fundamentals, math for ML, agent architecture, OS automation, voice pipelines, vector DBs).

### Notes
- No code written. This release exists purely to lock down concept, architecture, and security posture before implementation begins.
- Next milestone: define and implement Cipher v0.1 (`User -> LLM -> Response`).
