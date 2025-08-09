import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.mixins import UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True)
    full_name: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    is_recruiter: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    languages: Mapped[list[str] | None] = mapped_column(
        sa.ARRAY(sa.String), default=list
    )
    password_hash: Mapped[str | None]
