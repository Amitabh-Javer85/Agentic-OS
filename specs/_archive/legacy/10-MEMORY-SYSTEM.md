# AGENTIC OS — MEMORY SYSTEM SPECIFICATION

The Memory System manages the AI's knowledge hierarchy, providing the right context at the right time. It implements a multi-tiered architecture inspired by Karpathy's LLM OS memory model: ROM (weights), RAM (context window), and Disk (vault + vector store).

## 1. Memory Hierarchy

### Level 0: ROM (Model Weights)
- **Nature**: Pre-trained knowledge frozen within the foundational model's parameters (e.g., Claude 3.5 Sonnet).
- **Characteristics**: Cannot be modified at runtime.
- **Access**: Accessed implicitly during the inference process without consuming context window tokens.

### Level 1: L1 Cache (Hot Memory)
- **Nature**: The immediate, persistent context injected into every session.
- **Contents**: System prompts, user profiles, current active priorities, current project context, and the daily plan.
- **Source**: Loaded synchronously from `vault/_config/` and current `daily-notes/`.
- **Update Frequency**: Refreshed at session start and periodically upon significant state changes.
- **Size Allocation**: Capped at ~2K tokens.

### Level 2: Working Memory (Context Window)
- **Nature**: The active, short-term memory of the ongoing session.
- **Contents**: Current conversation thread, recently accessed notes, tool call inputs, and execution results.
- **Management**: Utilizes a sliding window protocol. As the token limit approaches, older turns are selectively summarized or evicted.
- **Size Allocation**: 8K-128K tokens, dynamically adjusted based on the underlying model's limits.

### Level 3: Episodic Memory (Vector Store)
- **Nature**: Semantic index of the entire knowledge base.
- **Contents**: High-dimensional semantic embeddings of all markdown files in the vault.
- **Infrastructure**: Local instance of ChromaDB or Qdrant.
- **Embedding Model**: `all-MiniLM-L6-v2` (for speed) or `bge-small-en-v1.5` (for higher retrieval accuracy).
- **Capability**: Enables fast semantic similarity search across the user's entire history and knowledge graph.

### Level 4: Long-term Memory (Vault Filesystem)
- **Nature**: The source of truth; the full Obsidian vault structure (`raw/`, `wiki/`, `output/`).
- **Access**: Direct, precise file access via system tools (read, write, list).
- **Search**: Full-text search capabilities, optionally integrated with the Obsidian Local REST API for ecosystem compatibility.

```mermaid
flowchart TD
    subgraph Context Assembly
        L1[L1 Cache: Hot Memory\n2K Tokens]
        L2[L2: Working Memory\nSliding Window]
        L3[L3: Episodic Memory\nVector Search Results]
        L4[L4: Long-term Memory\nSpecific File Content]
    end
    
    Context Assembly -->|Assembled Prompt| LLM[LLM / ROM]
    
    Vault[(Obsidian Vault)] -->|Loads Config| L1
    Vault -->|File Reads| L4
    
    Embedder[Embedding Pipeline] -->|Updates| VS[(Vector Store)]
    Vault -.->|File Changes| Embedder
    VS -->|Semantic Search| L3
```

## 2. Context Assembly Algorithm

The Context Builder dynamically constructs the prompt for each request to maximize relevance while strictly adhering to token budgets.

**Algorithm:**
1. **Load L1 Hot Memory**: Inject system prompt, user profile, and high-level priorities.
2. **Load L2 Working Memory**: Append the recent conversation history (sliding window).
3. **Analyze Request**: Determine if semantic search or direct file access is needed based on the user's prompt.
4. **Retrieve L3 Episodic Memory**: If needed, execute vector search and append top-k relevant note summaries.
5. **Retrieve L4 Long-term Memory**: If specific files are referenced, load their exact content.
6. **Assemble & Truncate**: Combine all segments. If the total exceeds the token budget, truncate starting with the lowest priority.
   - *Priority Order*: System > Conversation History > Semantic Matches > Raw File Content.

## 3. Memory Operations

- **Write**: Automatically save conversation transcripts, transaction receipts, and generated outputs back to the vault filesystem.
- **Index**: Generate and update semantic embeddings asynchronously whenever vault files are created, modified, or deleted.
- **Search**: Perform k-NN (k-Nearest Neighbors) vector similarity searches, applying metadata filters (e.g., date ranges, tags) to narrow results.
- **Forget**: Implement retention policies to archive old conversations and prune the vector store of obsolete embeddings.
- **Summarize**: Background tasks that compress long conversation threads into dense summaries to preserve L2 context space.

## 4. Vector Store Management

- **Embedding Pipeline**: Uses a file system watcher (`chokidar` or similar) → File Chunker → Embedding Model → Vector Database.
- **Chunking Strategy**: Employs a `MarkdownHeaderTextSplitter` to ensure chunks are logically separated by markdown headers, preserving semantic boundaries.
- **Metadata Preservation**: Frontmatter fields (YAML) from markdown files are parsed and stored as filterable metadata alongside the vectors in the database.
- **Incremental Updates**: Tracks file hashes; only re-embeds documents that have changed, saving compute resources.
- **Deduplication**: Ensures identical chunks are not duplicated in the vector store.

## 5. Conversation Persistence

- **Storage**: Every conversation session is serialized and saved as a markdown file to `vault/conversations/`.
- **Receipts**: Actions taken by the agent (e.g., tool executions, file edits) are summarized and saved to `vault/receipts/` for auditability.
- **Linking**: Conversations can be linked from daily notes using standard Obsidian wikilinks (`[[...]]`).
- **Searchability**: Conversations are ingested by the embedding pipeline, making past chats searchable via semantic queries.

## 6. Performance Requirements

- **Vector Search Latency**: `< 100ms` for retrieving top-k results to ensure snappy interactive responses.
- **Embedding Generation**: `< 500ms` per document (on standard CPU, faster with GPU acceleration).
- **Index Rebuild**: `< 5 minutes` for a full rebuild of a 10,000 document vault.
- **Memory Footprint**: The local vector database and embedding model must consume `< 2GB` of system RAM.
