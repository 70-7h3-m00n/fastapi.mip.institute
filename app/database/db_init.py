from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

from app.config import config

engine = create_async_engine(
    config.postgres.dsn, future=True, echo=config.postgres.db_echo, poolclass=NullPool
)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


async def get_db() -> AsyncGenerator:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


db_session = asynccontextmanager(get_db)
