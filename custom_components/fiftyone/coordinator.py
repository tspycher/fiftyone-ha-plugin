"""Data update coordinator for FiftyOne."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FiftyOneApiClient, FiftyOneApiError
from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class FiftyOneDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching FiftyOne data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: FiftyOneApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api_client = api_client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        try:
            data: dict[str, Any] = {}

            # Fetch stocks
            try:
                data["stocks"] = await self.api_client.async_get_stocks()
            except FiftyOneApiError as err:
                _LOGGER.warning("Failed to fetch stocks: %s", err)
                data["stocks"] = []

            # Fetch webcams
            try:
                data["webcams"] = await self.api_client.async_get_webcams()
            except FiftyOneApiError as err:
                _LOGGER.warning("Failed to fetch webcams: %s", err)
                data["webcams"] = {}

            # Fetch aviation data for LSZI
            try:
                data["aviation"] = await self.api_client.async_get_aviation_lszi()
                _LOGGER.debug("Fetched aviation data: %s", data["aviation"])
            except FiftyOneApiError as err:
                _LOGGER.warning("Failed to fetch aviation data: %s", err)
                data["aviation"] = {}

            _LOGGER.debug(
                "Data update complete - stocks: %d, webcams: %d, aviation: %s",
                len(data.get("stocks", [])),
                len(data.get("webcams", {})),
                "yes" if data.get("aviation") else "no",
            )

            return data

        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
