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

    async def _request_json(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """Make a JSON request to the API."""
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

    async def _request_bytes(self, url: str) -> bytes:
        """Fetch bytes from a URL."""
        try:
            async with self._session.get(url) as response:
                if response.status != 200:
                    raise FiftyOneApiError(
                        f"Request failed with status {response.status}"
                    )
                return await response.read()
        except aiohttp.ClientError as err:
            raise FiftyOneApiError(f"Error fetching data: {err}") from err

    async def async_get_stocks(self) -> list[dict[str, Any]]:
        """Get stock information.

        Returns list of stocks with: symbol, quantity, name?, price?, value?
        """
        return await self._request_json("GET", "/stocks")

    async def async_get_webcams(self) -> dict[str, str | None]:
        """Get webcam URLs.

        Returns dict with keys: basel, bern, lucern, zurich (values are URLs or None)
        """
        return await self._request_json("GET", "/webcams")

    async def async_get_webcam_image(self, url: str) -> bytes:
        """Fetch webcam image from URL."""
        return await self._request_bytes(url)

    async def async_get_aviation_lszi(self) -> dict[str, Any]:
        """Get aviation data for LSZI.

        Returns: {weather: AviationWeather, runway: Runway}
        """
        return await self._request_json("GET", "/aviation/lszi")

    async def async_get_latest_image(
        self, code: str | None = None, max_height: int = 900
    ) -> bytes:
        """Get latest family image."""
        params = {"max_height": max_height}
        if code:
            params["code"] = code

        url = f"{self._api_url}/image/latest"
        timeout = aiohttp.ClientTimeout(total=60)
        try:
            async with self._session.get(url, params=params, timeout=timeout) as response:
                if response.status != 200:
                    raise FiftyOneApiError(
                        f"Failed to get image with status {response.status}"
                    )
                return await response.read()
        except aiohttp.ClientError as err:
            raise FiftyOneApiError(f"Error getting image: {err}") from err

    async def async_get_random_image(
        self, code: str | None = None, max_height: int = 900
    ) -> bytes:
        """Get random family image."""
        params = {"max_height": max_height}
        if code:
            params["code"] = code

        url = f"{self._api_url}/image/random"
        timeout = aiohttp.ClientTimeout(total=60)
        try:
            async with self._session.get(url, params=params, timeout=timeout) as response:
                if response.status != 200:
                    raise FiftyOneApiError(
                        f"Failed to get image with status {response.status}"
                    )
                return await response.read()
        except aiohttp.ClientError as err:
            raise FiftyOneApiError(f"Error getting image: {err}") from err

    async def async_test_connection(self) -> bool:
        """Test if the API is reachable."""
        try:
            # Use the root endpoint which returns a random movie quote
            await self._request_json("GET", "/")
            return True
        except FiftyOneApiError:
            return False
