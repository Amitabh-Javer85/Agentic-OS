# MASTER BUILDER PROMPT: AGENTIC OS (ARMS v2)

> **Instructions for the Coding Agent / Builder Session:**
> You are the Systems Engineer responsible for developing, maintaining, and extending **Agentic OS**.
> 
> Follow the modernized specifications in `specs/00` through `specs/04` and the task list in `TODO.md`.
> **Never revert to legacy middleware architecture.** Do not build custom proxy backends or distributed container networks when the agent CLI and native tools provide direct capabilities.

---

## 🎯 Architecture Directives

1. **Root Router (`CLAUDE.md`):** Always ensure the project root has a concise `CLAUDE.md` under 80 lines that links to `vault/AGENTS.md` and 1-page domain indexes in `memory/*.md`.
2. **The 60-Line Skill Standard:** Never author an individual `SKILL.md` file exceeding 60 lines. Decompose complex or multi-task workflows into a lean router file pointing to templates or scripts.
3. **Hardened Local Runner:** Any programmatic triggers must run through `apps/runner/server.py` or native CLI. Never introduce unauthenticated endpoints or shell execution (`shell=True` is strictly forbidden).
4. **Approval Queue for Risky Operations:** If a skill or routine sends emails, spends funds, deletes files, or publishes external data, it must write a payload to `output/approval_queue.jsonl` and exit cleanly. Never bypass human review in headless mode.
5. **Git-Centric State:** All skills, memory indexes, and code must be committed as clean atomic Git commits. Never rely on unversioned sync tools for primary state.
6. **Router Lint Verification:** After creating or relocating any documents, run `python scripts/lint-routers.py` to ensure zero broken links.

---

## 📋 Recommended Work Sequence

When picking up development tasks from `TODO.md`:
1. Check `output/runs.log` and `output/approval_queue.jsonl` for pending operational issues.
2. Run `python scripts/lint-routers.py` to verify documentation health.
3. Run `python tests/test_runner_security.py` before modifying runner logic.
4. Add new skills by running `/skill-creator` or following the `skills/weekly-digest` reference pattern.
5. Log every completed task in `TODO.md` and commit with a clean git message.
