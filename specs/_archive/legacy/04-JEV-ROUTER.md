# AGENTIC OS — JEV ROUTER SPECIFICATION

## 1. Purpose & Concept
JEV (named after the TypeSafe AI System-1 concept) is the intelligent request classifier that sorts every incoming request into the right processing tier. It acts as the "System 1" fast-thinking layer, modeled after Kahneman's dual-process theory as highlighted by Karpathy.

- **"System 1" fast classifier**: Rapidly assesses requests and determines handling strategy.
- **Cheapest/Fastest Principle**: Always determines the most efficient way to handle a request, minimizing cost and latency.
- **Confidence-gated cascade**: Routes to the simplest tier that can handle the task, escalating only when confidence falls below thresholds.
- **Target**: Sub-200ms classification latency.

## 2. The Three Tiers

### Tier 1: Deterministic (No AI)
- **Description**: Rules + saved data, no AI needed. Uses pattern matching, cached responses, and direct lookups.
- **Examples**: 
  - "What are my priorities?" → Read `priorities.md`.
  - "What time is it?" → Read system clock.
- **Latency**: <10ms
- **Cost**: $0
- **Implementation**: Regex patterns, keyword matching, SQLite lookups, cached semantic matches.

### Tier 2: Quick Answer (Small Fast Model)
- **Description**: Small, fast model (e.g., Claude 3 Haiku, GPT-4o-mini, local Qwen/Phi). Ideal for summarization, simple Q&A, and formatting tasks without complex reasoning.
- **Examples**:
  - "Summarize today's AI news" → Haiku reads RSS.
  - "Rewrite this email" → Quick LLM call.
- **Latency**: 100-500ms
- **Cost**: <$0.001
- **Implementation**: Direct LLM call with a constrained context window.

### Tier 3: Real Work (Frontier Model + Tools)
- **Description**: Full agentic loop using frontier models (e.g., Claude 3.5 Sonnet, GPT-4o). Opens terminal, executes code, runs background skills. For complex research, multi-step workflows, and analysis.
- **Examples**:
  - "Research competitors and write a report" → Multi-agent workflow.
  - "Build me a landing page" → Claude Code terminal session.
- **Latency**: 5s - 5min
- **Cost**: $0.01 - $5.00
- **Implementation**: Agentic loop with robust tool access, reflection, and multi-step reasoning capabilities.

## 3. Classification Algorithm

1. **Tier 0 Check**: Exact match against cached intents/responses. If found → instant return.
2. **Rule Engine**: Fast pattern matching against known deterministic commands and keywords.
3. **SLM Classification**: A Small Language Model classifies intent, domain, complexity, and urgency.
4. **Confidence Gate**: 
   - If confidence >= 0.85 → route to the classified tier.
   - If confidence < 0.85 → escalate to Tier 3 for deep reasoning.

```mermaid
flowchart TD
    A[Incoming Request] --> B{Tier 0 Check\n(Cache/Exact Match)}
    B -- Match --> C[Return Cached Response\n<5ms]
    B -- No Match --> D{Rule Engine\n(Regex/Keywords)}
    D -- Match --> E[Tier 1: Deterministic\n<10ms]
    D -- No Match --> F[SLM Classification\n(Intent, Domain, Complexity)]
    F --> G{Confidence Gate\n>= 0.85}
    G -- Yes (Tier 2 classified) --> H[Tier 2: Quick Answer\n100-500ms]
    G -- Yes (Tier 3 classified) --> I[Tier 3: Real Work\n5s-5m]
    G -- No (< 0.85) --> I
```

## 4. Classification Schema

The JEV router outputs a structured classification for downstream handling:

```json
{
  "tier": 1,
  "confidence": 0.92,
  "intent": "lookup | summarize | research | code | schedule | ...",
  "domain": "memory | productivity | research | content | community | clients | sales | finance",
  "urgency": "immediate | normal | background",
  "requires_tools": ["vault_read", "calendar", "web_search"],
  "estimated_cost": "$0.00",
  "estimated_latency_ms": 10
}
```

## 5. Implementation Options

- **JEV (TypeSafe AI)**: Fastest, purpose-built System-1 classifier utilizing typed structures and guaranteed output schemas.
- **Semantic Router (Aurelio Labs)**: Vector-space routing using embeddings. Extremely fast but less granular than LLM-based parsing.
- **RouteLLM (LMSYS)**: Open-source framework optimized for cheap/expensive model routing based on complexity thresholds.
- **Custom Fine-Tuned SLM**: Training a small model (e.g., Phi-3, Qwen 2.5) specifically on user intents and workflows.
- **Rule-based + Embedding Hybrid**: Fast layer of regex combined with semantic similarity search against known query clusters.

## 6. Training & Calibration

- **Defining Intent Categories**: Mapped to standard OS primitives (e.g., File I/O, App Launch, Context Retrieval, Web Search).
- **Calibrating Confidence Thresholds**: Start at 0.85, adjust dynamically based on error rates and tier 3 invocation frequency.
- **Feedback Loop**: User corrections or agent failure traces are fed back to tune embeddings/rules or fine-tune the SLM.
- **A/B Testing**: Randomly sample a subset of requests assigned to Tier 2 and route them to Tier 3 to measure quality differential and adjust thresholds.

## 7. Performance Requirements

- **Classification Latency**: <200ms
- **Accuracy Target**: >90% correct tier assignment
- **False Positive Rate for Tier 3**: <15% (avoid over-routing simple tasks to expensive models)
