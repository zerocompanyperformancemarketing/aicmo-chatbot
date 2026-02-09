# CLAUDE.md — AICMO Chatbot

## Project Overview

Podcast Knowledge Chatbot that turns a podcast library into a searchable knowledge platform.
Uses multi-agent RAG: users ask questions, a LangGraph supervisor routes to specialized agents
(search, quote, summary, recommendation) that query Typesense via MCP tools and synthesize answers.

## Tech Stack

| Layer        | Technology                                             |
|------------- |--------------------------------------------------------|
| API          | FastAPI 0.128+, Python 3.12, Uvicorn                  |
| Agents       | LangGraph + LangGraph Supervisor, LangChain OpenAI    |
| Tools        | FastMCP (HTTP transport), 9 Typesense-backed tools     |
| Search       | Typesense 30.1 (auto-embedding, hybrid keyword+vector) |
| Database     | MySQL 8.0, SQLAlchemy 2.0 async, aiomysql             |
| LLM          | OpenRouter API (openai/gpt-5.2 via ChatOpenAI)        |
| Frontend     | Next.js 15 (public + internal modes)                   |
| Infra        | Docker Compose, uv package manager                     |

## Key Directories

```
api/              FastAPI backend — agents, ingestion pipeline, DB models, routers
  agents/         LangGraph multi-agent system (supervisor + 4 specialist agents)
  ingestion/      VTT parsing → speaker detection → metadata → chunking → Typesense
  routers/        /chat and /ingest endpoints
  db/             SQLAlchemy models & async CRUD (Conversation, Message)
mcp/              FastMCP server — 9 tools (search, filter, metadata, scrape, slack)
  tools/          Tool implementations (search.py, filter.py, metadata.py)
  utils/          Typesense client, scraping, Slack webhook
frontend/         Next.js 15 chat UI (must be built via Docker — no Node.js on dev machine)
tests/            86-test pytest suite (all external services mocked)
  api/            API unit tests (vtt, chunker, metadata, speaker, pipeline, schemas, crud, routers)
  mcp/            MCP tool + utility tests (search, filter, metadata, scrape, slack)
db/               Runtime volumes (mysql-data/, typesense-data/)
transcripts/ Sample VTT file for testing ingestion
```

## Essential Commands

### Docker Compose (primary workflow)

```bash
docker-compose up -d          # Start all 5 services
docker-compose down            # Stop all services
docker-compose logs -f api     # Tail API logs (also: mcp, ts_db, mysql, frontend)
```

### Tests

```bash
cd tests && uv sync            # Install test deps (first time)
uv run pytest -v               # Run all 86 tests (~2s, all mocked)
uv run pytest api/ -v          # API tests only
uv run pytest mcp/ -v          # MCP tests only
```

Expected: `86 passed, 3 warnings` (warnings are harmless AsyncMock artifacts).

### Ingestion

```bash
# Single file
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/episode.vtt"}'

# Directory
curl -X POST http://localhost:8000/ingest/directory \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/path/to/transcripts"}'
```

### Chat

**Web Interface (recommended):**
- Open browser to http://localhost:3000/chat
- Type your question and click Send

**API (curl):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What did Julie Harrell say about profitability?"}'
```

## Environment

Two env files: `.env` (local dev, localhost hosts) and `.env.docker` (container hostnames).
Key variables: `OPENROUTER_API_KEY`, `TS_API_KEY`, `DB_*`, `MCP_URL`, `NEXT_PUBLIC_API_URL`, `SCRAPINGBEE_API_KEY`.

## Entry Points

- API server: `api/main.py` — FastAPI app with lifespan, creates DB tables on startup
- MCP server: `mcp/server.py` — FastMCP HTTP app, 9 tools registered
- Supervisor: `api/agents/supervisor.py` — LangGraph orchestrator for 4 agents
- Pipeline: `api/ingestion/pipeline.py` — VTT → speaker detect → metadata → chunk → Typesense

## Git Workflow (MANDATORY)

**Never commit directly to main.** Always create a branch first:

```bash
git checkout -b feature/<short-description>   # New feature
git checkout -b fix/<short-description>        # Bug fix
```

Perform all work on the branch for the remainder of the session.

## Additional Documentation

Check these files when working on specific areas:

| Topic                          | File                                           |
|-------------------------------|------------------------------------------------|
| Architecture & implementation | `.claude/docs/architecture.md`                 |
| Testing guide & patterns      | `.claude/docs/testing.md`                      |
| Ingestion pipeline details    | `.claude/docs/ingestion.md`                    |
| MCP tools reference           | `.claude/docs/mcp-tools.md`                    |
| Business requirements         | `REQUIREMENTS.MD`                              |
| Technical plan                | `PLAN.md`                                      |
| Test suite overview           | `tests/README.md`                              |
