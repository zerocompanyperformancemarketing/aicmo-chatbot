# AICMO Podcast Knowledge Chatbot

Multi-agent RAG chatbot that turns a podcast transcript library into a searchable knowledge platform. Users ask natural-language questions and a LangGraph supervisor routes them to specialized agents (search, quote, summary, recommendation) that query Typesense via MCP tools and synthesize answers.

## Architecture

```
┌──────────────┐         ┌──────────────┐
│   Next.js    │  HTTP   │   FastAPI    │
│   Frontend   │────────▶│   API :8000  │
└──────────────┘         └──────┬───────┘
                                │
                     LangGraph Supervisor
                      ┌────┬────┬────┐
                      │    │    │    │
                   Search Quote Sum  Rec    ◀── 4 specialist agents
                      │    │    │    │
                      └────┴────┴────┘
                                │
                          MCP client (HTTP)
                                │
                         ┌──────▼───────┐
                         │  FastMCP     │
                         │  Server :8001│
                         └──────┬───────┘
                                │
                 ┌──────────────┼──────────────┐
                 │              │              │
          ┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
          │ Typesense   │ │  MySQL   │ │  External   │
          │ :8108       │ │  :3306   │ │  APIs       │
          │ search +    │ │ users &  │ │ ScrapingBee │
          │ embeddings  │ │ history  │ │ Slack       │
          └─────────────┘ └──────────┘ └─────────────┘
```

## Tech Stack

| Layer    | Technology                                              |
| -------- | ------------------------------------------------------- |
| API      | FastAPI, Python 3.12, Uvicorn                           |
| Agents   | LangGraph + LangGraph Supervisor, LangChain OpenAI      |
| Tools    | FastMCP (HTTP transport), 9 Typesense-backed tools       |
| Search   | Typesense 30.1 (auto-embedding, hybrid keyword + vector) |
| Database | MySQL 8.0, SQLAlchemy 2.0 async, aiomysql                |
| LLM      | OpenRouter API (OpenAI-compatible)                       |
| Frontend | Next.js 15                                               |
| Infra    | Docker Compose, uv package manager                       |

## Project Structure

```
api/
  main.py               FastAPI entry point
  config.py             Settings from env vars
  agents/               LangGraph supervisor + 4 specialist agents
  ingestion/            VTT parsing, speaker detection, chunking, pipeline
  routers/              /chat and /ingest endpoints
  db/                   SQLAlchemy models & async CRUD
  models/               Pydantic request/response schemas
mcp/
  server.py             FastMCP server entry point
  tools/                search, filter, metadata, scrape, slack tools
  utils/                Typesense client, scraping, Slack helpers
frontend/               Next.js 15 chat UI (public + internal modes)
tests/                  86-test pytest suite (all external services mocked)
sample_transcript/      Sample VTT file for testing ingestion
docker-compose.yml      All 4 services
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Python 3.12+](https://www.python.org/) (for running tests locally)
- [uv](https://docs.astral.sh/uv/) (Python package manager, used by tests and Dockerfiles)

## Getting Started

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd aicmo-chatbot
   ```

2. **Create environment files**

   ```bash
   cp .env.example .env
   cp .env.example .env.docker
   ```

   Edit both files and fill in your API keys. The `.env` file uses `localhost` for service hosts (local dev). The `.env.docker` file needs container hostnames instead:

   | Variable  | `.env` value  | `.env.docker` value |
   | --------- | ------------- | ------------------- |
   | `TS_HOST` | `localhost`   | `ts_db`             |
   | `DB_HOST` | `localhost`   | `mysql`             |
   | `MCP_URL` | `http://localhost:8001/mcp` | `http://mcp:8001/mcp` |

3. **Start all services**

   ```bash
   docker-compose up -d
   ```

   This starts four containers: `ts_db` (Typesense), `mysql`, `mcp` (FastMCP), and `api` (FastAPI).

4. **Verify services are running**

   ```bash
   curl http://localhost:8000/health
   # {"status": "ok"}
   ```

5. **Ingest a sample transcript**

   ```bash
   curl -X POST http://localhost:8000/ingest \
     -H "Content-Type: application/json" \
     -d '{"file_path": "/app/sample_transcript/Balancing Profit and Social Responsibility with Julie Harrell _unedited_.vtt"}'
   ```

## Environment Variables

| Variable              | Description                                      | Required |
| --------------------- | ------------------------------------------------ | -------- |
| `TS_PORT`             | Typesense port (default `8108`)                  | Yes      |
| `TS_DATA_DIR`         | Typesense data volume path                       | Yes      |
| `TS_API_KEY`          | Typesense API key                                | Yes      |
| `TS_HOST`             | Typesense hostname                               | Yes      |
| `DB_HOST`             | MySQL hostname                                   | Yes      |
| `DB_PORT`             | MySQL port (default `3306`)                      | Yes      |
| `DB_USER`             | MySQL username                                   | Yes      |
| `DB_PASSWORD`         | MySQL password                                   | Yes      |
| `DB_NAME`             | MySQL database name                              | Yes      |
| `MCP_URL`             | FastMCP server URL                               | Yes      |
| `OPENROUTER_API_KEY`  | OpenRouter API key for LLM access                | Yes      |
| `OPENROUTER_BASE_URL` | OpenRouter base URL                              | Yes      |
| `OPENROUTER_MODEL`    | Model identifier (e.g. `openai/gpt-5.2`)        | Yes      |
| `SCRAPINGBEE_API_KEY` | ScrapingBee API key for web search/scrape tools  | No       |
| `SLACK_WEBHOOK_URL`   | Slack incoming webhook URL for notifications     | No       |

## Running Tests

Tests run outside Docker using `uv` and require no running services (all external calls are mocked).

```bash
cd tests
uv sync            # Install test dependencies (first time)
uv run pytest -v   # Run all 86 tests
```

Run subsets:

```bash
uv run pytest api/ -v   # API tests only
uv run pytest mcp/ -v   # MCP tests only
```

Expected output: `86 passed`.

## API Usage

### Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What did Julie Harrell say about profitability?"}'
```

### Ingest a single file

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/episode.vtt"}'
```

### Ingest a directory

```bash
curl -X POST http://localhost:8000/ingest/directory \
  -H "Content-Type: application/json" \
  -d '{"directory_path": "/path/to/transcripts"}'
```

### Health check

```bash
curl http://localhost:8000/health
```

## Development

### Running services locally (outside Docker)

You still need Typesense and MySQL running (via Docker or installed locally). Then:

**MCP server:**

```bash
cd mcp
uv sync
uv run uvicorn server:create_app --factory --host 0.0.0.0 --port 8001
```

**API server:**

```bash
cd api
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Make sure your `.env` file uses `localhost` for `TS_HOST`, `DB_HOST`, and `MCP_URL`.

### Viewing logs

```bash
docker-compose logs -f api     # API logs
docker-compose logs -f mcp     # MCP server logs
docker-compose logs -f ts_db   # Typesense logs
docker-compose logs -f mysql   # MySQL logs
```

### Stopping services

```bash
docker-compose down
```
