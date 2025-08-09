from __future__ import annotations
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Candidate
from app.models.enums import CandidateStage

router = APIRouter(tags=["candidates"])


# ---- Schemas ----
class CandidateBase(BaseModel):
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=32)
    languages: Optional[List[str]] = None
    stage: Optional[str] = None  # принимает русские значения или Enum-имя


class CandidateCreate(CandidateBase):
    pass


class CandidateUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=32)
    languages: Optional[List[str]] = None
    stage: Optional[str] = None


class CandidateOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    phone: Optional[str]
    languages: List[str] = []
    stage: str


def serialize(c: Candidate) -> CandidateOut:
    return CandidateOut(
        id=c.id,
        first_name=c.first_name,
        last_name=c.last_name,
        phone=c.phone,
        languages=c.languages or [],
        stage=c.stage.value if isinstance(c.stage, CandidateStage) else str(c.stage),
    )


def parse_stage(s: Optional[str]) -> CandidateStage:
    if s is None:
        return CandidateStage.NEW
    try:
        return CandidateStage(s)  # русское значение
    except ValueError:
        try:
            return CandidateStage[s]  # Enum-имя
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid stage: {s}") from e


# ---- Endpoints ----
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


@router.get("")
async def list_candidates(
    db: AsyncSession = Depends(get_db),
    phone: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = select(Candidate)
    if phone:
        stmt = stmt.where(Candidate.phone.ilike(f"%{phone}%"))
    if language:
        stmt = stmt.where(Candidate.languages.contains([language]))
    if stage:
        stmt = stmt.where(Candidate.stage == stage)
    stmt = stmt.limit(limit).offset(offset)
    res = await db.execute(stmt)
    return [serialize(c) for c in res.scalars().all()]


@router.get("/by-id/{candidate_id}", response_model=CandidateOut)
async def get_candidate(candidate_id: UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return serialize(obj)


@router.patch("/by-id/{candidate_id}", response_model=CandidateOut)
async def patch_candidate(
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


@router.put("/by-id/{candidate_id}", response_model=CandidateOut)
async def put_candidate(
    candidate_id: UUID, payload: CandidateCreate, db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Candidate not found")
    obj.first_name = payload.first_name
    obj.last_name = payload.last_name
    obj.phone = payload.phone
    obj.languages = payload.languages or []
    obj.stage = parse_stage(payload.stage)
    await db.commit()
    await db.refresh(obj)
    return serialize(obj)


@router.delete("/by-id/{candidate_id}", status_code=204)
async def delete_candidate(candidate_id: UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Candidate not found")
    await db.delete(obj)
    await db.commit()
    return None


@router.get("/export")
async def export_candidates(
    db: AsyncSession = Depends(get_db),
    phone: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    limit: int = Query(10000, ge=1, le=100000),
    offset: int = Query(0, ge=0),
):
    import io
    import csv

    stmt = select(Candidate)
    if phone:
        stmt = stmt.where(Candidate.phone.ilike(f"%{phone}%"))
    if language:
        stmt = stmt.where(Candidate.languages.contains([language]))
    if stage:
        stmt = stmt.where(Candidate.stage == stage)
    stmt = stmt.limit(limit).offset(offset)
    res = await db.execute(stmt)
    rows = [serialize(c) for c in res.scalars().all()]
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "first_name", "last_name", "phone", "languages", "stage"])
    for r in rows:
        w.writerow(
            [
                str(r.id),
                r.first_name,
                r.last_name,
                r.phone or "",
                "|".join(r.languages or []),
                r.stage,
            ]
        )
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=candidates.csv"},
    )


@router.get("/search")
async def search_candidates(
    db: AsyncSession = Depends(get_db),
    phone: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
):
    valid_cols = {
        "created_at": Candidate.created_at,
        "first_name": Candidate.first_name,
        "last_name": Candidate.last_name,
        "phone": Candidate.phone,
        "stage": Candidate.stage,
    }
    col = valid_cols.get(sort_by, Candidate.created_at)
    order = col.desc() if sort_dir.lower() == "desc" else col.asc()

    base = select(Candidate)
    if phone:
        base = base.where(Candidate.phone.ilike(f"%{phone}%"))
    if language:
        base = base.where(Candidate.languages.contains([language]))
    if stage:
        base = base.where(Candidate.stage == stage)

    from sqlalchemy import func as F

    total = (
        await db.execute(select(F.count()).select_from(base.subquery()))
    ).scalar_one()

    stmt = base.order_by(order).limit(limit).offset(offset)
    rows = (await db.execute(stmt)).scalars().all()
    return {
        "items": [serialize(c) for c in rows],
        "total": total,
        "limit": limit,
        "offset": offset,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
    }
