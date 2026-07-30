"""Unit tests for app.models.collection."""

from __future__ import annotations

import uuid

from app.models.collection import Collection


def _column_names(model: type) -> set[str]:
    return {column.name for column in model.__table__.columns}  # type: ignore[attr-defined]


def test_collection_table_name() -> None:
    assert Collection.__tablename__ == "collections"


def test_collection_has_expected_columns() -> None:
    assert _column_names(Collection) == {"id", "name", "description", "created_at", "updated_at"}


def test_collection_name_has_named_unique_constraint() -> None:
    constraint_names = {constraint.name for constraint in Collection.__table__.constraints}
    assert "uq_collections_name" in constraint_names


def test_collection_description_is_nullable() -> None:
    assert Collection.__table__.columns["description"].nullable is True


def test_collection_uses_uuid_primary_key() -> None:
    id_column = Collection.__table__.columns["id"]
    assert id_column.primary_key is True
    assert id_column.type.python_type is uuid.UUID


def test_collection_has_timestamp_columns() -> None:
    assert Collection.__table__.columns["created_at"].nullable is False
    assert Collection.__table__.columns["updated_at"].nullable is False
