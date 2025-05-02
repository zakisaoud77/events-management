import pytest
from httpx import AsyncClient
from httpx import ASGITransport
from app.main import app
from app.db.mongodb import create_mongodb_connection, close_mongodb_connection
from app.db.mongodb import get_db
from asyncio import sleep

async def cleanup_testdb():
    """
    Cleanup function that will drop all collections in the test mongodb database,
    to keep it clean before and after each running tests.
    """
    db = get_db()
    collections = await db.list_collection_names()
    for name in collections:
        print(f"Dropping collection : {name}")
        await db.drop_collection(name)

# Test  /add_event
@pytest.mark.asyncio
async def test_create_event():
    # await sleep(20)
    await create_mongodb_connection()
    await cleanup_testdb()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/events/add_event/", json={
            "start": "2024-04-01 12:00:00",
            "stop": "2025-08-01 10:00:00",
            "tags": ["Hello", "Test"]
        })
    await close_mongodb_connection()
    assert response.status_code == 200
    assert response.json()["start"] == "2024-04-01T12:00:00"


# Test  /list_events
@pytest.mark.asyncio
async def test_list_events():
    await create_mongodb_connection()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/events/list_events/?skip=0&limit=10")
    await close_mongodb_connection()
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["tags"] == ["Hello", "Test"]


# Test  /delete_event
@pytest.mark.asyncio
async def test_delete_event():
    await create_mongodb_connection()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/events/add_event/", json={
            "start": "2024-04-01 12:00:00",
            "stop": "2025-08-01 10:00:00",
            "tags": ["Deleting", "Test"]
        })
        event_id = response.json()["id"]
        response = await client.delete(f"/events/delete_event/{event_id}?force_delete=True")
        await sleep(2)
    await close_mongodb_connection()
    assert response.status_code == 200
    assert f"{event_id} has been deleted successfully" in response.content.decode('utf-8')

# Test /search_events
@pytest.mark.asyncio
async def test_search_events():
    await create_mongodb_connection()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/events/search_events/?tags=Hello&tags=Test")
    await close_mongodb_connection()
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["results"][0]["tags"] == ["Hello", "Test"]

# Test update events tags
@pytest.mark.asyncio
async def test_update_event_tags():
    await create_mongodb_connection()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/events/add_event/", json={
            "start": "2023-04-01 12:00:00",
            "stop": "2024-08-01 10:00:00",
            "tags": ["Updating", "Test"]
        })
        event_id = response.json()["id"]
        response = await client.patch(f"/events/update_event_tags/{event_id}/?tags=IAM&tags=Updated&replace=True")
    await close_mongodb_connection()
    assert response.status_code == 200
    assert response.json()["tags"] == ["IAM", "Updated"]

