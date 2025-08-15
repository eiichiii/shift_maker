from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..db import Base, engine, get_db
from ..models.shift_request import ShiftRequest
from ..services import shift_importer
from pydantic import BaseModel

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/shift-requests", tags=["shift-requests"])


class UploadResponse(BaseModel):
    message: str
    count: int


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=UploadResponse,
    responses={
        201: {"description": "Shift requests uploaded successfully"},
        400: {"description": "Failed to import shift requests"},
    },
)
async def upload_shift_requests(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadResponse:
    try:
        shift_requests: List[ShiftRequest] = shift_importer.parse_shift_requests(file)
        for req in shift_requests:
            db.add(req)
        db.commit()
        return UploadResponse(message="Upload successful", count=len(shift_requests))
    except Exception as e:  # pragma: no cover - simple error handling
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
