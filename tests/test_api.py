"""Tests for the FiftyOne API client."""
from __future__ import annotations

from unittest.mock import AsyncMock

import aiohttp
import pytest

from custom_components.fiftyone.api import FiftyOneApiClient, FiftyOneApiError


@pytest.fixture
def mock_session() -> AsyncMock:
    """Return a mock aiohttp session."""
    return AsyncMock(spec=aiohttp.ClientSession)


class TestFiftyOneApiClient:
    """Tests for FiftyOneApiClient."""

    def test_init_default_url(self, mock_session: AsyncMock) -> None:
        """Test initialization with default URL."""
        client = FiftyOneApiClient(session=mock_session)
        assert client._api_url == "https://api.fiftyone.dev"

    def test_init_custom_url(self, mock_session: AsyncMock) -> None:
        """Test initialization with custom URL."""
        client = FiftyOneApiClient(
            session=mock_session, api_url="https://custom.api.com"
        )
        assert client._api_url == "https://custom.api.com"

    @pytest.mark.asyncio
    async def test_async_test_connection_success(
        self, mock_session: AsyncMock
    ) -> None:
        """Test successful connection test."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={"text": "quote", "character": "char", "movie": "movie"}
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.request.return_value = mock_response

        client = FiftyOneApiClient(session=mock_session)
        result = await client.async_test_connection()

        assert result is True
        mock_session.request.assert_called_once_with("GET", "https://api.fiftyone.dev/")

    @pytest.mark.asyncio
    async def test_async_test_connection_failure(
        self, mock_session: AsyncMock
    ) -> None:
        """Test failed connection test."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.request.return_value = mock_response

        client = FiftyOneApiClient(session=mock_session)
        result = await client.async_test_connection()

        assert result is False

    @pytest.mark.asyncio
    async def test_async_get_stocks(self, mock_session: AsyncMock) -> None:
        """Test getting stocks."""
        expected_stocks = [
            {"symbol": "AAPL", "quantity": 10, "price": 150.0},
        ]

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=expected_stocks)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.request.return_value = mock_response

        client = FiftyOneApiClient(session=mock_session)
        result = await client.async_get_stocks()

        assert result == expected_stocks
        mock_session.request.assert_called_with(
            "GET", "https://api.fiftyone.dev/stocks"
        )

    @pytest.mark.asyncio
    async def test_async_get_webcams(self, mock_session: AsyncMock) -> None:
        """Test getting webcams."""
        expected_webcams = {
            "basel": "https://example.com/basel.jpg",
            "bern": None,
        }

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=expected_webcams)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.request.return_value = mock_response

        client = FiftyOneApiClient(session=mock_session)
        result = await client.async_get_webcams()

        assert result == expected_webcams

    @pytest.mark.asyncio
    async def test_async_get_aviation_lszi(self, mock_session: AsyncMock) -> None:
        """Test getting aviation data."""
        expected_data = {
            "weather": {"oat": 15.5, "valid": True},
            "runway": {"status": 1},
        }

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=expected_data)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.request.return_value = mock_response

        client = FiftyOneApiClient(session=mock_session)
        result = await client.async_get_aviation_lszi()

        assert result == expected_data

    @pytest.mark.asyncio
    async def test_async_get_latest_image(self, mock_session: AsyncMock) -> None:
        """Test getting latest image."""
        image_bytes = b"\x89PNG\r\n\x1a\n"

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(return_value=image_bytes)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.get.return_value = mock_response

        client = FiftyOneApiClient(session=mock_session)
        result = await client.async_get_latest_image(code="family", max_height=800)

        assert result == image_bytes
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert "image/latest" in call_args[0][0]
        assert call_args[1]["params"] == {"code": "family", "max_height": 800}

    @pytest.mark.asyncio
    async def test_async_get_random_image(self, mock_session: AsyncMock) -> None:
        """Test getting random image."""
        image_bytes = b"\x89PNG\r\n\x1a\n"

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(return_value=image_bytes)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.get.return_value = mock_response

        client = FiftyOneApiClient(session=mock_session)
        result = await client.async_get_random_image(code="vacation")

        assert result == image_bytes

    @pytest.mark.asyncio
    async def test_async_get_webcam_image(self, mock_session: AsyncMock) -> None:
        """Test getting webcam image."""
        image_bytes = b"\x89PNG\r\n\x1a\n"
        webcam_url = "https://example.com/webcam.jpg"

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(return_value=image_bytes)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.get.return_value = mock_response

        client = FiftyOneApiClient(session=mock_session)
        result = await client.async_get_webcam_image(webcam_url)

        assert result == image_bytes
        mock_session.get.assert_called_once_with(webcam_url)

    @pytest.mark.asyncio
    async def test_request_error_handling(self, mock_session: AsyncMock) -> None:
        """Test error handling for failed requests."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session.request.return_value = mock_response

        client = FiftyOneApiClient(session=mock_session)

        with pytest.raises(FiftyOneApiError) as exc_info:
            await client.async_get_stocks()

        assert "500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, mock_session: AsyncMock) -> None:
        """Test handling of connection errors."""
        mock_session.request.side_effect = aiohttp.ClientError("Connection failed")

        client = FiftyOneApiClient(session=mock_session)

        with pytest.raises(FiftyOneApiError) as exc_info:
            await client.async_get_stocks()

        assert "Connection failed" in str(exc_info.value)
