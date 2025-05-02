from typing import Optional, List
from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import datetime

# This model is used to create new event
class EventCreate(BaseModel):
    start: datetime = Field(..., description="Event start time (Mandatory)", examples=[1717027200, "2025-02-10 21:30"])
    stop: Optional[datetime] | None = Field(None, description="Event stop time (Optional)", examples=[1725027200, "2026-03-10 17:30"])
    tags: List[str] = Field(..., description="List of tags of the event", examples=["database", "cloud"])

    @model_validator(mode='after')
    def check_stop_after_start(self):
        if self.stop:
            if self.stop <= self.start:
                raise ValueError('stop datetime must be after start datetime')
        return self

    @field_validator("start", "stop", mode="before")
    @classmethod
    def date_formats_parsing(cls, date_value):
        if isinstance(date_value, str):
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%d %H",
                "%Y-%m-%d",
                "%Y/%m/%d %H:%M",
                "%Y/%m/%d %H",
                "%Y/%m/%d",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue
        return date_value

# This model is used to return a created event
class EventOut(EventCreate):
    id: str = Field(
        description="MongoDB ObjectId of the event",
        examples=["6631c5d82fda6e60f14e2a3a"]
    )