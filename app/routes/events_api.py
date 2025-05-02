from datetime import datetime
from fastapi import APIRouter, Query, Path, Depends, HTTPException
from app.models.events import EventCreate, EventOut, EventResponseList
from typing import Optional, List
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

# Get the list of all events
@router.get(
    "/list_events/",
    summary="List all events",
    description="Listing all events. To specify how many events you would like to get, you can use skip and limit parameters",
    response_model=EventResponseList
)
async def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100)
):
    try:
        events_list_from_db = await events_crud.get_all_events(skip, limit)
        return events_list_from_db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot get events list, because of: {str(e)}")

# Get the list of running events
@router.get(
    "/running_events/",
    summary="List all running events",
    description="Listing all running events. You can use skip and limit parameters, to specify the number of returned events",
    response_model=EventResponseList
)
async def list_running_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100)
):
    try:
        events_list_from_db = await events_crud.get_running_events(skip, limit)
        return events_list_from_db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot get running events list, because of: {str(e)}")

# Search events by tags
@router.get(
    "/search_events/",
    summary="Searching events based on tags",
    description="Searching the list of events which contain a specific list of tags",
    response_model=EventResponseList
)
async def search_events(
    tags: List[str] = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100)
):
    try:
        events_db_list = await events_crud.search_event(tags, skip, limit)
        return events_db_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot find events, because of: {str(e)}")