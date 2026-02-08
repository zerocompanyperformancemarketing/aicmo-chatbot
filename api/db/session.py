from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import Config

DATABASE_URL = (
    f"mysql+aiomysql://{Config.DB_USER}:{Config.DB_PASSWORD}"
    f"@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
