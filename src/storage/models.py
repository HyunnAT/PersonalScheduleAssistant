from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Event:
    id: Optional[int]
    event: str
    start_time: datetime
    end_time: Optional[datetime]
    location: Optional[str]
    reminder_minutes: int

    def __post_init__(self):
        # Validate start_time and end_time to ensure they follow ISO 8601 format
        if not isinstance(self.start_time, datetime):
            raise ValueError("start_time must be a datetime object in ISO format.")
        if self.end_time and not isinstance(self.end_time, datetime):
            raise ValueError("end_time must be a datetime object in ISO format.")