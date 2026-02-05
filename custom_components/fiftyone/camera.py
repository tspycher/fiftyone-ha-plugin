"""Camera platform for FiftyOne integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
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
    webcams = coordinator.data.get("webcams", [])
    for webcam in webcams:
        if isinstance(webcam, dict) and "id" in webcam:
            entities.append(FiftyOneWebcam(coordinator, entry, webcam))

    # Add family pictures camera (slideshow-style)
    pictures = coordinator.data.get("pictures", [])
    if pictures:
        entities.append(FiftyOnePictureCamera(coordinator, entry))

    async_add_entities(entities)


class FiftyOneWebcam(CoordinatorEntity[FiftyOneDataUpdateCoordinator], Camera):
    """Representation of a FiftyOne webcam."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
        webcam_data: dict[str, Any],
    ) -> None:
        """Initialize the camera."""
        CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)

        self._webcam_id = webcam_data["id"]
        self._attr_unique_id = f"{entry.entry_id}_webcam_{self._webcam_id}"
        self._attr_name = webcam_data.get("name", f"Webcam {self._webcam_id}")
        self._cached_image: bytes | None = None

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return the camera image."""
        try:
            self._cached_image = await self.coordinator.api_client.async_get_webcam_image(
                self._webcam_id
            )
            return self._cached_image
        except Exception as err:
            _LOGGER.error("Error getting webcam image: %s", err)
            return self._cached_image


class FiftyOnePictureCamera(CoordinatorEntity[FiftyOneDataUpdateCoordinator], Camera):
    """Representation of a FiftyOne family pictures camera."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_name = "Family Pictures"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the camera."""
        CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)

        self._attr_unique_id = f"{entry.entry_id}_family_pictures"
        self._current_picture_index = 0
        self._cached_image: bytes | None = None

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return the current family picture."""
        pictures = self.coordinator.data.get("pictures", [])
        if not pictures:
            return None

        # Cycle through pictures
        self._current_picture_index = (self._current_picture_index + 1) % len(pictures)
        picture = pictures[self._current_picture_index]

        if isinstance(picture, dict) and "id" in picture:
            try:
                self._cached_image = await self.coordinator.api_client.async_get_picture_image(
                    picture["id"]
                )
                return self._cached_image
            except Exception as err:
                _LOGGER.error("Error getting family picture: %s", err)
                return self._cached_image

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        pictures = self.coordinator.data.get("pictures", [])
        if pictures and self._current_picture_index < len(pictures):
            current = pictures[self._current_picture_index]
            if isinstance(current, dict):
                return {
                    "current_picture": current.get("name", "Unknown"),
                    "total_pictures": len(pictures),
                    "picture_index": self._current_picture_index,
                }
        return {"total_pictures": len(pictures)}
