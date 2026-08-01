"""Service for the Collection domain.

Owns all Collection business rules and coordinates
``CollectionRepository``. Knows nothing about HTTP or FastAPI - callers
(API routes) are responsible for translating the domain exceptions
raised here into HTTP responses.

Business rules
--------------
- Field-level validation (non-empty/max-length ``name``, max-length
  ``description``) is enforced by ``CollectionCreate`` /
  ``CollectionUpdate`` and is intentionally not duplicated here.
- Collection name uniqueness is enforced by the database
  (``uq_collections_name``, migration ``f9986a0c2268``), not by this
  service. A proactive duplicate check here would just re-implement
  what the DB already guarantees, and would still be racy without also
  handling the constraint violation. As of now, writing a duplicate
  name surfaces as an uncaught ``sqlalchemy.exc.IntegrityError`` from
  the repository/session - this is a deliberate, documented gap, not an
  oversight. Revisit only if/when a route needs a friendlier
  domain-level error for this case.
- No other business rules currently apply (no soft-delete, no
  ownership/authorization, no archiving) - this service is a thin,
  validated pass-through to the repository plus not-found translation.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.core.exceptions import NotFoundError
from app.models.collection import Collection
from app.repositories.collection import CollectionRepository
from app.schemas.collection import CollectionCreate, CollectionUpdate


def _coerce_payload[SchemaT: BaseModel](
    schema_cls: type[SchemaT], data: SchemaT | None, kwargs: dict[str, Any]
) -> SchemaT:
    """Resolve a schema instance from either an explicit ``data`` object
    or loose keyword arguments, never both. Kwargs are routed through
    ``schema_cls`` itself so field validation stays owned by the schema.
    """
    if data is not None and kwargs:
        raise TypeError("Provide either a schema instance or keyword arguments, not both.")
    if data is not None:
        return data
    return schema_cls(**kwargs)


class CollectionService:
    """Owns Collection business rules and coordinates CollectionRepository."""

    def __init__(self, repository: CollectionRepository) -> None:
        self._repository = repository

    async def create_collection(self, data: CollectionCreate | None = None, **kwargs: Any) -> Collection:
        payload = _coerce_payload(CollectionCreate, data, kwargs)
        collection = Collection(name=payload.name, description=payload.description)
        return await self._repository.create(collection)

    async def get_collection(self, collection_id: UUID) -> Collection:
        collection = await self._repository.get_by_id(collection_id)
        if collection is None:
            raise NotFoundError(f"Collection {collection_id} not found")
        return collection

    async def list_collections(self, skip: int = 0, limit: int = 100) -> Sequence[Collection]:
        return await self._repository.get_page(skip=skip, limit=limit)

    async def update_collection(
        self, collection_id: UUID, data: CollectionUpdate | None = None, **kwargs: Any
    ) -> Collection:
        payload = _coerce_payload(CollectionUpdate, data, kwargs)
        collection = await self.get_collection(collection_id)

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(collection, field, value)

        return await self._repository.update(collection)

    async def delete_collection(self, collection_id: UUID) -> None:
        await self.get_collection(collection_id)
        await self._repository.delete(collection_id)
