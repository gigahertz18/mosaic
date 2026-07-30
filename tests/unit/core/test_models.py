"""Unit tests asserting core domain model shape via SQLAlchemy metadata.

These tests never touch a live database — they only inspect mapped
columns, which keeps them fast and dependency-free per the project's
unit-testing rules.
"""

from __future__ import annotations

from app.db.base import Base
from app.models import Chunk, Collection, Document, DocumentStatus, Embedding
from app.models.embedding import EMBEDDING_DIMENSIONS


def _column_names(model: type) -> set[str]:
    return {column.name for column in model.__table__.columns}  # type: ignore[attr-defined]


def test_all_core_models_are_registered_on_shared_metadata() -> None:
    table_names = set(Base.metadata.tables.keys())
    assert {"collections", "documents", "chunks", "embeddings"} <= table_names


def test_collection_has_expected_columns() -> None:
    assert {"id", "name", "description", "created_at", "updated_at"} <= _column_names(Collection)


def test_document_has_expected_columns_and_default_status() -> None:
    assert {"id", "collection_id", "filename", "content_type", "storage_key", "status"} <= _column_names(Document)
    status_column = Document.__table__.columns["status"]
    assert status_column.default.arg == DocumentStatus.PENDING


def test_chunk_belongs_to_document() -> None:
    assert {"id", "document_id", "sequence", "content"} <= _column_names(Chunk)


def test_embedding_has_configured_vector_dimensions() -> None:
    assert {"id", "chunk_id", "model", "vector"} <= _column_names(Embedding)
    vector_column = Embedding.__table__.columns["vector"]
    assert vector_column.type.dim == EMBEDDING_DIMENSIONS
