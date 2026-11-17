# AGENTIC OS — MEMORY SYSTEM & ROUTER FILES

## 1. Memory Architecture & Philosophy

The memory system replaces complex, opaque vector databases and deep folder hierarchies with transparent, Git-versioned **Markdown Router Files**. 

Claude Code loads the master router automatically from the **project root (`./CLAUDE.md`)** at session start. By pointing directly to 1-page domain indexes, the agent achieves instant, zero-token "first-hop" context retrieval without wading through thousands of files.

```text
Project Root (./)
├── CLAUDE.md                    # Master Workspace Router (Auto-loaded by Claude Code)
├── vault/
│   ├── AGENTS.md                # System Constitution & Write Rules (Imported by CLAUDE.md)
│   ├── raw/                     # Immutable source documents (read-only for AI)
│   └── wiki/                    # Compiled knowledge base (AI writes here)
├── memory/                      # 1-Page Domain Area Indexes (<50 lines each)
│   ├── CONTENT.md               # Pointers to content, drafts, and media
│   ├── SYSTEM.md                # Pointers to architecture, configs, and tools
│   └── CLIENTS.md               # Pointers to client proposals and deliverables
└── output/
    └── artifacts/               # Compiled deliverables and reports
```

---

## 2. Root Master Router (`./CLAUDE.md`)

The root `CLAUDE.md` must be concise (under 80 lines) and provide:
1. **User & System Profile:** 1-line statement of identity and role.
2. **Constitution Import:** Explicit reference to `vault/AGENTS.md` (which Claude Code does not load by default).
3. **Core Work Domains Table:** Mapping domains to their respective 1-page area index files.
4. **Living Pointer Rule:** Mandatory rule requiring the agent to update area indexes whenever files are created or moved.

```markdown
# Agentic OS Workspace Router

## Identity & Role
You are the primary cognitive engine of Agentic OS, operating directly within this repository.

## Constitution
Always follow the write and safety rules defined in [AGENTS.md](vault/AGENTS.md).
1. Files in `vault/raw/` are immutable.
2. AI writes to `vault/wiki/` and `output/artifacts/`.
3. Destructive actions require entries in `output/approval_queue.jsonl`.

## Domain Router Index
| Domain | Area Index File | Description |
| :--- | :--- | :--- |
| **System & Tooling** | [SYSTEM.md](memory/SYSTEM.md) | Specs, runner code, scripts, and configurations |
| **Content & Research**| [CONTENT.md](memory/CONTENT.md) | Video notes, articles, and research compilations |
| **Clients & Projects**| [CLIENTS.md](memory/CLIENTS.md) | Business pipelines, proposals, and deliverables |

## The Living Pointer Rule
When you create, move, or archive a file, update the corresponding index in `memory/` during the same turn.
```

---

## 3. Area Index Standards (`memory/*.md`)

Each area index file is strictly capped at **under 50 lines**. It contains clean single-line pointers:

```markdown
# Content Domain Index

## Active Work
- [Field Notes](example-vault/wiki/index.md) — Fictional garden community demo note
- [ARMS Video Summary](output/artifacts/arms-video-notes.md) — Core takeaways from RoboNuggets Claude 5.5 guide

## Reference Sources
- [Legacy Specs Archive](specs/_archive/legacy/) — Tagged v0.1 legacy specifications
```

---

## 4. Router Drift Prevention: Automated Lint Script (`scripts/lint-routers.py`)

Relying solely on LLM compliance creates router drift over time. The automated lint routine runs as a scheduled check:
* **Dead-Link Detection:** Parses every markdown link in `./CLAUDE.md` and `memory/*.md`, asserting that the target file exists on disk.
* **Orphan-File Detection:** Scans `vault/wiki/` and `output/artifacts/` to detect any files that are not referenced in any router index.
* **Reporting:** Generates `output/artifacts/lint-report.md`.
* **Exit Code:** Exits with code `1` if broken links are discovered, code `0` if clean.

---

## 5. Preservation of Existing Vault Content

Existing content in `Agentic OS/vault/` is fully preserved:
* `vault/raw/` remains the immutable intake zone.
* `vault/wiki/` remains the compiled knowledge zone.
* `vault/AGENTS.md` remains the active behavioral constitution.
* Legacy spec history is preserved under `specs/_archive/legacy/` and tagged `v0.1-legacy-specs`.

---

## 6. Memory Scaling Thresholds

1. **0 to 500 Files:** Markdown Router files provide instantaneous, zero-cost navigation.
2. **500 to 2,000 Files:** Agent tool-based search (`ripgrep` / native file search) combined with area indexes maintains sub-second precision.
3. **2,000+ Files:** Add a local, zero-network SQLite FTS5 full-text indexer script to index markdown content without altering the router conventions.

---

## 7. Acceptance Criteria

- [ ] Master router is located at `./CLAUDE.md` at repository root.
- [ ] `./CLAUDE.md` explicitly references and links `vault/AGENTS.md`.
- [ ] Every area index file in `memory/` is verified under 50 lines.
- [ ] `scripts/lint-routers.py` correctly catches broken links and unindexed orphan files.
- [ ] Memory scaling boundaries are defined with clear file-count thresholds.
