"""hf0003: add search indexes"""

from alembic import op

revision = "19712a57289c"
down_revision = "616847670079"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_candidates_phone", "candidates", ["phone"], if_not_exists=True)
    op.create_index("ix_candidates_stage", "candidates", ["stage"], if_not_exists=True)
    op.create_index(
        "ix_candidates_languages_gin",
        "candidates",
        ["languages"],
        postgresql_using="gin",
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_candidates_languages_gin", table_name="candidates", if_exists=True
    )
    op.drop_index("ix_candidates_stage", table_name="candidates", if_exists=True)
    op.drop_index("ix_candidates_phone", table_name="candidates", if_exists=True)
