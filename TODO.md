# Agentic OS — Modular Task & Verification Tracker (ARMS v2)

This task tracker divides the implementation and evolution of Agentic OS into discrete, modular features. Each feature includes clear implementation tasks and an explicit **Verification Check** to confirm functionality before checking off.

---

## 🟢 Module 1: Foundation & Security Hardening (Zero-RCE Runner)
*Architecture, loopback isolation, authentication, and execution boundaries.*

- [x] **1.1 Legacy Code & Spec Archival**
  - *Tasks:* Tag Git repository `v0.1-legacy-specs`, move legacy specs (`00`-`15`) to `specs/_archive/legacy/`, move legacy bridge to `_archive/legacy-bridge/`.
  - *Verification:* `git tag` lists `v0.1-legacy-specs`; `Get-ChildItem specs/_archive/legacy` shows 16 archived files.
- [x] **1.2 Loopback HTTP Runner Server**
  - *Tasks:* Build `apps/runner/server.py` binding strictly to `127.0.0.1:3000` (IPv4 loopback).
  - *Verification:* `curl -I http://127.0.0.1:3000/` returns `200 OK`; external interface binding attempts fail.
- [x] **1.3 Cryptographic Token Authentication**
  - *Tasks:* Implement `get_or_create_token()` generating `.local-token` (mode `0600`). Enforce `Authorization: Bearer <token>` on all `/api/v1/*` routes.
  - *Verification:* Requests without token return HTTP `401 Unauthorized`; requests with valid token return `200 OK`.
- [x] **1.4 Cross-Origin & DNS Rebinding Shield**
  - *Tasks:* Validate `Origin` and `Referer` headers against `127.0.0.1` and `localhost`. Drop untrusted origins with HTTP `403`.
  - *Verification:* `python tests/test_runner_security.py` asserts cross-origin POST returns `403 Forbidden`.
- [x] **1.5 Skill Allowlist & Subprocess Safety**
  - *Tasks:* Dynamic discovery of registered skills in `skills/`. Enforce `shell=False` execution. Reject arbitrary command injection.
  - *Verification:* Executing `"rm -rf /"` returns HTTP `400 Bad Request`.
- [x] **1.6 Concurrency Mutex File Lock**
  - *Tasks:* Implement `.workspace.lock` preventing simultaneous conflicting agent writes.
  - *Verification:* Runner returns HTTP `423 Locked` if lock is held by an active process.

---

## 🟢 Module 2: Memory & Router Index Architecture
*Master workspace navigation, area indexes, and automated link integrity.*

- [x] **2.1 Root Master Workspace Router**
  - *Tasks:* Write `./CLAUDE.md` at repository root (<80 lines), importing `vault/AGENTS.md` and defining the domain router table.
  - *Verification:* Claude Code session startup auto-detects `./CLAUDE.md`.
- [x] **2.2 Domain Area Index Creation**
  - *Tasks:* Create 1-page domain indexes (`memory/SYSTEM.md`, `memory/CONTENT.md`, `memory/CLIENTS.md`) under 50 lines each with single-line pointers.
  - *Verification:* Each markdown file in `memory/` is under 50 lines.
- [x] **2.3 Existing Vault Content Preservation**
  - *Tasks:* Preserve `vault/raw/`, `vault/wiki/`, and `vault/AGENTS.md` without destructive alteration; index them in router files.
  - *Verification:* `vault/AGENTS.md` and `example-vault/wiki/index.md` remain intact and readable.
- [x] **2.4 Automated Router Link Linter**
  - *Tasks:* Build `scripts/lint-routers.py` to validate all markdown links in routers and detect orphan files in `vault/wiki/` and `output/artifacts/`.
  - *Verification:* `python scripts/lint-routers.py` outputs `SUCCESS: All router links verified` and exits with code `0`.

---

## 🟢 Module 3: Skill Engine & Skill Trees
*Codifying standard operating procedures into <60 line router trees.*

- [x] **3.1 Unified Skill Manifest Specification**
  - *Tasks:* Standardize `skill.yaml` schema (`name`, `model`, `effort`, `max_budget_usd`, `timeout_seconds`, `allowed_tools`, `risk_tier`).
  - *Verification:* `skills/weekly-digest/skill.yaml` validates against runner parser.
- [x] **3.2 Reference Skill: Weekly Digest Tree**
  - *Tasks:* Author `skills/weekly-digest/SKILL.md` (<60 lines) + `templates/digest-template.md`.
  - *Verification:* Line count of `skills/weekly-digest/SKILL.md` is strictly under 60 lines.
- [x] **3.3 Meta-Skill: Skill Creator**
  - *Tasks:* Author `skills/skill-creator/SKILL.md` (<60 lines) to guide authoring new skills following ARMS standards.
  - *Verification:* Line count is strictly under 60 lines and follows the 1-batch question prompt pattern.
