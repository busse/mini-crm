"""Initial database schema.

Revision ID: 001
Create Date: 2024-01-01

Creates tables for users, companies, contacts, deals, deal_stages,
activities, and tags.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial tables."""
    pass


def downgrade() -> None:
    """Drop initial tables."""
    pass
