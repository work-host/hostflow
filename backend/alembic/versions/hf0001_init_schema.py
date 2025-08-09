"""init schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'hf0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    candidatestage = postgresql.ENUM(
        'Новый',
        'Контакт установлен',
        'Ожидаем документы',
        'Документы получены',
        'Заказ разрешения',
        'Виза',
        'Красная бумага',
        'Готов к выезду',
        'Планируем приезд',
        'На базе клиента',
        'Трудоустроен',
        'Отклонён',
        name='candidatestage',
        create_type=True
    )
    candidatestage.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('TRUE'), nullable=False),
        sa.Column('is_recruiter', sa.Boolean(), server_default=sa.text('TRUE'), nullable=False),
        sa.Column('languages', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=False)

    op.create_table(
        'candidates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=32), nullable=True),
        sa.Column('languages', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('stage', postgresql.ENUM(name='candidatestage', create_type=False), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='fk_candidates_owner_id_users', ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_candidates_phone', 'candidates', ['phone'], unique=False)

def downgrade():
    op.drop_index('ix_candidates_phone', table_name='candidates')
    op.drop_table('candidates')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    candidatestage = postgresql.ENUM(name='candidatestage')
    candidatestage.drop(op.get_bind(), checkfirst=True)
