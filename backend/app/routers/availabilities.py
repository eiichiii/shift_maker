from typing import List
from datetime import date, datetime
from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
import csv
from io import StringIO

from ..db import Base, engine, get_db
from ..models.availability import Availability
from ..models.member import Member

Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/availabilities", tags=["availabilities"])


class AvailabilityCreate(BaseModel):
    member_id: int
    dates: List[date]


class AvailabilityResponse(BaseModel):
    id: int
    member_id: int
    date: date

    class Config:
        from_attributes = True


class MemberAvailabilityResponse(BaseModel):
    member_id: int
    member_name: str
    dates: List[date]


class AvailabilityUploadResponse(BaseModel):
    message: str
    processed_dates: int
    processed_members: int
    total_availabilities: int
    error_count: int
    errors: List[str] = []


@router.post("/", status_code=status.HTTP_201_CREATED)
def set_member_availability(
    availability: AvailabilityCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Set availability for a member (replaces existing availability)."""
    # Verify member exists
    member = db.query(Member).filter(Member.id == availability.member_id).first()
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with id {availability.member_id} not found"
        )
    
    # Remove existing availability for this member
    db.query(Availability).filter(Availability.member_id == availability.member_id).delete()
    
    # Add new availability
    for date_item in availability.dates:
        db_availability = Availability(
            member_id=availability.member_id,
            date=date_item
        )
        db.add(db_availability)
    
    db.commit()
    return {"message": f"Availability set for member {availability.member_id}", "count": len(availability.dates)}


@router.get("/member/{member_id}", response_model=MemberAvailabilityResponse)
def get_member_availability(
    member_id: int,
    db: Session = Depends(get_db),
) -> MemberAvailabilityResponse:
    """Get availability for a specific member."""
    member = db.query(Member).filter(Member.id == member_id).first()
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with id {member_id} not found"
        )
    
    availabilities = db.query(Availability).filter(Availability.member_id == member_id).all()
    dates = [availability.date for availability in availabilities]
    
    return MemberAvailabilityResponse(
        member_id=member_id,
        member_name=member.name,
        dates=sorted(dates)
    )


@router.get("/", response_model=List[MemberAvailabilityResponse])
def list_all_availabilities(db: Session = Depends(get_db)) -> List[MemberAvailabilityResponse]:
    """List availability for all members."""
    members = db.query(Member).all()
    result = []
    
    for member in members:
        availabilities = db.query(Availability).filter(Availability.member_id == member.id).all()
        dates = [availability.date for availability in availabilities]
        
        result.append(MemberAvailabilityResponse(
            member_id=member.id,
            member_name=member.name,
            dates=sorted(dates)
        ))
    
    return result


@router.delete("/member/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def clear_member_availability(
    member_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Clear all availability for a specific member."""
    member = db.query(Member).filter(Member.id == member_id).first()
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Member with id {member_id} not found"
        )
    
    db.query(Availability).filter(Availability.member_id == member_id).delete()
    db.commit()


@router.post(
    "/upload-csv",
    status_code=status.HTTP_201_CREATED,
    response_model=AvailabilityUploadResponse,
)
def upload_availabilities_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> AvailabilityUploadResponse:
    """Upload availability data from CSV file.
    
    Expected CSV format:
    ,nameA,nameB,nameC
    2025/8/1,×,○,○
    2025/8/4,○,○,○
    2025/8/30,○,○,×
    
    Where:
    - First column is empty in header, followed by member names
    - Data rows start with date, followed by availability (○ = available, × = not available)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    try:
        content = file.file.read().decode('utf-8')
        csv_reader = csv.reader(StringIO(content))
        
        processed_dates = 0
        processed_members = 0
        total_availabilities = 0
        error_count = 0
        errors = []
        
        # Read header row to get member names
        header = next(csv_reader)
        if len(header) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV must have at least one member column"
            )
        
        # Skip first empty column, get member names
        member_names = [name.strip() for name in header[1:] if name.strip()]
        
        # Get member IDs from names
        member_name_to_id = {}
        for name in member_names:
            member = db.query(Member).filter(Member.name == name).first()
            if member:
                member_name_to_id[name] = member.id
            else:
                errors.append(f"Member '{name}' not found in database")
                error_count += 1
        
        processed_members = len(member_name_to_id)
        
        # Clear ALL existing availability data before uploading new data
        db.query(Availability).delete(synchronize_session=False)
        db.flush()  # Ensure the delete is committed before proceeding
        
        # Process data rows
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                if len(row) < 2:
                    continue
                    
                # Parse date from first column
                date_str = row[0].strip()
                if not date_str:
                    continue
                    
                try:
                    # Try different date formats
                    if '/' in date_str:
                        parsed_date = datetime.strptime(date_str, '%Y/%m/%d').date()
                    elif '-' in date_str:
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    else:
                        raise ValueError("Invalid date format")
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid date format '{date_str}'. Use YYYY/MM/DD or YYYY-MM-DD")
                    error_count += 1
                    continue
                
                # Process availability for each member
                for i, availability_str in enumerate(row[1:]):
                    if i < len(member_names):
                        member_name = member_names[i]
                        if member_name in member_name_to_id:
                            member_id = member_name_to_id[member_name]
                            availability_str = availability_str.strip()
                            
                            # Check if available (○ means available)
                            if availability_str in ['○', 'o', 'O', '1', 'true', 'True', 'available']:
                                # Create availability record
                                new_availability = Availability(
                                    member_id=member_id,
                                    date=parsed_date
                                )
                                db.add(new_availability)
                                total_availabilities += 1
                            elif availability_str in ['×', 'x', 'X', '0', 'false', 'False', 'not available']:
                                # Don't create record for unavailable (absence means unavailable)
                                pass
                            else:
                                errors.append(f"Row {row_num}, Member '{member_name}': Invalid availability '{availability_str}'. Use ○ for available, × for not available")
                                error_count += 1
                
                processed_dates += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                error_count += 1
                continue
        
        # Commit all changes
        db.commit()
        
        return AvailabilityUploadResponse(
            message=f"CSV processed successfully. Processed {processed_dates} dates for {processed_members} members with {total_availabilities} availability records. Errors: {error_count}",
            processed_dates=processed_dates,
            processed_members=processed_members,
            total_availabilities=total_availabilities,
            error_count=error_count,
            errors=errors
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process CSV file: {str(e)}"
        )