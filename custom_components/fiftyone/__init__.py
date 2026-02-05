"""The FiftyOne integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .coordinator import FiftyOneDataUpdateCoordinator
from .api import FiftyOneApiClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS_LIST: list[Platform] = [Platform.SENSOR, Platform.CAMERA, Platform.IMAGE]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up FiftyOne from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api_client = FiftyOneApiClient(
        session=async_get_clientsession(hass),
        api_url=entry.data.get("api_url"),
    )

    coordinator = FiftyOneDataUpdateCoordinator(
        hass=hass,
        api_client=api_client,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_LIST)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS_LIST):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
