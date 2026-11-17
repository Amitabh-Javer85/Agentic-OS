# Agentic OS — Skill Engine Specification

## Overview

The Skill Engine implements the **Skill Backbone** pattern. It provides a structured methodology and execution environment for turning manual, repetitive work into formalized, automated processes. 

Every domain has tasks, repeat tasks become skills, and reliable skills become automations. 

**Progression Path:**
`DOMAIN` (area of your life/business) → `TASK` (something you do again and again) → `SKILL` (the task written down, once, Claude runs it) → `AUTOMATION` (a skill that runs by itself)

---

## 1. The Skill Backbone Philosophy

The philosophy emphasizes **progressive automation** rather than immediate full automation. 

### Core Tenets
- **Manual → Skill → Automation:** Start by doing it manually. Once understood, encode it as a skill. Once proven reliable, schedule or trigger it automatically.
- **Rules of Thumb:**
  - *"Done it by hand twice → make it a skill"*
  - *"Skill works 5 times in a row → automate it"*
  - *"It sends, spends, or publishes → keep it manual (human-in-the-loop)"*
- **Portability:** Skills are filesystem-based, version-controlled, and readable by both humans and AI. They live in standard markdown and scripts.

---

## 2. Skill Definition Format

Every skill is defined by a `SKILL.md` file. This acts as both the prompt for the Agentic OS and the configuration file for the execution engine.

### SKILL.md Standard Template

```yaml
---
name: vault-cleanup
description: Archives old notes and organizes the vault
domain: memory
trigger:
  type: schedule  # schedule | event | manual
  schedule: "0 7 * * 0"  # Sundays at 7:00 AM
requires:
  - vault_read
  - vault_write
model: tier2  # tier1 (fast/cheap) | tier2 (balanced) | tier3 (complex reasoning)
human_review: false
automation_ready: true
created: 2026-01-15
last_run: 2026-09-24
run_count: 47
success_rate: 0.98
---
# Vault Cleanup

## Purpose
Archive notes older than 90 days that haven't been linked to main hub pages, ensuring the active workspace remains uncluttered.

## Steps
1. Scan `wiki/` for notes with no backlinks and `updated_at` > 90 days ago.
2. Move identified notes to `wiki/_archive/`.
3. Update `_master-index.md` to reflect changes.
4. Generate a cleanup report in `output/reports/`.

## Scripts
- `scripts/scan-orphans.py`
- `scripts/archive-notes.py`
```

---

## 3. Skill Directory Structure

Skills are organized by domain in the filesystem.

```text
skills/
├── _registry.md              # Master index of all skills and their status
├── memory/
│   └── vault-cleanup/
│       ├── SKILL.md
│       └── scripts/
├── productivity/
│   └── plan-today/
│       ├── SKILL.md
│       └── scripts/
├── research/
│   └── morning-intel/
│       ├── SKILL.md
│       └── scripts/
├── content/
│   └── content-cascade/
│       ├── SKILL.md
│       └── scripts/
├── community/
│   └── qa-digest/
│       ├── SKILL.md
│       └── scripts/
├── clients/
│   └── proposal/
│       ├── SKILL.md
│       └── scripts/
├── sales/
│   └── lead-research/
│       ├── SKILL.md
│       └── scripts/
└── finance/
    └── receipts/
        ├── SKILL.md
        └── scripts/
```

---

## 4. The Eight Domains

The OS categorizes operations into eight primary domains. Here is how skills map to these domains:

| Domain | Example Task | Skill Name | Trigger | Connectors |
|--------|-------------|------------|---------|------------|
| **Memory** | Tidy notes | `/vault-cleanup` | 📅 Sundays | Obsidian |
| **Productivity**| Plan my day | `/plan-today` | 📅 Daily 7:00 | Calendar, Gmail |
| **Research** | Catch up on AI news | `/morning-intel` | 📅 Daily 6:30 | X, GitHub, Web |
| **Content** | Repurpose videos | `/content-cascade` | ⚡ Video goes live | YouTube, LinkedIn |
| **Community** | Answer members | `/qa-digest` | 📅 Fridays | Discord |
| **Clients** | Write proposals | `/proposal` | 👆 Manual | Gmail, Docs |
| **Sales** | Research new leads | `/lead-research` | ⚡ Form submitted | Gmail, Web |
| **Finance** | Sort receipts | `/receipts` | 📅 1st of month | Gmail, Drive |

---

## 5. Skill Execution Engine

The Execution Engine is responsible for running skills reliably.

### Lifecycle
1. **Discovery & Selection:** JEV parses the user query or an automation trigger. It consults `skills/_registry.md` to identify the appropriate skill.
2. **Load:** The engine loads `SKILL.md`, parsing the YAML frontmatter for requirements and the markdown for instructions.
3. **Validate:** Checks if required connectors (`vault_read`, etc.) are authenticated and available.
4. **Execute:** 
   - Follows the `# Steps` sequentially.
   - Executes referenced scripts via secure sandboxing.
   - Streams progress updates to the UI/CLI.
5. **Verify:** Checks if the defined output state (e.g., report generated, files moved) matches expectations.
6. **Persist:** Updates the YAML frontmatter (`last_run`, `run_count`, `success_rate`).

### Handling Failures and Approval
- **Error Handling:** Built-in retry logic for transient errors (e.g., API timeouts). Hard errors halt execution and notify the user.
- **Human-in-the-Loop (HITL):** If `human_review: true`, the engine pauses before irreversible actions (sending emails, publishing posts, spending money) and prompts the user via the UI for approval.

