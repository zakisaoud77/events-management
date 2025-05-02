from datetime import datetime
from fastapi import APIRouter, Query, Path, Depends, HTTPException
from fastapi.responses import JSONResponse
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

# Deleting event from ID
@router.delete(
    "/delete_event/{event_id}",
    summary="Deleting an event",
    description="Deleting an event by ID. If the event is running, it will be deleted only if `force_delete=true`",
)
async def delete_event(
    event_id: str = Path(...),
    force_delete: bool = Query(False, description="Force deletion of the event")
):
    try:
        delete_event = await events_crud.delete_event(event_id=event_id, force_delete=force_delete)
        if delete_event:
            return JSONResponse(
                status_code=200,
                content=f"event {event_id} has been deleted successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"We cannot delete the event {event_id}, its an ongoing event and force_delete=False"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting event {event_id} because of: {str(e)}")

# Deleting all events
@router.delete(
    "/delete_all_events/",
    summary = "Deleting all events",
    description = "Deleting all events. If there is some running events, they will be deleted only if `force_delete=true`",
)
async def delete_all_events(
    force_delete: bool = Query(False, description="Force deletion of all events")
):
    try:
        total_events, deleted_events = await events_crud.delete_all_events(force_delete=force_delete)
        if total_events == deleted_events > 0:
            return JSONResponse(
                status_code=200,
                content=f"All of {deleted_events} events have been deleted successfully"
            )
        elif total_events > deleted_events > 0:
            return JSONResponse(
                status_code=200,
                content=f"All of {deleted_events} stopped events have been deleted successfully"
            )
        elif total_events == deleted_events == 0:
            return JSONResponse(
                status_code=404,
                content=f"There is no events to delete ! all events have been deleted"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"We cannot delete events, because there is only running events and force_delete=False"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting all events because of: {str(e)}")