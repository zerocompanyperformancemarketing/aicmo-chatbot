import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "aicmo_chatbot")

    # Typesense
    TS_PORT: str = os.getenv("TS_PORT", "8108")
    TS_DATA_DIR: str = os.getenv("TS_DATA_DIR", "./db/typesense-data")
    TS_API_KEY: str = os.getenv("TS_API_KEY", "")
    TS_HOST: str = os.getenv("TS_HOST", "localhost")

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5.1")

    # Urlbox
    URLBOX_API_KEY: str = os.getenv("URLBOX_API_KEY", "")
    URLBOX_API_SECRET: str = os.getenv("URLBOX_API_SECRET", "")

    # Stability AI
    STABILITYAI_API_KEY: str = os.getenv("STABILITYAI_API_KEY", "")

    # Anthropic
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # ScrapingBee
    SCRAPINGBEE_API_KEY: str = os.getenv("SCRAPINGBEE_API_KEY", "")

    # Slack
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_TRUNCATE: int = int(os.getenv("LOG_TRUNCATE", "500"))

    # Phoenix (self-hosted tracing)
    PHOENIX_COLLECTOR_ENDPOINT: str = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:4317")
