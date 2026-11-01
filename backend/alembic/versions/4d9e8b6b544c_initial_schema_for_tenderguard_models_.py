"""Initial schema for TenderGuard models on Neon PostgreSQL

Revision ID: 4d9e8b6b544c
Revises:
Create Date: 2026-11-01 16:58:46.940275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.models import Base


# revision identifiers, used by Alembic.
revision: str = '4d9e8b6b544c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema idempotently."""
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind, checkfirst=True)
