# Cipher — LLM Sizing & Local Deployment Reference

This is a **reference doc**, not a roadmap change. It exists to capture model-sizing/hardware facts for when they become relevant, without pulling local model execution earlier than `ROADMAP.md` schedules it. If anything here ever conflicts with `ROADMAP.md`, `ROADMAP.md` wins.

## Current Decision (unchanged)

Cipher is **cloud-first** through v0.1–v1.0: hosted LLM APIs behind the model-agnostic interface (`ARCHITECTURE.md` §4). Local model execution is listed under **"Beyond v1.0"** in `ROADMAP.md` — a future option, not a current requirement. "No GPU yet" is a reason to stay cloud-first, not a reason to squeeze a quantized model onto CPU early.

**v0.1 specifically uses a free-tier cloud LLM API** (e.g. Gemini, Groq, or OpenRouter's free models) rather than a paid API or a self-hosted model — this satisfies the zero-dollar-cost goal without taking on local inference infrastructure before v0.1's "Simple → Working" step needs it (`ROADMAP.md`). The `LLMClient` interface stays swappable either way, so moving to a paid tier or a different free provider later is a contained change.

This decision is backed by a measured hardware check (2026-09-07), not a guess: the current dev machine is an AMD Ryzen 3 5425U (4C/8T) with integrated AMD Radeon graphics — no dedicated GPU/VRAM — and 7.35 GB RAM. Per the sizing table below, that ceiling is ~1-3B quantized models, which rules out a locally-hosted "main brain" outright. Local inference on this machine is worth exploring as a small standalone learning exercise, not as Cipher's actual v0.1 path.

This doc exists so that when a local model *does* become relevant, the sizing math doesn't have to be re-derived from scratch.

## v0.1 Free-Tier Model Selection (OpenRouter)

**Original evaluation (2026-09-09)** used Artificial Analysis benchmark scores (intelligence/coding/agentic indices) against OpenRouter's free-model catalog and picked `thinkingmachines/inkling-small:free` as primary. **Superseded (2026-09-10)** once Phase 3's live CLI testing showed benchmark scores alone weren't sufficient — actual reachability and free-tier latency/reliability matter just as much for a model Cipher will actually call.

| Model | Status | Notes |
|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | **Primary** (2026-09-10) | 120B total / 12B active MoE. 5/5 successful test calls, 2.6-22s response time (~8s avg). Tools: yes. Context: 262,144. |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | Fallback (demoted 2026-09-10) | 550B total / 55B active MoE. Was primary briefly — worked but slow/unreliable: 3/5 successful, 2 outright timeouts (one past 30s, one past 60s). Keep as a documented manual fallback for when `nemotron-3-super` is itself rate-limited; don't default to it. Tools: yes. Context: 1,000,000. |
| ~~`thinkingmachines/inkling-small:free`~~ | Rejected (2026-09-10) | `HTTP 403 Forbidden`: *"only available on agentic harnesses. Try plugging it into a coding agent or productivity app listed on https://openrouter.ai/apps."* Gated to recognized integrations Cipher's plain HTTP client isn't part of — a real access restriction, not a code bug (error handling caught and reported it correctly). Was the original 2026-09-09 pick on benchmark scores alone. |
| `thinkingmachines/inkling:free` | Untested / suspect | Same provider/family as the rejected `inkling-small` — presumed to carry the same "agentic harness" restriction. Not verified either way. |
| `google/gemma-4-31b-it:free` | Untested / inconclusive | Returned `429` rate-limiting (provider-side) on every attempt during testing (2026-09-10). Not ruled out, just never got a clean response to evaluate. |

**Why `nemotron-3-super` over `nemotron-3-ultra`:** same provider/account path already confirmed reachable (lower risk of a new 403), but roughly 1/4 the active parameters (12B vs 55B) — which tracks directly with the large speed/reliability difference observed. Cipher's request timeout is 60s (`cli.py`) to give free-tier latency headroom generally, not tuned to either model specifically.

**Fallbacks are manual, not routed.** Per `ROADMAP.md` v0.1 ("one interface, one provider behind it to start") and the "never implement a future version's complexity early" working agreement, fallback models are *not* wired into automatic multi-model routing — that's explicitly a "Beyond v1.0" item (`ROADMAP.md`) and the reason `OmniRoute` was rejected below. They're a documented, manually-swappable option (via `CIPHER_MODEL` env var) if the primary is rate-limited or down. OpenRouter's free-tier rate limit is 20 req/min; 50/day, or 1,000/day with $10+ lifetime credits purchased — docs don't confirm whether that's pooled account-wide or bucketed per model.

Re-evaluate this table if OpenRouter's free catalog changes materially, or when v0.2+ needs push the decision (e.g. tool-calling reliability under real use, not just the `tools` capability flag).

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
