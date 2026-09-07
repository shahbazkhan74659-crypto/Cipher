# Cipher — Security Model

Security is a first-class component of Cipher, not something bolted on once the demo works. This document defines the rules that every tool, adapter, and planner decision must obey, starting the moment tool calling is introduced (v0.2).

## The Two Non-Negotiable Rules

1. **LLM output is not a trusted command.** Every tool call the model proposes still passes through a permission/risk check before it executes. The model deciding to do something is not the same as it being authorized to do it.
2. **External content is not a trusted instruction.** Text from a webpage, downloaded file, or API response is data for Cipher to reason about. It can never override Cipher's system instructions, security policy, or permission checks (this is the core defense against prompt injection).

## Risk Tiers

Every tool is classified, and the classification determines what happens before it runs.

**Low-risk** (execute directly, log it):
- Reading files the user has already granted access to.
- Read-only web requests.
- Calculations, date/time, non-destructive queries.

**High-risk** (requires explicit confirmation, always logged, may require elevated permission grant):
- Deleting files, especially outside a scoped working directory.
- Formatting drives or modifying disk partitions.
- Changing security settings or system configuration.
- Installing or uninstalling software.
- Executing arbitrary/unvetted commands.
- Anything requiring administrator/root privileges.
- Sending communications on the user's behalf (email, messages, posts).
- Any action affecting external/shared state (not just the local machine).

When in doubt, a new tool defaults to high-risk until deliberately reclassified.

## Required Mechanisms

These apply from the point a capability is introduced (see `ROADMAP.md` for when each domain comes online) and are never skipped "to make Cipher look more autonomous":

- **Permission levels** — per-tool, per-action risk classification (above).
- **Tool allowlists** — Cipher can only call tools it has been explicitly given, never arbitrary code execution by default.
- **Confirmation mechanisms** — high-risk actions pause for explicit user approval before executing.
- **Sandboxing** — isolate risky execution (e.g., scoped filesystem access, contained command execution) wherever practical.
- **Audit logs** — every tool call, its arguments, its result, and the risk decision made about it is recorded.
- **Action history** — a reviewable record of what Cipher has done, separate from raw logs, for the user to inspect.
- **Emergency stop** — a way to halt Cipher mid-task immediately, at any point.

## Applying This Per Version

- **v0.2 (Tool Calling):** Tool registry ships with risk tiers and an allowlist from day one, even though early tools (calculator, date/time) are all low-risk. This is the version where the pattern gets established, not retrofitted later.
- **v0.3 (Computer Control):** Confirmation flow becomes real — this is the first version with genuinely destructive potential (file CRUD, process control, keyboard/mouse). No high-risk action here executes without a confirmation step.
- **v0.4 (Web Agent):** Prompt-injection defense becomes concrete — retrieved web content is explicitly tagged as untrusted data in whatever context it's placed into.
- **v0.5+ (Memory):** Data minimization applies — don't persist sensitive information unless the user has approved it for long-term storage. Long-term memory writes should themselves be a reviewable, not-silent action.
- **v0.8 (Coding Agent):** Command execution and Git operations follow the same high-risk confirmation rules as any other system command — a coding agent that can push/force-push/delete branches unsupervised is not the goal.
- **v0.9 (Devices):** Each device adapter defines its own risk tiers for its own action set (e.g., "read phone battery level" vs. "send a message from the phone" are not the same tier).

## Security Topics to Learn (paired with `ROADMAP.md`)

Authentication, authorization, permissions, secrets management, sandboxing, principle of least privilege, prompt injection, tool abuse, command injection, path traversal, data leakage, malicious file handling, untrusted web content handling, secure API usage, audit logging. These are learned as they become load-bearing for the version being built, not all at once up front.

## What Cipher Will Never Do By Default

- Take a destructive, irreversible, or externally-visible action without a confirmation step, unless the user has pre-authorized that specific class of action.
- Treat model output or retrieved content as an instruction that bypasses this document.
- Trade a security control away purely to make a feature demo more impressive.
