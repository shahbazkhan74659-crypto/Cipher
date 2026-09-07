# Cipher — LLM Sizing & Local Deployment Reference

This is a **reference doc**, not a roadmap change. It exists to capture model-sizing/hardware facts for when they become relevant, without pulling local model execution earlier than `ROADMAP.md` schedules it. If anything here ever conflicts with `ROADMAP.md`, `ROADMAP.md` wins.

## Current Decision (unchanged)

Cipher is **cloud-first** through v0.1–v1.0: hosted LLM APIs behind the model-agnostic interface (`ARCHITECTURE.md` §4). Local model execution is listed under **"Beyond v1.0"** in `ROADMAP.md` — a future option, not a current requirement. "No GPU yet" is a reason to stay cloud-first, not a reason to squeeze a quantized model onto CPU early.

**v0.1 specifically uses a free-tier cloud LLM API** (e.g. Gemini, Groq, or OpenRouter's free models) rather than a paid API or a self-hosted model — this satisfies the zero-dollar-cost goal without taking on local inference infrastructure before v0.1's "Simple → Working" step needs it (`ROADMAP.md`). The `LLMClient` interface stays swappable either way, so moving to a paid tier or a different free provider later is a contained change.

This decision is backed by a measured hardware check (2026-09-07), not a guess: the current dev machine is an AMD Ryzen 3 5425U (4C/8T) with integrated AMD Radeon graphics — no dedicated GPU/VRAM — and 7.35 GB RAM. Per the sizing table below, that ceiling is ~1-3B quantized models, which rules out a locally-hosted "main brain" outright. Local inference on this machine is worth exploring as a small standalone learning exercise, not as Cipher's actual v0.1 path.

This doc exists so that when a local model *does* become relevant, the sizing math doesn't have to be re-derived from scratch.

## When Local Actually Becomes Relevant

Not "as soon as I get a GPU." A concrete trigger, e.g.:
- Cloud API cost/latency becomes a real constraint at Cipher's actual usage volume.
- An explicit offline/privacy requirement shows up for a specific tool domain.
- Hardware exists (GPU acquired) **and** there's a stated reason to use it beyond "it's there."

Until one of those is true, treat this doc as background knowledge, not a task.

## Parameter Count vs. Laptop Practicality (no GPU, CPU inference)

| Model size | Laptop practicality | Rough capability |
|---|---|---|
| 0.5–1.5B | Easy | Basic commands, simple conversation |
| 3B | Good | Solid prototype, basic tool calling/reasoning |
| 7–8B | Best CPU target | Strong general-assistant behavior |
| 13–14B | Heavy | Better reasoning, noticeably slower |
| 30B+ | Painful on CPU | Not worth it without a GPU |
| 70B+ | Impractical | GPU required |

## Quantization Memory Math (7B example)

| Precision | Approx. weight size |
|---|---|
| FP16 | ~14 GB |
| INT8 | ~7 GB |
| 4-bit | ~3.5–5 GB |

Actual RAM need is higher than weight size alone — KV cache, context length, and runtime overhead add on top. Rule of thumb by system RAM:

| System RAM | Reasonable local target |
|---|---|
| 8 GB | ~1–3B |
| 16 GB | ~3–8B (quantized) |
| 32 GB | ~7–14B |
| 64 GB | more headroom, still CPU-bound without a GPU |

## Why Parameter Count Isn't the Real Lever

A smaller model with a solid tool-calling/permission system (`TOOLS.md`, `SECURITY.md`) is more useful to Cipher than a larger model with no tools — this matches the project's own thesis in `ARCHITECTURE.md`: the Planner, Tool Router, and permission layer carry more of Cipher's real capability than raw model size does. When local models do enter the picture, prioritize the interface/tool architecture being solid over chasing a bigger local model.

## Out of Scope Here

Training a small model from scratch (e.g. 10M–100M param) is a valid **separate learning project** per `DEVELOPMENT.md`'s "concepts too large for Cipher's codebase get their own standalone project" rule — it is not part of Cipher's assistant path and doesn't belong on this sizing table.
