# Testing Guide

## Setup

```bash
cd tests
uv sync          # Install deps from tests/pyproject.toml
```

## Running Tests

```bash
uv run pytest -v                    # All 86 tests
uv run pytest api/ -v               # API tests only (49 tests)
uv run pytest mcp/ -v               # MCP tests only (37 tests)
uv run pytest api/test_chunker.py -v  # Single module
uv run pytest api/test_chunker.py::TestChunkSegments::test_overlap_words_carry_over -v  # Single test
```

Expected output: `86 passed, 3 warnings in ~2s`
The 3 warnings are harmless `AsyncMock` artifacts from pytest-asyncio.

## Test Structure

All external services are **fully mocked** — no MySQL, Typesense, LLM, or ScrapingBee needed.

```
tests/
├── conftest.py                      # Adds api/ and mcp/ to sys.path
├── api/
│   ├── test_vtt_parser.py           # 11 tests — VTT cue parsing, merging, edge cases
│   ├── test_chunker.py              # 8 tests — Word chunking, overlap, speaker attribution
│   ├── test_metadata_extractor.py   # Filename-based metadata parsing
│   ├── test_metadata_extractor_async.py  # LLM-based extraction (mocked)
│   ├── test_speaker_detector.py     # Speaker detection (mocked LLM)
│   ├── test_pipeline.py             # Full pipeline orchestration (mocked)
│   ├── test_schemas.py              # 12 tests — Pydantic model validation
│   ├── test_crud.py                 # 6 tests — DB CRUD (mocked AsyncSession)
│   ├── test_chat_router.py          # Chat endpoint (mocked supervisor)
│   └── test_ingest_router.py        # Ingest endpoints (mocked pipeline)
└── mcp/
    ├── test_search.py               # Transcript search tool
    ├── test_filter.py               # Industry/speaker filter tools
    ├── test_metadata.py             # Episode metadata tools
    ├── test_scrape_utils.py         # Web scraping & search
    └── test_slack_utils.py          # Slack webhook
```

## Writing New Tests

- Place API tests in `tests/api/`, MCP tests in `tests/mcp/`
- Mock all external calls (Typesense, MySQL, LLM, HTTP)
- Use `pytest.mark.asyncio` for async tests
- Use `unittest.mock.AsyncMock` for async function mocks
- `conftest.py` handles path setup — imports work as `from ingestion.chunker import ...`

## Coverage by Module

| Module           | Tests | Key assertions                                    |
|-----------------|-------|---------------------------------------------------|
| VTT Parser      | 11    | Cue merging, timestamp handling, empty input       |
| Chunker         | 8     | Word count, overlap, speaker tags, edge cases      |
| Metadata        | 3+    | Filename parsing, LLM extraction, fallback         |
| Speaker Detect  | 3+    | LLM response parsing, error handling               |
| Pipeline        | 3+    | End-to-end orchestration, file/directory modes     |
| Schemas         | 12    | All Pydantic models, validation, defaults          |
| CRUD            | 6     | Create/get conversation, add message, list          |
| Routers         | 5     | Chat + ingest HTTP endpoints, error responses      |
| MCP Search      | 4+    | Typesense query construction, result formatting    |
| MCP Filter      | 4+    | Industry/speaker faceted filtering                 |
| MCP Metadata    | 5+    | Episode detail, list speakers/industries           |
| Scraping        | 5+    | ScrapingBee calls, HTML parsing, error handling    |
| Slack           | 5+    | Webhook POST, message formatting                   |
