"""Fixtures for repository integration tests.

These tests run against a live Postgres instance - the ``db`` service
defined in ``docker/docker-compose.yml`` - and assume the schema has
already been migrated. ``make test-integration`` runs ``alembic upgrade
head`` before invoking pytest for exactly this reason.

Each test gets its own connection with an outer transaction that is
rolled back on teardown, so tests never need to truncate tables or
depend on ordering.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession

from app.core.config import DatabaseSettings
from app.db.session import create_engine


@pytest.fixture(scope="session")
def db_settings() -> DatabaseSettings:
    """Connection settings matching the ``db`` service in docker-compose.yml."""
    return DatabaseSettings(
        host="db",
        port=5432,
        user="mosaic",
        password="mosaic",
        name="mosaic",
    )


@pytest.fixture
async def db_engine(db_settings: DatabaseSettings) -> AsyncIterator[AsyncEngine]:
    # Function-scoped (rather than session-scoped) so the engine's
    # connection pool is always bound to the event loop of the test that
    # is currently running, since pytest-asyncio gives each test its own loop.
    engine = create_engine(db_settings)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_connection(db_engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    async with db_engine.connect() as connection:
        yield connection


@pytest.fixture
async def db_session(db_connection: AsyncConnection) -> AsyncIterator[AsyncSession]:
    """A session bound to a connection whose outer transaction is rolled
    back after the test, isolating it from every other test.
    """
    transaction = await db_connection.begin()
    session = AsyncSession(bind=db_connection, expire_on_commit=False, autoflush=False)
    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
