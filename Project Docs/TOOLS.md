# Cipher — Tools

Cipher does not get raw, unrestricted access to the OS, filesystem, or internet. It gets a defined set of **tools** — narrow, purpose-built functions the LLM can choose to call. This document defines the tool contract and the planned tool catalog by domain. No tools are implemented yet; this is the design these will follow once each version comes online (see `ROADMAP.md`).

## Why Tools, Not Raw Access

Giving an LLM a shell and saying "go" is not an architecture, it's a liability. A tool is a contract: a fixed name, a fixed set of typed arguments, a defined result shape, and a declared risk tier (`SECURITY.md`). The LLM can only do what a tool explicitly allows it to do.

## The Tool Contract

Every tool, regardless of domain, defines:

- **Name** — unique, descriptive (e.g. `read_file`, `search_web`).
- **Description** — what it does and when to use it; this is what the LLM reads to decide whether to call it.
- **Parameters** — typed, validated. Invalid arguments are rejected before execution, not passed through and hoped for.
- **Result shape** — a predictable structure the LLM (and the code) can rely on, including how errors are represented.
- **Risk tier** — low-risk (direct execution) or high-risk (requires confirmation) per `SECURITY.md`.
- **Owning adapter** — which domain module implements it (see below), so it stays swappable.

## Tool Registry

Introduced in v0.2. A central registry that:
- Holds every tool available to Cipher and their metadata (schema, risk tier, adapter).
- Is the single place the Tool Router consults to validate and dispatch a proposed call.
- Enforces the allowlist — a tool not in the registry cannot be called, period.

## Interface Preference Per Tool

When a tool's domain has multiple possible implementations, prefer (in order, see `ARCHITECTURE.md` §3):
1. Official application/API integration
2. Accessibility APIs
3. Native OS APIs
4. CLI
5. GUI automation
6. Vision-based interaction

A tool's implementation should be documented with which tier it uses and why, so a future upgrade path (e.g., replacing GUI automation with a real API once one exists) is visible.

## Tool Catalog by Domain

Illustrative signatures below describe the *shape* of each domain's tools, not a final API — they will be refined when each version is actually implemented.

### System / Computer Control (v0.3)
`launch_app()`, `close_app()`, `list_processes()`, `get_system_info()`, `run_command()` (high-risk), `send_keystroke()`, `move_mouse()`/`click()` (GUI-automation fallback tier).

### Filesystem (v0.2 read-only, v0.3 full CRUD)
`read_file()`, `list_directory()`, `create_file()` (high-risk), `write_file()` (high-risk), `move_file()` (high-risk), `delete_file()` (high-risk), `search_files()`.

### Web (v0.4)
`search_web()`, `open_webpage()`, `extract_web_content()`, `download_file()` (high-risk), `call_api()`.

### Memory / Knowledge (v0.5)
`remember()` (write to long-term memory, high-risk in the sense that it's a deliberate, reviewable action), `recall()`, `search_knowledge_base()` (RAG retrieval).

### Voice (v0.6)
Not exposed as LLM-callable tools in the usual sense — STT/TTS sit in the input/output pipeline itself (`ARCHITECTURE.md` §1). Documented here for completeness once implemented.

### Vision / Computer Use (v0.7)
`take_screenshot()`, `read_screen_text()` (OCR), `find_ui_element()`, `describe_screen()`.

### Coding (v0.8)
`read_repo_file()`, `search_code()`, `edit_file()` (high-risk), `run_tests()`, `run_terminal_command()` (high-risk), `git_status()`, `git_diff()`, `git_commit()` (high-risk).

### Devices (v0.9)
Per-adapter, defined when each device integration is built (Android, Bluetooth, USB, Display, Network) — no shared signature, since devices don't share a protocol (`ARCHITECTURE.md` §1, Device Manager).

## Tool Design Rules

- A tool does one thing. Compose tools in the planner, don't build a mega-tool that branches internally on hidden logic.
- A tool never silently escalates its own risk tier (e.g., a "read" tool must never also write).
- Every high-risk tool call is logged with its arguments and the confirmation decision, per `SECURITY.md`.
- New tools are added by writing the tool + registering it — never by widening an existing tool's scope to cover a new case.
