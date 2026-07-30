"""Unit tests for app.db.session.

Building an async SQLAlchemy engine and session factory does not open a
socket connection until a query is actually executed, so these exercise
real construction without requiring a live PostgreSQL instance.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.config import DatabaseSettings
from app.db.session import create_engine, create_session_factory, get_db_session, get_engine


def test_create_engine_builds_engine_from_settings(database_settings: DatabaseSettings) -> None:
    engine = create_engine(database_settings)

    assert isinstance(engine, AsyncEngine)
    assert engine.url.database == database_settings.name
    assert engine.url.host == database_settings.host


def test_create_session_factory_builds_sessions(database_settings: DatabaseSettings) -> None:
    engine = create_engine(database_settings)
    session_factory = create_session_factory(engine)

    session = session_factory()
    try:
        assert isinstance(session, AsyncSession)
    finally:
        pass  # closing requires an event loop; covered via get_db_session below


async def test_get_engine_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOSAIC_ENVIRONMENT", "test")
    monkeypatch.setenv("MOSAIC_DB_HOST", "db")
    monkeypatch.setenv("MOSAIC_DB_USER", "mosaic")
    monkeypatch.setenv("MOSAIC_DB_PASSWORD", "mosaic")
    monkeypatch.setenv("MOSAIC_DB_NAME", "mosaic")
    monkeypatch.setenv("MOSAIC_STORAGE_ENDPOINT", "minio:9000")
    monkeypatch.setenv("MOSAIC_STORAGE_ACCESS_KEY", "mosaic")
    monkeypatch.setenv("MOSAIC_STORAGE_SECRET_KEY", "mosaic123")

    get_engine.cache_clear()
    try:
        first = get_engine()
        second = get_engine()
        assert first is second
    finally:
        get_engine.cache_clear()


async def test_get_db_session_yields_an_async_session(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOSAIC_ENVIRONMENT", "test")
    monkeypatch.setenv("MOSAIC_DB_HOST", "db")
    monkeypatch.setenv("MOSAIC_DB_USER", "mosaic")
    monkeypatch.setenv("MOSAIC_DB_PASSWORD", "mosaic")
    monkeypatch.setenv("MOSAIC_DB_NAME", "mosaic")
    monkeypatch.setenv("MOSAIC_STORAGE_ENDPOINT", "minio:9000")
    monkeypatch.setenv("MOSAIC_STORAGE_ACCESS_KEY", "mosaic")
    monkeypatch.setenv("MOSAIC_STORAGE_SECRET_KEY", "mosaic123")

    get_engine.cache_clear()
    try:
        session_gen = get_db_session()
        session = await anext(session_gen)
        assert isinstance(session, AsyncSession)
        await session_gen.aclose()
    finally:
        get_engine.cache_clear()
