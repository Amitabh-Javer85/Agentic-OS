# Content & Research Domain Index

## Active Research & Notes
- [Field Notes: Fictional Garden](../example-vault/wiki/index.md) — Fictional demo note from example vault
- [ARMS Migration Plan](../specs/00-OVERVIEW.md) — Architectural modernization overview

## Output Artifacts & Reports
- [Router Lint Report](../output/artifacts/lint-report.md) — Output of weekly automated router linting
- [Execution Audit Log](../output/runs.log) — Master JSONL log of all headless runs
- [Approval Queue](../output/approval_queue.jsonl) — Pending human-in-the-loop requests

## Knowledge Base Vault
- [Vault Raw Intake](../vault/raw/) — Immutable external source material
- [Vault Compiled Wiki](../vault/wiki/) — Synthesized evergreen notes

## Starter Skills & Evaluation
- [Daily plan](../skills/plan-today/SKILL.md), [manifest](../skills/plan-today/skill.yaml), [template](../skills/plan-today/templates/plan-template.md) — Three priorities and calendar availability
- [Research brief](../skills/research-brief/SKILL.md), [manifest](../skills/research-brief/skill.yaml), [template](../skills/research-brief/templates/brief-template.md) — Source-linked evergreen synthesis
- [Content cascade](../skills/content-cascade/SKILL.md), [manifest](../skills/content-cascade/skill.yaml), [template](../skills/content-cascade/templates/cascade-template.md) — Thread and newsletter drafts
- [Skill creator manifest](../skills/skill-creator/skill.yaml) — Explicit tools and budget for meta-skill
- [Catalog evaluator](../tests/evaluate_skill_catalog.py) — Static checks and isolated budgeted live evaluations
- [Runner execution tests](../tests/test_runner_execution.py) — Offline permission, budget, failure, and mutex regression checks
- [Planning fixture](../tests/golden-prompts/plan-today-eval.json), [research fixture](../tests/golden-prompts/research-brief-eval.json), [draft fixture](../tests/golden-prompts/content-cascade-eval.json) — Synthetic evidence and output assertions
