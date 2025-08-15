from typing import Dict, List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
from pathlib import Path

from ..db import get_db
from ..models.member import Member
from ..models.availability import Availability

router = APIRouter(prefix="/shift-generation", tags=["shift-generation"])

# Path to the data file for storing generated schedules
DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "latest_schedule.json"


class ScheduleGenerationResponse(BaseModel):
    message: str
    schedule: dict
    member_assignments: Dict[str, int]
    available_dates: List[str]


def generate_date_range(start_date: date, end_date: date) -> List[date]:
    """Generate a list of dates between start_date and end_date (inclusive)."""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def simple_schedule_assignment(
    members: List[Member], 
    availabilities: Dict[int, List[date]], 
    dates: List[date]
) -> Dict[date, List[str]]:
    """
    Simple round-robin assignment that respects availability.
    This is a basic implementation - could be enhanced with optimization algorithms.
    """
    schedule = {d: [] for d in dates}
    member_assignment_count = {m.id: 0 for m in members}
    
    # Target: 4 members per day
    target_per_day = 4
    
    for target_date in dates:
        available_members = []
        for member in members:
            member_available_dates = availabilities.get(member.id, [])
            if target_date in member_available_dates:
                available_members.append(member)
        
        # Sort available members by their current assignment count (ascending)
        available_members.sort(key=lambda m: member_assignment_count[m.id])
        
        # Assign up to target_per_day members
        assigned_count = 0
        for member in available_members:
            if assigned_count >= target_per_day:
                break
            
            schedule[target_date].append(member.name)
            member_assignment_count[member.id] += 1
            assigned_count += 1
    
    return schedule


@router.post("/generate", response_model=ScheduleGenerationResponse)
def generate_shift_schedule(db: Session = Depends(get_db)) -> ScheduleGenerationResponse:
    """Generate shift schedule based on uploaded availability data."""
    
    # Get all members
    members = db.query(Member).all()
    if not members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No members found. Please add members first."
        )
    
    # Get all availabilities
    all_availabilities = db.query(Availability).all()
    if not all_availabilities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No availability data found. Please upload availability data using CSV first."
        )
    
    member_availabilities = {}
    all_unique_dates = set()
    
    for availability in all_availabilities:
        if availability.member_id not in member_availabilities:
            member_availabilities[availability.member_id] = []
        member_availabilities[availability.member_id].append(availability.date)
        all_unique_dates.add(availability.date)
    
    # Get all unique dates from availability data
    dates = sorted(list(all_unique_dates))
    
    # Generate schedule
    daily_assignments = simple_schedule_assignment(members, member_availabilities, dates)
    
    # Format for frontend (convert dates to strings)
    formatted_dates = {}
    member_assignment_count = {}
    
    for date_obj, assigned_members in daily_assignments.items():
        date_str = date_obj.isoformat()
        formatted_dates[date_str] = assigned_members
        
        # Count assignments per member
        for member_name in assigned_members:
            member_assignment_count[member_name] = member_assignment_count.get(member_name, 0) + 1
    
    # Count committee members and gender distribution
    committee_count = sum(1 for m in members if m.is_committee)
    gender_count = {
        "male": sum(1 for m in members if m.gender == "M"),
        "female": sum(1 for m in members if m.gender == "F")
    }
    
    # Create the schedule data structure
    schedule_data = {
        "dates": formatted_dates,
        "assign_count": member_assignment_count,
        "committee_count": committee_count,
        "gender_count": gender_count,
        "unapplied_rules": []  # Could add constraint violations here
    }
    
    # Save to data file for the /schedules/latest endpoint
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(schedule_data, f, indent=2)
    
    return ScheduleGenerationResponse(
        message=f"Schedule generated successfully for {len(dates)} dates",
        schedule=schedule_data,
        member_assignments=member_assignment_count,
        available_dates=[d.isoformat() for d in dates]
    )