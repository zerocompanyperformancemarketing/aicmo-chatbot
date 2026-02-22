import re
from datetime import datetime
from pydantic import BaseModel, field_validator, model_validator


# --- Request Models ---

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    full_name: str
    is_admin: bool = False


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class RegisterResponse(BaseModel):
    message: str
    username: str


class IngestFileRequest(BaseModel):
    file_path: str
    force: bool = False


class IngestDirectoryRequest(BaseModel):
    directory_path: str
    force: bool = False


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


class ConversationSummary(BaseModel):
    id: str
    preview: str
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    conversations: list[ConversationSummary]


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
