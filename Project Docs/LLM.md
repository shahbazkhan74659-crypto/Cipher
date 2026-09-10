# Cipher — LLM Sizing & Local Deployment Reference

This is a **reference doc**, not a roadmap change. It exists to capture model-sizing/hardware facts for when they become relevant, without pulling local model execution earlier than `ROADMAP.md` schedules it. If anything here ever conflicts with `ROADMAP.md`, `ROADMAP.md` wins.

## Current Decision (unchanged)

Cipher is **cloud-first** through v0.1–v1.0: hosted LLM APIs behind the model-agnostic interface (`ARCHITECTURE.md` §4). Local model execution is listed under **"Beyond v1.0"** in `ROADMAP.md` — a future option, not a current requirement. "No GPU yet" is a reason to stay cloud-first, not a reason to squeeze a quantized model onto CPU early.

**v0.1 specifically uses a free-tier cloud LLM API** (e.g. Gemini, Groq, or OpenRouter's free models) rather than a paid API or a self-hosted model — this satisfies the zero-dollar-cost goal without taking on local inference infrastructure before v0.1's "Simple → Working" step needs it (`ROADMAP.md`). The `LLMClient` interface stays swappable either way, so moving to a paid tier or a different free provider later is a contained change.

This decision is backed by a measured hardware check (2026-09-07), not a guess: the current dev machine is an AMD Ryzen 3 5425U (4C/8T) with integrated AMD Radeon graphics — no dedicated GPU/VRAM — and 7.35 GB RAM. Per the sizing table below, that ceiling is ~1-3B quantized models, which rules out a locally-hosted "main brain" outright. Local inference on this machine is worth exploring as a small standalone learning exercise, not as Cipher's actual v0.1 path.

This doc exists so that when a local model *does* become relevant, the sizing math doesn't have to be re-derived from scratch.

## v0.1 Free-Tier Model Selection (OpenRouter)

Evaluated OpenRouter's live free-model catalog (`:free` suffix, $0 prompt/completion pricing) on 2026-09-09 against Artificial Analysis benchmark scores (intelligence/coding/agentic indices), context length, and tool-calling support.

| Model | Role | Intelligence | Coding | Agentic | Context | Tools |
|---|---|---|---|---|---|---|
| `thinkingmachines/inkling-small:free` | **Primary** | 26.1 | 52.9 | 25.0 | 1,048,576 | Yes |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | Fallback | 23.4 | 49.3 | 21.7 | 1,000,000 | Yes |
| `thinkingmachines/inkling:free` | Fallback | 25.5 | 52.1 | 24.3 | 1,048,576 | Yes |
| `google/gemma-4-31b-it:free` | Fallback | 15.4 | 43.4 | 6.7 | 262,144 | Yes |

**Primary: `thinkingmachines/inkling-small:free`.** Best benchmark scores in the free pool despite being the most parameter-efficient of the four (12B active / 276B total MoE) — outscores its own larger sibling (`inkling`, 41B active / 975B total) and NVIDIA's 550B `nemotron-3-ultra`. Supports tool/function calling (needed starting v0.2) and a 1M+ token context window (headroom for v0.5 memory/RAG and v0.8 coding — not needed yet, just doesn't block later).

**Fallbacks are manual, not routed.** Per `ROADMAP.md` v0.1 ("one interface, one provider behind it to start") and the "never implement a future version's complexity early" working agreement, these three are *not* wired into automatic multi-model routing — that's explicitly a "Beyond v1.0" item (`ROADMAP.md`). They're a documented, manually-swappable option if the primary hits OpenRouter's free-tier rate limit (20 req/min; 50/day, or 1,000/day with $10+ lifetime credits purchased). OpenRouter's docs don't explicitly confirm whether that quota is pooled account-wide or bucketed per model, but their own guidance to "spread load across models" when rate-limited implies separate buckets — unverified, would need an empirical check.

Re-evaluate this table if OpenRouter's free catalog changes materially, or when v0.2+ needs push the decision (e.g. a fallback turns out to be the better tool-calling fit).

## Future Candidate: Automatic Multi-Provider Routing (OmniRoute)

Evaluated and rejected for v0.1 (2026-09-10): **OmniRoute** (self-hosted, open-source AI gateway, 160-290+ providers, ~500+ models via one OpenAI-compatible endpoint, with automatic 4-tier fallback across free/cheap/paid providers). Not a fit today because its entire purpose — automatic multi-provider routing — is exactly the "Model routing (right model for the task, not one model for everything)" item listed under **Beyond v1.0** in `ROADMAP.md`. Using it now would mean building v1.0-era routing architecture underneath v0.1's "User -> LLM -> Response" step, on top of requiring a self-hosted gateway process v0.1 has no other need for.

Additional caveats worth remembering if this is revisited later: its own docs note free tiers vanish without notice, and it lists providers whose terms of service prohibit proxy access — that needs a deliberate ToS/security review (`SECURITY.md`) before adoption, not just a capability check. It also obscures which underlying model actually answered a given request unless you inspect its logs, which cuts against the "retrieved/generated context should be traceable" principle this project already applies to RAG (`MEMORY.md`).

**Revisit when:** Cipher actually reaches the "Beyond v1.0" model-routing item on its own terms — i.e., after v1.0's Planner exists and there's a real, stated reason to route across models/providers per task, not before.

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
