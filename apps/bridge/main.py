"""Agentic OS — The Bridge (FastAPI backend)

Core responsibilities:
- Unified backend for all client requests (Obsidian Plugin, CLI, etc.)
- Pipeline processing: receive → normalize → enrich → route → execute → stream → persist
- Context assembly from vault + session history
- LLM orchestration with streaming and tool calling
- State & session management
- Skill & tool execution coordination
"""

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Optional

import httpx
import tiktoken
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# --- LLM connector ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

def call_llm(messages: list, max_tokens: int = 500) -> str:
    """Call Anthropic Claude API. Falls back to simulated response if no key."""
    if not ANTHROPIC_API_KEY:
        return f"[simulated] Agentic OS received: \"{messages[-1].get('content','')}\". Vault context: available."

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": max_tokens,
        "messages": messages,
    }
    try:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]
    except Exception as e:
        return f"[error] LLM call failed: {e}. Falling back to simulated."

# --- Config ---
VAULT_PATH = Path(os.getenv("VAULT_PATH", "./vault"))
DB_PATH = Path(os.getenv("DB_PATH", "./.data/bridge.db"))
SYSTEM_PROMPT = """You are the Agentic OS assistant. Help the user with their tasks.
Follow the workflow: Understand → Retrieve from vault if relevant → Reason → Act."""
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "16000"))

# --- Ensure directories & DB ---
VAULT_PATH.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS sessions ("
        "session_id TEXT PRIMARY KEY, "
        "context_json TEXT, "
        "updated_at REAL DEFAULT 0)"
    )
    conn.commit()
    return conn

# --- FastAPI app ---
app = FastAPI(title="Agentic OS Bridge", version="0.1.0")

# --- Pydantic models ---
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    client_source: str = Field(default="cli", description="Source: obsidian or cli")

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    tokens_used: int = 0

class StatusResponse(BaseModel):
    status: str = "ok"
    vault_path: str
    session_store: str

# --- Vault client ---
class VaultClient:
    """Wrapper around Obsidian Local REST API + direct filesystem fallback."""

    def __init__(self, vault_path: Path):
        self.vault = vault_path
        self.base_url = "http://127.0.0.1:27124"  # Obsidian Local REST API

    def read_file(self, rel_path: str) -> Optional[str]:
        """Read a file from the vault.

        1. Try Obsidian Local REST API first
        2. Fallback to direct filesystem read
        """
        # Try direct filesystem first (always works)
        full = self.vault / rel_path
        if full.is_file():
            try:
                return full.read_text(encoding="utf-8")
            except Exception:
                return None

        # Try Obsidian REST API
        try:
            resp = httpx.get(f"{self.base_url}/vault/{rel_path}", timeout=5.0)
            if resp.status_code == 200:
                return resp.text
        except Exception:
            pass

        return None

    def write_file(self, rel_path: str, content: str) -> bool:
        """Write a file to the vault (wiki/ or output/ only)."""
        full = self.vault / rel_path
        try:
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")
            return True
        except Exception:
            return False

vault_client = VaultClient(VAULT_PATH)

# --- Helpers ---
_tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(_tokenizer.encode(text))

def truncate_context(messages: list, max_tokens: int = MAX_CONTEXT_TOKENS) -> list:
    """Trim conversation to fit within token budget, keeping system prompt + newest messages."""
    # Count from the end, drop oldest user/assistant pairs
    total = sum(count_tokens(m.get("content", "")) for m in messages)
    if total <= max_tokens:
        return messages

    result = [messages[0]]  # keep system prompt
    for m in reversed(messages[1:]):
        if count_tokens("\n".join(m.get("content", "") for m in result)) >= max_tokens:
            break
        result.insert(1, m)  # insert after system prompt
    return result

# --- Startup: ensure DB ---
@app.on_event("startup")
def on_startup():
    _get_db()

# --- REST Endpoints ---

@app.get("/api/v1/status", response_model=StatusResponse)
def status():
    """Health check + basic env info."""
    conn = _get_db()
    row = conn.execute("SELECT session_id, updated_at FROM sessions ORDER BY updated_at DESC LIMIT 1").fetchone()
    return StatusResponse(
        status="ok",
        vault_path=str(VAULT_PATH),
        session_store=f"sqlite:{DB_PATH}",
    )

@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Send a text message. Supports SSE-style response via JSON."""
    session_id = req.session_id or f"cli-{int(time.time())}"

    # Read vault context if available
    vault_ctx = vault_client.read_file("wiki/index.md") or ""

    # Assemble context: system + recent chat + vault snippet
    # In a full impl, pull from DB session history + vector memory
    user_msg = {"role": "user", "content": req.message}
    all_messages = [{"role": "system", "content": SYSTEM_PROMPT}, user_msg]
    all_messages = truncate_context(all_messages)

    # Real LLM call (falls back to simulated if no key)
    reply = call_llm(all_messages)
    tokens = count_tokens(reply)

    # Persist session
    conn = _get_db()
    conn.execute(
        "INSERT OR REPLACE INTO sessions (session_id, context_json, updated_at) VALUES (?, ?, ?)",
        (session_id, json.dumps({"messages": all_messages, "vault_ctx": vault_ctx}), time.time())
    )
    conn.commit()

    return ChatResponse(reply=reply, session_id=session_id, tokens_used=tokens)

# --- WebSocket Endpoint for streaming ---

@app.websocket("/api/v1/stream")
async def stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            session_id = msg.get("session_id") or f"ws-{int(time.time())}"
            user_msg = msg.get("message", "")

            # Same context assembly as REST endpoint
            vault_ctx = vault_client.read_file("wiki/index.md") or ""
            user_msg_obj = {"role": "user", "content": user_msg}
            all_messages = [{"role": "system", "content": SYSTEM_PROMPT}, user_msg_obj]
            all_messages = truncate_context(all_messages)

            # Stream tokens back (simulated)
            await websocket.send_text(json.dumps({
                "type": "session_start",
                "session_id": session_id,
                "vault_ctx_loaded": len(vault_ctx) > 0,
            }))

            # Simulated streaming response
            reply = f"Agentic OS: processing \"{user_msg}\"."
            for chunk in [reply[i:i+20] for i in range(0, len(reply), 20)]:
                await websocket.send_text(json.dumps({
                    "type": "token",
                    "content": chunk,
                }))
                await asyncio.sleep(0.05)

            await websocket.send_text(json.dumps({
                "type": "session_end",
                "session_id": session_id,
            }))
    except WebSocketDisconnect:
        pass

# --- CLI entry point (run via: uvicorn apps.bridge.main:app --host 127.0.0.1 --port 8000) ---
if __name__ == "__main__":
    print("Agentic OS Bridge starting...")