---

## 6. Automation Layer

When `automation_ready: true` is set, the skill can be handed off to the Automation Layer.

- **n8n Integration:** The system syncs automated skills with an underlying n8n instance or a native scheduler.
- **Triggers:**
  - **Cron:** Managed via `schedule` in frontmatter (e.g., `0 7 * * *`).
  - **Webhooks:** Skills can expose a webhook endpoint for external services to trigger them.
  - **Event-Driven:** File watchers, email parsers, or form submissions.
- **Monitoring:** The OS tracks automation health, alerting the user if an automated skill fails consecutively.

---

## 7. Skill Lifecycle Management

### Creation
- **Conversational:** User asks JEV, "I do this task every day, can we make it a skill?" JEV scaffolding the directory and `SKILL.md`.
- **Templates:** Use `agentic-os create skill <name> --domain <domain>`.

### Promotion Path
1. **Testing:** Run manually via CLI/UI. `automation_ready: false`.
2. **Refinement:** Adjust prompts, add scripts for robustness.
3. **Promotion:** Once `success_rate` > 0.95 and `run_count` > 5, the system suggests marking `automation_ready: true`.

### Analytics
The system aggregates data from frontmatter to provide a dashboard:
- Top used skills
- Time saved (estimated)
- Failure bottlenecks

---

## 8. Built-in Starter Skills

The OS ships with templates for the 8 primary domains to help users bootstrap.

### 1. Memory: `/vault-cleanup`
```yaml
---
name: vault-cleanup
domain: memory
trigger: { type: schedule, schedule: "0 7 * * 0" }
model: tier2
human_review: false
automation_ready: true
---
# Vault Cleanup
## Purpose
Keep the knowledge graph clean by archiving stale, orphaned notes.
## Steps
1. Scan for notes without backlinks unmodified in 90 days.
2. Move to `_archive/`.
3. Append a summary to `_reports/weekly-cleanup.md`.
```

### 2. Productivity: `/plan-today`
```yaml
---
name: plan-today
domain: productivity
trigger: { type: schedule, schedule: "0 7 * * *" }
model: tier2
human_review: true
automation_ready: false
---
# Plan Today
## Purpose
Generate a daily briefing and time-block schedule.
## Steps
1. Read calendar events for today.
2. Read top priority items from `tasks.md`.
3. Generate a time-blocked schedule and draft an email to self.
4. WAIT FOR APPROVAL before sending email.
```

### 3. Research: `/morning-intel`
```yaml
---
name: morning-intel
domain: research
trigger: { type: schedule, schedule: "30 6 * * *" }
model: tier3
human_review: false
automation_ready: true
---
# Morning Intel
## Purpose
Summarize latest AI research and news.
## Steps
1. Fetch RSS feeds (HuggingFace, Arxiv AI).
2. Summarize top 5 papers.
3. Save to `wiki/research/daily-intel-{{date}}.md`.
```

### 4. Content: `/content-cascade`
```yaml
---
name: content-cascade
domain: content
trigger: { type: event, source: "youtube_publish" }
model: tier3
human_review: true
automation_ready: false
---
# Content Cascade
## Purpose
Turn a YouTube video into tweets and a LinkedIn post.
## Steps
1. Download video transcript.
2. Draft 1 LinkedIn post and a 3-tweet thread.
3. Save to `drafts/social/`.
4. WAIT FOR APPROVAL before queuing to Buffer.
```

### 5. Community: `/qa-digest`
```yaml
---
name: qa-digest
domain: community
trigger: { type: schedule, schedule: "0 17 * * 5" }
model: tier2
human_review: false
automation_ready: true
---
# QA Digest
## Purpose
Summarize weekly Discord Q&A for the newsletter.
## Steps
1. Fetch messages from `#q-and-a` channel for the last 7 days.
2. Extract the top 3 questions and answers.
3. Format as a markdown newsletter section in `community/digests/`.
```

### 6. Clients: `/proposal`
```yaml
---
name: proposal
domain: clients
trigger: { type: manual }
model: tier3
human_review: true
automation_ready: false
---
# Proposal Generator
## Purpose
Draft a client proposal based on meeting notes.
## Steps
1. Read `clients/meeting-notes/{{client_name}}.md`.
2. Generate a standard proposal utilizing `templates/proposal.md`.
3. Calculate estimated timelines.
4. Save draft to `clients/proposals/{{client_name}}-draft.md`.
```

### 7. Sales: `/lead-research`
```yaml
---
name: lead-research
domain: sales
trigger: { type: event, source: "typeform_submit" }
model: tier3
human_review: false
automation_ready: true
---
# Lead Research
## Purpose
Enrich inbound lead data before sales calls.
## Steps
1. Receive company domain from trigger.
2. Search web for company news, recent funding, and key executives.
3. Generate a brief in `sales/leads/{{company_name}}.md`.
4. Ping Slack channel `#sales` with a link to the brief.
```

### 8. Finance: `/receipts`
```yaml
---
name: receipts
domain: finance
trigger: { type: schedule, schedule: "0 9 1 * *" }
model: tier2
human_review: true
automation_ready: false
---
# Receipt Processor
## Purpose
Extract data from receipt PDFs and update the ledger.
## Steps
1. Scan `finance/inbox/` for PDF receipts.
2. Extract Date, Vendor, Amount, and Category.
3. Append rows to `finance/ledger.csv`.
4. Move processed PDFs to `finance/archive/{{YYYY-MM}}/`.
```
