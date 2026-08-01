"""Unit tests for app.services.collection.CollectionService.

CollectionRepository is fully mocked here - no real database is used.
Persistence behavior itself (including the get_by_name lookup added
alongside this service) is covered by the repository's own integration
tests, not here.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import NotFoundError
from app.models.collection import Collection
from app.repositories.collection import CollectionRepository
from app.schemas.collection import CollectionCreate, CollectionUpdate
from app.services.collection import CollectionService


def _make_collection(**overrides: object) -> Collection:
    defaults: dict[str, object] = {
        "id": uuid.uuid4(),
        "name": "Docs",
        "description": "some docs",
    }
    defaults.update(overrides)
    return Collection(**defaults)


@pytest.fixture
def repository() -> AsyncMock:
    return AsyncMock(spec=CollectionRepository)


@pytest.fixture
def service(repository: AsyncMock) -> CollectionService:
    return CollectionService(repository)


class TestCreateCollection:
    async def test_creates_collection_from_schema(self, service: CollectionService, repository: AsyncMock) -> None:
        repository.create.return_value = _make_collection(name="Docs", description="some docs")

        result = await service.create_collection(CollectionCreate(name="Docs", description="some docs"))

        assert result.name == "Docs"
        repository.create.assert_awaited_once()
        created_arg = repository.create.await_args.args[0]
        assert isinstance(created_arg, Collection)
        assert created_arg.name == "Docs"
        assert created_arg.description == "some docs"

    async def test_creates_collection_from_kwargs(self, service: CollectionService, repository: AsyncMock) -> None:
        repository.create.return_value = _make_collection(name="Docs", description=None)

        result = await service.create_collection(name="Docs")

        assert result.name == "Docs"
        created_arg = repository.create.await_args.args[0]
        assert created_arg.description is None

    async def test_rejects_both_schema_and_kwargs(self, service: CollectionService) -> None:
        with pytest.raises(TypeError):
            await service.create_collection(CollectionCreate(name="Docs"), name="Other")

    async def test_kwargs_are_validated_like_the_schema(self, service: CollectionService) -> None:
        with pytest.raises(PydanticValidationError):
            await service.create_collection(name="")


class TestGetCollection:
    async def test_returns_collection_when_found(self, service: CollectionService, repository: AsyncMock) -> None:
        collection = _make_collection()
        repository.get_by_id.return_value = collection

        result = await service.get_collection(collection.id)

        assert result is collection
        repository.get_by_id.assert_awaited_once_with(collection.id)

    async def test_raises_not_found_when_missing(self, service: CollectionService, repository: AsyncMock) -> None:
        repository.get_by_id.return_value = None
        missing_id = uuid.uuid4()

        with pytest.raises(NotFoundError):
            await service.get_collection(missing_id)


class TestListCollections:
    async def test_returns_page_from_repository(self, service: CollectionService, repository: AsyncMock) -> None:
        collections = [_make_collection(), _make_collection()]
        repository.get_page.return_value = collections

        result = await service.list_collections()

        assert result == collections
        repository.get_page.assert_awaited_once_with(skip=0, limit=100)

    async def test_forwards_custom_skip_and_limit(self, service: CollectionService, repository: AsyncMock) -> None:
        repository.get_page.return_value = []

        await service.list_collections(skip=10, limit=25)

        repository.get_page.assert_awaited_once_with(skip=10, limit=25)


class TestUpdateCollection:
    async def test_updates_provided_fields_from_schema(self, service: CollectionService, repository: AsyncMock) -> None:
        collection = _make_collection(name="Old", description="old desc")
        repository.get_by_id.return_value = collection
        repository.update.return_value = collection

        result = await service.update_collection(collection.id, CollectionUpdate(name="New"))

        assert result.name == "New"
        assert result.description == "old desc"  # untouched field preserved
        repository.update.assert_awaited_once_with(collection)

    async def test_updates_provided_fields_from_kwargs(self, service: CollectionService, repository: AsyncMock) -> None:
        collection = _make_collection(name="Old", description="old desc")
        repository.get_by_id.return_value = collection
        repository.update.return_value = collection

        result = await service.update_collection(collection.id, description="New desc")

        assert result.name == "Old"
        assert result.description == "New desc"

    async def test_raises_not_found_when_missing(self, service: CollectionService, repository: AsyncMock) -> None:
        repository.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.update_collection(uuid.uuid4(), name="New")

        repository.update.assert_not_awaited()

    async def test_rejects_both_schema_and_kwargs(self, service: CollectionService, repository: AsyncMock) -> None:
        collection = _make_collection()
        repository.get_by_id.return_value = collection

        with pytest.raises(TypeError):
            await service.update_collection(collection.id, CollectionUpdate(name="New"), name="Other")


class TestDeleteCollection:
    async def test_deletes_when_found(self, service: CollectionService, repository: AsyncMock) -> None:
        collection = _make_collection()
        repository.get_by_id.return_value = collection

        await service.delete_collection(collection.id)

        repository.delete.assert_awaited_once_with(collection.id)

    async def test_raises_not_found_when_missing(self, service: CollectionService, repository: AsyncMock) -> None:
        repository.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            await service.delete_collection(uuid.uuid4())

        repository.delete.assert_not_awaited()
