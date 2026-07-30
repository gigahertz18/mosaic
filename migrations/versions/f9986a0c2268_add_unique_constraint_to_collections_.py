"""Add unique constraint to collections.name.

Revision ID: f9986a0c2268
Revises: 0001
Create Date: 2026-07-30 06:26:50.247794

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f9986a0c2268"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint("uq_collections_name", "collections", ["name"])


def downgrade() -> None:
    op.drop_constraint("uq_collections_name", "collections", type_="unique")
