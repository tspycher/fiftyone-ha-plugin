"""API client for FiftyOne."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class FiftyOneApiError(Exception):
    """Exception for FiftyOne API errors."""


class FiftyOneApiClient:
    """API client for FiftyOne."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        api_url: str | None = None,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._api_url = api_url or API_BASE_URL

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """Make a request to the API."""
        url = f"{self._api_url}{endpoint}"

        try:
            async with self._session.request(method, url, **kwargs) as response:
                if response.status != 200:
                    raise FiftyOneApiError(
                        f"API request failed with status {response.status}"
                    )
                return await response.json()
        except aiohttp.ClientError as err:
            raise FiftyOneApiError(f"Error communicating with API: {err}") from err

    async def async_get_stocks(self) -> dict[str, Any]:
        """Get stock information."""
        return await self._request("GET", "/stocks")

    async def async_get_weather(self) -> dict[str, Any]:
        """Get weather information."""
        return await self._request("GET", "/weather")

    async def async_get_webcams(self) -> list[dict[str, Any]]:
        """Get list of webcams."""
        return await self._request("GET", "/webcams")

    async def async_get_webcam_image(self, webcam_id: str) -> bytes:
        """Get webcam image."""
        url = f"{self._api_url}/webcams/{webcam_id}/image"

        try:
            async with self._session.get(url) as response:
                if response.status != 200:
                    raise FiftyOneApiError(
                        f"Failed to get webcam image with status {response.status}"
                    )
                return await response.read()
        except aiohttp.ClientError as err:
            raise FiftyOneApiError(f"Error getting webcam image: {err}") from err

    async def async_get_family_pictures(self) -> list[dict[str, Any]]:
        """Get family pictures."""
        return await self._request("GET", "/pictures")

    async def async_get_picture_image(self, picture_id: str) -> bytes:
        """Get a specific picture."""
        url = f"{self._api_url}/pictures/{picture_id}"

        try:
            async with self._session.get(url) as response:
                if response.status != 200:
                    raise FiftyOneApiError(
                        f"Failed to get picture with status {response.status}"
                    )
                return await response.read()
        except aiohttp.ClientError as err:
            raise FiftyOneApiError(f"Error getting picture: {err}") from err

    async def async_test_connection(self) -> bool:
        """Test if the API is reachable."""
        try:
            await self._request("GET", "/health")
            return True
        except FiftyOneApiError:
            return False
