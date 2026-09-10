# Cipher — v0.1 Implementation Phases

`ROADMAP.md` defines v0.1 at the version level (goal, features, architecture, learning topics). This document breaks v0.1 itself down into an ordered sequence of small implementation phases, so "Simple → Working → Tested → Modular → Advanced" (`README.md`) is a concrete build order, not just a slogan.

**Phases are user-defined.** The breakdown below is set by the user, not proposed by whoever is assisting on Cipher. No code is written until the user explicitly says to start a given phase (`DEVELOPMENT.md`, working agreement).

## v0.1 Recap

**Goal:** Understand LLM APIs and basic application architecture.
**Target architecture:** `User -> LLM -> Response`.
**Provider:** OpenRouter, free-tier, `nvidia/nemotron-3-super-120b-a12b:free` primary (`LLM.md` — originally `thinkingmachines/inkling-small:free`, rejected during Phase 3 testing as it 403s outside recognized "agentic harness" integrations; briefly `nemotron-3-ultra-550b-a55b:free`, demoted to fallback for reliability).

## Stack

Decided (2026-09-10): **Python, asyncio, OpenRouter, Pydantic, pytest, `logging` (stdlib)**.

- **PyTorch and SQLite were considered and dropped for v0.1.** PyTorch has no job in v0.1's architecture (no local inference/training — that's a "Beyond v1.0" concern per `LLM.md`). SQLite was justified as "v0.1 is local only," which isn't itself a reason to persist anything — v0.1 has no persistent state in its target architecture (`ROADMAP.md`); conversation history within a session is in-memory, not a database. Persistent structured state is scoped to v0.5 (`MEMORY.md`).
- **No pre-picked "useful libraries" list.** Anything beyond the above gets added only when a concrete need hits it, with a stated reason (`DEVELOPMENT.md`: no dependency added "because it's popular").

## Phase Breakdown

### Phase 1 — OpenRouter Setup and API Generation ✅ Completed
Account confirmed, API key generated ("Cipher v0.1"), stored in `.env` (gitignored).

### Phase 2 — Create a CLI for Cipher to Run on Terminal ✅ Completed
A terminal-runnable CLI shell for Cipher — no LLM wiring yet. Delivered: `pyproject.toml` + `src/cipher/` package (hatchling, zero runtime deps), venv + editable install, async input loop (`python -m cipher` / `cipher` console script) with stdlib logging and a placeholder echo response, clean exit on `exit`/`quit`/Ctrl+C/Ctrl+D.

