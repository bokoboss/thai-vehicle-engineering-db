"""Create the evidence-first Phase 0 relational foundation.

Revision ID: 0001_phase0_foundation
Revises:
Create Date: 2026-08-31
"""

from alembic import op

from app.db.base import Base


revision = "0001_phase0_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The authoritative physical contract is expressed once in SQLAlchemy metadata.
    # Alembic still owns the versioned upgrade/rollback boundary, and this keeps the
    # SQLite and PostgreSQL-compatible DDL paths identical for Phase 0.
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
