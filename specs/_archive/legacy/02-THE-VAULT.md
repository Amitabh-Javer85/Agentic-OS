# AGENTIC OS — THE VAULT SPECIFICATION

The Vault is the shared memory layer — an Obsidian vault of plain markdown files that serves as the persistent storage ("disk") of the Agentic OS.

Based on Karpathy's LLM Wiki methodology: "Compile, Don't Retrieve"

## 1. Vault Philosophy
- **Plain markdown files**: Universal, portable, and future-proof.
- **The AI organizes, the human dumps and reviews**: The human interface is optimized for rapid input; the AI handles the structuring.
- **Three-zone architecture**: `raw/` (inputs), `wiki/` (compiled knowledge), and `output/` (deliverables).
- **Immutable sources, living knowledge, compiled outputs**: Source material is never modified, knowledge base notes are constantly updated, and outputs are generated artifacts.
- **Wikilinks for knowledge graph navigation**: Every concept is explicitly linked `[[like this]]`, forming a dense graph.
- **Atomic notes (Zettelkasten-inspired)**: One primary concept per note to maximize reusability.

## 2. Directory Structure

The complete vault layout represents the flow of information through the OS:

```text
vault/
├── AGENTS.md                    # Agent constitution & rules
├── _config/
│   ├── schema.md                # Vault schema definition
│   ├── templates/               # Note templates
│   └── ontologies/              # Controlled vocabulary
├── raw/                         # Dump zone (human writes here)
│   ├── articles/
│   ├── tweets/
│   ├── papers/
│   ├── transcripts/
│   ├── voice-memos/
│   └── misc/
├── wiki/                        # Knowledge zone (AI writes here)
│   ├── _master-index.md         # Global index maintained by AI
│   ├── concepts/                # Abstract ideas & principles
│   ├── entities/                # People, tools, organizations
│   ├── syntheses/               # Topic summaries & reviews
│   └── [domain-folders]/        # Domain-specific wikis
│       ├── ai-agents/
│       │   ├── _index.md
│       │   ├── autonomous-coding.md
│       │   └── tool-use-patterns.md
│       ├── rag-systems/
│       │   ├── _index.md
│       │   ├── vector-databases.md
│       │   └── chunking-strategies.md
│       └── content-creation/
│           ├── _index.md
│           └── hook-frameworks.md
├── output/                      # Results zone (AI answers land here)
│   ├── query-results/
│   ├── reports/
│   ├── slide-decks/
│   └── daily-digests/
├── daily-notes/                 # Daily journal entries
├── conversations/               # Chat session logs
├── receipts/                    # Audit trail of every request
└── projects/                    # Active project folders
```

## 3. AGENTS.md (Agent Constitution)

The `AGENTS.md` file resides at the root and contains the absolute rules that all autonomous agents must follow when interacting with the vault.

### 3.1 Naming Conventions
- **Kebab-case strictly**: All files and folders must use `kebab-case.md` for maximum cross-platform compatibility and predictable URL encoding.
- **No spaces or special characters**: Spaces are forbidden. Special characters except hyphens are forbidden in filenames.

### 3.2 Linking Rules
- **Always use `[[wikilinks]]`**: When mentioning an entity or concept that exists or *should* exist, wrap it in double brackets.
- **Contextual linking**: Do not just list links at the bottom; weave them naturally into sentences.

### 3.3 Atomic Note Rules
- **One idea per note**: If a note grows beyond a single core concept, break it down and link the new sub-notes.

### 3.4 Provenance Rules
- **Backlink to raw sources**: Every claim, fact, or summary in the `wiki/` MUST include a citation back to the original document in the `raw/` folder.

### 3.5 AI Content Marking
- **Use callouts**: Sections generated autonomously by the agent must be marked using Obsidian callout blocks (e.g., `> [!ai] Generated autonomously`).

### 3.6 Forbidden Operations
- **NEVER delete `raw/` files**: The ingest zone is append-only.
- **NEVER edit without backlinks**: You cannot update a wiki page without citing the source of the new information.

## 4. Note Templates

YAML frontmatter ensures consistent metadata for querying.

### 4.1 Concept Note
```yaml
---
type: concept
aliases: []
tags: []
date_created: {{date}}
date_modified: {{date}}
status: seed | growing | evergreen
---
```

### 4.2 Entity Note
```yaml
---
type: entity
category: person | organization | tool
aliases: []
tags: []
url: ""
related_concepts: []
---
```

### 4.3 Raw Source Note
```yaml
---
type: raw
source_type: article | tweet | paper | transcript | memo | misc
author: ""
url: ""
date_ingested: {{date}}
processed: false
---
```

### 4.4 Daily Note
```yaml
---
type: daily
date: {{date}}
mood: ""
focus: ""
---
```

### 4.5 Conversation Receipt
```yaml
---
type: receipt
session_id: ""
date: {{date}}
tokens_used: 0
primary_agent: ""
---
```

### 4.6 Query Result
```yaml
---
type: output
query: ""
date_generated: {{date}}
sources_used: []
---
```

### 4.7 Project Note
```yaml
---
type: project
status: active | archived | planned
deadline: ""
priority: high | medium | low
---
```

## 5. The Three Core Operations

### 5.1 Ingest (`raw/` → `wiki/`)
- **Trigger**: New files appear in the `raw/` directory.
- **Process**:
  - The AI agent parses the raw document.
  - Extracts key entities and concepts.
  - Creates new pages in `wiki/` or updates existing ones.
  - Maintains strict backlinks to the original file in `raw/`.
  - Updates the `_master-index.md` and domain-specific `_index.md` files.
  - The `raw/` file's YAML frontmatter `processed` flag is set to `true`.

### 5.2 Query (`wiki/` → `output/`)
- **Trigger**: The user asks a question or requests a report.
- **Process**:
  - The AI searches the `wiki/` zone exclusively (relying on pre-compiled knowledge, avoiding the noise of `raw/`).
  - Synthesizes the answer from the atomic notes.
  - Creates a formatted deliverable.
  - The deliverable is saved to the `output/` directory with proper citations back to the `wiki/` pages.

### 5.3 Lint (`wiki/` maintenance)
- **Trigger**: Run on a schedule or manual command.
- **Process**:
  - Scan for orphan notes and attempt to link them.
  - Detect broken `[[wikilinks]]` and either create stubs or fix typos.
  - Identify duplicate concepts and merge them.
  - Flag outdated information.
  - Reconcile conflicting facts by comparing source materials.

## 6. Metadata Schema

Standard YAML frontmatter fields applied across the vault:
- **`type`**: (Required) Must match an allowed template type.
- **`tags`**: (Optional) Array of strings. Use standard taxonomy defined in `_config/ontologies/`.
- **`aliases`**: (Optional) Array of strings. Alternative names for wikilink resolution.
- **`date_created`**: (Required) ISO 8601 format.
- **`date_modified`**: (Required) ISO 8601 format.
- **`processed`**: (Boolean) Only used for `raw/` notes to track ingestion status.

## 7. Vault Access Methods

The OS interacts with the Vault through several interfaces:
1. **Obsidian Local REST API (port 27124)**: Allows agents to perform live reads/writes while the Obsidian app is open, providing immediate visual feedback to the user.
2. **Direct filesystem access**: For high-performance, bulk operations, or CLI tools running in the background.
3. **MCP (Model Context Protocol) server**: For secure, standardized access by LLM agents, abstracting file operations into semantic endpoints.
4. **Dataview queries**: For structured retrieval within the vault itself.
