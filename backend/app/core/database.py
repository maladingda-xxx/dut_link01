from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from pgvector.asyncpg import register_vector

from app.core.config import settings


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""


engine = create_async_engine(settings.database_url, echo=settings.debug)


@event.listens_for(engine.sync_engine, "connect")
def _register_pgvector(dbapi_connection, connection_record):
    """Register the pgvector type codec on each new asyncpg connection."""
    dbapi_connection.run_async(register_vector)


async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
