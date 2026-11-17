# Agentic OS — Session Handover (ARMS v2)

Updated: 2026-11-16 (Africa/Johannesburg). Runtime inspected: Claude Code 2.1.316.

## Current state

Modules 1–6 remain the established baseline. Development for Modules 7–9 is
implemented, with the live checks below explicitly deferred by the operator.
Do not mark those checks complete based on offline tests.

- **Module 7:** `AgenticOS-WeeklyDigest` is registered in Windows Task Scheduler,
  `Ready`, every Friday at 09:00 SAST; next run at verification was
  2026-11-06 09:00. It runs as the current limited interactive user and requires
  sign-in. `scripts/register-routine.ps1` reproduces registration.
- **VPS deployment:** Prepared and locally tested; no remote or VPS was supplied.
  The operator chose to defer live deployment. Keep TODO 7.4 open.
- **Module 8:** Complete. Native MCP audit and community-server vetting SOP are in
  `docs/mcp-connectors.md`; the compact checklist is in `memory/SYSTEM.md`.
  The offline `apps/research-brief.html` micro-app builds cited extractive briefs
  and downloads Markdown; two real Chromium acceptance tests pass.
- **Module 9:** Three skills, manifests, templates, and golden fixtures are present:
  `plan-today`, `research-brief`, and `content-cascade`. Static validation passes.
  Direct Codex execution produced all three fixture outputs in isolated workspaces on 2026-11-16; output checks passed. This did not verify the Claude runner, scoped permissions, or per-run cost.
- **Fresh checkout:** Run `python scripts/init-workspace.py` first. It creates
  missing private data and governance files without overwriting existing data.

## Verified checks

These checks passed on this Windows workstation:

| Command | Result |
| --- | --- |
| `python tests/test_runner_security.py` | 5 HTTP security checks |
| `python tests/test_runner_execution.py` | 12 isolated execution regressions |
| `python tests/test_routines.py` | 6 real Git Bash tests with inert git/skill stubs |
| `python tests/test_workspace_init.py` | 3 isolated initialization tests |
| `python tests/test_micro_app.py` | 2 real Chromium end-to-end tests |
| `python tests/evaluate_skill_catalog.py` | Three catalog routers, runner-accepted manifests, fixtures, and template links |
| `python scripts/lint-routers.py` | No broken links or orphan artifacts |

The tests use Python's standard library except the optional browser suite,
which requires Playwright plus Chromium. No dependency installation was needed.
Router files remain below their line caps. Required checks ran before commits.
A clean staged-checkout snapshot was also initialized from scratch and passed
all 28 offline test cases, catalog validation, and router lint without private data.

## Codex weekly digest fixture

On 2026-11-16, Codex followed the weekly-digest skill in an isolated synthetic
Git workspace. Its report passed the five golden section checks, cited the two
recent commits and pending approval, and preserved inputs and the living pointer.
This does not verify execution by the scheduled Claude runner, its timeout or cost.
The Windows task currently reports Ready, but its action still requires Claude.

## Live runtime limitation

The manual weekly-digest run and isolated plan-today evaluation timed out at
180 seconds; no artifact was accepted. A subsequent minimal no-tool Claude
request returned **402 Insufficient credits** from the configured provider.
An isolated probe without inherited provider overrides returned **Not logged in**.
No credentials, global environment settings, or billing were changed. The operator
chose to finish offline checks and document pending live verification.

After restoring usable Claude access locally, run each feature independently:

```powershell
python tests/evaluate_skill_catalog.py --live --skill plan-today
python tests/evaluate_skill_catalog.py --live --skill research-brief
python tests/evaluate_skill_catalog.py --live --skill content-cascade
powershell -NoProfile -File scripts/run-routine.ps1 -SkillName weekly-digest
```

The catalog evaluator uses synthetic temporary workspaces, checks output evidence,
backlinks, living pointers, immutable sources, and budget caps. The direct Codex fixture checks are recorded in TODO 9.1–9.3. Run these commands to verify the separate Claude runtime when available. Do not substitute static checks or fabricated
artifacts for model execution. Headless output logs remain gitignored.

## MCP audit findings

The Claude runtime listed Context7, Figma, and Supabase as needing authentication;
Playwright failed to connect within 30 seconds. Google Workspace, Filesystem,
and n8n were not listed. No audited connection was healthy. Codex's connected
apps are separate from Claude's runtime configuration. Daily planning therefore
uses an optional local calendar Markdown export and explicitly reports missing
calendar input. No new MCP server was installed.

## Changes important to maintainers

- The runner now reads the actual registered SKILL.md into stdin; repository
  skills do not depend on globally installed slash commands.
- Manifests require explicit fields, positive finite budgets, valid timeouts,
  nonempty tool rules, and unique keys. Invalid manifests fail closed.
- `--tools` and `--allowed-tools` are both set; `dontAsk` denies prompts.
  `Edit(./path)` permissions cover Edit and Write. Scoped `Write(path)` rules
  never match Claude's file checks and are rejected. Ambient MCP and hooks are disabled.
- Windows npm shims resolve to the package's native executable (or Node entrypoint),
  preserving `shell=False`. Failure JSON retains reported cost and error details.
- Mutex acquisition is exclusive. A stale lock requires owner verification before
  manual removal; it is never automatically expired while another process may run.
- The Linux routine requires a clean tree and successful fast-forward pull,
  preserves failed skill exit codes, and queues publishing intent after success.
  Automatic `git add`/commit/push was removed because headless publishing must
  require human review. Approval status alone executes no external action.
- `.gitattributes` keeps Bash files on LF across Windows/Linux checkouts.

## Architectural invariants

1. Claude Code is the engine. Never add Docker, Redis, Qdrant, or backend proxies.
2. Do not modify or resurrect `_archive/` or `specs/_archive/`.
3. Keep every skill router strictly under 60 lines and provide `skill.yaml`.
4. Bind the runner only to `127.0.0.1`, require Bearer authentication on protected
   APIs, preserve origin checks, and execute subprocesses with `shell=False`.
5. Update `memory/*.md` pointers in the same turn as file creation/moves/deletion;
   preserve raw intake and keep memory indexes under 50 lines.
6. Send/spend/publish/delete intents go to `output/approval_queue.jsonl` in headless
   mode. Never convert a scheduling or sync task into automatic publication.
7. Commit reviewed code and documentation; exclude credentials, private vault
   content, and generated operational logs. No GitHub publication occurred.

## Next work

Restore Claude access and finish the three live skill acceptance checks, then
exercise the registered weekly run. Provision a VPS only when the operator
supplies a host and remote; follow `docs/routines.md` and retain publication review.
Module 10 remains future scope. See `git log` for separate routine, application,
and skill-catalog implementation commits; README contains the work-sample walkthrough.
