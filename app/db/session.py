"""Async SQLAlchemy engine and session factory.

The engine is built once from injected :class:`~app.core.config.DatabaseSettings`
and exposed to FastAPI routes via the ``get_db_session`` dependency.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import DatabaseSettings, Settings, get_settings


def create_engine(database_settings: DatabaseSettings) -> AsyncEngine:
    """Create a new async SQLAlchemy engine for the given database settings."""
    return create_async_engine(
        database_settings.async_dsn,
        echo=database_settings.echo,
        pool_size=database_settings.pool_size,
        max_overflow=database_settings.max_overflow,
    )


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Return the process-wide cached engine, built from cached settings."""
    settings: Settings = get_settings()
    return create_engine(settings.database)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Build a session factory bound to the given engine."""
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a request-scoped ``AsyncSession``."""
    session_factory = create_session_factory(get_engine())
    async with session_factory() as session:
        yield session
