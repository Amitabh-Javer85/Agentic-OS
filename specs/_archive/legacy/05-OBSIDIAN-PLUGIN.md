# AGENTIC OS — OBSIDIAN PLUGIN SPECIFICATION

The Obsidian Plugin is "Front Door #1" — it lives inside the Obsidian vault and provides orb + dashboard + terminal tabs.

## 1. Purpose
- Primary interface for users who live in Obsidian
- Three UI modes: Orb (minimal), Dashboard (overview), Terminal (command line)
- Direct access to vault for reading/writing
- Seamless integration with Obsidian's native features

## 2. Plugin Architecture
- **Language/Framework**: TypeScript Obsidian plugin using the official API.
- **Communication**: Communicates with The Bridge via REST API and WebSocket connections.
- **Obsidian APIs**: Uses Obsidian's `metadataCache`, vault API, and editor API for interacting with the file system.
- **Configuration**: Settings panel for managing Bridge connection URL, API keys, and UI preferences.

## 3. UI Components

### 3.1 The Orb
- Floating action button (always visible, draggable).
- Color states indicating system status:
  - **Cyan**: Idle / Ready
  - **Purple**: Thinking / Processing
  - **Amber**: Speaking / Audio playback
  - **Red**: Warning / Error state
- Click to expand to the dashboard or terminal modes.
- Shows quick status (e.g., "processing", "ready", "listening").

### 3.2 Dashboard Tab
- **Today's Priorities**: Pulled dynamically from the vault using dataview-like queries or Bridge context.
- **Recent Conversations**: History of interactions with the agent.
- **Active Skills/Automations**: Status of background tasks or active agents.
- **Quick Actions**: Buttons for common operations (new note, ingest, query).
- **System Health**: Connection status to the Bridge, latency, and model availability.

### 3.3 Terminal Tab
- Embedded chat interface in the Obsidian right/left sidebar.
- Streaming responses from the Bridge.
- Full markdown rendering in responses, including mermaid and code blocks.
- Command history for easy repetition.
- Slash commands for explicit actions:
  - `/ingest`: Trigger document ingestion
  - `/query`: Ask a specific question against the vault
  - `/lint`: Run format/linting on the current note
  - `/skill`: Execute a specific skill
  - `/plan`: Generate an action plan

## 4. Key Features
- **Voice Input**: Dedicated button to trigger microphone input, connecting directly to the Bridge's Speech Service.
- **Context-Awareness**: The plugin tracks the currently active note and selected text, passing this context to the Bridge automatically.
- **Direct Vault Modification**: The plugin can create new notes or edit existing ones natively based on Bridge commands.
- **Trigger Vault Operations**: Initiate larger ingest, lint, or query operations from within the UI.
- **Real-Time Skill Execution Status**: Visualize what the agent is doing in real-time.

## 5. Technical Implementation
- **Plugin Structure**: 
  - `manifest.json`: Defines plugin ID (`agentic-os-plugin`), version, and dependencies.
  - `main.ts`: Entry point handling registration of views, commands, and events.
- **Communication**: Use Obsidian's `requestUrl` for REST calls (to handle CORS issues inherently) and standard `WebSocket` API for real-time streaming (SSE or WS).
- **Settings Storage**: Uses `Plugin.saveData` and `Plugin.loadData` for persistent settings.
- **Integration Points**:
  - Command Palette: Register slash commands and toggles.
  - Ribbon Icon: Quick access to toggle the UI.
  - Status Bar: Tiny indicator of Bridge connection status.

## 6. Development Setup
- **Prerequisites**: Node.js v18+, npm.
- **Scaffold**: Built from the `obsidian-sample-plugin` template.
- **Workflow**: Hot-reload development using `npm run dev` pointing to a local sandbox vault's `.obsidian/plugins/agentic-os` directory.
- **Testing**: Manual testing in a dedicated sandbox vault.
