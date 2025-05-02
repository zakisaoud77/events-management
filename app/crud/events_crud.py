from app.db.mongodb import get_db
from app.models.events import EventCreate, EventOut
import asyncio
from typing import List
from fastapi import HTTPException
from datetime import datetime

# Create new event
async def create_event(event: EventCreate):
    await asyncio.sleep(0.5)
    db = get_db()
    new_event = await db["events"].insert_one(event.dict())
    new_event_out = get_event_out(id=str(new_event.inserted_id), event=event.dict())
    return new_event_out

def get_event_out(id: str, event: dict):
    return EventOut(id=id, **event)

def get_time_now():
    return datetime.now()

# Get the list of all events
async def get_all_events(skip, limit):
    db = get_db()
    events = []
    total_events = await db["events"].count_documents({})
    all_events = db["events"].find({}).skip(skip).limit(limit)
    async for event in all_events:
        events.append(get_event_out(id=str(event["_id"]), event=event))
    return {
        "total": total_events,
        "skip": skip,
        "limit": limit,
        "results": events
    }

# Get running events
async def get_running_events(skip, limit):
    now = get_time_now()
    db = get_db()
    running_events = []
    query = {
        "$or": [
            {"start": {"$lte": now}, "stop": {"$gte": now}},
            {"start": {"$lte": now}, "$or": [ {"stop": None}, {"stop": { "$exists": False }} ] }
        ]
    }
    total_running_events = await db["events"].count_documents(query)
    events = db["events"].find(query).skip(skip).limit(limit)
    async for event in events:
        running_events.append(get_event_out(id=str(event["_id"]), event=event))
    return {
        "total": total_running_events,
        "skip": skip,
        "limit": limit,
        "results": running_events
    }

# Search an event from tags
async def search_event(tags: List[str], skip, limit):
    db = get_db()
    events = []
    query = {"tags": {"$in": tags}}
    total_events = await db["events"].count_documents(query)
    events_db_list = db["events"].find(query).skip(skip).limit(limit)
    async for event in events_db_list:
        events.append(get_event_out(id=str(event["_id"]), event=event))
    if not events:
        raise HTTPException(status_code=404, detail=f"Events with at least one tag from tags {tags} don't exist")
    return {
        "total": total_events,
        "skip": skip,
        "limit": limit,
        "results": events
    }