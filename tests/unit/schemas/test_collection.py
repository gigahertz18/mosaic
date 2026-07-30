"""Unit tests for app.schemas.collection."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.collection import CollectionCreate, CollectionRead, CollectionUpdate


class TestCollectionCreate:
    def test_accepts_name_only(self) -> None:
        schema = CollectionCreate(name="Docs")
        assert schema.name == "Docs"
        assert schema.description is None

    def test_accepts_name_and_description(self) -> None:
        schema = CollectionCreate(name="Docs", description="Some docs")
        assert schema.description == "Some docs"

    def test_rejects_empty_name(self) -> None:
        with pytest.raises(ValidationError):
            CollectionCreate(name="")

    def test_rejects_missing_name(self) -> None:
        with pytest.raises(ValidationError):
            CollectionCreate()  # type: ignore[call-arg]

    def test_rejects_name_over_max_length(self) -> None:
        with pytest.raises(ValidationError):
            CollectionCreate(name="a" * 256)

    def test_rejects_description_over_max_length(self) -> None:
        with pytest.raises(ValidationError):
            CollectionCreate(name="Docs", description="a" * 2001)

    def test_accepts_name_at_max_length(self) -> None:
        schema = CollectionCreate(name="a" * 255)
        assert len(schema.name) == 255

    def test_accepts_description_at_max_length(self) -> None:
        schema = CollectionCreate(name="Docs", description="a" * 2000)
        assert schema.description is not None
        assert len(schema.description) == 2000


class TestCollectionUpdate:
    def test_all_fields_optional(self) -> None:
        schema = CollectionUpdate()
        assert schema.name is None
        assert schema.description is None

    def test_accepts_partial_name_update(self) -> None:
        schema = CollectionUpdate(name="Renamed")
        assert schema.name == "Renamed"
        assert schema.description is None

    def test_rejects_empty_name_when_provided(self) -> None:
        with pytest.raises(ValidationError):
            CollectionUpdate(name="")

    def test_rejects_name_over_max_length(self) -> None:
        with pytest.raises(ValidationError):
            CollectionUpdate(name="a" * 256)

    def test_rejects_description_over_max_length(self) -> None:
        with pytest.raises(ValidationError):
            CollectionUpdate(description="a" * 2001)


class TestCollectionRead:
    def test_builds_from_orm_like_object(self) -> None:
        now = datetime.now(UTC)

        class _FakeCollection:
            id = uuid.uuid4()
            name = "Docs"
            description = None
            created_at = now
            updated_at = now

        schema = CollectionRead.model_validate(_FakeCollection())
        assert schema.name == "Docs"
        assert schema.description is None
        assert schema.created_at == now

    def test_serializes_all_expected_fields(self) -> None:
        now = datetime.now(UTC)
        schema = CollectionRead(
            id=uuid.uuid4(),
            name="Docs",
            description="Some docs",
            created_at=now,
            updated_at=now,
        )
        dumped = schema.model_dump()
        assert set(dumped) == {"id", "name", "description", "created_at", "updated_at"}
