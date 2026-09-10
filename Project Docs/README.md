# Cipher

Cipher is a personal AI assistant and long-term software/AI engineering project. It is not a weekend build — it is planned as a multi-year (roughly 4-5 year) effort that doubles as a practical laboratory for learning AI/ML, agentic systems, and systems programming.

## What Cipher Is

Cipher's end goal is to become an **AI operating layer** for a personal computer, not just another chatbot:

- Understands natural language and (eventually) voice.
- Reasons about goals and plans multi-step tasks.
- Uses tools to interact with the OS, files, the web, code, and external devices.
- Maintains memory (short-term, long-term, and a retrievable knowledge base).
- Keeps the human in control of anything dangerous or irreversible.

That end state is the destination, not the starting point. See `ROADMAP.md` for how we get there version by version.

## What Cipher Is Not

- Not a wrapper that glues together three orchestration frameworks and calls it done (`DEVELOPMENT.md`, "avoid framework glue").
- Not a system that gets unrestricted OS/file/network access on day one.
- Not a project judged by demo impressiveness — judged by reliability, security, and actual task completion (see `ROADMAP.md`, Success Criteria).

## Project Status

**Planning phase.** As of 2026-08-31, no code has been written. This documentation set exists to lock down the concept, the architecture, the security posture, and the incremental build plan before implementation starts on Cipher v0.1.

## Document Map

| Document | Purpose |
|---|---|
| `README.md` | This file — orientation and navigation. |
| `ARCHITECTURE.md` | The target (v1.0+) system architecture and the design principles every version must respect. |
| `ROADMAP.md` | Version-by-version build plan (v0.1 → v1.0 → beyond), with a personalized learning path mapped to each version. |
| `PHASES.md` | Implementation-phase breakdown for the version currently being built (v0.1) — the ordered build steps within a version. |
| `SECURITY.md` | The security model: risk tiers, permission checks, sandboxing, audit logging. Non-negotiable, applies from v0.2 onward. |
| `TOOLS.md` | The tool interface contract and the tool catalog, organized by capability domain. |
| `MEMORY.md` | Cipher's own memory system design (short-term, long-term, knowledge/RAG) — distinct from any assistant's session memory. |
| `DEVELOPMENT.md` | How we work: the Learn → Build → Break → Debug → Improve cycle, coding standards, and an honest assessment of current background vs. gaps. |
| `LLM.md` | Reference: model sizing, quantization, and local-hardware math for when local model execution becomes relevant (still a "Beyond v1.0" item — see `ROADMAP.md`). |
| `CHANGELOG.md` | Version history, starting from v0.0.0 (planning). |

## Working Agreement

- Build incrementally: **Simple → Working → Tested → Modular → Advanced.**
- Never implement a future version's complexity early.
- Security and user control are never traded away for the appearance of autonomy.
- Push back on bad ideas with reasons, not just agreement.
