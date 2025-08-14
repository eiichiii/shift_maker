"""Router for schedule-related endpoints."""
from __future__ import annotations

from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter(prefix="/schedules", tags=["schedules"])

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "latest_schedule.json"


def load_latest_schedule() -> dict:
    """Load the latest schedule from the data file.

    Returns
    -------
    dict
        Parsed JSON data. If the data file does not exist, an empty
        dictionary is returned.
    """
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@router.get("/latest")
def get_latest_schedule() -> dict:
    """Return the latest shift result.

    The returned JSON includes:
        * members for each date
        * assignment counts for members
        * number of committee members
        * gender statistics
        * unapplied rules
    """
    return load_latest_schedule()
