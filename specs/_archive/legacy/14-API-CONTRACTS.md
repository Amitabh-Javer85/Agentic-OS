# AGENTIC OS — API CONTRACTS

This document defines every API endpoint, request/response schema, and inter-service communication contract for the Agentic OS.

## 1. The Bridge API (Main Backend)

### 1.1 REST Endpoints

| Method | Path | Request Body | Response Body | Error Codes | Description |
|---|---|---|---|---|---|
| `POST` | `/api/v1/chat` | `ChatRequest` | `ChatResponse` | 400, 401, 500 | Send a text message to the system. |
| `GET` | `/api/v1/chat/{id}` | None | `ChatSession` | 401, 404, 500 | Get history for a conversation. |
| `DELETE` | `/api/v1/chat/{id}` | None | `{ success: boolean }` | 401, 404, 500 | Delete a conversation. |
| `POST` | `/api/v1/voice` | `multipart/form-data` | `VoiceResponse` | 400, 401, 500 | Send voice input (audio blob). |
| `GET` | `/api/v1/context` | None | `ContextState` | 401, 500 | Get current system context state. |
| `POST` | `/api/v1/skill/{name}` | `SkillExecutionRequest`| `SkillExecutionResponse` | 400, 401, 404, 500 | Execute a specific skill. |
| `GET` | `/api/v1/skills` | None | `SkillListResponse` | 401, 500 | List all available skills. |
| `GET` | `/api/v1/status` | None | `SystemStatus` | 500 | Get system health and metrics. |
| `POST` | `/api/v1/ingest` | `IngestRequest` | `IngestResponse` | 400, 401, 500 | Trigger vault ingestion pipeline. |
| `POST` | `/api/v1/query` | `QueryRequest` | `QueryResponse` | 400, 401, 500 | Query the vault/wiki. |
| `POST` | `/api/v1/lint` | None | `LintResponse` | 401, 500 | Run vault lint operations. |
| `GET` | `/api/v1/memory/search` | `?q=string&limit=int` | `SearchResponse` | 400, 401, 500 | Semantic search over vector memory. |
| `GET` | `/api/v1/config` | None | `ConfigState` | 401, 500 | Get system configuration. |
| `PUT` | `/api/v1/config` | `ConfigUpdate` | `ConfigState` | 400, 401, 500 | Update configuration. |
| `POST` | `/api/v1/approve/{id}`| None | `{ success: boolean }` | 401, 404, 500 | HITL approval for pending task. |
| `POST` | `/api/v1/reject/{id}` | `RejectRequest` | `{ success: boolean }` | 401, 404, 500 | HITL rejection for pending task. |

### 1.2 WebSocket Endpoints

| Protocol | Path | Payload Format | Description |
|---|---|---|---|
| `WS` | `/api/v1/stream` | `StreamEvent` | Real-time chat and token streaming. |
| `WS` | `/api/v1/events` | `SystemEvent` | System-wide event stream (status, background tasks). |

### 1.3 Request/Response Schemas

#### TypeScript Interfaces

```typescript
export interface ChatRequest {
  message: string;
  sessionId?: string;
  contextOverrrides?: Record<string, any>;
}

export interface ChatResponse {
  message: string;
  sessionId: string;
  metadata: {
    tierHandled: number;
    tokensUsed: number;
    latencyMs: number;
  };
}

export interface VoiceResponse {
  transcription: string;
  replyText: string;
  replyAudioUrl?: string;
  sessionId: string;
}

export interface SkillExecutionRequest {
  parameters: Record<string, any>;
  async?: boolean;
}

export interface SkillExecutionResponse {
  jobId: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'requires_approval';
  result?: any;
  error?: string;
}

export interface IngestRequest {
  sourcePaths: string[];
  forceRebuild?: boolean;
}

export interface IngestResponse {
  jobId: string;
  status: string;
  filesProcessed: number;
}

export interface QueryRequest {
  query: string;
  filterTags?: string[];
  limit?: number;
}

export interface QueryResponse {
  answer: string;
  sources: Array<{ path: string; score: number; text: string }>;
}

export interface ContextState {
  activeWorkspace: string;
  recentEntities: string[];
  systemLoad: number;
  activeTasks: string[];
}

export interface SystemStatus {
  status: 'ok' | 'degraded' | 'down';
  components: {
    bridge: 'up' | 'down';
    vault: 'up' | 'down';
    speech: 'up' | 'down';
    vectorDB: 'up' | 'down';
  };
  uptime: number;
}

export interface ApprovalRequest {
  taskId: string;
  description: string;
  impact: string[];
  expiresAt: string;
}

export interface StreamEvent {
  type: 'token' | 'tool_call' | 'tool_result' | 'done' | 'error';
  content?: string;
  toolData?: any;
}
```

#### JSON Schemas
*Example for ChatRequest:*
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ChatRequest",
  "type": "object",
  "properties": {
    "message": { "type": "string", "minLength": 1 },
    "sessionId": { "type": "string" },
    "contextOverrides": { "type": "object", "additionalProperties": true }
  },
  "required": ["message"]
}
```

## 2. Speech Service API

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/stt` | Transcribe uploaded audio blob. |
| `WS` | `/api/v1/stt/stream` | Continuous audio streaming for transcription. |
| `POST` | `/api/v1/tts` | Generate audio from text (Kokoro). |
| `WS` | `/api/v1/tts/stream` | Stream audio output chunk-by-chunk. |
| `GET` | `/api/v1/voices` | List available TTS voices. |

## 3. JEV Router API (Internal)

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/classify` | Analyze request to determine handling tier. |

```typescript
export interface ClassificationRequest {
  text: string;
  historyContext: string[];
}

export interface ClassificationResponse {
  tier: 1 | 2 | 3;
  confidence: number;
  extractedIntents: string[];
  suggestedAction?: string;
}
```

## 4. Vault Access API (via Obsidian Local REST API)

Key endpoints for interacting with the Obsidian Vault.

| Method | Path | Description |
|---|---|---|
| `GET` | `/vault/{filepath}` | Read raw markdown content of a file. |
| `PUT` | `/vault/{filepath}` | Create a new file or overwrite existing. |
| `PATCH` | `/vault/{filepath}` | Modify file (Operations: `append`, `prepend`, `replace`). |
| `DELETE` | `/vault/{filepath}` | Delete a file. |
| `POST` | `/search/` | Search vault contents (Obsidian native search syntax). |
| `GET` | `/active/` | Get currently active note in the Obsidian UI. |

## 5. Inter-Service Communication

### 5.1 Message Broker (Redis Pub/Sub)
- **Channel `sys.events`**: Global lifecycle events (startup, shutdown).
- **Channel `tasks.status`**: Status updates for async skill executions.
- **Channel `vault.changes`**: File watcher events (create, modify, delete) emitted to trigger ingestions.

### 5.2 Error Handling Conventions
All API errors return a standard JSON structure:
```json
{
  "error": {
    "code": "ERROR_CODE_STRING",
    "message": "Human readable description",
    "details": {}
  }
}
```

### 5.3 Retry Policies
- Internal service calls (e.g., Bridge to LLM API): Exponential backoff, max 3 retries.
- Vault API writes: Fast fail on lock, retry after 50ms up to 3 times.

## 6. Authentication

- **Format**: Bearer Token in `Authorization` header (`Authorization: Bearer <token>`).
- **Generation**: API keys are generated via an offline CLI script and stored securely in a `.env` or system keychain.
- **CORS**: Configurable via `.env` to restrict access to trusted frontends (Obsidian Plugin, Jarvis HUD). Default is strict `localhost:port` matching.