- [x] **3.4 Skill Evaluation Fixture**
  - *Tasks:* Create `tests/golden-prompts/weekly-digest-eval.json` defining input context, required section assertions, and cost caps.
  - *Verification:* Fixture file exists and parses as valid JSON with assertion rules.

---

## 🟢 Module 4: Headless Execution & Audit Logging
*Non-interactive execution, budgeting, and atomic JSONL telemetry.*

- [x] **4.1 Headless CLI Invocation Wrapper**
  - *Tasks:* Build `execute_skill(skill_name)` in `server.py` executing `claude -p` with `--allowed-tools`, `--max-budget-usd`, and `--output-format json`.
  - *Verification:* Running `python apps/runner/server.py trigger weekly-digest` executes cleanly.
- [x] **4.2 Atomic JSONL Execution Logging**
  - *Tasks:* Implement automatic logging to `output/runs.log` with `run_id`, `timestamp`, `skill`, `model`, `duration_ms`, `exit_code`, and `cost_usd`.
  - *Verification:* Inspecting `output/runs.log` confirms valid JSON lines formatted per spec.
- [x] **4.3 Automated Security Test Suite**
  - *Tasks:* Create `tests/test_runner_security.py` verifying loopback binding, auth rejection, origin rejection, and skill allowlisting.
  - *Verification:* `python tests/test_runner_security.py` outputs `5 PASSED, 0 FAILED`.

---

## 🟢 Module 5: Visual Command Centre (Dashboard)
*Single-page, zero-dependency operator portal.*

- [x] **5.1 Zero-Framework HTML Dashboard**
  - *Tasks:* Build `apps/command-centre/index.html` with responsive dark-mode styling and zero external CDN/npm dependencies.
  - *Verification:* Page loads cleanly offline from `http://127.0.0.1:3000/`.
- [x] **5.2 Headless Skill Launcher Panel**
  - *Tasks:* Display registered skills dynamically via `GET /api/v1/status` with one-click trigger buttons.
  - *Verification:* Clicking "Trigger Run" executes the skill and updates the UI button state to "Running...".
- [x] **5.3 Artifacts Stream Panel**
  - *Tasks:* Poll `GET /api/v1/artifacts` to display recent files in `output/artifacts/` with copy-path shortcuts.
  - *Verification:* New files saved in `output/artifacts/` appear dynamically in the dashboard table.
- [x] **5.4 Execution Audit Log Panel**
  - *Tasks:* Poll `GET /api/v1/runs` to display the last 10 executions, exit statuses, durations, and dollar costs.
  - *Verification:* Runs logged to `output/runs.log` render in the dashboard table.

---

## 🟢 Module 6: HITL Approval Queue & Safety Governance
*Human-in-the-loop confirmation gates for high-stakes actions.*

- [x] **6.1 JSONL Approval Queue Storage**
  - *Tasks:* Initialize `output/approval_queue.jsonl` schema for pending `send`, `spend`, or `publish` intent records.
  - *Verification:* File exists and supports structured append operations.
- [x] **6.2 Approval & Rejection API Endpoints**
  - *Tasks:* Implement `POST /api/v1/approval-queue/{id}/approve` and `reject` in `server.py`.
  - *Verification:* Status flips from `"pending"` to `"approved"` or `"rejected"` with timestamp.
- [x] **6.3 Command Centre Review Widget**
  - *Tasks:* Add approval queue review section in `apps/command-centre/index.html` with working Approve / Reject buttons.
  - *Verification:* Pending items render in the queue card and disappear when resolved.

---

## 🟡 Module 7: Automated Scheduled Routines (Local & Cloud)
*Unattended execution via operating system schedulers and Git synchronization.*

- [x] **7.1 Windows Scheduled Task Script**
  - *Tasks:* Write `scripts/run-routine.ps1` to execute registered routines from Windows Task Scheduler.
  - *Verification:* Running `.\scripts\run-routine.ps1 -SkillName "weekly-digest"` triggers execution.
  - *Codex fixture result (2026-11-16):* A direct isolated Codex execution generated the weekly digest with all five required sections, recent fictional Git history, artifact and pending approval; raw inputs and approval queue remained unchanged. This does not verify the scheduled Claude runner or its cost cap.
- [x] **7.2 Linux VPS Crontab Script**
  - *Tasks:* Write `scripts/run-routine.sh` including `git pull --rebase` before execution and atomic `git commit` + `git push` upon completion.
  - *Verification:* Script passes syntax check via `bash -n scripts/run-routine.sh`.
- [x] **7.3 Register First Local Scheduled Routine**
  - *Tasks:* Register a weekly Task Scheduler job on Windows for `weekly-digest` running every Friday morning.
  - *Verification:* Windows Task Scheduler shows task `AgenticOS-WeeklyDigest` in `Ready` state.
  - *Result (2026-11-05):* Registered for Friday 09:00 SAST as the limited current interactive user; native query reports `Ready`, next run 2026-11-06 09:00. Reproducible registration: `scripts/register-routine.ps1`.
