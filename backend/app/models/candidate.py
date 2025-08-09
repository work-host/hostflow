import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base import Base
from app.db.mixins import UUIDMixin, TimestampMixin, SoftDeleteMixin
from app.models.enums import CandidateStage
from typing import List
from uuid import UUID as _UUID

# Важно: сохраняем в БД ЗНАЧЕНИЯ enum (русские строки), а не ИМЕНА ('NEW' и т.п.)
_stage_enum = sa.Enum(
    CandidateStage,
    name="candidatestage",
    values_callable=lambda cls: [e.value for e in cls],  # -> ['Новый', ...]
    native_enum=True,
)


class Candidate(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "candidates"
    first_name: Mapped[str] = mapped_column(sa.String(100))
    last_name: Mapped[str] = mapped_column(sa.String(100))
    phone: Mapped[str | None] = mapped_column(sa.String(32), index=True)
    languages: Mapped[List[str]] = mapped_column(ARRAY(sa.String), default=list)
    stage: Mapped[CandidateStage] = mapped_column(
        _stage_enum, default=CandidateStage.NEW
    )
    owner_id: Mapped[_UUID | None] = mapped_column(
        sa.ForeignKey("users.id"), nullable=True
    )
