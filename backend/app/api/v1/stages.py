from fastapi import APIRouter
from app.models.enums import CandidateStage

router = APIRouter(prefix="/api/v1/stages", tags=["stages"])


@router.get("", response_model=list[str])
def list_stages():
    return [s.value for s in CandidateStage]
