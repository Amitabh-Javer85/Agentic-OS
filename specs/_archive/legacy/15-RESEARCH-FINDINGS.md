# AGENTIC OS — RESEARCH FINDINGS & REFERENCES

> **Purpose:** This document captures all research conducted during the design phase. It serves as the knowledge base behind every architectural decision in the spec documents.

---

## 1. Karpathy's LLM OS Concept

### 1.1 Core Thesis
Andrej Karpathy conceptualizes Large Language Models not as chatbots, but as the **CPU/kernel process** of an emerging operating system. The LLM orchestrates memory, storage, tools, and peripherals through natural language reasoning.

### 1.2 The Architectural Mapping

| Traditional OS Component | LLM OS Equivalent | Function |
| :--- | :--- | :--- |
| **CPU / Kernel** | LLM Inference Engine | Instruction execution, reasoning, routing |
| **RAM** | Context Window | Short-term working memory, volatile, expensive |
| **Disk / Filesystem** | RAG / Vector DB / Files | Persistent long-term storage |
| **ROM** | Model Weights | Static world knowledge from pretraining |
| **Peripherals** | Tools, APIs, I/O | Python, browsers, calculators, audio |
| **System Calls** | Function/Tool Calling | JSON function calls, MCP protocol |
| **Programs** | Prompts & Workflows | Natural language instructions |
| **Scheduler** | Agentic Loop | ReAct, plan-and-solve control loops |
| **Security** | Prompt Boundaries | Permissions, sandboxing (currently primitive) |

### 1.3 Software 1.0 → 2.0 → 3.0
1. **Software 1.0** — Explicit programming (C++, Python, Java)
2. **Software 2.0** — Deep learning (gradient descent writes the code in weights)
3. **Software 3.0** — Natural language orchestration (English as the programming language)

### 1.4 System 1 vs System 2 Thinking
From Kahneman's *Thinking, Fast and Slow*:
- **System 1 (Fast):** Standard autoregressive token generation. Constant compute per token. Fluent but hallucination-prone.
- **System 2 (Slow):** Variable test-time compute. Tree of Thoughts, Monte Carlo Tree Search, chain-of-thought. What reasoning models (o-series) implement.

### 1.5 The "LLM Wiki" Methodology — "Compile, Don't Retrieve"

**Problem with standard RAG:** Ephemeral amnesia. Search → answer → discard. No compounding value.

**Solution:** An AI agent continuously compiles raw sources into a structured, interlinked markdown wiki.

```
raw/ (immutable sources) → [AI Compiler] → wiki/ (compiled knowledge base)
                                                    ↓
                                            output/ (query results, reports)
```

**Three Core Operations:**
1. **Ingest** — Parse raw sources, extract entities/concepts, create/update wiki pages
2. **Query** — Search the pre-compiled wiki (not raw files) for fast, holistic answers
3. **Lint** — Review wiki for broken links, orphans, duplicates, contradictions

