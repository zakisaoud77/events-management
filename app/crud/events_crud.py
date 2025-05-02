from app.db.mongodb import get_db
from app.models.events import EventCreate, EventOut
import asyncio
from bson import ObjectId
from typing import List
from fastapi import HTTPException
from datetime import datetime
from pymongo import ReturnDocument

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

def get_event_id(event_id: str):
    try:
        obj_id = ObjectId(event_id)
        return obj_id
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid event ID format")

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

# Deleting event by event_id
async def delete_event(event_id: str, force_delete: bool = False):
    validated_event_id  = get_event_id(event_id)
    db = get_db()
    event = await db["events"].find_one({"_id": validated_event_id})
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with id {event_id} is not found")
    time_now = get_time_now()
    is_ongoing = (
        event["start"] <= time_now and
        (
            event.get("stop") is None or event.get("stop") > time_now
        )
    )
    start_in_future  = (event["start"] > time_now)
    if is_ongoing and not force_delete:
        print(f"We cannot delete the event {event_id}, its an ongoing event and force_delete=False")
        return False
    elif start_in_future and not force_delete:
        print(f"We cannot delete the event {event_id}, it will start in the future and force_delete=False")
        return False
    else:
        await db["events"].delete_one({"_id": validated_event_id})
        print(f"event {event_id} has been deleted successfully")
        return True

# Deleting all events
async def delete_all_events(force_delete: bool = False):
    now = get_time_now()
    db = get_db()
    total_events = await get_all_events(skip=0,limit=100)
    if force_delete:
        deleted_events = await db["events"].delete_many({})
    else:
        query_stopped_events = {"stop": {"$lte": now}}
        deleted_events = await db["events"].delete_many(query_stopped_events)

    if deleted_events.deleted_count > 0:
        print(f"All of {deleted_events.deleted_count} events have been deleted successfully")
        return total_events["total"], deleted_events.deleted_count
    elif total_events["total"] != 0 and deleted_events.deleted_count == 0:
        print(f"There is no events to delete, there is no stopped events and force_delete=False")
        return total_events["total"], 0
    else :
        print(f"There is no events to delete ! all events have been deleted")
        return 0, 0

async def update_event_based_on_id(event_id, update_query:dict):
    validated_event_id = get_event_id(event_id)
    db = get_db()
    updated_event = await db["events"].find_one_and_update(
        {"_id": validated_event_id},
        update_query,
        return_document=ReturnDocument.AFTER
    )
    return updated_event

# Updating event tags
async def updating_event_tags(event_id:str, tags:List[str], replace:bool = False):
    if replace:
        update_query = {"$set": {"tags": tags}}
    else:
        update_query = {"$addToSet": {"tags": {"$each": tags}}}
    updated_event = await update_event_based_on_id(event_id, update_query)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    else:
        updated_event_out = get_event_out(id=str(updated_event["_id"]), event=updated_event)
        return updated_event_out

# Updating event datetime
async def updating_event_datetime(event_id:str, start:datetime, stop:datetime=None):
    update_query = {"$set": {"start": start, "stop": stop}}
    updated_event = await update_event_based_on_id(event_id, update_query)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    else:
        updated_event_out = get_event_out(id=str(updated_event["_id"]), event=updated_event)
        return updated_event_out