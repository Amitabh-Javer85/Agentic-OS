# AGENTIC OS — SKILLS & ROUTINES SPECIFICATION

## 1. The ARMS Skills Philosophy

A skill is a standardized operating procedure codified as an executable command.
* **The Do-It-Twice Rule:** When you perform the same task by hand twice, turn it into a skill.
* **The 60-Line Rule:** Keep `SKILL.md` under 60 lines. Short skills get followed; long skills get skimmed or misapplied.
* **Skill Trees:** When a skill exceeds 150 lines or handles multiple tasks, decompose it into a lean router `SKILL.md` that directs the agent to read *only* the matching sub-file (template, checklist, script).
* **Headless Triggering:** Skills can run interactively in chat or non-interactively via the CLI runner (`claude -p`).

---

## 2. Unified Skill Manifest Schema (`skill.yaml`)

Every skill directory contains a `skill.yaml` (or frontmatter) defining its execution parameters:

```yaml
name: weekly-digest
description: Aggregates project logs and weekly notes into an executive status summary.
version: "1.0.0"
model: sonnet                   # Alias: haiku | sonnet | opus (parameterized, not hardcoded)
effort: medium                  # CLI --effort flag: low | medium | high | max
max_budget_usd: 0.35            # Hard dollar spend cap per run
timeout_seconds: 180            # Execution timeout before process kill
allowed_tools:                  # Strict tool allowlist (passed to --allowed-tools)
  - "Read"
  - "Edit"
  - "Bash(git status)"
  - "Bash(git log*)"
risk_tier: internal_write       # read_only | internal_write | destructive_external
schedule: "0 9 * * 5"           # Cron schedule (optional)
```

---

## 3. Skill Tree & Router Directory Structure

```text
skills/
├── skill-creator/               # Meta-skill to author new skills
│   └── SKILL.md
└── weekly-digest/               # Domain skill tree
    ├── skill.yaml               # Manifest with execution boundaries
    ├── SKILL.md                 # Lean router (<60 lines)
    ├── templates/
    │   └── digest-template.md   # Output markdown structure
    └── scripts/
        └── extract-git-logs.py  # Local deterministic helper script
```

---

## 4. Headless Execution Engine & Audit Logging

Headless skills are invoked by the runner using the non-interactive CLI:
```powershell
claude -p "/weekly-digest" --allowed-tools "Read,Edit,Bash(git status)" --max-budget-usd 0.35 --effort medium --output-format json
```

### JSONL Run Audit Log (`output/runs.log`)
Every headless invocation appends an atomic JSON line to `output/runs.log`:

```json
{
  "run_id": "run-20261105-173000-101",
  "timestamp": "2026-11-05T17:30:00Z",
  "skill": "weekly-digest",
  "model": "claude-sonnet-4-6",
  "effort": "medium",
  "duration_ms": 12450,
  "exit_code": 0,
  "cost_usd": 0.038,
  "output_path": "output/artifacts/weekly-digest-2026-w45.md",
  "approval_requested": false,
  "error": null
}
```

---

## 5. Routines (Automated Scheduled Workflows)

Routines are scheduled prompts that execute without an interactive user watching.

### 5.1 Local Scheduling (Windows)
Registered using native Windows Task Scheduler via PowerShell (`scripts/run-routine.ps1`):
```powershell
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At 9:00AM
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "apps/runner/server.py trigger weekly-digest"
Register-ScheduledTask -TaskName "AgenticOS-WeeklyDigest" -Trigger $Trigger -Action $Action
```

### 5.2 Always-On Cloud Scheduling (Linux VPS)
Registered in crontab via `scripts/run-routine.sh`:
```bash
0 9 * * 5 cd /home/agent/Agentic-OS && ./scripts/run-routine.sh weekly-digest >> output/cron.log 2>&1
```

---

## 6. Skill Evaluation Test Suite (Golden Prompts)

To ensure skills do not regress across model or prompt updates, every skill includes an evaluation fixture in `tests/golden-prompts/<skill>-eval.json`:
* **Input:** Sample input context or trigger payload.
* **Expected Output Checks:**
  1. File output was generated in `output/artifacts/`.
  2. Output contains required H2 section headers.
  3. No unapproved destructive tool calls were attempted.
  4. Cost remained strictly below `max_budget_usd`.

---

## 7. Acceptance Criteria

- [ ] All `SKILL.md` router files are verified under 60 lines.
- [ ] Skill manifest validates `allowed_tools`, `max_budget_usd`, and `timeout_seconds`.
- [ ] Headless runner logs valid JSON lines matching the schema to `output/runs.log`.
- [ ] Scheduled routine script works across both Windows PowerShell and Linux bash.
- [ ] At least one skill evaluation runs against a golden prompt fixture and asserts success.
