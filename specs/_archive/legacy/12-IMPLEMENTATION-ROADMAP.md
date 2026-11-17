# AGENTIC OS — IMPLEMENTATION ROADMAP

This document defines the phased implementation plan for building the Agentic OS.

## Phase 0: Foundation (Week 1-2)
**Goal:** Project scaffolding and vault setup

### Tasks:
- Set up the Obsidian vault with the defined folder structure (`raw/`, `wiki/`, `sys/`).
- Create `AGENTS.md`, system templates, and schema definition files.
- Install necessary Obsidian plugins: Local REST API, Dataview, Templater.
- Create the `specs/` directory with all comprehensive design documents.
- Set up the Docker Compose skeleton for local deployment.
- Set up monorepo structure (e.g., Turborepo or npm workspaces).

### Deliverables:
- Configured Obsidian vault.
- Docker Compose file.
- Monorepo with package structure.

### Risks/Dependencies:
- **Dependency:** Obsidian Local REST API configuration complexity.

## Phase 1: The Core (Week 3-4)
**Goal:** The Bridge + Vault integration

### Tasks:
- Build The Bridge FastAPI server baseline.
- Implement basic chat endpoint with a single LLM connection (e.g., OpenAI or Anthropic SDK).
- Connect The Bridge to the Obsidian vault via Local REST API.
- Implement basic vault file read/write operations within The Bridge.
- Implement basic conversation state persistence (SQLite or JSON).
- Implement initial context assembly (pre-pending system prompt + recent conversation).

### Deliverables:
- Working Bridge API.
- Basic vault integration.
- CLI-based chat interaction.

### Risks/Dependencies:
- **Risk:** Handling markdown parsing edge cases when reading from the Vault.

## Phase 2: Intelligence Layer (Week 5-6)
**Goal:** JEV Router + Tiered Processing

### Tasks:
- Implement the JEV (Jarvis/Edith/Vision) request classifier.
- Build Tier 1 handler: Exact matches, fast rules, cached lookups.
- Build Tier 2 handler: Fast, small LLM calls for simple tasks.
- Build Tier 3 handler: Full agent loop with tool access.
- Implement confidence-gated cascade routing between tiers.

### Deliverables:
- Working 3-tier request routing architecture.
- Measurable latency and cost savings from the tiered approach.

### Risks/Dependencies:
- **Risk:** Fine-tuning the confidence thresholds to avoid routing complex queries to Tier 1/2.

## Phase 3: Knowledge Engine (Week 7-8)
**Goal:** Vault Operations + Vector Search

### Tasks:
- Implement the Ingest pipeline (processing `raw/` inputs into structured `wiki/` notes).
- Implement the Query pipeline (retrieving data from `wiki/` to synthesize outputs).
- Implement Lint operations to ensure vault data integrity.
- Set up ChromaDB or Qdrant vector store container.
- Build the embedding pipeline to sync vault contents to the vector DB.
- Implement semantic search endpoint in The Bridge.

### Deliverables:
- Working automated knowledge compilation.
- Semantic search across the vault contents.

### Risks/Dependencies:
- **Dependency:** Requires Phase 1 vault read/write stability.
- **Risk:** Keeping the vector DB in sync with real-time vault changes.

## Phase 4: Voice (Week 9-10)
**Goal:** Speech Service

### Tasks:
- Deploy Kokoro-FastAPI container for local TTS.
- Deploy faster-whisper service for local STT.
- Integrate Silero VAD for intelligent endpointing and silence detection.
- Build voice endpoints in The Bridge.
- Test end-to-end voice interaction (Audio in -> LLM -> Audio out).

### Deliverables:
- Working voice input/output API.
- Sub-second voice latency for responses.

### Risks/Dependencies:
- **Risk:** Hardware constraints (GPU memory) when running local LLM + TTS + STT simultaneously.

## Phase 5: Front Door - Obsidian Plugin (Week 11-13)
**Goal:** Obsidian Plugin with Orb, Dashboard, Terminal

### Tasks:
- Scaffold Obsidian plugin from community sample template.
- Build the Orb (floating action button with state-indicative colors).
- Build Terminal tab (traditional chat interface).
- Build Dashboard tab (system overview panel).
- Connect the plugin to The Bridge via REST and WebSocket.
- Add voice input button functionality.

### Deliverables:
- Working custom Obsidian plugin.
- Integrated chat, voice, and dashboard inside Obsidian.

### Risks/Dependencies:
- **Dependency:** Bridge REST and WS APIs must be stable.

## Phase 6: Skills & Automation (Week 14-16)
**Goal:** Skill Engine + Starter Skills

### Tasks:
- Build the Skill Engine execution framework within The Bridge.
- Create 8 starter skills defined via `SKILL.md` specifications.
- Integrate with local n8n instance for scheduled workflow execution.
- Build the skill creation workflow (allowing the OS to write its own skills).
- Implement skill analytics and success rate tracking.

### Deliverables:
- 8 functional, tested skills.
- Scheduled automation capabilities via n8n.

### Risks/Dependencies:
- **Risk:** Unpredictable agent behavior when writing its own skills; requires strict sandboxing.

## Phase 7: Connectors & Polish (Week 17-19)
**Goal:** External service integration & Hardening

### Tasks:
- Implement Gmail connector using MCP (Model Context Protocol).
- Implement Calendar connector (MCP).
- Implement Drive connector (MCP).
- Implement YouTube connector.
- Implement the Human-In-The-Loop (HITL) approval flow for high-stakes actions.
- Conduct security audit and system hardening.
- Performance optimization (profiling Bridge API, caching).

### Deliverables:
- Working Google Workspace integrations.
- Functional HITL approval system.
- Production-ready security posture.

### Risks/Dependencies:
- **Dependency:** External API rate limits and OAuth consent configurations.

## Phase 8: Integration & Launch (Week 20-22)
**Goal:** Full system integration testing and documentation

### Tasks:
- Conduct end-to-end testing across all request paths.
- Perform comprehensive performance benchmarking.
- Write final system documentation.
- Create user guides for operating and extending the OS.

### Deliverables:
- Fully integrated, polished Agentic OS.
- Complete user documentation.

## Success Metrics
- **Tier 1 hit rate:** >40% of requests handled without heavy AI calls.
- **Latency:** <2s for Tier 1-2 responses; <30s for Tier 3 deep executions.
- **Voice latency:** <1.5s round-trip time.
- **Data accuracy:** >95% entity extraction accuracy during vault ingestion.
- **Skill execution:** >90% success rate on defined skills.
- **Cost:** <$50/month in LLM API costs for personal use.
