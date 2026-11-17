# Skill: Weekly Digest

## Triggers
- Command: `/weekly-digest`
- Phrases: "generate weekly digest", "compile weekly summary", "run weekly report"

## Router Table
| Task / Sub-function | Reference File | Action |
| :--- | :--- | :--- |
| **Output Structure** | [digest-template.md](templates/digest-template.md) | Follow exact markdown layout |
| **Git Log Review** | Git history | Run `git log --since="7 days ago" --oneline` |

## Execution Steps
1. Run `git status` and `git log --since="7 days ago" --oneline` to review recent activity.
2. Scan `output/artifacts/` for deliverables created during the past 7 days.
3. Check `output/approval_queue.jsonl` for pending human-in-the-loop items.
4. Read [digest-template.md](templates/digest-template.md) and fill each section with concrete facts.
5. Save the output to `output/artifacts/weekly-digest-YYYY-MM-DD.md`.
6. Update [CONTENT.md](../../memory/CONTENT.md) with a pointer to the newly generated digest.

## Guardrails
- NEVER make external network requests or attempt to publish output automatically.
- NEVER modify files in `vault/raw/`.
- If no git commits exist in the past 7 days, state "No recent commits" rather than hallucinating changes.