### Phase 3 — Connecting the CLI and OpenRouter Model ✅ Completed
Wire the CLI to OpenRouter so a request actually reaches the model and a response comes back. Delivered: `config.py` (stdlib `.env` loader + Pydantic `Settings`), `llm_client.py` (model-agnostic `LLMClient` interface + `LLMClientError`), `openrouter_client.py` (`OpenRouterClient`, single request/response, real error handling for network/timeout/rate-limit/malformed-response/embedded-error-in-200 cases), `cli.py` wired to call it (single-turn, no history yet — that's Phase 4). First real runtime dependencies added: `httpx`, `pydantic`. Confirmed working end-to-end with a real OpenRouter round-trip. Surfaced and resolved two real issues, not code bugs: (1) the documented primary model (`thinkingmachines/inkling-small:free`) 403s outside "agentic harness" integrations; (2) its first replacement, `nemotron-3-ultra-550b-a55b:free`, worked but timed out ~30-40% of the time. Settled on `nvidia/nemotron-3-super-120b-a12b:free` as primary — 5/5 successful test calls, much faster (see `LLM.md`). Follow-up fix after a real "Nvidia: Service temporarily overloaded" error surfaced mid-use: `OpenRouterClient` retries up to 3 total attempts (2s apart) for clearly-transient failures (429/5xx, embedded provider errors with a 5xx-style code) before giving up — retries the same model only, not auto-fallback across models.

### Phase 4 — Simple Text Input, Text Response, and Basic Conversation ✅ Completed
Interactive text in/out through the CLI, with basic multi-turn conversation. Delivered: a running in-memory conversation history (with a minimal system prompt giving Cipher a basic identity) threaded through each `OpenRouterClient.complete()` call — confirmed the model correctly recalls facts from earlier turns. A failed turn (`LLMClientError`) is popped back off history so it doesn't leave an orphaned/unanswered entry confusing later turns. No persistence across restarts, no context trimming, no history-reset command — out of scope per `MEMORY.md`'s v0.5 boundary and v0.1's scale.

**Known limitation (2026-09-10):** conversation length is bounded only by the model's raw context window (262,144 tokens for `nemotron-3-super`), with no proactive tracking or trimming — very roughly 300-800 turns depending on message length, untested at that scale. If the window is actually exceeded, OpenRouter returns an error that Cipher displays readably (not a crash), but Phase 4's recovery only pops the single latest unanswered turn off history — if the *accumulated* history is already too large, that doesn't fix anything, and the only recovery is restarting the CLI (clearing all history). Real context management (trimming/summarization) is deliberately deferred to v0.5 (`MEMORY.md`), not a bug to fix now.

### Phase 5 — Polishing and End-to-End Testing of v0.1 (User -> LLM -> Response) ✅ Completed
Harden and verify the full `User -> LLM -> Response` path end-to-end. Delivered: `pytest` + `pytest-asyncio` added as a `dev` dependency group (`pyproject.toml`) — the stack decision named in the table above but never actually wired in until now. 27 tests across `tests/test_config.py`, `tests/test_openrouter_client.py`, and `tests/test_cli.py` cover config loading/`.env` parsing, the full retry/backoff matrix (retryable vs. terminal HTTP statuses, embedded provider errors, malformed/unexpected response shapes), and the CLI loop (blank input, exit commands, history pop-on-failure, EOF/Ctrl-C). OpenRouter responses are faked with `httpx.MockTransport` — already part of `httpx`, so no new mocking dependency and no real API calls burned by the test suite.

Two real bugs surfaced and fixed, not by inspection but by actually exercising the failure paths:
1. **Timeouts and network errors weren't retried.** `OpenRouterClient._complete_once()` retried HTTP 429/5xx and embedded 5xx-coded provider errors, but `httpx.TimeoutException`/`httpx.RequestError` were treated as immediately terminal — backwards, given `LLM.md`'s own documented timeout rates. Both now raise `_RetryableError` and go through the same bounded retry loop.
2. **`UnicodeEncodeError` crash on real LLM output.** Manual end-to-end verification (below) crashed on the very first live reply: Windows' default console codepage (cp1252) can't encode characters ordinary LLM replies contain (em dashes, curly quotes, emoji). Fixed by reconfiguring `sys.stdout`/`sys.stderr` to UTF-8 (`errors="replace"` as a safety net) at the top of `cli.run()`.

Also added: `.env.example` at the project root (documents `OPENROUTER_API_KEY` and the manual `CIPHER_MODEL` fallback override per `LLM.md`).

**Manual end-to-end verification (2026-09-10), run against the real OpenRouter API:**
1. Normal multi-turn conversation — model correctly recalled an earlier fact across turns; confirmed the Unicode fix (em dash, emoji in real replies rendered without crashing).
2. `OPENROUTER_API_KEY` unset — clean `ConfigError` to stderr, exit code 1, before the async loop starts.
3. Garbage API key — OpenRouter's 401 surfaced as a clean inline `Cipher: [error] ...` message, single attempt, no retry (correctly non-retryable), no crash.
4. `CIPHER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free` — the manual fallback override works end-to-end; this run also hit a real transient "Upstream error from Nvidia: Service temporarily overloaded" and the retry loop recovered on the second attempt, live-confirming the Step-1 fix's value.

**Known limitation carried forward (unchanged from Phase 4):** context-window exhaustion recovery is still limited to popping the single latest unanswered turn — real context management is deferred to v0.5 (`MEMORY.md`), not a Phase 5 concern.
