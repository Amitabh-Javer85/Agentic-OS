# System & Tooling Domain Index

## Active Specifications
- [00: Overview & Principles](../specs/00-OVERVIEW.md) — Vision, ARMS principles, and scope
- [01: Architecture & Security](../specs/01-ARCHITECTURE-AND-SECURITY.md) — Zero-RCE runner, Git sync, HITL approval queue
- [02: Skills & Routines](../specs/02-SKILLS-AND-ROUTINES.md) — Skill manifests, headless execution, and runs.log
- [03: Memory & Routers](../specs/03-MEMORY-AND-ROUTERS.md) — Root router standards, index rules, and linter
- [04: Visual Command Centre](../specs/04-COMMAND-CENTRE.md) — Single-page dashboard and static API

## Applications & Infrastructure
- [Local Runner Server](../apps/runner/server.py) — Hardened 127.0.0.1 execution runner and API
- [Visual Command Centre UI](../apps/command-centre/index.html) — Local web dashboard
- [Command Centre screenshot](../docs/command-centre-demo.png) — Local app displaying fictional approvals, artifacts, and runs
- [Router Linter Script](../scripts/lint-routers.py) — Link validator and orphan file detector
- [Workspace Initializer](../scripts/init-workspace.py) — Create missing private vault/output paths after cloning; preserve existing data
- [Initializer Acceptance Checks](../tests/test_workspace_init.py) — Clean-checkout lint and private-file preservation
- [Windows Routine Runner](../scripts/run-routine.ps1) — PowerShell scheduled task runner
- [Linux Routine Runner](../scripts/run-routine.sh) — Bash crontab runner
- [Task Registration](../scripts/register-routine.ps1) — Friday 09:00 limited current-user scheduled task
- [Routine Operations](../docs/routines.md) — Windows verification and approval-gated VPS deployment
- [Routine Acceptance Checks](../tests/test_routines.py) — Real Bash with isolated git/skill stubs; failure gates and pending publication
- [Git Line Endings](../.gitattributes) — Keep Bash routines executable after Windows/Linux checkouts
- [MCP Connector Audit & Vetting](../docs/mcp-connectors.md) — Native runtime health, capabilities, and community-server review SOP
- [Evidence Desk](../apps/research-brief.html) — Offline single-file research brief builder; local Markdown export
- [Micro-App Browser Acceptance](../tests/test_micro_app.py) — End-to-end build, attribution, download, validation, and inert-input checks

## MCP Vetting Checklist
- Review upstream source/version and tool effects; restrict scopes; pin; authorize install; check native health and disposable read-only test; record review and rollback in the [SOP](../docs/mcp-connectors.md).

## Governance & Archive
- [Session Handover](../HANDOVER.md) — Current state, architecture decisions, and next steps
- [Vault Constitution](../vault/AGENTS.md) — AI write rules and permission limits
- [Legacy Specs Archive](../specs/_archive/legacy/) — Tagged v0.1 legacy specifications
- [Legacy Bridge Archive](../_archive/legacy-bridge/) — Archived FastAPI demo code
