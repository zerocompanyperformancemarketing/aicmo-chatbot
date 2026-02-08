from datetime import datetime
from pydantic import BaseModel


# --- Request Models ---

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class IngestFileRequest(BaseModel):
    file_path: str


class IngestDirectoryRequest(BaseModel):
    directory_path: str


# --- Response Models ---

class Source(BaseModel):
    episode_title: str
    speaker: str
    timestamp: str
    text_snippet: str


class ChatResponse(BaseModel):
    response: str
    sources: list[Source] = []
    conversation_id: str


class IngestResponse(BaseModel):
    status: str
    episode_id: str
    chunks_created: int


class IngestDirectoryResponse(BaseModel):
    status: str
    episodes_processed: int


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: list[dict] | None = None
    created_at: datetime


class ConversationResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []


# --- Data Models ---

class EpisodeMetadata(BaseModel):
    title: str
    guest_names: list[str]
    host_names: list[str]
    industry: str
    topic_tags: list[str]
    summary: str
    episode_link: str | None = None
    duration_seconds: int = 0
    source_file: str = ""


class TranscriptChunk(BaseModel):
    episode_id: str
    text: str
    speaker: str
    start_time: float
    end_time: float
    chunk_index: int
    guest_names: list[str] = []
    industry: str = ""
    topic_tags: list[str] = []


class ParsedCue(BaseModel):
    start_time: float
    end_time: float
    text: str
    speaker: str = ""
