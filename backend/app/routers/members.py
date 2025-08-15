from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..db import Base, engine, get_db
from ..models.member import Member

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/members", tags=["members"])


class MemberCreate(BaseModel):
    name: str
    gender: str
    is_committee: bool = False


class MemberResponse(BaseModel):
    id: int
    name: str
    gender: str
    is_committee: bool

    class Config:
        from_attributes = True


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=MemberResponse,
)
def create_member(
    member: MemberCreate,
    db: Session = Depends(get_db),
) -> MemberResponse:
    """Create a new member."""
    db_member = Member(
        name=member.name,
        gender=member.gender,
        is_committee=member.is_committee,
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@router.get("/", response_model=List[MemberResponse])
def list_members(db: Session = Depends(get_db)) -> List[Member]:
    """List all members."""
    return db.query(Member).all()