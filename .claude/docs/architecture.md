# Architecture

## Service Topology (Docker Compose)

```
┌──────────┐    ┌──────────┐    ┌───────────┐    ┌─────────┐
│ Frontend │───▶│   API    │───▶│    MCP    │───▶│Typesense│
│ :3000    │    │ :8000    │    │ :8001     │    │ :8108   │
└──────────┘    └────┬─────┘    └───────────┘    └─────────┘
                     │
                     ▼
                ┌─────────┐
                │  MySQL  │
                │ :3306   │
                └─────────┘
```

- **API** depends on MCP (started), Typesense (started), MySQL (healthy)
- **MCP** depends on Typesense (started)
- Volumes: `db/typesense-data/`, `db/mysql-data/`

## Multi-Agent System

The LangGraph supervisor (`api/agents/supervisor.py`) routes user queries to 4 agents:

| Agent          | File                              | Purpose                        |
|---------------|-----------------------------------|--------------------------------|
| Search Agent  | `api/agents/search_agent.py`      | Transcript search via MCP      |
| Quote Agent   | `api/agents/quote_agent.py`       | Extract verbatim quotes        |
| Summary Agent | `api/agents/summary_agent.py`     | Generate episode summaries     |
| Recommendation| `api/agents/recommendation_agent.py`| Suggest relevant episodes    |

All agents get their tools from the MCP server via `api/agents/utils/mcp_client.py`.
System prompts live in `api/agents/utils/prompts.py`.

## LLM Configuration

OpenRouter provides the LLM via OpenAI-compatible API (`api/agents/utils/llm.py`):

```python
ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    model="openai/gpt-5.2",
    temperature=0.0
)
```

## Database Models

Defined in `api/db/models.py`:

- **Conversation**: `id` (UUID PK), `created_at`, `updated_at`, messages (relationship)
- **Message**: `id` (int PK), `conversation_id` (FK), `role`, `content`, `sources` (JSON), `created_at`

Async session setup: `api/db/session.py`
CRUD operations: `api/db/crud.py`

## Typesense Auto-Embedding

Typesense handles vector embeddings automatically (no external embedding service needed):
- Model: `ts/all-MiniLM-L12-v2`
- Field config: `embed.from = ["text"]` with model_config
- Enables hybrid search (keyword + semantic similarity)
- Schema creation: `mcp/utils/typesense_client.py`

## Request Flow

1. User sends message to `POST /chat` (`api/routers/chat.py`)
2. Router loads/creates conversation, appends user message to DB
3. Supervisor receives message + conversation history
4. Supervisor selects agent(s), agent calls MCP tools
5. MCP server queries Typesense, returns results
6. Agent synthesizes answer, supervisor returns to router
7. Router saves assistant message to DB, returns response with sources
