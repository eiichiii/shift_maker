import csv
from io import StringIO
from typing import List
from fastapi import UploadFile
from ..models.shift_request import ShiftRequest


def parse_shift_requests(file: UploadFile) -> List[ShiftRequest]:
    """Parse CSV file and return list of ShiftRequest models."""
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    shift_requests: List[ShiftRequest] = []
    for row in reader:
        shift_requests.append(
            ShiftRequest(
                employee_name=row.get("employee_name", ""),
                start_time=row.get("start_time", ""),
                end_time=row.get("end_time", ""),
            )
        )
    return shift_requests
