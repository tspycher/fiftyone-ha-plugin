"""Image platform for FiftyOne integration."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONF_IMAGE_SOURCES, DOMAIN
from .coordinator import FiftyOneDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FiftyOne image entities based on a config entry."""
    coordinator: FiftyOneDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[ImageEntity] = []

    # Add image entities for each configured source code
    image_sources = entry.data.get(CONF_IMAGE_SOURCES, [])
    for source in image_sources:
        code = source.get("code")
        name = source.get("name", code)
        if code:
            entities.append(FiftyOneLatestImage(coordinator, entry, code, name))
            entities.append(FiftyOneRandomImage(coordinator, entry, code, name))

    async_add_entities(entities)


class FiftyOneLatestImage(CoordinatorEntity[FiftyOneDataUpdateCoordinator], ImageEntity):
    """Image entity showing the latest image for a source code."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
        code: str,
        name: str,
    ) -> None:
        """Initialize the image entity."""
        CoordinatorEntity.__init__(self, coordinator)
        ImageEntity.__init__(self, coordinator.hass)

        self._code = code
        self._attr_unique_id = f"{entry.entry_id}_image_{code}_latest"
        self._attr_name = f"{name} Latest"
        self._cached_image: bytes | None = None
        self._image_last_updated: datetime | None = None

    @property
    def image_last_updated(self) -> datetime | None:
        """Return when the image was last updated."""
        return self._image_last_updated

    async def async_image(self) -> bytes | None:
        """Return the latest image."""
        try:
            self._cached_image = await self.coordinator.api_client.async_get_latest_image(
                code=self._code
            )
            self._image_last_updated = datetime.now()
            self.async_write_ha_state()
            return self._cached_image
        except Exception as err:
            _LOGGER.error("Error getting latest image for %s: %s", self._code, err)
            return self._cached_image


class FiftyOneRandomImage(CoordinatorEntity[FiftyOneDataUpdateCoordinator], ImageEntity):
    """Image entity showing a random image for a source code."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
        code: str,
        name: str,
    ) -> None:
        """Initialize the image entity."""
        CoordinatorEntity.__init__(self, coordinator)
        ImageEntity.__init__(self, coordinator.hass)

        self._code = code
        self._attr_unique_id = f"{entry.entry_id}_image_{code}_random"
        self._attr_name = f"{name} Random"
        self._cached_image: bytes | None = None
        self._image_last_updated: datetime | None = None

    @property
    def image_last_updated(self) -> datetime | None:
        """Return when the image was last updated."""
        return self._image_last_updated

    async def async_image(self) -> bytes | None:
        """Return a random image."""
        try:
            self._cached_image = await self.coordinator.api_client.async_get_random_image(
                code=self._code
            )
            self._image_last_updated = datetime.now()
            self.async_write_ha_state()
            return self._cached_image
        except Exception as err:
            _LOGGER.error("Error getting random image for %s: %s", self._code, err)
            return self._cached_image
