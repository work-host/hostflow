"""hf0002: search indexes

Revision ID: 3647bac7d477
Revises: hf0001
Create Date: 2025-08-09 14:20:00
"""

from alembic import op

revision = "3647bac7d477"
down_revision = "hf0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_candidates_languages ON candidates USING GIN (languages)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_candidates_stage ON candidates (stage)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_candidates_name ON candidates (last_name, first_name)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_candidates_name")
    op.execute("DROP INDEX IF EXISTS ix_candidates_stage")
    op.execute("DROP INDEX IF EXISTS ix_candidates_languages")
