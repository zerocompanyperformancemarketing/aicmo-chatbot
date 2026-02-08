# Ingestion Pipeline

## Overview

The ingestion pipeline converts podcast VTT (Web Video Text Tracks) transcript files into
searchable, semantically-chunked documents in Typesense.

## Pipeline Flow

```
VTT File
  │
  ▼
Parse VTT (api/ingestion/vtt_parser.py)
  │  Merges overlapping/adjacent cues, extracts timestamps + raw text
  ▼
Detect Speakers (api/ingestion/speaker_detector.py)
  │  LLM analyzes transcript to identify speakers and attribute segments
  ▼
Extract Metadata (api/ingestion/metadata_extractor.py)
  │  Episode title from filename + LLM extracts topics, industry, guest info
  ▼
Chunk Text (api/ingestion/chunker.py)
  │  500-word chunks with 50-word overlap, preserves speaker attribution
  ▼
Upsert to Typesense (mcp/utils/typesense_client.py)
     Auto-embedding generates vectors for hybrid search
```

## Key Components

### VTT Parser (`api/ingestion/vtt_parser.py`)
- Parses WebVTT subtitle files using `webvtt-py`
- Merges overlapping/adjacent cues into continuous segments
- Outputs list of segments with start/end timestamps and text

### Speaker Detector (`api/ingestion/speaker_detector.py`)
- Sends transcript text to LLM for speaker identification
- Returns speaker names with their attributed text segments
- Fallback: extracts speaker name from filename if LLM fails

### Metadata Extractor (`api/ingestion/metadata_extractor.py`)
- **Filename parsing**: Extracts episode title, guest name from VTT filename
- **LLM extraction**: Analyzes first/last N words for topics, industry, description
- Combines both sources into complete episode metadata

### Chunker (`api/ingestion/chunker.py`)
- Splits text into **500-word chunks** with **50-word overlap**
- Preserves speaker attribution within each chunk
- Overlap ensures context continuity across chunk boundaries

### Pipeline Orchestrator (`api/ingestion/pipeline.py`)
- Coordinates all steps in sequence
- Supports single file (`ingest_file`) and directory (`ingest_directory`) modes
- Idempotent: re-ingesting the same file updates existing records

## API Endpoints

- `POST /ingest` — Single VTT file: `{"file_path": "/path/to/file.vtt"}`
- `POST /ingest/directory` — Directory of VTTs: `{"directory_path": "/path/to/dir"}`

Both endpoints are defined in `api/routers/ingest.py`.

## Typesense Document Schema

Each chunk becomes a Typesense document with fields:
- `id`: Unique chunk identifier
- `text`: Chunk content (auto-embedded for vector search)
- `episode_title`: Source episode
- `speaker`: Attributed speaker
- `industry`: Episode industry/category
- `start_timestamp`, `end_timestamp`: Time range in source audio
- `chunk_index`: Position within episode

Schema creation handled in `mcp/utils/typesense_client.py`.
