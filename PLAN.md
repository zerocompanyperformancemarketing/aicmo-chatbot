# Implementation Plan — Podcast Knowledge Chatbot (Backend)

## Scope

Backend-only: FastAPI + LangGraph Agents + FastMCP + Typesense.
No frontend, no authentication for now. Focus on core chatbot and ingestion functionality.

---

## Current State

- **Typesense 30.1** service defined in `docker-compose.yml`
- **Empty directories**: `api/`, `api/agents/`, `mcp/`, `db/`
- **One sample transcript**: VTT format, ~37 min episode, no speaker labels
  - Podcast: "The Bliss Business Podcast"
  - Hosts: Steven Sikash, Mike Liske
  - Guest: Julie Harrell (President, Cooper Scoopers)
- **.env**: Typesense config + OpenRouter API key (model: `openai/gpt-5.2`)

### Key Observations About the VTT Format

- Standard WebVTT with fine-grained timestamps (short phrases per cue, 2-5 words each)
- **No speaker labels** — speaker attribution must be inferred
- Cues need to be merged into complete sentences before chunking
- Episode metadata (guest name, title) can be partially extracted from filename

---

## Target Directory Structure

```
aicmo-chatbot/
├── docker-compose.yml          # All services
├── .env                        # Environment variables
├── REQUIREMENTS.MD
├── PLAN.md
│
├── api/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings (from .env)
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── pipeline.py         # Orchestrates full ingestion flow
│   │   ├── vtt_parser.py       # Parse VTT → timestamped text
│   │   ├── chunker.py          # Merge cues + chunk into ~500-word segments
│   │   ├── speaker_detector.py # LLM-based speaker attribution agent
│   │   └── metadata_extractor.py # LLM-based metadata extraction from filename + content
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── supervisor.py       # LangGraph supervisor (query router)
│   │   ├── search_agent.py     # Semantic search across transcripts
│   │   ├── quote_agent.py      # Extract quotes with speaker attribution
│   │   ├── summary_agent.py    # Topic-based summaries
│   │   ├── recommendation_agent.py  # Episode/speaker recommendations
│   │   │
│   │   ├── state/
│   │   │   ├── __init__.py
│   │   │   └── agent_state.py  # LangGraph state definitions (shared state schema, per-agent state)
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── llm.py          # LLM client factory (OpenRouter ChatOpenAI setup)
│   │       ├── mcp_client.py   # FastMCP client setup and LangChain tool adapter
│   │       └── prompts.py      # Shared system prompts and prompt templates
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models for API + internal data
│   │
│   └── routers/
│       ├── __init__.py
│       ├── chat.py             # POST /chat — main chatbot endpoint
│       └── ingest.py           # POST /ingest — trigger transcript ingestion
│
├── mcp/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── server.py               # FastMCP server entry point
│   ├── utils/
│   │   ├── __init__.py
│   │   └── typesense_client.py # Typesense client setup and collection helpers
│   └── tools/
│       ├── __init__.py
│       ├── search.py           # search_transcripts tool
│       ├── filter.py           # filter_by_industry, filter_by_speaker tools
│       └── metadata.py         # get_episode_metadata, get_speaker_info tools
│
├── db/
│   └── typesense-data/         # Typesense data volume (gitignored)
│
└── sample_transcript/
    └── *.vtt                   # Sample transcripts for testing
```

---

## Phase 1: Foundation & Infrastructure

### 1.1 Docker Compose Setup

Add services to `docker-compose.yml`:

| Service     | Image / Build        | Port  | Purpose                        |
|-------------|----------------------|-------|--------------------------------|
| `ts_db`     | typesense/typesense:30.1 | 8108  | Search engine (already defined) |
| `api`       | Build from `api/`    | 8000  | FastAPI backend                |
| `mcp`       | Build from `mcp/`    | 8001  | FastMCP tool server            |

- All services on a shared Docker network
- `api` depends on `ts_db` and `mcp`
- `mcp` depends on `ts_db`
- Volume mount `sample_transcript/` into `api` for ingestion

### 1.2 Python Project Setup

**Package manager:** `uv` (Astral) — used for dependency management and virtualenvs in both services.

**api/pyproject.toml** (managed by `uv`):
- `fastapi`, `uvicorn`
- `langchain-openai` (ChatOpenAI for OpenRouter)
- `langgraph` (agent orchestration)
- `fastmcp` (FastMCP client to connect agents to MCP tools)
- `typesense` (Python client)
- `webvtt-py` (VTT parsing)
- `pydantic-settings`

