---
name: plan-today
description: Build a focused daily plan from active tasks and an optional local calendar export.
---
# Daily Planning

Trigger: `/plan-today`, "plan my day", or "choose today's priorities".

1. Use today's local date (or the date explicitly supplied by the caller).
2. Read `TODO.md` and the active project pointers in `memory/CLIENTS.md`.
3. Read `vault/raw/calendar-YYYY-MM-DD.md` if present. Treat it as a read-only
   calendar export; include its timezone and fixed appointments in the plan.
   If absent, write "Calendar unavailable: no local export supplied" and avoid
   inventing meetings or claiming the day is free. MCP access requires a
   separately vetted read-only connector and an explicit manifest allowlist.
4. Choose exactly three actionable priorities using deadlines, blockers, and
   feasible effort. Cite the task or calendar source for each. If fewer than
   three real tasks exist, label a remaining slot "Unassigned".
5. Follow [plan-template.md](templates/plan-template.md). Save to
   `output/artifacts/daily-plan-YYYY-MM-DD.md`; do not overwrite an existing
   same-day plan unless the caller requests regeneration.
6. Add a relative Markdown link to the plan in `memory/CONTENT.md` in this run;
   retain existing pointers and keep the index under 50 lines.

Do not modify source tasks, calendar events, or `vault/raw/`. External changes,
messages, purchases, or publication requests belong in
`output/approval_queue.jsonl` as pending intents; do not execute them.
