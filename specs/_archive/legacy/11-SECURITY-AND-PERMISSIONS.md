# AGENTIC OS — SECURITY & PERMISSIONS SPECIFICATION

Karpathy warned that prompt injection is the modern buffer overflow. The Agentic OS must be built with security-first principles.

## 1. Threat Model

The Agentic OS is exposed to several security risks due to the integration of LLMs with system tools and external APIs.
- **Prompt injection via vault documents (data/instruction confusion):** Malicious instructions embedded in documents retrieved from the vault or web that hijack the agent's intent.
- **Unauthorized tool execution:** Invocation of tools by the AI without proper authorization or beyond intended scope.
- **Credential theft/leakage:** Exposure of API keys, tokens, or personal information in logs, prompts, or external API calls.
- **Unintended destructive actions:** Deletion of files, unauthorized email sending, or data corruption due to model hallucination or injection.
- **Data exfiltration through tool abuse:** Covert transmission of sensitive vault data to external servers via web requests or API calls.
- **Model hallucination acting on false information:** Execution of actions based on fabricated facts or incorrect logic by the LLM.

## 2. Security Principles

- **Principle of least privilege for all tools and connectors:** Agents and tools operate with the minimum permissions necessary to perform their functions.
- **Human-in-the-loop (HITL) for destructive/financial/public actions:** Any action that mutates external state significantly or involves finances requires explicit user approval.
- **Strict separation of read and write permissions:** Clear boundary between read operations (safe) and write operations (potentially unsafe).
- **Audit trail for every action:** Comprehensive logging of all tool invocations, prompts, responses, and HITL decisions.
- **Sandboxed code execution:** Execution of generated code within isolated environments to prevent host system compromise.
- **Local-first (data stays on your machine):** Preference for local processing and storage; external API calls must be explicitly configured and minimized.

## 3. Permission System

Define a capability-based permission model to control agent actions.

### Permission Levels

| Level | Name | Examples | Approval |
|-------|------|----------|----------|
| 0 | Read-Only | Read vault, search web, query database | Auto |
| 1 | Write-Local | Create notes, update wiki, save files locally | Auto |
| 2 | Write-External-Safe | Create calendar event, create draft email | Auto |
| 3 | Write-External-Risky | Send email, post to social media, update CRM | HITL Required |
| 4 | Financial/Destructive | Make purchase, delete files, publish code | HITL Required |

### Tool Permission Registry

Every tool must be registered with an explicit permission level.

| Tool Name | Permission Level | Description |
|-----------|------------------|-------------|
| `read_file` | 0 - Read-Only | View contents of local files |
| `search_web` | 0 - Read-Only | Perform internet searches |
| `write_file` | 1 - Write-Local | Create or modify local files |
| `create_calendar_event` | 2 - Write-External-Safe | Add events to calendar without inviting external parties |
| `send_email` | 3 - Write-External-Risky | Send emails to external recipients |
| `delete_directory` | 4 - Financial/Destructive | Permanently delete local directories |

## 4. Human-in-the-Loop (HITL) Gates

- **How HITL approval works:** When a tool requiring level 3 or 4 permission is invoked, execution pauses. A request is generated and pushed to the UI for user approval. The agent waits for the response before proceeding.
- **Approval UI in Obsidian Plugin:** A dedicated modal or side pane displaying the pending action, requested parameters, and potential impact.
- **Timeout behavior (auto-cancel after X minutes):** Pending HITL requests expire and auto-deny after 5 minutes of inactivity to prevent hanging states.
- **Audit logging of approvals/denials:** Every HITL decision is recorded with user identity (if applicable), timestamp, action details, and decision outcome.

## 5. Authentication & Session Security

- **API key management for The Bridge:** API keys are encrypted at rest using system-level keychains (e.g., Windows Credential Manager) and injected into memory only when needed.
- **Session tokens for frontends:** Ephemeral JWTs used for communication between frontends (Obsidian/HUD) and the backend OS, rotated periodically.
- **OAuth2 token lifecycle for connectors:** External integrations use standard OAuth2 flows with secure refresh token storage and automatic revocation on anomalous activity.
- **Encrypted credential storage:** No plaintext passwords or keys are stored in the vault or configuration files.

## 6. Prompt Injection Mitigation

- **Input sanitization:** Stripping known control characters and validating input structures before passing to the LLM.
- **System/user prompt boundaries:** Strict structural separation (e.g., using XML tags `<system>`, `<user>`, `<context>`) to delineate instructions from data.
- **Instruction hierarchy (system > user > retrieved context):** Enforcing that system instructions override any conflicting instructions found in user input or retrieved context.
- **Content tagging (mark AI-generated vs human content):** Metadata indicating origin to adjust trust levels during processing.
- **Suspicious pattern detection:** Pre-filtering inputs for common injection patterns (e.g., "ignore all previous instructions").

## 7. Code Execution Sandboxing

- **Docker containers for code execution:** Ephemeral, minimal Docker containers spawned per execution request.
- **Resource limits (CPU, memory, time):** Hard limits enforced via cgroups (e.g., 512MB RAM, 0.5 CPU, 30s timeout).
- **Network isolation:** Disabling external network access by default; explicit whitelisting required.
- **Filesystem restrictions:** Read-only access to necessary host directories; write access restricted to an ephemeral scratch volume.

## 8. Audit & Compliance

- **Every request logged to vault/receipts/:** Full request/response payloads stored as structured markdown/JSON for review.
- **Every tool invocation logged:** Capturing tool name, arguments, execution time, and raw output.
- **Every HITL decision logged:** Including the context presented to the user and the timestamp.
- **Log retention policy:** Automated archival or deletion of logs older than 90 days, configurable by the user.
