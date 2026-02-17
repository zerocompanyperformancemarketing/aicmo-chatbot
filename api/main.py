import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import Config
from auth import hash_password
from routers import auth, chat, ingest
from db.crud import get_user_by_username, create_user
from db.models import Base
from db.session import engine

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

import os
from arize.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor # Optional, for deeper OpenAI traces


# Setup OTel via Arize AX's convenience function
tracer_provider = register(
    space_id=Config.ARIZE_SPACE_ID,
    api_key=Config.ARIZE_API_KEY,
    project_name="AICMO-Chatbot" # Choose a project name
)

# Instrument LangChain (which includes LangGraph)
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
# Optionally instrument OpenAI for deeper traces if using OpenAI models
OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

logging.info("LangGraph (via LangChain instrumentor) and OpenAI instrumented for Arize AX.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API starting up — creating DB tables")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed admin user
    existing = await get_user_by_username("admin")
    if existing is None:
        await create_user(
            username="admin",
            password_hash=hash_password("aicmochatbot2026!"),
            full_name="Admin",
            email="admin@aicmo.com",
        )
        logger.info("Seeded admin user")
    logger.info("API startup complete")
    yield
    logger.info("API shutting down")
    await engine.dispose()


app = FastAPI(
    title="AICMO Podcast Chatbot API",
    description="Multi-agent RAG chatbot for podcast transcript knowledge base",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(ingest.router)


@app.get("/health")
async def health():
    """Service health check."""
    return {"status": "ok"}
