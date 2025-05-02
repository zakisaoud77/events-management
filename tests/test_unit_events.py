import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app
from datetime import datetime

# Test /add_event
@pytest.mark.asyncio
@patch("app.crud.events_crud.create_event", new_callable=AsyncMock)
async def test_add_event_mocked(mock_create_event):
    mock_create_event.return_value = {
        "id": "123456",
        "start": "2024-04-01 12:00:00",
        "stop": "2025-08-01 10:00:00",
        "tags": ["Hello", "Test"]
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/events/add_event/", json={
            "start": "2024-04-01 12:00:00",
            "stop": "2025-08-01 10:00:00",
            "tags": ["Hello", "Test"]
        })

    assert response.status_code == 200
    data = response.json()
    assert data["start"] == "2024-04-01T12:00:00"
    assert data["tags"] == ["Hello", "Test"]
    mock_create_event.assert_awaited_once()

# Test  /list_events
@pytest.mark.asyncio
@patch("app.crud.events_crud.get_all_events", new_callable=AsyncMock)
async def test_list_events_mocked(mock_get_events):
    mock_get_events.return_value = {
        "total": 2,
        "skip": 0,
        "limit": 10,
        "results": [
            {
                "id": "1",
                "start": "2024-04-01T12:00:00",
                "stop": "2024-04-01T14:00:00",
                "tags": ["Hello", "test2"]
            },
            {
                "id": "2",
                "start": "2022-05-01T21:00:00",
                "stop": "2023-05-01T18:00:00",
                "tags": ["Cloud","AWS"]
            }
        ]
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/events/list_events/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert len(data["results"]) == 2
    mock_get_events.assert_awaited_once_with(0, 10)

# Test  /running_events
@pytest.mark.asyncio
@patch("app.crud.events_crud.get_running_events", new_callable=AsyncMock)
async def test_running_events_mocked(mock_running_events):
    mock_running_events.return_value = {
        "total": 2,
        "skip": 0,
        "limit": 10,
        "results": [
            {
                "id": "1",
                "start": "2024-04-01T12:00:00",
                "stop": "2026-04-01T14:00:00",
                "tags": ["Hello", "test2"]
            },
            {
                "id": "2",
                "start": "2022-05-01T21:00:00",
                "tags": ["Cloud","AWS"]
            }
        ]
    }
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/events/running_events/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert len(data["results"]) == 2
    mock_running_events.assert_awaited_once_with(0, 10)

# Test search events
@pytest.mark.asyncio
@patch("app.crud.events_crud.search_event", new_callable=AsyncMock)
async def test_search_events(mock_search_event):
    mock_search_event.return_value = {
        "total": 2,
        "skip": 0,
        "limit": 10,
        "results": [
            {
                "id": "1",
                "start": "2024-01-01T12:00:00",
                "stop": "2024-01-01T13:00:00",
                "tags": ["Test1", "Cloud"]
            },
            {
                "id": "2",
                "start": "2024-02-01T12:00:00",
                "stop": "2024-02-01T13:00:00",
                "tags": ["Test2"]
            }
        ]
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/events/search_events/?tags=Test1&skip=0&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["tags"] == ["Test1", "Cloud"]

# Test /delete_event
@pytest.mark.asyncio
@patch("app.crud.events_crud.delete_event", new_callable=AsyncMock)
async def test_delete_event_success(mock_delete_event):
    mock_delete_event.return_value = True

    event_id = "e213124124123"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/events/delete_event/{event_id}?force_delete=true")

    assert response.status_code == 200
    assert f"event {event_id} has been deleted successfully" in response.text
    mock_delete_event.assert_awaited_once_with(event_id=event_id, force_delete=True)

# Test /delete_all_events/
@pytest.mark.asyncio
@patch("app.crud.events_crud.delete_all_events", new_callable=AsyncMock)
async def test_delete_all_events(mock_delete_all_events):
    mock_delete_all_events.return_value = (3, 3)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete(f"/events/delete_all_events/?force_delete=true")

    assert response.status_code == 200
    assert "3 events have been deleted successfully" in response.text
    mock_delete_all_events.assert_awaited_once_with(force_delete=True)

# Test "/update_event_tags/
@pytest.mark.asyncio
@patch("app.crud.events_crud.updating_event_tags", new_callable=AsyncMock)
async def test_update_event_tags(mock_update_tags):
    event_id = "e2131313ef1231233"
    mock_update_tags.return_value = {
        "id": event_id,
        "start": "2023-07-22T13:00:00",
        "stop": "2024-04-17T19:00:00",
        "tags": ["Tag1", "Tag2"]
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.patch(
            f"/events/update_event_tags/{event_id}/?tags=Tag1&tags=Tag2&replace=True"
        )
    assert response.status_code == 200
    data = response.json()
    assert data["tags"] == ["Tag1", "Tag2"]
    assert data["id"] == event_id
    mock_update_tags.assert_awaited_once_with(event_id=event_id, tags=["Tag1", "Tag2"], replace=True)