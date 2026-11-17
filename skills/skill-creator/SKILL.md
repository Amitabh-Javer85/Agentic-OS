# Skill: Skill Creator

## Triggers
- Command: `/skill-creator`
- Phrases: "make this a skill", "create a skill for", "turn this into a skill"

## Input Discovery (Ask in One Batch)
1. **Trigger:** What `/name` and trigger phrases will invoke this skill?
2. **Steps:** What does a perfect run look like from input to output?
3. **Guardrails:** What should this skill NEVER do?
4. **Tools & Budget:** What tools does it need, and what is its maximum cost cap?

## Execution Steps
1. Create directory `skills/<skill-name>/`.
2. Write `skills/<skill-name>/skill.yaml` defining:
   - `name`, `description`, `model`, `effort`, `max_budget_usd`, `timeout_seconds`, `allowed_tools`, `risk_tier`.
3. Write `skills/<skill-name>/SKILL.md` (STRICTLY under 60 lines) containing:
   - Triggers, Router Table (if sub-files needed), Step-by-step instructions, and Hard Guardrails.
4. If the skill has complex templates, checklists, or scripts, place them in `templates/` or `scripts/`.
5. Add the new skill to the Active Skills list in [CLAUDE.md](../../CLAUDE.md).

## Guardrails
- NEVER write a single `SKILL.md` exceeding 60 lines; decompose thick skills into sub-files.
- NEVER permit destructive external actions (`send`, `spend`, `publish`) without setting `risk_tier: destructive_external` and specifying the HITL approval queue flow.
