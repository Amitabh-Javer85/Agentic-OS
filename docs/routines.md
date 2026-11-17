# Scheduled routines

## Windows

Run `powershell -NoProfile -File scripts/register-routine.ps1` from the checkout.
It registers `AgenticOS-WeeklyDigest` for Friday 09:00 in the workstation's local
timezone, using the resolved Python path and quoted absolute workspace paths.
Registration is idempotent; use `-WhatIf` to inspect without changing the task.
The limited current-user task requires the user to be signed in. No password is stored.
Verify with `Get-ScheduledTask -TaskName AgenticOS-WeeklyDigest` and
`Get-ScheduledTaskInfo -TaskName AgenticOS-WeeklyDigest`.
Run `scripts/run-routine.ps1 -SkillName weekly-digest` to exercise the same path now.
Claude must be installed, authenticated, and on the scheduled user's PATH.
The runner uses native executables, manifest tool permissions, budget/timeout caps,
and no ambient MCP servers or hooks. A stale `.workspace.lock` is never expired
automatically; verify its PID is no longer running before removing it manually.

Manifests use a deliberately small YAML subset: one scalar field per line and a
block list for `allowed_tools`; required fields and duplicate keys are validated.
File write permissions use `Edit(./path/**)` rules, covering both Edit and Write
tools. `Write(path)` rules do not match Claude's file permission checks and are
rejected. CLI built-in availability and permission rules are set separately.

Verification on 2026-11-05: the task is `Ready`, next run 2026-11-06 09:00 SAST.
The manual weekly-digest invocation timed out (exit 124) and was logged.
A minimal no-tool Claude probe returned `402 Insufficient credits` from the
configured provider. Removing inherited provider overrides for a separate probe
returned `Not logged in`; environment or credentials were not changed. Restore
usable Claude access locally before expecting generated scheduled artifacts.
Live verification was explicitly deferred by the operator; registration success
does not establish a successful scheduled model run.

## Linux VPS deployment

Prerequisites: a user-provided VPS, reviewed Git remote, outbound SSH access,
Python 3.10+, Git, authenticated Claude CLI, and a private checkout owned by the
routine user. No containers, database services, or proxy processes are needed.
Use a read-only deploy key for pulling code. Keep credentials outside the repository.
After cloning, initialize private `vault/raw`, `vault/wiki`, `output/artifacts`,
and the ignored logs/queue as needed; copy the vault constitution through your
private provisioning process. Run security tests and router lint before enabling
a schedule. Never commit private notes or tokens.

Example crontab (set VPS timezone to Africa/Johannesburg; use your actual path):

```cron
PATH=/home/agent/.local/bin:/usr/local/bin:/usr/bin:/bin
0 9 * * 5 /bin/bash /home/agent/Agentic-OS/scripts/run-routine.sh weekly-digest >> /home/agent/Agentic-OS/output/cron.log 2>&1
```

`run-routine.sh` requires a clean checkout and a successful fast-forward pull.
It propagates execution failures and queues a `publish` intent after success.
A human reviews artifacts, selects safe files and pointers, commits, and pushes;
approval status alone never executes a push. This supersedes the old automatic
commit/push requirement, which conflicts with the headless publishing safeguard.
Live deployment is unverified until a VPS and remote are supplied and a real
scheduled artifact round trip is observed. Local script tests are not that proof.

References: [Claude CLI](https://code.claude.com/docs/en/cli-reference),
[permission modes](https://code.claude.com/docs/en/permission-modes), and
[ScheduledTasks](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/).
