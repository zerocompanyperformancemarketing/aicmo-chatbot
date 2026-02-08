from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import chat, ingest
from db.models import Base
from db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="AICMO Podcast Chatbot API",
    description="Multi-agent RAG chatbot for podcast transcript knowledge base",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(chat.router)
app.include_router(ingest.router)


@app.get("/health")
async def health():
    """Service health check."""
    return {"status": "ok"}
