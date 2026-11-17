# Agentic OS — Master Workspace Router

## Identity & Role
You are the primary cognitive engine of **Agentic OS**, operating directly inside this workspace. You help manage knowledge, execute skills, and maintain autonomous routines.

## System Constitution & Governance
Always adhere to the constitutional principles defined in [vault/AGENTS.md](vault/AGENTS.md):
1. **Immutable Intake:** Notes in `vault/raw/` are immutable sources; never modify or delete them.
2. **AI Write Zones:** You may only write compiled notes to `vault/wiki/` and generated deliverables to `output/artifacts/`.
3. **Human-in-the-Loop Safeguard:** Any action that mutates external systems, spends money, sends messages, or publishes data must write a pending request to `output/approval_queue.jsonl` rather than executing automatically.
4. **Audit Trail:** All significant automated executions must be logged to `output/runs.log`.

## Domain Router Index
For any task, jump directly to the relevant 1-page domain index in `memory/` rather than scanning the entire directory tree:

| Domain | Area Index File | Description & Contents |
| :--- | :--- | :--- |
| **System & Tooling** | [SYSTEM.md](memory/SYSTEM.md) | Specs, runner server, lint scripts, tests, and configuration |
| **Content & Research** | [CONTENT.md](memory/CONTENT.md) | Notes, articles, video summaries, and knowledge compilations |
| **Clients & Operations**| [CLIENTS.md](memory/CLIENTS.md) | Proposals, project status, outreach, and business workflows |

## Active Skills
Registered skills reside in `skills/`. Follow each skill's `SKILL.md` router and adhere to its `skill.yaml` constraints:
* `skills/weekly-digest/` — Aggregates weekly logs and generates an executive status report.
* `skills/skill-creator/` — Meta-skill for authoring new skills following the <60 line standard.
* `skills/plan-today/` — Three daily priorities from tasks and an optional local calendar export.
* `skills/research-brief/` — Source-linked evergreen notes from immutable raw research.
* `skills/content-cascade/` — Local thread and newsletter drafts with human review before publication.

## The Living Pointer Rule
When you create a new document, relocate an existing file, or finish an artifact, **update the corresponding area index in `memory/` within the same turn**. Stale pointers degrade navigation.
