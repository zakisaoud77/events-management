from datetime import datetime
from fastapi import APIRouter, Query, Path, Depends, HTTPException
from app.models.events import EventCreate, EventOut
from app.crud import events_crud
import asyncio

router = APIRouter()

# Add new event
@router.post(
    "/add_event/",
    summary="Create a new event",
    description="Creating new event, by giving a start datetime and a set of tags. stop datetime is optional",
    response_model=EventOut
)
async def add_event(event: EventCreate):
    try:
        await asyncio.sleep(0.5)
        new_event = await events_crud.create_event(event)
        return new_event
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot create new event because of: {str(e)}")
