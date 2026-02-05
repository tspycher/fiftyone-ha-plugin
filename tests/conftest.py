"""Fixtures for FiftyOne tests."""
from __future__ import annotations

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.fiftyone.api import FiftyOneApiClient


@pytest.fixture
def mock_stocks_response() -> list[dict]:
    """Return mock stocks data."""
    return [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "quantity": 10,
            "price": 150.00,
            "value": 1500.00,
        },
        {
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "quantity": 5,
            "price": 140.00,
            "value": 700.00,
        },
    ]


@pytest.fixture
def mock_webcams_response() -> dict[str, str | None]:
    """Return mock webcams data."""
    return {
        "basel": "https://example.com/basel.jpg",
        "bern": "https://example.com/bern.jpg",
        "lucern": "https://example.com/lucern.jpg",
        "zurich": None,
    }


@pytest.fixture
def mock_aviation_response() -> dict:
    """Return mock aviation data."""
    return {
        "weather": {
            "oat": 15.5,
            "valid": True,
            "timestamp": 1704067200,
            "age": 120,
            "alt": 1575,
            "cloud_base": 3500,
            "da": 2100,
            "dew": 8.0,
            "gust_kmh": 25.0,
            "gust_kt": 13.5,
            "hpa": 1013.25,
            "humidity": 65.0,
            "pa": 1650,
            "rain_rate_mm": 0.0,
            "spread": 7.5,
            "wind_dir": 270,
            "wind_kmh": 15.0,
            "wind_kt": 8.1,
        },
        "runway": {
            "status": 1,
            "altitude": 1575,
            "additional": None,
            "text": "Runway open",
        },
    }


@pytest.fixture
def mock_api_client(
    mock_stocks_response: list[dict],
    mock_webcams_response: dict[str, str | None],
    mock_aviation_response: dict,
) -> AsyncMock:
    """Return a mock API client."""
    client = AsyncMock(spec=FiftyOneApiClient)
    client.async_test_connection.return_value = True
    client.async_get_stocks.return_value = mock_stocks_response
    client.async_get_webcams.return_value = mock_webcams_response
    client.async_get_aviation_lszi.return_value = mock_aviation_response
    client.async_get_latest_image.return_value = b"\x89PNG\r\n\x1a\n"
    client.async_get_random_image.return_value = b"\x89PNG\r\n\x1a\n"
    client.async_get_webcam_image.return_value = b"\x89PNG\r\n\x1a\n"
    return client


@pytest.fixture
def mock_config_entry() -> MagicMock:
    """Return a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.data = {
        "api_url": "https://api.fiftyone.dev",
        "image_sources": [
            {"code": "family", "name": "Family Photos"},
            {"code": "vacation", "name": "Vacation"},
        ],
    }
    return entry