**mcp/pyproject.toml** (managed by `uv`):
- `fastmcp`
- `typesense`
- `pydantic-settings`

Dockerfiles will use `uv` to install deps (`COPY --from=ghcr.io/astral-sh/uv ...` multi-stage pattern).

### 1.3 Typesense Collections

**Collection: `episodes`**
```json
{
  "name": "episodes",
  "fields": [
    {"name": "title", "type": "string"},
    {"name": "guest_names", "type": "string[]"},
    {"name": "host_names", "type": "string[]"},
    {"name": "industry", "type": "string", "facet": true},
    {"name": "topic_tags", "type": "string[]", "facet": true},
    {"name": "episode_link", "type": "string", "optional": true},
    {"name": "summary", "type": "string"},
    {"name": "duration_seconds", "type": "int32"},
    {"name": "source_file", "type": "string"}
  ]
}
```

**Collection: `transcript_chunks`**
```json
{
  "name": "transcript_chunks",
  "fields": [
    {"name": "episode_id", "type": "string", "reference": "episodes.id"},
    {"name": "text", "type": "string"},
    {"name": "speaker", "type": "string", "facet": true},
    {"name": "start_time", "type": "float"},
    {"name": "end_time", "type": "float"},
    {"name": "chunk_index", "type": "int32"},
    {"name": "guest_names", "type": "string[]"},
    {"name": "industry", "type": "string", "facet": true},
    {"name": "topic_tags", "type": "string[]", "facet": true},
    {"name": "embedding", "type": "float[]",
      "embed": {
        "from": ["text"],
        "model_config": {
          "model_name": "openai/text-embedding-3-large",
          "api_key": "OPENROUTER_API_KEY"
        }
      }
    }
  ]
}
```

- Auto-embedding on `text` field using OpenAI `text-embedding-3-large` via Typesense's remote embedding support
- Denormalized metadata (`guest_names`, `industry`, `topic_tags`) on chunks for efficient filtering
- `speaker` field faceted for speaker-based queries

---

## Phase 2: Ingestion Pipeline

### 2.1 VTT Parser (`api/ingestion/vtt_parser.py`)

- Use `webvtt-py` to parse VTT files
- Extract list of `(start_time, end_time, text)` cues
- Merge consecutive short cues into complete sentences/paragraphs
  - Strategy: concatenate cues until a sentence-ending punctuation or a natural pause (>2s gap between cues)
- Output: list of merged segments with start/end timestamps

### 2.2 Speaker Detection Agent (`api/ingestion/speaker_detector.py`)

**Hybrid approach — LLM with optional manual override:**

1. **Manual metadata path**: If a metadata JSON file is provided alongside the VTT (e.g., `episode.json` with speaker timestamp ranges), use that directly
2. **LLM agent path** (default): Use OpenRouter LLM to identify speakers
   - **Step 1**: Extract speaker names from the filename + first few minutes of transcript (introductions)
   - **Step 2**: For each merged segment, use LLM to assign the most likely speaker based on:
     - Contextual clues ("Julie, welcome" → next speaker is Julie)
     - Conversation flow (question/answer patterns)
     - Content attribution ("As I mentioned in my business...")
   - **Step 3**: Validation pass — ensure speaker assignments are consistent and reasonable (no rapid impossible switches)

- Process in batches to manage token costs
- Use structured output (JSON mode) to get clean speaker labels
- Include confidence score; flag low-confidence assignments for review

### 2.3 Metadata Extraction (`api/ingestion/metadata_extractor.py`)

**From filename:**
- Parse episode title and guest name from filename pattern
- Example: `"Balancing Profit and Social Responsibility with Julie Harrell _unedited_.vtt"`
  → title: "Balancing Profit and Social Responsibility"
  → guest: "Julie Harrell"

**From transcript content (via LLM):**
- Feed the first ~2000 words + last ~500 words to the LLM
- Extract:
  - Industry/category of the guest's business
  - 3-5 topic tags
  - Brief episode summary (2-3 sentences)
  - Host names
  - Guest company/role
- Use structured output (JSON mode) for reliable extraction

### 2.4 Text Chunker (`api/ingestion/chunker.py`)

