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

