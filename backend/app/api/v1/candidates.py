from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, literal
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.db import get_db
from app.models.candidate import Candidate
from app.models.enums import CandidateStage
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateOut

router = APIRouter(tags=["candidates"])


def serialize(c: Candidate) -> dict:
    return {
        "id": c.id,
        "first_name": c.first_name,
        "last_name": c.last_name,
        "phone": c.phone,
        "languages": c.languages or [],
        "stage": c.stage.value if isinstance(c.stage, CandidateStage) else c.stage,
    }


def parse_stage(s: Optional[str]) -> CandidateStage:
    if s is None:
        return CandidateStage.NEW
    if isinstance(s, CandidateStage):
        return s
    return CandidateStage(s)


@router.post("", response_model=CandidateOut, status_code=201)
async def create_candidate(
    payload: CandidateCreate, db: AsyncSession = Depends(get_db)
):
    obj = Candidate(
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        languages=payload.languages or [],
        stage=parse_stage(payload.stage),
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return serialize(obj)


@router.get("", response_model=list[CandidateOut])
async def list_candidates(
    db: AsyncSession = Depends(get_db),
    phone: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = select(Candidate)
    if phone:
        stmt = stmt.where(Candidate.phone.ilike(f"%{phone}%"))
    if language:
        stmt = stmt.where(
            func.array_position(Candidate.languages, literal(language)) is not None
        )  # noqa: E711
    stmt = stmt.limit(limit).offset(offset)
    res = await db.execute(stmt)
    return [serialize(c) for c in res.scalars().all()]


@router.get("/{candidate_id}", response_model=CandidateOut)
async def get_candidate(candidate_id: UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return serialize(obj)


@router.patch("/{candidate_id}", response_model=CandidateOut)
async def update_candidate(
    candidate_id: UUID, payload: CandidateUpdate, db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if payload.first_name is not None:
        obj.first_name = payload.first_name
    if payload.last_name is not None:
        obj.last_name = payload.last_name
    if payload.phone is not None:
        obj.phone = payload.phone
    if payload.languages is not None:
        obj.languages = payload.languages
    if payload.stage is not None:
        obj.stage = parse_stage(payload.stage)

    await db.commit()
    await db.refresh(obj)
    return serialize(obj)
