from fastapi import APIRouter
from models.schemas import IngestFileRequest, IngestDirectoryRequest, IngestResponse, IngestDirectoryResponse
from ingestion.pipeline import ingest_file, ingest_directory

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestFileRequest):
    """Trigger ingestion pipeline for a single VTT file."""
    result = await ingest_file(request.file_path)
    return IngestResponse(**result)


@router.post("/ingest/directory", response_model=IngestDirectoryResponse)
async def ingest_dir(request: IngestDirectoryRequest):
    """Batch ingest all VTT files in a directory."""
    result = await ingest_directory(request.directory_path)
    return IngestDirectoryResponse(**result)
