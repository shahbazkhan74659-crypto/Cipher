# Cipher — Roadmap

## Development Rule

**Simple → Working → Tested → Modular → Advanced.**
Not: Complex → Broken → Impossible to debug.

Each version introduces a manageable set of capabilities. We do not build v1.0's architecture while implementing v0.1. See `DEVELOPMENT.md` for the Learn → Build → Break → Debug → Improve cycle this roadmap runs on.

---

## Current Background Assessment

Before mapping learning topics to versions, an honest read of where you're starting from.

**Solid foundation already in place:**
- Python — general proficiency assumed; depth in async/OOP to be confirmed in practice during v0.1-v0.2.
- Async/ASGI and WebSocket experience (from Django Channels) — directly useful, independent of Django itself. Streaming LLM responses, real-time voice I/O, and long-running task updates in Cipher are the same shape of problem as Channels consumers. Cipher does not use Django — it adds no value here (no ORM/admin/templates needed); if a web/API layer is ever needed, a lightweight ASGI framework (FastAPI/Starlette) covers the same async/WebSocket model. This background is a real head start for v0.1 (streaming) and v0.6 (voice).
- Java, Spring Boot, Thymeleaf — transfers as general backend/OOP/architecture literacy, not directly reused in Cipher (Python-first project), but useful for understanding design patterns and layered architecture.
- Git/GitHub, Linux/Ubuntu, APIs, general web development — assumed baseline, not re-taught from scratch.
- Prior computer vision exposure (underwater hand-gesture project, MediaPipe) — a real advantage for v0.7 (screen understanding/computer vision). You are not starting CV from zero.
- Hardware/fire-safety project — general systems-thinking and hardware-adjacent debugging experience, loosely relevant to v0.9 (device control).

**Gaps to close deliberately (not assumed, not skipped):**
- Math for ML (linear algebra, probability, statistics, calculus) — no evidence of formal coverage. Needed before v0.5's embeddings/RAG start feeling like magic, and before v1.0-and-beyond deep learning work.
- Classical ML (scikit-learn workflow: train/validation/test, overfitting, regularization, evaluation) — not yet covered. Needed to reason about anything statistical Cipher does, and as a stepping stone to deep learning.
- Deep learning fundamentals (PyTorch, backprop, gradient descent, transformers) — not yet covered. Needed once Cipher starts doing more than calling a hosted LLM API (fine-tuning, local models, understanding *why* the model behaves as it does).
- LLM internals (tokenization, attention, context windows, embeddings) — treat as unknown until confirmed otherwise; needed to debug Cipher's core reasoning engine intelligently rather than treating it as a black box.
- Agent architecture concepts independent of any framework (planning, tool calling, reflection, multi-agent orchestration) — this is the conceptual core of v0.2 through v1.0 and needs to be learned as *concepts*, not "how do I use LangChain."
- OS-level automation and accessibility APIs (Windows-specific, since this project runs on Windows 11) — not yet covered. Needed for v0.3 and v0.7.
- Voice/audio pipelines (STT, TTS, streaming audio, VAD, wake-word) — not yet covered. Needed for v0.6; your Channels/WebSocket background gives you the plumbing, not the audio-specific concepts.
- Vector databases and retrieval architecture — not yet covered. Needed for v0.5.
- Security concepts specific to AI agents (prompt injection, tool abuse, sandboxing an LLM-driven system) — general security literacy assumed from web dev (auth, injection classes), but the AI-specific failure modes are new territory. Needed starting v0.2, hardened through every subsequent version.

This assessment should be revisited and corrected as we actually work — it's a starting hypothesis, not a fixed verdict.

---

## Version Plan

Each version below lists: goal, features, architecture additions, and the learning topics that pair with it. Math/ML/DL topics are introduced only when a concrete version needs them, not preemptively.

