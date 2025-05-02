from app.db.mongodb import get_db
from app.models.events import EventCreate, EventOut
import asyncio

# Create new event
async def create_event(event: EventCreate):
    await asyncio.sleep(0.5)
    db = get_db()
    new_event = await db["events"].insert_one(event.dict())
    new_event_out = get_event_out(id=str(new_event.inserted_id), event=event.dict())
    return new_event_out

def get_event_out(id: str, event: dict):
    return EventOut(id=id, **event)

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
