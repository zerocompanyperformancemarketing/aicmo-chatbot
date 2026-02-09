import logging
from fastapi import APIRouter
from models.schemas import IngestFileRequest, IngestDirectoryRequest, IngestResponse, IngestDirectoryResponse
from ingestion.pipeline import ingest_file, ingest_directory

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestFileRequest):
    """Trigger ingestion pipeline for a single VTT file."""
    logger.info(f"POST /ingest | file_path={request.file_path!r}")
    result = await ingest_file(request.file_path)
    logger.info(f"POST /ingest response | status={result['status']}, episode_id={result.get('episode_id')}")
    return IngestResponse(**result)


@router.post("/ingest/directory", response_model=IngestDirectoryResponse)
async def ingest_dir(request: IngestDirectoryRequest):
    """Batch ingest all VTT files in a directory."""
    logger.info(f"POST /ingest/directory | directory_path={request.directory_path!r}")
    result = await ingest_directory(request.directory_path)
    logger.info(f"POST /ingest/directory response | episodes_processed={result.get('episodes_processed')}")
    return IngestDirectoryResponse(**result)