### v0.1 — Basic AI Assistant
**Goal:** Understand LLM APIs and basic application architecture.
**Features:** Text input, text response, basic conversation, basic configuration, model abstraction (one interface, one provider behind it to start). The provider is a **free-tier cloud LLM API** (e.g. Gemini, Groq, or OpenRouter's free models) — see `LLM.md` for why, given the current machine's hardware.
**Architecture:** `User -> LLM -> Response`.
**Learn:** LLM API mechanics (requests, tokens, context windows, streaming), basic prompt design, Python project structure/packaging, config management, logging basics.

### v0.2 — Tool Calling
**Goal:** Understand tool/function calling and controlled execution.
**Features:** Calculator, time/date, basic filesystem read tools, a tool registry, tool selection. (Controlled command execution moved to v0.3 — `TOOLS.md`'s catalog and `SECURITY.md`'s confirmation-prompt mechanism both scope it there, not here.)
**Architecture:** `User -> LLM -> Tool Selection -> Tool -> Result -> LLM -> Response`.
**Learn:** Function/tool calling mechanics, structured outputs, the "LLM output is not a trusted command" boundary (`SECURITY.md`), first pass at risk tiers and allowlists.

### v0.3 — Computer Control
**Goal:** Safe interaction with the local OS.
**Features:** Open/close applications, process management, controlled command execution, full filesystem CRUD, keyboard/mouse automation, basic system info. Permission checks and confirmation prompts introduced here — not optional.
**Architecture:** OS/Files adapters behind the Tool Router; permission layer sits in front of every tool call.
**Learn:** Windows process/permission model, accessibility APIs, the interface-preference hierarchy (`ARCHITECTURE.md` §3), why GUI automation is a last resort not a default.

### v0.4 — Web Agent
**Goal:** Controlled internet access.
**Features:** Web search, webpage retrieval, information extraction, research/summarization, API calls, controlled file downloads.
**Architecture:** Web adapter; external content flows through the "not a trusted instruction" boundary.
**Learn:** HTTP/HTTPS fundamentals if any gaps remain, prompt injection via web content, source citation, controlled tool design (`search_web()`, `open_webpage()`, `extract_web_content()` as the shape, not final API).

### v0.5 — Memory
**Goal:** Persistent state and knowledge retrieval.
**Features:** Conversation memory, task state, long-term memory (user-approved), knowledge base, RAG, vector search.
**Architecture:** Memory Manager (`MEMORY.md`) sits alongside the LLM core.
**Learn:** Linear algebra basics (vectors, dot products — this is what embeddings *are*), embeddings conceptually, vector databases, chunking/retrieval strategy, SQLite for structured state, the distinction between retrieved context and model reasoning.

### v0.6 — Voice
**Goal:** Natural voice interaction.
**Features:** Speech-to-text, text-to-speech, voice commands, streaming interaction, wake word (later).
**Architecture:** `Microphone -> STT -> Cipher Core -> TTS -> Speaker`, streaming throughout.
**Learn:** Audio fundamentals, STT/TTS APIs and tradeoffs, voice activity detection, streaming audio over WebSockets (this is where the Channels/ASGI background pays off directly).

### v0.7 — Computer Vision / Computer Use
**Goal:** Screen understanding as a fallback interaction layer.
**Features:** Screenshots, OCR, UI element detection, accessibility-tree integration, vision-based interaction when nothing higher-level exists.
**Architecture:** `Screen -> Screenshot -> Vision/OCR/Accessibility -> UI Understanding -> Action Selection -> Keyboard/Mouse/API`.
**Learn:** Image fundamentals, OCR, object/UI-element detection, vision-language models — leverages prior MediaPipe/CV experience directly.

### v0.8 — Coding Agent
**Goal:** Cipher can work on real codebases (including its own).
**Features:** Repository understanding, code search, file editing, terminal access, test execution, debugging loop, Git integration, iterative planning.
**Architecture:** Coding adapter; the `Understand -> Plan -> Modify -> Test -> Observe -> Debug -> Modify -> Test` loop from `DEVELOPMENT.md`.
**Learn:** Formalize the loop already used informally; static analysis basics; how to structure a coding agent's context (repo maps, relevant file selection).

### v0.9 — External Device Control
**Goal:** Modular device integration.
**Features:** Android phone, Bluetooth devices, speakers, displays, USB/network devices — via a Device Manager with per-device adapters.
**Architecture:** `Device Manager -> [Android | Bluetooth | USB | Display | Network] Adapter`. No universal protocol; adapters are the point.
**Learn:** Bluetooth/USB/network protocol basics as needed per device, ADB where relevant, casting protocols.

### v1.0 — Integrated Personal AI Agent
**Goal:** Combine every prior capability behind a real Planner that decomposes multi-step goals across tool domains.
**Features:** Full goal understanding, planning, task decomposition, dependency management, execution, observation, replanning, verification, final reporting.
**Architecture:** The full diagram in `ARCHITECTURE.md` §1.
**Learn:** Agent planning architectures (deliberately framework-independent understanding first), multi-agent patterns if useful, evaluation of agent reliability, human-in-the-loop design.

---

## Beyond v1.0

Not scheduled — directions to grow into once v1.0 is real and stable:

- Better planning, memory, and reasoning quality.
- Multimodal interaction.
- More autonomous workflows (with proportionally stronger guardrails).
- More device integrations.
- Local model execution as hardware allows; hybrid local/cloud routing.
- A genuine personal knowledge system built on the v0.5 memory/RAG foundation.
- Model routing (right model for the task, not one model for everything).
- Self-evaluation.
- Offline capability where practical.

## Hardware & Budget Constraints (current)

Cipher starts **cloud-first**: hosted LLM APIs, CPU-friendly local components, free/low-cost services where practical. Every model-facing component (LLM, embeddings, STT, TTS) sits behind an interface from v0.1 onward specifically so that local or hybrid execution can be swapped in later without a rewrite, once better hardware is available. The architecture is not designed around a GPU we don't currently have.

**Measured, not assumed (2026-09-07):** current development machine is an AMD Ryzen 3 5425U (4C/8T), integrated AMD Radeon graphics (no dedicated GPU/VRAM), 7.35 GB RAM. Per `LLM.md`'s sizing table this supports roughly 1-3B quantized models locally at best — nowhere near enough for a capable "main brain," and not enough to run several specialized local models concurrently. This is why v0.1 calls a **free-tier cloud API** rather than a self-hosted model: it's the only option that gives Cipher a genuinely useful assistant at zero dollar cost on this hardware. Local inference on this machine remains available as a small, separate learning exercise (`DEVELOPMENT.md` — concepts too large/tangential for Cipher's own codebase get their own standalone project), not as Cipher's v0.1 path. Revisit once real GPU hardware exists (see `LLM.md`'s trigger conditions).

## Success Criteria

Cipher is judged by reliability, security, maintainability, observability, extensibility, actual task completion, error recovery, tool accuracy, latency, cost, and user control — not by how impressive a demo sounds. A system that reliably completes 50 useful tasks beats a system that claims full computer autonomy and occasionally deletes something it shouldn't have.
