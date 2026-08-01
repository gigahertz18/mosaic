"""Integration tests for CollectionRepository against a live schema."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.repositories.collection import CollectionRepository


def _make_collection(**overrides: object) -> Collection:
    defaults: dict[str, object] = {
        "name": f"collection-{uuid.uuid4()}",
        "description": "a test collection",
    }
    defaults.update(overrides)
    return Collection(**defaults)


@pytest.fixture
def repository(db_session: AsyncSession) -> CollectionRepository:
    return CollectionRepository(db_session)


async def test_create_persists_collection_and_populates_defaults(repository: CollectionRepository) -> None:
    collection = _make_collection(name="create-me")

    created = await repository.create(collection)

    assert created.id is not None
    assert created.name == "create-me"
    assert created.created_at is not None
    assert created.updated_at is not None


async def test_get_by_id_returns_matching_collection(repository: CollectionRepository) -> None:
    created = await repository.create(_make_collection(name="fetch-me"))

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "fetch-me"


async def test_get_by_id_returns_none_when_missing(repository: CollectionRepository) -> None:
    fetched = await repository.get_by_id(uuid.uuid4())

    assert fetched is None


async def test_get_all_returns_every_created_collection(repository: CollectionRepository) -> None:
    first = await repository.create(_make_collection())
    second = await repository.create(_make_collection())

    collections = await repository.get_all()

    ids = {c.id for c in collections}
    assert first.id in ids
    assert second.id in ids


async def test_update_persists_field_changes(repository: CollectionRepository) -> None:
    created = await repository.create(_make_collection(name="before-update"))
    created.name = "after-update"
    created.description = "updated description"

    updated = await repository.update(created)

    assert updated.name == "after-update"
    assert updated.description == "updated description"

    refetched = await repository.get_by_id(created.id)
    assert refetched is not None
    assert refetched.name == "after-update"


async def test_delete_removes_collection(repository: CollectionRepository) -> None:
    created = await repository.create(_make_collection(name="delete-me"))

    await repository.delete(created.id)

    assert await repository.get_by_id(created.id) is None


async def test_delete_is_a_no_op_for_missing_collection(repository: CollectionRepository) -> None:
    # Should not raise even though nothing exists with this id.
    await repository.delete(uuid.uuid4())


async def test_get_by_name_returns_matching_collection(repository: CollectionRepository) -> None:
    created = await repository.create(_make_collection(name="unique-name"))

    fetched = await repository.get_by_name("unique-name")

    assert fetched is not None
    assert fetched.id == created.id


async def test_get_by_name_returns_none_when_missing(repository: CollectionRepository) -> None:
    fetched = await repository.get_by_name("non-existent-name")

    assert fetched is None
