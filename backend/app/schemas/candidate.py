from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID

class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    languages: List[str] = []
    stage: Optional[str] = None  # опционально

class CandidateUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    languages: Optional[List[str]] = None
    stage: Optional[str] = None

class CandidateOut(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    phone: Optional[str] = None
    languages: List[str] = []
    stage: Optional[str] = None
