# AGENTIC OS — ARCHITECTURE & SECURITY SPECIFICATION

## 1. System Architecture

The modern Agentic OS architecture eliminates heavy middleware daemons and connects the user interface directly to filesystem-backed state and the Claude Code agent runtime.

```mermaid
flowchart TD
    subgraph UI ["User Interfaces"]
        CC["Command Centre (HTML Dashboard)\nhttp://127.0.0.1:3000"]
        Terminal["Interactive Terminal\n(claude CLI)"]
    end

    subgraph SecurityBoundary ["Security & Execution Boundary (127.0.0.1 Only)"]
        Runner["Secure Local Runner (apps/runner/server.py)\n- Bearer Token Auth\n- Strict Origin Check\n- Fixed Skill Allowlist\n- shell=False Subprocess"]
        Lock[("workspace.lock (File Mutex)")]
        ApprovalQueue[("output/approval_queue.jsonl\n(HITL Gate)")]
    end

    subgraph ClaudeRuntime ["Claude Code Engine"]
        CLI["claude -p /<skill>\n--allowed-tools <list>\n--max-budget-usd <cap>\n--effort <level>\n--output-format json"]
    end

    subgraph MemoryLayer ["Memory & Workspace (Git Tracked)"]
        RootRouter["./CLAUDE.md (Root Master Router)"]
        AreaIndexes["memory/*.md (1-Page Domain Indexes)"]
        VaultRaw["vault/raw/ (Immutable Inputs)"]
        VaultWiki["vault/wiki/ (Compiled Knowledge)"]
        Outputs["output/artifacts/ (Deliverables)"]
        AuditLog["output/runs.log (JSONL Execution Log)"]
    end

    subgraph SyncEngine ["Sync Engine"]
        GitRepo[("Private Git Repo\n(GitHub / GitLab)")]
        VPS["Linux VPS (24/7 Routines)\nCron + Tailscale / SSH"]
    end

    CC -->|POST /api/v1/run-skill\n+ Bearer Token| Runner
    Runner -->|Check Lock & Allowlist| Lock
    Runner -->|Execute (shell=False)| CLI
    CLI -->|Reads Root Context| RootRouter
    CLI -->|Reads/Writes| AreaIndexes & VaultWiki & Outputs
    CLI -->|Writes Pending Action| ApprovalQueue
    ApprovalQueue -.->|Human Click 'Approve'| CC
    Runner -->|Appends Result| AuditLog

    MemoryLayer <-->|Scheduled Commit / Push / Pull| GitRepo
    GitRepo <-->|Scheduled Pull / Push| VPS
```

---

## 2. Hardened Zero-RCE Local Runner

Exposing an unauthenticated agent execution endpoint over HTTP allows drive-by browser requests and DNS rebinding attacks to achieve Remote Code Execution (RCE). The local runner (`apps/runner/server.py`) enforces six strict security controls:

1. **Strict Loopback Binding:** The server binds strictly to `127.0.0.1` (IPv4 loopback), never `0.0.0.0`.
2. **Bearer Token Authentication:** Every HTTP request must provide an `Authorization: Bearer <token>` header. A cryptographically random token is generated on startup if absent and written to `.local-token` (file permission `0600`, gitignored).
3. **Origin & Referer Validation:** The server verifies that the `Origin` or `Referer` matches `http://127.0.0.1:3000` or `http://localhost:3000`. Any external or cross-origin web browser request is immediately rejected with HTTP `403 Forbidden`.
4. **Strict Skill Allowlist:** The runner rejects free-form prompt strings. It accepts only pre-registered skill names matching `^[a-zA-Z0-9_-]+$` present in the skill registry.
5. **No Shell Invocation (`shell=False`):** Execution is invoked strictly as an argument list:
   ```python
   subprocess.run(["claude", "-p", f"/{skill_name}", ...], shell=False, check=False)
   ```
6. **No Public VPS Exposure:** The runner is never exposed to public internet ports on the VPS. Headless triggers on the VPS are initiated via local cron or through an authenticated SSH / Tailscale session.

---

## 3. Headless Permissions & Guardrails

Running `claude -p` non-interactively requires explicit boundaries to prevent infinite loops, runaway costs, or destructive actions:

### 3.1 Per-Skill Permission Manifest
Every skill defines its execution boundary in its manifest (`skills/<skill>/skill.yaml`):
* `allowed_tools`: Explicit tool names passed to `--allowed-tools` (e.g. `"Read, Edit, Bash(git status)"`). All other tools are denied by default.
* `max_budget_usd`: Hard cost cap passed to `--max-budget-usd` (e.g. `0.25`).
* `timeout_seconds`: Process watchdog timer enforced by Python `subprocess.run(timeout=...)`.
* `effort`: Claude's native reasoning effort passed to `--effort` (`low`, `medium`, `high`, `max`).

### 3.2 Human-in-the-Loop (HITL) Approval Queue
Headless routines are strictly forbidden from performing external write actions (`send`, `spend`, `publish`):
1. When a routine requires an external state mutation, it generates a structured intent payload and appends it to `output/approval_queue.jsonl`:
   ```json
   {
     "id": "act-20261105-001",
     "timestamp": "2026-11-05T17:00:00Z",
     "skill": "newsletter-publisher",
     "action": "publish_post",
     "target": "Ghost CMS",
     "payload_path": "output/artifacts/newsletter-draft.md",
     "status": "pending"
   }
   ```
2. The skill exits cleanly with status `WAITING_APPROVAL`.
3. The user inspects the draft and clicks **Approve** or **Reject** in the Command Centre, or runs:
   ```powershell
   python apps/runner/server.py approve act-20261105-001
   ```

### 3.3 Concurrency Mutex (`.workspace.lock`)
To prevent race conditions and index corruption from concurrent local and scheduled routine writes, the runner acquires a file lock (`.workspace.lock`) with PID and timestamp before executing. If a lock is held, new requests are queued or rejected with HTTP `423 Locked`.

---

## 4. State Synchronization: Git over Syncthing

Syncthing is not a backup system—it propagates deletions and corruptions instantly, produces `.sync-conflict` files during concurrent writes, and lacks versioned exclude lists.

### Primary Sync: Private Git Repository
* **Workspace Repository:** The workspace is tracked in a private Git repository.
* **Workstation Flow:** Edits, new skills, and router updates are committed and pushed as atomic commits.
* **VPS Flow:** The VPS runs scheduled `git pull --rebase` before running scheduled routines, commits generated artifacts upon completion, and pushes.
* **Audit & Rollback:** Every modification produces an immutable git diff that can be inspected or rolled back.
* **Secrets Policy:** `.env` and `.local-token` are strictly gitignored. Credentials reside exclusively in local machine environment variables or secure OS keychains.
* **Syncthing Role (Optional):** Strictly relegated to optional, one-way sync for large media/binary assets in `output/media/`.

---

## 5. Acceptance Criteria

- [ ] Runner binds exclusively to `127.0.0.1:3000`; connections from other interfaces fail.
- [ ] Requests without a valid `Authorization: Bearer <token>` header return HTTP `401 Unauthorized`.
- [ ] Cross-origin browser requests with an untrusted `Origin` header return HTTP `403 Forbidden`.
- [ ] Execution rejects any skill name not in the pre-registered allowlist.
- [ ] Subprocess execution runs with `shell=False`.
- [ ] Destructive external actions write to `output/approval_queue.jsonl` rather than executing automatically.
- [ ] `.workspace.lock` successfully prevents simultaneous concurrent runs.
