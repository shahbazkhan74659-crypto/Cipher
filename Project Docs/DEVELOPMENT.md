# Cipher — Development Approach

## Roles in This Project

Whoever is assisting on Cipher (human mentor or AI assistant) is expected to act as: engineering mentor, software architect, ML tutor, coding partner, security reviewer, and research assistant — not just a code generator. When asked "how do I build X," the expected process is:

1. Identify what component/domain X belongs to (`ARCHITECTURE.md`, `TOOLS.md`).
2. Identify what concepts need to be understood first, not just the code.
3. Decide whether Cipher should implement X now or later, per `ROADMAP.md`.
4. Decide what architecture is appropriate, and what risks exist (`SECURITY.md`).
5. Find the simplest working implementation.
6. Then implement it.

## The Learn → Build → Break → Debug → Improve Cycle

For every important concept introduced by a version in `ROADMAP.md`:

```text
Learn concept
    |
Build tiny standalone example
    |
Implement it in Cipher
    |
Break it intentionally
    |
Debug it
    |
Improve the architecture
```

Cipher is simultaneously a real software project and a practical AI/ML laboratory. Concepts too large or tangential to build directly into Cipher (e.g., a from-scratch neural net exercise) get their own small standalone project rather than being forced into Cipher's codebase.

## Coding Standards

- Clean, modular architecture — small files, small modules, each independently understandable.
- Type hints where they add clarity.
- Real error handling — anticipate the failure modes listed in `ARCHITECTURE.md` §2 (Failure-aware), don't just wrap everything in a bare `except`.
- Logging on anything that matters for observability or debugging later.
- No dependency or framework added "because it's popular" — every library choice gets a stated reason. Cipher does not use Django: it's a CLI/API-first agent system with no need for an ORM, admin panel, or templates. If a web/API layer is ever needed, a lightweight ASGI framework (FastAPI/Starlette) preserves the async/WebSocket experience (`ROADMAP.md`, Current Background Assessment) without that unused weight.
- No giant monolithic files. No premature abstraction for hypothetical future needs — three similar lines beats a speculative helper.
- Testable code, and tests for the parts that matter.
- Security considered at write time, not bolted on after (`SECURITY.md`).
- Never claim code works without having actually verified it (tests, run, or explicit statement that it's unverified).

## Modifying Existing Cipher Code

1. Understand the current architecture before touching it.
2. Identify the actually relevant files — don't guess.
3. Explain the change and why, before making it.
4. Make the smallest sensible change that accomplishes the goal.
5. Test it.
6. If it fails, diagnose the root cause — don't randomly permute the code hoping something works.

## How Teaching Should Work

When a new concept needs explaining:

1. Explain the concept simply.
2. Explain why Cipher specifically needs it.
3. Show a small example.
4. Give a practical exercise.
5. Show how it plugs into Cipher.
6. Cover common mistakes.
7. Be explicit about what's important to actually understand vs. what can be treated as an implementation detail for now.

Don't drown the explanation in theory that has no practical connection to what's being built. Don't hide real complexity just to make an explanation sound easier than it is.

## Honest Pushback

If an approach is technically impossible, insecure, needlessly complex, inefficient, expensive, based on a misunderstanding, or likely to cause architectural problems later — say so directly, and explain: what's wrong, why, what would work better, and what the tradeoffs are. Agreement is not the goal; engineering accuracy is.

## Background & Learning Path

See `ROADMAP.md` → "Current Background Assessment" and the per-version "Learn" sections for the concrete, version-mapped learning plan. That assessment should be revisited as work actually happens, not treated as fixed.

## Hardware & Cost Constraints

Cloud APIs and CPU-friendly components by default; the architecture keeps model-facing components swappable (`ARCHITECTURE.md` §4) so local/hybrid execution is a future option, not a current requirement. Don't design around hardware that isn't owned yet.
