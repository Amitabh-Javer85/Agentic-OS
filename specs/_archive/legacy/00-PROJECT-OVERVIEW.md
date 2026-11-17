# AGENTIC OS — PROJECT OVERVIEW

## 1. Vision & Mission

The Agentic OS is designed to serve as a personal AI operating system that acts as a true "second brain" and an active "digital assistant." The vision is to build an integrated environment where your thoughts, knowledge, and actions are seamlessly interwoven. 

Key pillars of this vision include:
- **Single Front Door:** Interact with the OS natively through an Obsidian plugin (for text-heavy, knowledge-based work with optional voice input).
- **One Shared Brain (The Bridge):** A unified backend intelligence layer powered by advanced LLMs like Claude, Codex, or any custom model, acting as the CPU of the OS.
- **One Shared Memory (The Vault):** All knowledge and state are stored as plain markdown files in an Obsidian vault, serving as the system's disk drive. 
- **Voice-First Interaction:** Utilizing Whisper for "ears" (Speech-to-Text) and Kokoro for "voice" (Text-to-Speech) for natural, conversational interactions.
- **Inspired by Andrej Karpathy's LLM OS Concept:** Treating the LLM as the CPU, its context window as RAM, the markdown vault as the disk, and connected tools/connectors as peripheral devices.

## 2. Architecture Overview (High Level)

The system relies on a central hub (The Bridge) that orchestrates traffic between the user interface, the intelligence layer, memory storage, and external tools.

```mermaid
flowchart TD
    %% User Interfaces (Front Door)
    User((User))
    User --> |Text / Voice| ObsidianPlugin[Obsidian Plugin]

    %% Main Backend
    ObsidianPlugin --> TheBridge{THE BRIDGE \n(Unified Backend)}

    %% Peripheral Systems connected to The Bridge
    SpeechService[Speech Service\nWhisper STT + Kokoro TTS] <--> |Audio in/out| TheBridge
    TheVault[(The Vault\nraw/, wiki/, output/)] <--> |Markdown / State| TheBridge
    Connectors[Connector Layer\nGmail, Calendar, Drive, etc.] <--> |API Calls| TheBridge

    %% Intelligence Layer Routing
    TheBridge --> JEVRouter{JEV Router\n(Classifier)}
    JEVRouter --> Tier1[Tier 1\nSimple/Fast Models]
    JEVRouter --> Tier2[Tier 2\nBalanced Models]
    JEVRouter --> Tier3[Tier 3\nComplex/Reasoning Models]
```

## 3. Core Principles

The Agentic OS is built upon robust philosophies of modern AI engineering:

- **"Compile, Don't Retrieve":** Favor generating and maintaining static, pre-computed structures over constant dynamic retrieval.
- **Software 3.0:** Embrace natural language as the fundamental programming and interface layer.
- **Tiered Intelligence:** Optimize cost and latency by routing requests to the most appropriate model tier (using the cheapest, fastest model capable of handling the task).
- **Skill Backbone:** A structured progression for capabilities: Domain → Task → Skill → Automation.
- **Rules of Thumb for Automation:**
  - *If you've done it by hand twice, make it a skill.*
  - *If a skill works 5 times in a row, automate it.*
  - *If an action sends, spends, or publishes, keep a human in the loop.*
- **Local-First & Plain-Text Sovereignty:** Ensure that the user's data remains under their control, avoiding vendor lock-in by using plain markdown files.
- **Human-in-the-Loop:** Required for any destructive or high-stakes actions (sending emails, publishing content, spending money).

## 4. System Components Summary

1. **The Vault:** An Obsidian-based knowledge base acting as the system's long-term memory (disk), storing everything in plain text.
2. **The Bridge:** The unified backend orchestrator that ties all components together, managing state, context, and external tool execution.
3. **JEV Router:** An intelligent request classifier that routes tasks to the appropriate model tier based on complexity and requirements.
4. **Obsidian Plugin:** The primary text-based "front door" for seamless interaction while working within the knowledge base.
5. **Speech Service:** Handles voice input and output locally, combining Whisper (STT) and Kokoro (TTS) for natural communication.
6. **Skill Engine:** A framework for defining, storing, and executing atomic tasks and workflows.
7. **Connector Layer:** The integration suite for third-party services (Google Workspace, YouTube, etc.) to perform real-world actions.
8. **Memory & Context System:** Manages the LLM's context window (RAM), handling short-term conversational context and long-term retrieval from the Vault.

