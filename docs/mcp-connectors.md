# MCP connector audit and vetting procedure

Audit date: 2026-11-05. Runtime: locally installed Claude Code 2.1.316.
Evidence: native `claude --version` and `claude mcp list` executed from this workspace.
The health check contacts configured connector endpoints but performs no application writes.

| Claude Code connector | Native health result | Current capability |
| --- | --- | --- |
| Context7 plugin | Needs authentication | Documentation lookup unavailable through this MCP connection |
| Playwright plugin | Failed to connect; 30-second timeout | Browser automation unavailable through this MCP connection |
| Figma plugin | Needs authentication | Design operations unavailable through this MCP connection |
| Supabase plugin | Needs authentication | Database operations unavailable through this MCP connection |
| Google Workspace | Not listed | Calendar, mail, and Drive are not available to this runtime through MCP |
| Filesystem | Not listed | Claude's native Read/Edit/Write tools supply local file access; they are not an MCP server |
| n8n | Not listed | Workflow access is not configured in this runtime |

No audited MCP connector is currently healthy. Authentication and connection repair are operator setup tasks; do not mark an unavailable integration as working. Connector configuration can differ by account, project, and machine. Re-run the native health check after setup changes.

Codex exposes separate connected-app tools, including Google Drive, Calendar, Gmail, GitHub, and Figma. Their presence in this development chat does not install or authorize those connectors in Claude Code. Agentic OS scheduled jobs run Claude Code, so they must not assume access to Codex's tools. Local exported inputs remain the offline fallback.

## Community GitHub MCP server vetting checklist

1. Identify the exact upstream repository, maintainer, license, release, and source commit. Confirm the package or binary is published by that maintainer; inspect installation scripts and dependencies before executing them.
2. Read source for startup behavior, filesystem access, command execution, network destinations, telemetry, credential handling, and each tool's actual effects. Treat tool descriptions as claims requiring review.
3. Classify tools by permission and side effect. Prefer a narrowly scoped read-only token and a disposable repository/account. Deny send, spend, publish, delete, workflow execution, and repository mutation during initial tests.
4. Pin the reviewed version or commit. Record the executable, arguments, approved workspace roots, endpoint hosts, transport, and requested scopes. Keep credentials in local environment/secret storage; never commit or print them.
5. Install only after the operator authorizes the specific server and permissions. Use Claude Code's native MCP management rather than adding a proxy/backend. Follow the current official documentation for the selected transport.
6. Run `claude mcp list` and inspect the health result. Then perform one known read-only request on the disposable resource. Confirm the expected data, denied mutation access, and absence of unexpected local writes or network destinations. A healthy connection alone does not prove correct permissions.
7. Record the reviewed source version, exact approved tools/scopes, health and read-only test results, reviewer, and rollback/removal method here before enabling routine use. Re-vet upgrades and permission changes.

Headless jobs must expose only vetted tools. Do not enable a general-purpose MCP server merely to make a job succeed. The runner uses strict MCP isolation by default; any future connector enablement must preserve the approval queue boundary. An intent to send, spend, publish, or delete is appended to `output/approval_queue.jsonl`; approval records a decision and does not automatically execute the action.

Official reference: [Claude Code MCP documentation](https://code.claude.com/docs/en/mcp).

## Offline micro-app: Evidence Desk

Open `apps/research-brief.html` directly in a browser. No server, package install, account, model call, or network connection is required. Load the fictional demo, choose **Build brief**, review the cited excerpts, and choose **Download Markdown**. Paste your own source notes to use it for real research.

This is an extractive handoff tool: it quotes the first two sentences of each supplied source and keeps source identifiers. It does not infer conclusions or verify claims. Inputs remain in the current tab; downloaded drafts are local files. To retain a generated draft in the repository, save it in `output/artifacts/` and add its pointer to `memory/CONTENT.md` in the same operation. Source notes are rendered as text, including HTML-looking input.

Browser acceptance check (optional development dependency, not an application dependency): `python tests/test_micro_app.py`. It uses an already installed Python Playwright/browser to open the actual HTML, build and download the fictional brief, verify source attribution and exact excerpts, reject malformed inputs, invalidate stale downloads, and check that untrusted HTML is inert. If Playwright or its browser is unavailable, the test fails with a setup instruction; it does not silently claim a pass.
