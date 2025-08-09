from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Candidate
from sqlalchemy import Table, MetaData

router = APIRouter(prefix="/stages", tags=["stages"])

class StageOut(BaseModel):
    code: str
    name: str
    ord: int
    is_terminal: bool

    class Config:
        from_attributes = True

@router.get("/", response_model=List[StageOut])
def list_stages(db: Session = Depends(get_db)):
    # таблица stages была создана миграцией 0001 (без ORM-модели)
    md = MetaData()
    stages = Table("stages", md, autoload_with=db.get_bind())
    rows = db.execute(select(stages.c.code, stages.c.name, stages.c.ord, stages.c.is_terminal)
                      .order_by(stages.c.ord)).all()
    return [{"code": r.code, "name": r.name, "ord": r.ord, "is_terminal": r.is_terminal} for r in rows]
