"""SQLAlchemy ORM models for the core domain: Collection, Document, Chunk, Embedding.

Every model is imported here so that :data:`app.db.base.Base.metadata`
is fully populated for Alembic autogeneration.
"""

from app.models.chunk import Chunk
from app.models.collection import Collection
from app.models.document import Document, DocumentStatus
from app.models.embedding import Embedding

__all__ = ["Chunk", "Collection", "Document", "DocumentStatus", "Embedding"]
