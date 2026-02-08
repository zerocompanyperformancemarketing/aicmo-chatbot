# AICMO Chatbot — Test Suite

## Setup

From the `tests/` directory:

```bash
cd tests
uv sync
```

This installs all test dependencies (pytest, pytest-asyncio, pytest-mock, etc.) into a local `.venv`.

## Running Tests

**Run all tests:**

```bash
uv run pytest -v
```

**Run a specific module:**

```bash
uv run pytest api/test_vtt_parser.py -v
uv run pytest mcp/test_search.py -v
```

**Run a specific test class or method:**

```bash
uv run pytest api/test_chunker.py::TestChunkSegments::test_overlap_words_carry_over -v
```

**Run only API or MCP tests:**

```bash
uv run pytest api/ -v
uv run pytest mcp/ -v
```

## Test Coverage

| Module | File | Tests | What's tested |
|--------|------|------:|---------------|
| **API — Ingestion** | `test_vtt_parser.py` | 11 | Timestamp conversion, VTT cue merging, sentence splitting, gap detection |
| **API — Ingestion** | `test_chunker.py` | 8 | Word chunking, overlap carry-over, chunk indices, speaker attribution, metadata |
| **API — Ingestion** | `test_metadata_extractor.py` | 7 | Filename parsing (`extract_from_filename`) |
| **API — Ingestion** | `test_metadata_extractor_async.py` | 4 | LLM-based metadata extraction (mocked), JSON/markdown fence handling |
| **API — Ingestion** | `test_speaker_detector.py` | 4 | LLM-based speaker detection (mocked), batching, error handling |
| **API — Ingestion** | `test_pipeline.py` | 6 | Full pipeline orchestration, episode ID, guest fallback, directory ingestion (mocked) |
| **API — Schemas** | `test_schemas.py` | 12 | All Pydantic request/response/data models and defaults |
| **API — DB** | `test_crud.py` | 6 | `get_or_create_conversation`, `get_messages`, `save_message` (mocked sessions) |
| **API — Routers** | `test_chat_router.py` | 3 | Chat endpoint: new conversation, history loading, fallback response |
| **API — Routers** | `test_ingest_router.py` | 2 | Ingest single file and directory endpoints |
| **MCP — Tools** | `test_search.py` | 4 | Hybrid transcript search, filters, empty results, limit |
| **MCP — Tools** | `test_filter.py` | 4 | Industry and speaker faceted filtering |
| **MCP — Tools** | `test_metadata.py` | 5 | Episode metadata retrieval, speaker/industry aggregation |
| **MCP — Utils** | `test_scrape_utils.py` | 7 | ScrapingBee scraping, web search, extract rules, error handling |
| **MCP — Utils** | `test_slack_utils.py` | 3 | Slack webhook payload structure, missing URL error |
| | **Total** | **86** | |

## Expected Output

A successful run looks like:

```
======================== 86 passed, 3 warnings in ~2s ========================
```

The 3 warnings are `RuntimeWarning: coroutine was never awaited` from `session.add()` calls in CRUD tests — these are harmless artifacts of mocking synchronous methods on an `AsyncMock` session and do not affect correctness.

## How It Works

- **No external services required.** All tests mock external dependencies (MySQL, Typesense, LLM, ScrapingBee, Slack).
- `conftest.py` adds `api/` and `mcp/` to `sys.path` so test files can import source modules directly.
- Router tests use `sys.modules.setdefault()` to stub heavy transitive imports (LangGraph) that aren't needed for unit testing.