## 5. Technology Stack Decisions

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend** | FastAPI (Python) or Bun (Node.js) | FastAPI provides robust async support and easy integration with Python AI tools. Bun offers high performance for JS ecosystems. |
| **LLM** | Claude (primary), fallback to GPT/Codex | Claude for superior coding and reasoning. Switchable architecture allows flexibility. |
| **STT** | faster-whisper (local), Groq Whisper (cloud) | Local privacy vs. extreme cloud speed depending on user preference and hardware. |
| **TTS** | Kokoro-82M (local), ElevenLabs (premium) | Kokoro offers excellent local quality; ElevenLabs provides top-tier emotional range. |
| **Vault** | Obsidian + Local REST API + MCP | Leverages existing, robust plain-text ecosystems with programmatic access. |
| **Automation** | n8n (self-hosted) | Powerful visual workflow builder that integrates well with APIs and webhooks. |
| **Frontend** | TypeScript + Obsidian API | Native integration with the vault, offline-first, zero latency |
| **Router** | JEV / Semantic Router | Enables fast, deterministic routing of user intents to the right models or skills. |
| **Database** | SQLite (metadata), ChromaDB/Qdrant (vectors) | Lightweight relational data combined with scalable semantic search capabilities. |
| **Message Broker**| Redis Pub/Sub | Reliable, fast cross-component communication for a distributed microservice feel. |

## 6. Document Index

This specification suite consists of the following documents:

- **`00-PROJECT-OVERVIEW.md`** (this document)
- **`01-ARCHITECTURE.md`**: Detailed system architecture, data flows, and infrastructure design.
- **`02-THE-VAULT.md`**: Directory structure, metadata standards, and file formats for the Obsidian vault.
- **`03-THE-BRIDGE.md`**: Core backend logic, state management, and orchestration rules.
- **`04-JEV-ROUTER.md`**: Logic for intent classification and model tier routing.
- **`05-OBSIDIAN-PLUGIN.md`**: UX/UI and technical specifications for the Obsidian integration.
- **`06-JARVIS-HUD.md`**: Technical specs and UI design for the React-based frontend.
- **`07-SPEECH-SERVICE.md`**: Integration patterns for Whisper and Kokoro.
- **`08-SKILL-ENGINE.md`**: Framework for creating, managing, and executing skills.
- **`09-CONNECTORS.md`**: Specs for third-party integrations and API authentications.
- **`10-MEMORY-SYSTEM.md`**: Strategies for context window management and RAG implementation.
- **`11-SECURITY-AND-PERMISSIONS.md`**: Authentication, authorization, and "human-in-the-loop" safeguards.
- **`12-IMPLEMENTATION-ROADMAP.md`**: Phased execution plan for building the Agentic OS.
- **`13-VAULT-SCHEMA.md`**: Detailed YAML frontmatter and tagging schemas for the Vault.
- **`14-API-CONTRACTS.md`**: Standardized API schemas between components (e.g., Bridge ↔ HUD).

## 7. Key References

- **Andrej Karpathy's LLM OS Concept:** [Tweet / Vision Overview](https://twitter.com/karpathy/status/1723140225442083321)
- **Intro to Large Language Models:** [Karpathy's YouTube Lecture](https://www.youtube.com/watch?v=zjkBMFhNj_g)
- **Software Is Changing Again:** [Karpathy's Keynote]
- **Karpathy LLM Wiki:** [GitHub Gist / Wiki Pattern](https://gist.github.com/karpathy)
- **Tools & Frameworks:**
  - [FastAPI](https://fastapi.tiangolo.com/)
  - [Obsidian](https://obsidian.md/)
  - [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) / [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
  - [Kokoro TTS](https://github.com/hexgrad/kokoro)
  - [React Three Fiber](https://docs.pmnd.rs/react-three-fiber)
