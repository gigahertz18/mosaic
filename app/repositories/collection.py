"""Repository for the :class:`~app.models.collection.Collection` model.

Persistence only - no validation and no business rules. Uniqueness checks,
existence checks with domain-specific errors, etc. belong in the service
layer, not here.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection import Collection
from app.repositories.base import BaseRepository


class CollectionRepository(BaseRepository[Collection]):
    """CRUD persistence for ``Collection`` rows.

    ``create``, ``get_by_id``, ``get_all``, ``update``, and ``delete`` are
    all inherited from :class:`BaseRepository` unchanged - Collection has
    no lookups or persistence behavior beyond standard CRUD.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Collection)

    async def get_by_name(self, name: str) -> Collection | None:
        """Lookup a collection by its exact, case-sensitive name.
        This exists for lookups such as "does a collection with this name
        already exist?", needed by callers later.
        """

        return await self._first(self.model.name == name)