- Input: merged segments with speaker labels and timestamps
- Strategy: **500-word chunks with 50-word overlap**
- Chunk boundaries respect:
  - Speaker turns (prefer breaking between speakers)
  - Natural paragraph/topic boundaries
- Each chunk includes:
  - Text content
  - Primary speaker(s) for that chunk
  - Start/end timestamps
  - Chunk index (sequential)

### 2.5 Ingestion Pipeline Orchestrator (`api/ingestion/pipeline.py`)

Full flow:
```
VTT file
  → vtt_parser.parse(file_path)
  → speaker_detector.detect(segments, metadata_override=None)
  → metadata_extractor.extract(filename, segments)
  → chunker.chunk(segments_with_speakers)
  → typesense_client.upsert(episodes_collection, episode_doc)
  → typesense_client.upsert(transcript_chunks_collection, chunk_docs)
```

- Accept a directory path or single file
- Idempotent: re-ingesting same file updates existing records (keyed by source_file)
- Log progress and errors

---

## Phase 3: MCP Server (FastMCP)

### 3.1 Server Setup (`mcp/server.py`)

- FastMCP server running on port 8001
- SSE transport (`mcp.run(transport="sse")`)
- Connects to Typesense via Python client

### 3.2 MCP Tools

**`search_transcripts(query: str, limit: int = 10, industry: str = None, speaker: str = None) → list[dict]`**
- Hybrid search (semantic + keyword) on `transcript_chunks` collection
- Optional filters: industry, speaker
- Returns: chunk text, speaker, episode title, timestamps, relevance score

**`filter_by_industry(industry: str, limit: int = 10) → list[dict]`**
- Faceted search on `episodes` collection by industry
- Returns: matching episodes with metadata

**`filter_by_speaker(speaker_name: str, limit: int = 10) → list[dict]`**
- Search `transcript_chunks` where speaker matches
- Returns: chunks spoken by that person, with episode context

**`get_episode_metadata(episode_id: str) → dict`**
- Retrieve full episode metadata from `episodes` collection
- Returns: title, guest, industry, tags, summary, link

**`list_speakers() → list[dict]`**
- Aggregate unique speakers across all episodes
- Returns: speaker names with episode counts

**`list_industries() → list[dict]`**
- Aggregate unique industries from `episodes`
- Returns: industry names with episode counts

---

## Phase 4: LangGraph Agents

### 4.1 LLM Configuration

- Use `ChatOpenAI` pointed at OpenRouter:
  ```python
  ChatOpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key=OPENROUTER_API_KEY,
      model=OPENROUTER_MODEL  # openai/gpt-5.2
  )
  ```

### 4.2 MCP → LangGraph Tool Integration

- Use `fastmcp.Client` to connect to the FastMCP server via SSE
- Convert MCP tools into LangChain-compatible tools that agents can call
- All agents share the same FastMCP client connection

### 4.3 Agent Definitions

**Search Agent (`agents/search_agent.py`)**
- Tools: `search_transcripts`, `filter_by_industry`, `filter_by_speaker`
- Purpose: Find relevant transcript chunks based on user query
- Returns: relevant passages with metadata

**Quote Agent (`agents/quote_agent.py`)**
- Tools: `search_transcripts`, `get_episode_metadata`
- Purpose: Extract specific quotes with speaker attribution
- Behavior: Search for relevant content, then format as attributed quotes
- Returns: formatted quotes with speaker name, episode, and timestamp

**Summary Agent (`agents/summary_agent.py`)**
- Tools: `search_transcripts`, `get_episode_metadata`
- Purpose: Generate topic-based summaries across episodes
- Behavior: Gather content from multiple episodes on a topic, synthesize
- Returns: coherent summary with episode references

**Recommendation Agent (`agents/recommendation_agent.py`)**
- Tools: `filter_by_industry`, `list_speakers`, `list_industries`, `get_episode_metadata`
- Purpose: Suggest relevant episodes and speakers
- Behavior: Based on user's interest, find matching episodes
- Returns: episode recommendations with reasons

### 4.4 Supervisor (`agents/supervisor.py`)

- Use `langgraph-supervisor` to create a supervisor agent
- The supervisor acts as the **Query Router** from the requirements
- Receives user message, determines intent, delegates to appropriate agent(s)
- Can call multiple agents sequentially if needed (e.g., search → then summarize)
- System prompt instructs it to:
  - Route topic/keyword queries → Search Agent
  - Route "give me quotes about X" → Quote Agent
  - Route "summarize what guests say about X" → Summary Agent
  - Route "what episodes cover X industry" → Recommendation Agent
  - For complex queries, chain multiple agents

