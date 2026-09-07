# Cipher — Target Architecture

This document describes where Cipher is going (v1.0 and beyond), and the principles that constrain every version along the way. It is a destination map, not a build order — see `ROADMAP.md` for what actually gets built when.

## 1. End-State System Diagram (v1.0)

```text
                         CIPHER
                            |
          +-----------------+-----------------+
          |                 |                 |
        LLM              Memory             Voice
          |                 |                 |
          +-----------------+-----------------+
                            |
                         Planner
                            |
                       Tool Router
                            |
       +----------+---------+---------+----------+
       v          v         v         v          v
      OS       Files      Web      Coding     Devices
       |          |         |         |          |
      Apps       CRUD    Search    Execute    Control
```

- **LLM** — the reasoning core. Swappable (`Model-agnostic` principle below).
- **Memory** — short-term (conversation/task state), long-term (approved persistent facts), knowledge/RAG (see `MEMORY.md`).
- **Voice** — STT in, TTS out, sits alongside text as an input/output modality, not a separate brain.
- **Planner** — turns a goal into an ordered set of tool calls, handles replanning on failure.
- **Tool Router** — dispatches planner decisions to the correct tool/adapter, enforces the permission model from `SECURITY.md` before execution.
- **Domain adapters** (OS, Files, Web, Coding, Devices) — the actual capability implementations. Each is an independently replaceable module.

## 2. Architectural Principles

Every version of Cipher, from v0.1 onward, must respect these:

- **Modular** — each major capability (LLM provider, memory backend, a tool, a device adapter) is replaceable without rewriting the rest of the system.
- **Extensible** — adding a new tool or adapter should not require touching unrelated code. New capability = new module + registration, not a rewrite.
- **Observable** — tool calls, decisions, and errors are logged. If Cipher does something, there is a record of why.
- **Secure** — see `SECURITY.md`. No unrestricted power for convenience. Ever.
- **Testable** — important components have automated tests. "It looked right in the demo" is not verification.
- **Model-agnostic** — the system is not hard-wired to one LLM provider. Swapping the LLM should touch one adapter, not the whole codebase.
- **Hardware-agnostic** — supports cloud, local, and hybrid model execution (see `ROADMAP.md`, hardware constraints). Don't design around GPUs we don't have yet.
- **Failure-aware** — expect hallucinations, API failures, network failures, invalid tool arguments, permission errors, crashes, and unexpected UI changes. Design for graceful degradation and recovery, not the happy path only.

Cipher is deliberately **not** built as one monolithic file/framework stack. It is a collection of small, independently understandable modules.

## 3. Computer-Control Interface Hierarchy

When Cipher needs to interact with an application or the OS, it uses the **highest-level, most reliable interface available**, in this order:

1. Official application/API integration
2. Accessibility APIs
3. Native OS APIs
4. CLI / command-line interface
5. GUI automation (keyboard/mouse)
6. Vision-based interaction (screenshot + CV/OCR) — last resort

GUI automation and vision are fallbacks for when nothing more reliable exists, not the default approach.

## 4. Model Deployment Spectrum

```text
Cloud Model
      |
Local Model
      |
Hybrid Model
```

Cipher starts cloud-first (current hardware/budget constraint — see `ROADMAP.md`). The LLM/embedding/STT/TTS components are abstracted behind interfaces from the start so that local or hybrid execution can be swapped in later without an architectural rewrite.

## 5. Trust Boundaries

Two rules govern every tool call and every piece of retrieved content:

- **LLM output is not a trusted command.** A tool call proposed by the model still passes through the permission/risk-tier check in `SECURITY.md` before it executes.
- **Web/external content is not a trusted instruction.** Text pulled from a webpage, file, or API response is data to reason about, never an instruction that can override Cipher's system behavior or security policy (prompt-injection defense).

## 6. Where Components Enter the Roadmap

This diagram is the destination. Components are introduced incrementally:

| Component | First appears |
|---|---|
| LLM core (text in/out) | v0.1 |
| Tool Router + first tools | v0.2 |
| OS/Files adapters + permissions | v0.3 |
| Web adapter | v0.4 |
| Memory + RAG | v0.5 |
| Voice | v0.6 |
| Vision/computer-use | v0.7 |
| Coding adapter | v0.8 |
| Device adapters | v0.9 |
| Planner (full multi-step orchestration) | v1.0 |

Details, features, and learning topics per version live in `ROADMAP.md`.
