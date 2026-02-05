"""Camera platform for FiftyOne integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, WEBCAM_NAMES
from .coordinator import FiftyOneDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FiftyOne cameras based on a config entry."""
    coordinator: FiftyOneDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[Camera] = []

    # Add webcam cameras
    webcams = coordinator.data.get("webcams", {})
    for webcam_id, url in webcams.items():
        if url:  # Only add if URL is not None
            entities.append(FiftyOneWebcam(coordinator, entry, webcam_id, url))

    async_add_entities(entities)


class FiftyOneWebcam(CoordinatorEntity[FiftyOneDataUpdateCoordinator], Camera):
    """Representation of a FiftyOne webcam."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
        webcam_id: str,
        initial_url: str,
    ) -> None:
        """Initialize the camera."""
        CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)

        self._webcam_id = webcam_id
        self._attr_unique_id = f"{entry.entry_id}_webcam_{webcam_id}"
        self._attr_name = f"Webcam {WEBCAM_NAMES.get(webcam_id, webcam_id.title())}"
        self._cached_image: bytes | None = None

    @property
    def _current_url(self) -> str | None:
        """Get current URL from coordinator data."""
        webcams = self.coordinator.data.get("webcams", {})
        return webcams.get(self._webcam_id)

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return the camera image."""
        url = self._current_url
        if not url:
            return self._cached_image

        try:
            self._cached_image = await self.coordinator.api_client.async_get_webcam_image(url)
            return self._cached_image
        except Exception as err:
            _LOGGER.error("Error getting webcam image for %s: %s", self._webcam_id, err)
            return self._cached_image

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "webcam_id": self._webcam_id,
            "image_url": self._current_url,
        }
