# Cipher

A personal AI assistant and long-term software/AI engineering project — not a weekend build, but a multi-year (roughly 4–5 year) effort that doubles as a practical laboratory for learning AI/ML, agentic systems, and systems programming.

## What Cipher is

Cipher's end goal is an **AI operating layer** for a personal computer, not just another chatbot:

- Understands natural language and (eventually) voice.
- Reasons about goals and plans multi-step tasks.
- Uses tools to interact with the OS, files, the web, code, and external devices.
- Maintains memory (short-term, long-term, and a retrievable knowledge base).
- Keeps the human in control of anything dangerous or irreversible.

That end state is the destination, not the starting point — see `Project Docs/ROADMAP.md` for how it's built version by version.

## What Cipher is not

- Not a wrapper gluing together orchestration frameworks and calling it done.
- Not a system granted unrestricted OS/file/network access on day one.
- Not judged by demo impressiveness — judged by reliability, security, and actual task completion.

## Project status

**v0.2 in progress.** v0.1 ("Basic AI Assistant" — `User -> LLM -> Response`) is complete: a terminal CLI with real multi-turn conversation through OpenRouter, an automated test suite, and hardened error handling. Work has moved on to v0.2 (**Tool Calling** — `User -> LLM -> Tool Selection -> Tool -> Result -> LLM -> Response`): a tool registry and base interface exist, with a calculator and a date/time tool already working. Full detail and decision history live in `Project Docs/PHASES.md`, `Project Docs/LLM.md`, and `Project Docs/CHANGELOG.md`.

## Architecture principles

Every version, from v0.1 onward, is built to be:

- **Modular** — each capability (LLM provider, memory backend, a tool, a device adapter) is replaceable without rewriting the rest of the system.
- **Extensible** — a new tool or adapter is a new module + registration, not a rewrite.
- **Observable** — tool calls, decisions, and errors are logged.
- **Secure** — no unrestricted power for convenience, ever (see Security below).
- **Testable** — important components carry automated tests.
- **Model-agnostic** — swapping the LLM touches one adapter, not the whole codebase.
- **Hardware-agnostic** — supports cloud, local, and hybrid model execution; not designed around a GPU that doesn't exist yet.
- **Failure-aware** — designed for graceful degradation against hallucinations, API/network failures, invalid tool arguments, and permission errors — not just the happy path.

See `Project Docs/ARCHITECTURE.md` for the full target system diagram and design principles.

## Security model

Two non-negotiable rules govern every tool call, from the moment tool calling is introduced (v0.2) onward:

1. **LLM output is not a trusted command** — every proposed tool call passes through a permission/risk check before it executes.
2. **External content is not a trusted instruction** — text from a webpage, file, or API response is data to reason about, never something that can override Cipher's system behavior or security policy (the core prompt-injection defense).

Tools are classified into risk tiers (low-risk: execute and log; high-risk: requires explicit confirmation, always logged) — see `Project Docs/SECURITY.md` for the full model.

## Roadmap at a glance

| Version | Goal | Status |
|---|---|---|
| v0.1 | Basic AI assistant (`User -> LLM -> Response`) | Complete |
| v0.2 | Tool calling | In progress |
| v0.3 | Computer control (OS/files, permissions) | Planned |
| v0.4 | Web agent | Planned |
| v0.5 | Memory & RAG | Planned |
| v0.6 | Voice | Planned |
| v0.7 | Computer vision / computer use | Planned |
| v0.8 | Coding agent | Planned |
| v0.9 | External device control | Planned |
| v1.0 | Integrated personal AI agent (full planner) | Planned |

See `Project Docs/ROADMAP.md` for features, architecture additions, and the learning path mapped to each version.

## Tech stack

| Layer | Choice |
|---|---|
| Language | Python 3.11+ |
| LLM access | OpenRouter (free-tier cloud models), via `httpx` |
| Validation | Pydantic |
| Packaging | Hatchling, installed as the `cipher` CLI entry point |
| Testing | `pytest` + `pytest-asyncio` |

Cipher starts **cloud-first** — the current development machine has no dedicated GPU, so v0.1 calls a free-tier hosted model rather than running one locally. Every model-facing component sits behind an interface from the start so local/hybrid execution can be swapped in later without a rewrite. See `Project Docs/LLM.md` for the hardware math.

## Project structure

```
src/cipher/
  cli.py                 Terminal CLI entry point
  config.py               .env / environment configuration loading
  llm_client.py            Model-agnostic LLM client interface
  openrouter_client.py     OpenRouter provider implementation
  logging_setup.py         Logging configuration
  tools/
    base.py                 Tool interface contract
    registry.py              Tool registration/lookup
    calculator.py            Calculator tool
    datetime_tool.py         Date/time tool

tests/                  pytest suite (one file per module)
Project Docs/           Full documentation set — see below
```

## Getting started

**Prerequisites:** Python 3.11+, an [OpenRouter](https://openrouter.ai/) API key (free tier is sufficient for v0.1/v0.2).

```bash
# Install (editable) with dev dependencies
pip install -e ".[dev]"

# Configure your API key
cp .env.example .env
# then edit .env and set OPENROUTER_API_KEY=your-key-here

# Run the assistant
cipher

# Run the test suite
pytest
```

`CIPHER_MODEL` is an optional environment variable to override the default free-tier model (see `.env.example`).

## Documentation

This project keeps a living documentation set under `Project Docs/`, each file with one job:

| Document | Purpose |
|---|---|
| `README.md` | Orientation and navigation (a copy of this file's core content, kept as the canonical doc-map entry point) |
| `ARCHITECTURE.md` | The target (v1.0+) system architecture and the design principles every version must respect |
| `ROADMAP.md` | Version-by-version build plan (v0.1 → v1.0 → beyond), with a personalized learning path per version |
| `PHASES.md` | Implementation-phase breakdown for the version currently being built |
| `SECURITY.md` | The security model — risk tiers, permission checks, sandboxing, audit logging |
| `TOOLS.md` | The tool interface contract and the tool catalog |
| `MEMORY.md` | Cipher's own memory system design (short-term, long-term, knowledge/RAG) |
| `DEVELOPMENT.md` | The Learn → Build → Break → Debug → Improve cycle and coding standards |
| `LLM.md` | Model sizing, quantization, and local-hardware math for when local execution becomes relevant |
| `CHANGELOG.md` | Version history, starting from v0.0.0 (planning) |

## Working agreement

- Build incrementally: **Simple → Working → Tested → Modular → Advanced.**
- Never implement a future version's complexity early.
- Security and user control are never traded away for the appearance of autonomy.
- Push back on bad ideas with reasons, not just agreement.

## License

All rights reserved — see [`LICENSE`](LICENSE). This is not open-source software.
