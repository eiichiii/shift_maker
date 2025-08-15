from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
import csv
from io import StringIO

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


class MemberUploadResponse(BaseModel):
    message: str
    created_count: int
    updated_count: int
    error_count: int
    errors: List[str] = []


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


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete a member by ID."""
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if db_member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with id {member_id} not found"
        )
    
    db.delete(db_member)
    db.commit()


@router.post(
    "/upload-csv",
    status_code=status.HTTP_201_CREATED,
    response_model=MemberUploadResponse,
)
def upload_members_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> MemberUploadResponse:
    """Upload members from CSV file.
    
    Expected CSV format:
    name,gender,is_committee
    John Doe,M,true
    Jane Smith,F,false
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    try:
        content = file.file.read().decode('utf-8')
        csv_reader = csv.DictReader(StringIO(content))
        
        created_count = 0
        updated_count = 0
        error_count = 0
        errors = []
        
        # Validate required columns
        required_columns = {'name', 'gender', 'is_committee'}
        if not required_columns.issubset(set(csv_reader.fieldnames or [])):
            missing = required_columns - set(csv_reader.fieldnames or [])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing)}"
            )
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start from row 2 (header is row 1)
            try:
                # Validate and clean data
                name = row['name'].strip()
                gender = row['gender'].strip().upper()
                is_committee_str = row['is_committee'].strip().lower()
                
                if not name:
                    errors.append(f"Row {row_num}: Name cannot be empty")
                    error_count += 1
                    continue
                
                if gender not in ['M', 'F']:
                    errors.append(f"Row {row_num}: Gender must be 'M' or 'F', got '{gender}'")
                    error_count += 1
                    continue
                
                if is_committee_str in ['true', '1', 'yes', 'y']:
                    is_committee = True
                elif is_committee_str in ['false', '0', 'no', 'n']:
                    is_committee = False
                else:
                    errors.append(f"Row {row_num}: is_committee must be true/false, got '{is_committee_str}'")
                    error_count += 1
                    continue
                
                # Check if member already exists
                existing_member = db.query(Member).filter(Member.name == name).first()
                
                if existing_member:
                    # Update existing member
                    existing_member.gender = gender
                    existing_member.is_committee = is_committee
                    updated_count += 1
                else:
                    # Create new member
                    new_member = Member(
                        name=name,
                        gender=gender,
                        is_committee=is_committee
                    )
                    db.add(new_member)
                    created_count += 1
                    
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                error_count += 1
                continue
        
        # Commit all changes
        db.commit()
        
        return MemberUploadResponse(
            message=f"CSV processed successfully. Created: {created_count}, Updated: {updated_count}, Errors: {error_count}",
            created_count=created_count,
            updated_count=updated_count,
            error_count=error_count,
            errors=errors
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process CSV file: {str(e)}"
        )