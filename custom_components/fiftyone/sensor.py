"""Sensor platform for FiftyOne integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import FiftyOneDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up FiftyOne sensors based on a config entry."""
    coordinator: FiftyOneDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    # Add weather sensors
    if coordinator.data.get("weather"):
        entities.append(FiftyOneWeatherSensor(coordinator, entry))

    # Add stock sensors
    stocks_data = coordinator.data.get("stocks", {})
    if isinstance(stocks_data, dict):
        for stock_id in stocks_data.keys():
            entities.append(FiftyOneStockSensor(coordinator, entry, stock_id))
    elif isinstance(stocks_data, list):
        for stock in stocks_data:
            if isinstance(stock, dict) and "id" in stock:
                entities.append(FiftyOneStockSensor(coordinator, entry, stock["id"]))

    async_add_entities(entities)


class FiftyOneWeatherSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Representation of a FiftyOne weather sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_weather_temperature"
        self._attr_name = "Weather Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        weather = self.coordinator.data.get("weather", {})
        return weather.get("temperature")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        weather = self.coordinator.data.get("weather", {})
        return {
            k: v for k, v in weather.items() if k != "temperature"
        }


class FiftyOneStockSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Representation of a FiftyOne stock sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:chart-line"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
        stock_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._stock_id = stock_id
        self._attr_unique_id = f"{entry.entry_id}_stock_{stock_id}"
        self._attr_name = f"Stock {stock_id}"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        stocks = self.coordinator.data.get("stocks", {})
        if isinstance(stocks, dict):
            stock_data = stocks.get(self._stock_id, {})
        elif isinstance(stocks, list):
            stock_data = next(
                (s for s in stocks if s.get("id") == self._stock_id),
                {}
            )
        else:
            stock_data = {}

        return stock_data.get("price") or stock_data.get("value")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        stocks = self.coordinator.data.get("stocks", {})
        if isinstance(stocks, dict):
            stock_data = stocks.get(self._stock_id, {})
        elif isinstance(stocks, list):
            stock_data = next(
                (s for s in stocks if s.get("id") == self._stock_id),
                {}
            )
        else:
            stock_data = {}

        return {
            k: v for k, v in stock_data.items()
            if k not in ("price", "value", "id")
        }