- [ ] **7.4 VPS Git Auto-Sync Deployment**
  - *Tasks:* Provision a user-supplied Linux VPS and Git remote, configure read-only SSH pull access, and add a weekly cron entry. Queue publishing intent for human review.
  - *Verification:* VPS routine produces an artifact; after human-reviewed publication the workstation pulls the selected artifact and pointer down.
  - *Pending:* No Git remote or VPS target supplied. Deployment instructions and fail-closed scripts are prepared in `docs/routines.md`; local checks do not establish a live VPS round trip. Automatic headless `git push` was removed to preserve the publish approval rule.

---

## 🟢 Module 8: MCP Connectors & Application Integrations
*Plugging real tools into the agent via Model Context Protocol.*

- [x] **8.1 Model Context Protocol (MCP) Audit**
  - *Tasks:* Audit installed MCP servers (Google Workspace, Filesystem, n8n) and document capabilities.
  - *Verification:* MCP server status verified using native agent tools.
  - *Result (2026-11-05):* Native `claude mcp list` audited four configured plugins: three need authentication, Playwright timed out. Google Workspace/Filesystem/n8n are not listed. Capabilities and limitations recorded in `docs/mcp-connectors.md`; audit completion does not imply healthy connections.
- [x] **8.2 Safe GitHub MCP Server Vetting SOP**
  - *Tasks:* Codify procedure for researching, inspecting permissions, and installing community MCP servers with safe read-only tests.
  - *Verification:* Add SOP checklist to `memory/SYSTEM.md`.
- [x] **8.3 First Micro-App Creation (Applications L3)**
  - *Tasks:* Build a single-file micro-app (e.g. YouTube research summarizer or receipt extractor) stored in `apps/`.
  - *Verification:* Launch and execute the micro-app end-to-end.
  - *Result:* `apps/research-brief.html` opens offline; `python tests/test_micro_app.py` passes two real Chromium acceptance tests covering cited excerpts, Markdown download, invalid input, stale output prevention, and inert HTML. No model/API/network dependency.

---

## 🟢 Module 9: Skill Catalog Expansion (Starter Packs)
*Expanding capability across core personal operating domains.*

Implementation is present for all three skills, with scoped manifests, templates,
golden fixtures, and `tests/evaluate_skill_catalog.py`. Offline catalog checks pass.
On 2026-11-16, Codex executed each skill directly against its synthetic golden fixture in an isolated workspace. Output, source links, pointers, and source immutability passed. These checks do not establish Claude runner execution, manifest permission enforcement, or dollar cost; the standalone Codex CLI could not access the models tested.

- [x] **9.1 Domain Skill: Daily Planning (`skills/plan-today`)**
  - *Tasks:* Create `skill.yaml` and `SKILL.md` to scan daily calendar and active tasks to output a focused 3-priority plan.
  - *Verification:* Produces `output/artifacts/daily-plan-YYYY-MM-DD.md`.
  - *Result:* Direct Codex fixture execution produced a dated plan with three priorities and disclosed the unavailable calendar; existing output assertions passed. Cost was not measured.
- [x] **9.2 Domain Skill: Research Synthesis (`skills/research-brief`)**
  - *Tasks:* Create skill to read raw notes from `vault/raw/`, extract key insights, and compile an evergreen note into `vault/wiki/`.
  - *Verification:* Evergreen note generated with proper YAML frontmatter and backlinks.
  - *Result:* Direct Codex fixture execution produced a source-linked note and passed output assertions; the raw source remained unchanged and embedded instructions were not executed. Cost was not measured.
- [x] **9.3 Domain Skill: Content Draft Cascade (`skills/content-cascade`)**
  - *Tasks:* Turn long-form notes into thread outlines and newsletter drafts following verified templates.
  - *Verification:* Outputs formatted draft in `output/artifacts/`.
  - *Result:* Direct Codex fixture execution produced a source-linked draft and passed output assertions; the approval queue remained empty. Cost was not measured.

---

## ⚪ Module 10: Advanced Memory & Hybrid Scaling (Future Phase)
*Scaling past 2,000 files.*

- [ ] **10.1 File Count Monitoring in Linter**
  - *Tasks:* Add total indexed file count to `output/artifacts/lint-report.md`.
  - *Verification:* Report displays current total workspace note count.
- [ ] **10.2 Local SQLite FTS5 Full-Text Search Script**
  - *Tasks:* When workspace exceeds 2,000 files, build an incremental SQLite FTS5 indexer to provide instant local full-text search without external APIs.
  - *Verification:* Full-text search returns ranked results in <50ms.
