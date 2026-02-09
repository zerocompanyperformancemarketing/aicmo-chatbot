#!/bin/bash

curl -X POST http://localhost:8000/ingest/directory \
    -H "Content-Type: application/json" \
    -d '{"directory_path": "/app/transcripts"}'