### 1.6 Key Sources
- [LLM OS Tweet (Nov 2023)](https://x.com/karpathy/status/1723140519554191360)
- [Intro to Large Language Models Lecture](https://www.youtube.com/watch?v=zjkBMFhNj_g) — LLM OS slide at ~42:00
- [State of GPT Talk (Microsoft Build 2023)](https://www.youtube.com/watch?v=bZQun8Y4L2A)
- [Software Is Changing (Again) Keynote (June 2025)](https://www.youtube.com/watch?v=GQIHryrHbw6)
- [LLM Wiki Gist (April 2026)](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Software 2.0 Essay (2017)](https://karpathy.medium.com/software-2-0-aac12207959b)
- [Vibe Coding Tweet (Feb 2025)](https://x.com/karpathy/status/1886192184808149383)

---

## 2. Obsidian AI Integration Ecosystem

### 2.1 Key Plugins

| Plugin | Capabilities | Model Support |
| :--- | :--- | :--- |
| **Smart Connections** | Semantic links, Smart Chat, Smart Graph | Local embeddings, OpenAI, Anthropic, Ollama |
| **Copilot for Obsidian** | Sidebar chat, multi-note context, agentic actions | Claude, OpenAI, Gemini, Ollama, LM Studio |
| **Text Generator** | Inline generation, summarization, prompt templates | OpenAI, Anthropic, Gemini, Ollama |
| **Khoj** | Self-hostable second brain, semantic search, voice | Local LLMs, OpenAI, Anthropic, Gemini |
| **Local REST API** | Headless API server + built-in MCP server | Local HTTPS REST |
| **Obsidian MCP Tools** | Native MCP bridge with semantic search | MCP standard |

### 2.2 Plugin Development Architecture
- **Boilerplate:** [obsidian-sample-plugin](https://github.com/obsidianmd/obsidian-sample-plugin)
- **Stack:** TypeScript + esbuild → main.js + manifest.json + styles.css
- **Key APIs:** `this.app.vault` (file ops), `this.app.metadataCache` (AST/frontmatter), `Editor` (cursor/selection)
- **Network constraint:** `requestUrl` bypasses CORS but can't stream; `fetch` supports streaming but has CORS issues
- **Local embeddings:** Transformers.js (@xenova/transformers) or ONNX Runtime Web in Web Workers
- **Docs:** [docs.obsidian.md](https://docs.obsidian.md/)

### 2.3 Obsidian Local REST API
- **Port:** 27124 (HTTPS with self-signed cert)
- **Auth:** Bearer token
- **Key endpoints:** GET/PUT/PATCH/DELETE `/vault/{filepath}`, POST `/search/`, GET `/active/`
- **PATCH operations:** append, prepend, replace, delete with heading/block targeting
- **Built-in MCP server** for direct LLM client access
- [GitHub](https://github.com/coddingtonbear/obsidian-local-rest-api)

### 2.4 MCP Ecosystem for Obsidian
- [mcp-obsidian](https://github.com/MarkusPfundstein/mcp-obsidian) — REST API bridge
- [obsidian-mcp-server](https://github.com/marcelmarais/obsidian-mcp-server) — Direct filesystem access
- [obsidian-mcp-tools](https://github.com/jacksteamdev/obsidian-mcp-tools) — Native plugin

### 2.5 Framework Connectors
- **LangChain ObsidianLoader:** Parses vault + YAML frontmatter → Documents
- **LlamaIndex ObsidianReader:** Extracts tasks, tracks wikilinks/backlinks

---

## 3. Agentic Systems Architecture (2025-2026)

### 3.1 Tiered Routing Architecture

```
Tier 0: Deterministic     → Regex, cached, $0, <10ms
Tier 1: Fast Classifier   → SLM classification, 50-150ms, <$0.0001
Tier 2: Domain Worker      → Fast model (Haiku/4o-mini), 100-400ms
Tier 3: Frontier Supervisor → Full reasoning model + tools, 1-60s
```

### 3.2 Request Classification — JEV & Alternatives
- **JEV (TypeSafe AI):** Purpose-built System-1 classifier. No prose, only structured outputs with calibrated confidence. 70-500ms.
- **Semantic Router (Aurelio Labs):** Vector-space routing via embeddings. [GitHub](https://github.com/aurelio-labs/semantic-router)
- **RouteLLM (LMSYS):** Open-source cheap/expensive model routing. [GitHub](https://github.com/lm-sys/RouteLLM)
- **Confidence-Gated Cascade:** If confidence ≥ 0.85 → fast-path; if < 0.85 → escalate

### 3.3 Agent Framework Comparison

| Framework | Best For | Architecture |
| :--- | :--- | :--- |
| **Claude Code** | Engineering, CLI automation | Unix-style, MCP client, CLAUDE.md |
| **LangGraph** | Production stateful workflows | Directed cyclic graphs, checkpointing |
| **PydanticAI** | Clean Python agents | Type-safe, minimal abstraction |
| **Mastra** | TypeScript full-stack agents | Built-in workflows, Next.js native |
| **smolagents** | Lightweight Code Agents | ~1000 LOC, writes Python snippets |
| **CrewAI** | Multi-agent teams | Role-based, hierarchical delegation |

**Key Trend:** Moving from conversational multi-agent (AutoGen) → explicit graph-based state machines (LangGraph) or lightweight type-safe frameworks (PydanticAI, Mastra).

### 3.4 Speech Stack

| Component | Option 1 (Local/Free) | Option 2 (Cloud/Premium) |
| :--- | :--- | :--- |
| **STT** | faster-whisper (CTranslate2, 4x faster) | Groq Whisper API (<100ms) |
| **TTS** | Kokoro-82M (Apache 2.0, CPU real-time) | ElevenLabs (ultra-expressive) |
| **VAD** | Silero VAD (speech boundary detection) | — |
| **Streaming** | WebRTC via LiveKit | — |

- **whisper.cpp:** C/C++ port, CPU/Metal optimized. [GitHub](https://github.com/ggerganov/whisper.cpp)
- **faster-whisper:** CTranslate2, 4x faster, lower memory. [GitHub](https://github.com/SYSTRAN/faster-whisper)
- **Kokoro-82M:** 82M params, 350MB, 24kHz audio, real-time on CPU. [HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M)
- **Kokoro-FastAPI:** OpenAI-compatible `/v1/audio/speech` endpoint. Docker: `ghcr.io/remsky/kokoro-fastapi-cpu`
- **Silero VAD:** [GitHub](https://github.com/snakers4/silero-vad)
- **LiveKit:** Real-time voice agent framework. [GitHub](https://github.com/livekit/agents)

### 3.5 Automation Platform: n8n
n8n wins over Make for agentic backends:
- Self-hosted (unlimited runs, full data privacy)
- Native LangChain nodes, RAG nodes, vector stores
- Embedded JavaScript & Python Code nodes
- Perfect for scheduled skill execution and webhook triggers

### 3.6 Obsidian Plugin Technology Stack
- **3D Core:** N/A — Obsidian uses native rendering.
- **Post-processing:** N/A
- **Styling:** Tailwind CSS + glassmorphism
- **Animations:** Native Obsidian callouts
- **Reference repos:**
  - [obsidian-sample-plugin](https://github.com/obsidianmd/obsidian-sample-plugin) — Official sample plugin
  - [my-jarvis](https://github.com/harsh-raj00/my-jarvis) — Note: deprecated; single frontend focus
- **MCP-first:** Use official Google Workspace MCP servers
- **Least privilege scopes:** `gmail.readonly` not `mail.google.com`
- **HITL for writes:** Never auto-send — always `create_draft` + confirmation
- **Token lifecycle:** Encrypted storage, automatic refresh
- **Rate limiting:** Exponential backoff with jitter

### 3.8 Modern Protocol & Tools
- **Model Context Protocol (MCP):** Anthropic's open standard for agent ↔ tool communication. [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **DSPy:** Stanford's framework for programmatic prompt optimization. [GitHub](https://github.com/stanfordnlp/dspy)

---

## 4. Alternative / Enhanced Architecture Suggestions

Based on research findings, the following enhancements are recommended beyond the original diagrams:

### 4.1 Add Tier 0 (Cache Layer)
Before even hitting JEV, implement a deterministic cache layer:
- Exact-match intent cache
- Recent query deduplication
- Rule-based pattern matching
- Cost: $0, Latency: <10ms

### 4.2 Use MCP as the Universal Tool Protocol
Instead of custom REST integrations for each connector, standardize on MCP:
- MCP server for Obsidian vault
- MCP server for Gmail, Calendar, Drive
- MCP server for n8n workflows
- Any new tool = new MCP server

### 4.3 Add Redis as Message Bus
For reliable cross-component communication:
- The Bridge publishes events to Redis
- Frontends subscribe to their channels
- Skills publish progress updates
- Enables decoupled, event-driven architecture

### 4.4 Incremental Vector Indexing
Don't rebuild the entire vector store on every change:
- File watcher detects vault changes
- Only re-embed changed/new files
- Use ChromaDB's upsert with file hash for deduplication

### 4.5 Progressive Skill Disclosure
Don't load all skill definitions into context:
- At startup, inject only skill names + 1-line descriptions (~200 tokens)
- When JEV matches intent, dynamically load the full SKILL.md
- Saves context window budget for actual work

### 4.6 Conversation Summarization for Context Management
When conversations exceed context window:
- Automatically summarize older messages
- Keep recent 5-10 messages in full
- Store full history in vault for reference
- Use rolling summarization (newest messages replace oldest summaries)

---

## 5. Complete Reference URL Index

### Karpathy Sources
1. https://x.com/karpathy/status/1723140519554191360
2. https://www.youtube.com/watch?v=zjkBMFhNj_g
3. https://www.youtube.com/watch?v=bZQun8Y4L2A
4. https://www.youtube.com/watch?v=GQIHryrHbw6
5. https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
6. https://karpathy.medium.com/software-2-0-aac12207959b
7. https://x.com/karpathy/status/1886192184808149383

### Obsidian Ecosystem
8. https://docs.obsidian.md/
9. https://github.com/obsidianmd/obsidian-sample-plugin
10. https://github.com/coddingtonbear/obsidian-local-rest-api
11. https://github.com/brianpetro/obsidian-smart-connections
12. https://github.com/logancyang/obsidian-copilot
13. https://github.com/nhaouari/obsidian-textgenerator-plugin
14. https://github.com/khoj-ai/khoj
15. https://github.com/MarkusPfundstein/mcp-obsidian
16. https://github.com/marcelmarais/obsidian-mcp-server
17. https://github.com/jacksteamdev/obsidian-mcp-tools

### Agent Frameworks
18. https://github.com/pydantic/pydantic-ai
19. https://mastra.ai
20. https://github.com/huggingface/smolagents
21. https://github.com/lm-sys/RouteLLM
22. https://github.com/aurelio-labs/semantic-router
23. https://github.com/stanfordnlp/dspy
24. https://modelcontextprotocol.io

### Speech & Audio
25. https://github.com/ggerganov/whisper.cpp
26. https://github.com/SYSTRAN/faster-whisper
27. https://huggingface.co/hexgrad/Kokoro-82M
28. https://github.com/snakers4/silero-vad
29. https://github.com/livekit/agents

### LangChain / LlamaIndex
32. https://python.langchain.com/docs/integrations/document_loaders/obsidian/
33. https://llamahub.ai/l/readers/llama-index-readers-obsidian
