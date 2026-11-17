# AGENTIC OS — OVERVIEW & PRINCIPLES (ARMS v2)

## 1. Vision & System Scope

**Agentic OS** is a personal AI operating system engineered for the Claude 5.5 and Claude Code generation. It abandons heavyweight custom middleware, distributed service containers, and speculative proxy backends. Instead, it adopts the **ARMS framework** (**A**pplications, **R**outines, **M**emory, **S**kills) where **the agent with its native tools is the operating engine**, and the operating system is the structured, standing filesystem harness around it.

### Scope Definition
* **Single-User Architecture:** Designed exclusively for one operator working on a primary Windows workstation plus an optional 24/7 Linux VPS.
* **No Public Exposure:** The system never exposes public HTTP interfaces, multi-tenant databases, or open remote ports.
* **Local-First Sovereignty:** All knowledge, memories, logs, and artifacts are stored in plain Markdown, YAML, and JSON Lines on disk, version-controlled via private Git.

---

## 2. Core Architectural Principles

1. **Bottom-Up Construction:** Skills → Memory → Routines → Applications. Build what works first in code, verify it in practice, and codify specifications after code.
2. **The Agent IS the Engine:** Claude Code CLI (with its native file editing, bash execution, and MCP tool use) replaces custom backend proxies.
3. **Short Skills Get Followed, Long Ones Get Skimmed:** Skill files are strictly limited to `<60` lines. Larger workflows are decomposed into modular skill trees with lean routers.
4. **Router Files Over Deep Folders:** Single-page markdown pointer indexes (`<50` lines) beat deep labyrinthine folder structures for LLM navigation.
5. **Show, Don't Store:** Dashboards and command centers are transparent viewports into filesystem state; they never maintain separate competing databases.
6. **The Compounding Loop:** Every task performed twice becomes a skill; every new project area gets a pointer entry in the router.
7. **Plain-Text Sovereignty:** Git-backed Markdown files ensure zero vendor lock-in for your data.
8. **Human-in-the-Loop (HITL) by Design:** Any action that mutates external state, spends money, or publishes data requires explicit human confirmation via a dedicated approval queue.

---

## 3. What We Lose & What We Keep (Explicit Trade-Off Table)

| Feature / Subsystem | Legacy Status (`specs/00-15`) | New ARMS Plan 2.0 Status | Rationale & Trade-Off |
| :--- | :--- | :--- | :--- |
| **Obsidian 3D Orb & Canvas** | Core spec (`05`, `06`) | **Eliminated** | High maintenance overhead; zero utility for automated workflows. Obsidian remains strictly an offline Markdown editor. |
| **Live Speech / Voice Pipeline** | Core spec (`07`) | **Deferred / Dropped from Core** | Local Whisper + Kokoro containers require dedicated GPU VRAM and complex audio buffering. Focus on core text/tool execution first. |
| **Custom FastAPI Bridge Daemon** | Core prototype (`apps/bridge`) | **Replaced by Secure Local Runner** | The legacy bridge was an unauthenticated proxy. Replaced with an ultra-lean, hardened Python runner (`127.0.0.1` only). |
| **Redis Pub/Sub & Qdrant/Chroma**| Core spec (`01`, `10`) | **Eliminated** | Unnecessary distributed infrastructure. State lives in Git and Markdown; search is handled natively by agent ripgrep/tools. |
| **WebSocket Token Streaming** | Core spec (`03`, `14`) | **Eliminated in Headless** | Unattended headless jobs need atomic JSON results and audit logs, not token-by-token character streaming. |
| **Real-time Mobile / Multi-user**| Implicitly assumed | **Single-User Desktop + VPS** | Designed strictly for one operator on a Windows workstation plus one Linux VPS. No multi-tenant complexity. |
| **"Compile, Don't Retrieve"** | Core principle (`02`) | **Preserved & Elevated** | Raw notes compile into structured indexes and wiki pages. Compounding value without vector bloat. |
| **HITL Destructive Gates** | Core principle (`11`) | **Preserved & Formalized** | Send, spend, or publish actions require human approval via a real JSONL approval queue. |

---

## 4. Vendor Lock-in Decision Record & Exit Strategy

**Decision:** Agentic OS targets the Claude Code runtime and Anthropic models as its primary reasoning engine due to superior code synthesis, native tool use, and structured headless modes (`claude -p`).

**Exit Strategy:** The operating system avoids architectural lock-in by enforcing strict portability:
1. All skills are plain Markdown (`SKILL.md`) and standard YAML manifests (`skill.yaml`).
2. Routers are standard GitHub-flavored Markdown links.
3. The local execution runner (`apps/runner/server.py`) abstracts command execution into an isolated subprocess call. Migrating to an alternative agent runtime (e.g. Codex, OpenAI CLI, or open-source local agents) requires changing only the invocation command line in one runner file without altering skills, memory, or routines.

---

## 5. Document Index

This specification suite consists of five focused documents:

- **`00-OVERVIEW.md`** (this document): Vision, ARMS principles, scope, and trade-offs.
- **`01-ARCHITECTURE-AND-SECURITY.md`**: Git sync engine, VPS topology, zero-RCE runner design, headless permissions, and HITL approval queue.
- **`02-SKILLS-AND-ROUTINES.md`**: Skill manifests, skill trees, headless execution (`claude -p`), JSONL audit logging, and evals.
- **`03-MEMORY-AND-ROUTERS.md`**: Root `CLAUDE.md`, area indexes, router lint script, vault preservation, and scaling limits.
- **`04-COMMAND-CENTRE.md`**: Single-page HTML dashboard, static server binding, artifact streams, and approval UI.

---

## 6. Acceptance Criteria

- [ ] Document explicitly identifies system scope as single-user Windows + Linux VPS.
- [ ] All 8 core principles are defined with clear operational rationales.
- [ ] Trade-off table explicitly records all legacy features eliminated, replaced, or preserved.
- [ ] Vendor lock-in paragraph includes a concrete, decoupled exit strategy.
- [ ] Document index matches the exact 5 specification files on disk.
