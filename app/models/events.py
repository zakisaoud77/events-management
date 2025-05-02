from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# This model is used to create new event
class EventCreate(BaseModel):
    start: datetime = Field(..., description="Event start time (Mandatory)", examples=[1717027200, "2025-02-10 21:30"])
    stop: Optional[datetime] | None = Field(None, description="Event stop time (Optional)", examples=[1725027200, "2026-03-10 17:30"])
    tags: List[str] = Field(..., description="List of tags of the event", examples=["database", "cloud"])

# This model is used to return a created event
class EventOut(EventCreate):
    id: str = Field(
        description="MongoDB ObjectId of the event",
        examples=["6631c5d82fda6e60f14e2a3a"]
    )