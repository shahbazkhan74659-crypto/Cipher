# Cipher — Memory System

This document describes the memory architecture **Cipher itself** will implement (starting v0.5), as a product feature. It is unrelated to any development tool's own session memory — this is what lets Cipher remember things across conversations with its user.

## Why Memory Is Separate From the LLM Call

An LLM call is stateless. Everything it "knows" about the current interaction has to be handed to it as context. Memory is the system that decides what gets handed over, what gets persisted, and what gets thrown away. Without a deliberate memory design, Cipher either forgets everything every session or accumulates an unbounded, unfiltered context dump — both are failures.

## Memory Types

```text
Conversation
     |
Memory Manager
     +-- Short-Term Memory
     +-- Long-Term Memory
     +-- User-Approved Preferences
     +-- Knowledge / RAG
```

### Short-Term Memory
The current conversation and current task state. Lives for the duration of a session/task, discarded (or summarized) afterward. This is closest to what a plain chatbot already has.

### Long-Term Memory
Persistent facts and history explicitly worth keeping across sessions — e.g., ongoing project context, prior decisions, user goals. Written deliberately, not automatically, and reviewable by the user. Writing to long-term memory is treated as an action, not a side effect (see `SECURITY.md` — data minimization, no unnecessary storage of sensitive information).

### User-Approved Preferences
How the user wants Cipher to behave — tone, confirmation thresholds, default tools, standing instructions. Distinct from factual long-term memory because it changes *behavior*, not just *knowledge*.

### Knowledge / RAG
Retrieval-augmented generation over a document/knowledge base: local documents, project notes, PDFs, codebases, and approved external information. Cipher retrieves relevant chunks at query time rather than trying to hold everything in context.

## RAG Pipeline (v0.5)

```text
Documents
   |
Parsing
   |
Chunking
   |
Embeddings
   |
Vector Database
   |
Retriever
   |
Relevant Context
   |
LLM
   |
Response
```

Sources: local documents, project documentation, personal notes, PDFs, codebases, and web information that has already passed through the "untrusted content" boundary in `SECURITY.md`.

**Critical distinction Cipher must maintain:** retrieved context and the model's own reasoning are not the same thing. Responses that rely on retrieved knowledge should be traceable back to what was retrieved, so a wrong answer can be diagnosed as a retrieval problem vs. a reasoning problem.

## Storage — Candidates, Not Decisions

Nothing below is committed; these are the reasonable default candidates to evaluate when v0.5 is actually built, consistent with the cloud-first/CPU-friendly constraint in `ROADMAP.md`:

- Structured state (short-term/task state, preferences): SQLite to start — simple, file-based, no server to run.
- Vector storage (embeddings for RAG): a lightweight embedded/vector-capable store to start; revisit if scale demands a dedicated vector DB.
- Long-term factual memory: likely layered on the same SQLite store initially, with retrieval logic distinguishing it from RAG knowledge chunks.

## Data Handling Principle

Do not store sensitive information unless it's necessary and the user has approved it. Every long-term write is an explicit, logged action (`SECURITY.md`), not something that happens silently as a side effect of a conversation.

## Where This Sits in the Roadmap

Memory is introduced in **v0.5**, after tool calling (v0.2), computer control (v0.3), and the web agent (v0.4) already exist — so there's real task state and real retrieved content worth remembering before the memory system is built to hold it. See `ROADMAP.md` for the full sequencing and the math/ML prerequisites (embeddings require basic linear algebra — vectors, dot products).
