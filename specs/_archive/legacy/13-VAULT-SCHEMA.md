# AGENTIC OS — VAULT SCHEMA SPECIFICATION

This document defines the exact schema, templates, and validation rules for every file type in the vault.

## 1. File Naming Conventions

- **All files:** kebab-case (e.g., `machine-learning-transformers.md`)
- **Date-prefixed for timestamped content:** `2026-09-25-morning-intel.md`
- **Index files:** `_index.md`, `_master-index.md`
- **Templates:** `_template-{type}.md` (e.g., `_template-concept.md`)

## 2. YAML Frontmatter Schemas

Define complete schemas for each note type with required/optional fields, types, and validation rules:

### 2.1 Concept Note
```yaml
---
id: string (required, format: YYYYMMDD-type-slug)
title: string (required)
type: "concept" (required)
tags: string[] (required, format: domain/topic)
status: "seed" | "growing" | "evergreen" | "archived" (required)
aliases: string[] (optional)
sources: string[] (required, format: [[wikilink]])
related: string[] (optional, format: [[wikilink]])
created: datetime (required)
updated: datetime (required)
---
```

### 2.2 Entity Note
```yaml
---
id: string (required, format: YYYYMMDD-entity-slug)
name: string (required)
type: "entity" (required)
entity_type: "person" | "organization" | "tool" | "location" (required)
tags: string[] (optional)
aliases: string[] (optional)
related: string[] (optional, format: [[wikilink]])
created: datetime (required)
updated: datetime (required)
---
```

### 2.3 Raw Source Note
```yaml
---
id: string (required, format: YYYYMMDD-source-slug)
title: string (required)
type: "source" (required)
source_url: string (optional)
author: string (optional)
date_published: date (optional)
tags: string[] (optional)
related_concepts: string[] (optional, format: [[wikilink]])
created: datetime (required)
updated: datetime (required)
---
```

### 2.4 Daily Note
```yaml
---
id: string (required, format: YYYY-MM-DD-daily)
date: date (required, format: YYYY-MM-DD)
type: "daily" (required)
tags: ["journal/daily"] (required)
mood: string (optional)
metrics: object (optional, key-value pairs)
created: datetime (required)
updated: datetime (required)
---
```

### 2.5 Conversation Receipt
```yaml
---
id: string (required, format: YYYYMMDD-HHMMSS-receipt)
title: string (required)
type: "receipt" (required)
agent: string (required)
session_duration: number (optional, in seconds)
tokens_used: number (optional)
tags: ["log/conversation"] (required)
created: datetime (required)
---
```

### 2.6 Query Result
```yaml
---
id: string (required, format: YYYYMMDD-query-slug)
query: string (required)
type: "query" (required)
tags: ["log/query"] (required)
sources_used: string[] (required, format: [[wikilink]])
created: datetime (required)
---
```

### 2.7 Project Note
```yaml
---
id: string (required, format: YYYYMMDD-project-slug)
title: string (required)
type: "project" (required)
status: "planning" | "active" | "paused" | "completed" (required)
deadline: date (optional)
priority: "low" | "medium" | "high" | "critical" (required)
tags: string[] (required, format: project/topic)
related: string[] (optional, format: [[wikilink]])
created: datetime (required)
updated: datetime (required)
---
```

### 2.8 Skill Definition
```yaml
---
id: string (required, format: YYYYMMDD-skill-slug)
name: string (required)
type: "skill" (required)
description: string (required)
parameters: object (required, JSON Schema format)
tags: ["system/skill"] (required)
version: string (required, semantic versioning)
created: datetime (required)
updated: datetime (required)
---
```

### 2.9 Report
```yaml
---
id: string (required, format: YYYYMMDD-report-slug)
title: string (required)
type: "report" (required)
author: string (required, agent or user)
tags: string[] (required, format: report/topic)
period: string (optional, e.g., "2026-Q3")
created: datetime (required)
updated: datetime (required)
---
```

## 3. Content Structure Rules

- **Header hierarchy:** H1 = title, H2 = sections, H3 = subsections. Do not skip levels (e.g., H1 to H3).
- **Callout conventions:**
  - `> [!AI-Summary]` for auto-generated synopses.
  - `> [!Human-Note]` for manual user annotations.
  - `> [!Source]` for direct quotes or excerpts.
- **Link format:** Always use `[[wikilinks]]`. Never use standard markdown links `[text](url)` for internal vault references.
- **Code block formatting:** Always specify the language (e.g., ```python).
- **Image embedding conventions:** Use `![[image-name.png]]` syntax for local assets.

## 4. Validation Rules

- **Required frontmatter fields per type:** Must strictly adhere to the schemas defined in Section 2.
- **Valid status transitions:** e.g., Concept status must flow `seed` -> `growing` -> `evergreen`.
- **Link integrity:** No broken `[[links]]`; all referenced files must exist.
- **Tag taxonomy compliance:** Tags must exist in the defined taxonomy.
- **File naming pattern matching:** Must conform to the rules in Section 1.

## 5. Tag Taxonomy

Define the controlled vocabulary of tags:
```text
ai/
  ai/agents
  ai/retrieval
  ai/training
  ai/models
business/
  business/strategy
  business/marketing
  business/finance
tech/
  tech/architecture
  tech/devops
  tech/frontend
  tech/backend
system/
  system/config
  system/log
  system/skill
log/
  log/conversation
  log/query
  log/error
journal/
  journal/daily
  journal/weekly
```

## 6. Index File Formats

Define the structure for key navigation files:

- **_master-index.md (global table of contents):** Contains MOCs (Maps of Content) for top-level directories and core concepts. Uses dynamic queries (Dataview) where possible.
- **_index.md (per-folder index):** A high-level overview of the folder's purpose and a structured list or query of its contents.
- **_registry.md (skill registry):** A tabular summary of all registered skills in the vault, detailing Name, Version, Description, and link to the Skill Definition note.