---

## Phase 5: FastAPI Endpoints

### 5.1 Chat Endpoint

```
POST /chat
Body: { "message": "string", "conversation_id": "string (optional)" }
Response: {
  "response": "string",
  "sources": [
    { "episode_title": "...", "speaker": "...", "timestamp": "...", "text_snippet": "..." }
  ],
  "conversation_id": "string"
}
```

- Routes message to LangGraph supervisor
- Returns structured response with source references
- `conversation_id` for future conversation memory (stateless for now)

### 5.2 Ingest Endpoint

```
POST /ingest
Body: { "file_path": "string" } OR multipart file upload
Response: { "status": "success", "episode_id": "...", "chunks_created": N }
```

- Triggers the ingestion pipeline for a single VTT file
- Returns ingestion results

### 5.3 Ingest Directory Endpoint

```
POST /ingest/directory
Body: { "directory_path": "string" }
Response: { "status": "success", "episodes_processed": N }
```

- Batch ingest all VTT files in a directory

### 5.4 Health & Utility Endpoints

```
GET /health              — Service health check
GET /episodes            — List all episodes (with optional industry filter)
GET /episodes/{id}       — Get episode details
GET /speakers            — List all speakers
GET /industries          — List all industries
```

---

## Phase 6: Implementation Order

This is the build sequence — each step is testable before moving to the next.

### Step 1: Project scaffolding
- Create all files/directories
- Write Dockerfiles for `api` and `mcp`
- Update `docker-compose.yml` with all services
- Write `config.py` and Pydantic settings
- Verify all containers start

### Step 2: Typesense collections
- Write collection creation script
- Create `episodes` and `transcript_chunks` collections
- Verify via Typesense API

### Step 3: VTT parser + chunker
- Implement `vtt_parser.py` — parse and merge cues
- Implement `chunker.py` — 500-word chunks with overlap
- Test with sample transcript (no speaker labels yet)

### Step 4: Metadata extraction
- Implement `metadata_extractor.py` — filename parsing + LLM extraction
- Test with sample transcript → verify extracted metadata

### Step 5: Speaker detection
- Implement `speaker_detector.py` — LLM-based speaker identification
- Test with sample transcript → verify speaker labels

### Step 6: Full ingestion pipeline
- Implement `pipeline.py` — wire together parser → speaker → metadata → chunker → Typesense
- Ingest sample transcript end-to-end
- Verify data in Typesense (search, facets)

### Step 7: MCP tools
- Implement FastMCP server with all tools
- Test each tool independently against Typesense data
- Verify SSE transport works

### Step 8: LangGraph agents
- Implement each agent with MCP tool access
- Test agents individually with sample queries
- Implement supervisor with routing logic
- Test multi-agent flows

### Step 9: FastAPI endpoints
- Wire up `/chat` endpoint to supervisor
- Wire up `/ingest` endpoint to pipeline
- Add utility endpoints
- Test full request flow

### Step 10: Integration testing
- End-to-end: ingest transcript → chat about it
- Test all use cases from requirements:
  - Topic search
  - Speaker queries
  - Quote extraction
  - Episode recommendations
  - Industry filtering

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Embedding model | OpenAI `text-embedding-3-large` via Typesense | Higher quality embeddings; Typesense handles embedding calls on insert/search |
| LLM provider | OpenRouter (`openai/gpt-5.2`) | Already configured; single API for all LLM calls |
| MCP transport | SSE | HTTP-based, works across Docker containers |
| Chunk size | 500 words / 50-word overlap | Balance between context and retrieval precision |
| Speaker detection | LLM agent with manual override | Handles no-label VTTs while allowing manual correction |
| Search strategy | Hybrid (semantic + keyword) | Typesense supports both; covers exact matches and semantic similarity |
| State management | Stateless for now | No conversation memory; add later with MySQL |

---

## Out of Scope (For Now)

- Frontend (Next.js) — planned for a later phase
- Authentication & authorization
- Conversation history / memory (MySQL)
- CI/CD pipeline
- Rate limiting
- Analytics/logging dashboard
- Bulk transcript upload UI
