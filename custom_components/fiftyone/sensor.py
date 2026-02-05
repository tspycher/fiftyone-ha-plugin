"""Sensor platform for FiftyOne integration."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
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

    # Add stock sensors
    stocks_data = coordinator.data.get("stocks", [])
    for stock in stocks_data:
        if isinstance(stock, dict) and "symbol" in stock:
            entities.append(FiftyOneStockPriceSensor(coordinator, entry, stock["symbol"]))
            entities.append(FiftyOneStockValueSensor(coordinator, entry, stock["symbol"]))
            entities.append(FiftyOneStockQuantitySensor(coordinator, entry, stock["symbol"]))

    # Add aviation sensors (always create them, they'll show unavailable if no data)
    entities.append(FiftyOneAviationTemperatureSensor(coordinator, entry))
    entities.append(FiftyOneAviationHumiditySensor(coordinator, entry))
    entities.append(FiftyOneAviationPressureSensor(coordinator, entry))
    entities.append(FiftyOneAviationWindSpeedSensor(coordinator, entry))
    entities.append(FiftyOneAviationWindDirectionSensor(coordinator, entry))
    entities.append(FiftyOneAviationCloudBaseSensor(coordinator, entry))
    entities.append(FiftyOneAviationDensityAltitudeSensor(coordinator, entry))
    entities.append(FiftyOneAviationPressureAltitudeSensor(coordinator, entry))
    # Runway sensor
    entities.append(FiftyOneRunwayStatusSensor(coordinator, entry))

    async_add_entities(entities)


class FiftyOneStockPriceSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Representation of a FiftyOne stock price sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "CHF"
    _attr_icon = "mdi:currency-usd"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
        symbol: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._symbol = symbol
        self._attr_unique_id = f"{entry.entry_id}_stock_{symbol}_price"
        self._attr_name = f"{symbol} Price"

    def _get_stock_data(self) -> dict[str, Any]:
        """Get stock data for this symbol."""
        stocks = self.coordinator.data.get("stocks", [])
        return next((s for s in stocks if s.get("symbol") == self._symbol), {})

    @property
    def native_value(self) -> float | None:
        """Return the stock price."""
        return self._get_stock_data().get("price")


class FiftyOneStockValueSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Representation of a FiftyOne stock total value sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "CHF"
    _attr_icon = "mdi:cash-multiple"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
        symbol: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._symbol = symbol
        self._attr_unique_id = f"{entry.entry_id}_stock_{symbol}_value"
        self._attr_name = f"{symbol} Value"

    def _get_stock_data(self) -> dict[str, Any]:
        """Get stock data for this symbol."""
        stocks = self.coordinator.data.get("stocks", [])
        return next((s for s in stocks if s.get("symbol") == self._symbol), {})

    @property
    def native_value(self) -> float | None:
        """Return the total stock value."""
        return self._get_stock_data().get("value")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        stock = self._get_stock_data()
        return {
            "name": stock.get("name"),
            "symbol": stock.get("symbol"),
            "quantity": stock.get("quantity"),
            "price": stock.get("price"),
        }


class FiftyOneStockQuantitySensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Representation of a FiftyOne stock quantity sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:counter"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
        symbol: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._symbol = symbol
        self._attr_unique_id = f"{entry.entry_id}_stock_{symbol}_quantity"
        self._attr_name = f"{symbol} Quantity"

    def _get_stock_data(self) -> dict[str, Any]:
        """Get stock data for this symbol."""
        stocks = self.coordinator.data.get("stocks", [])
        return next((s for s in stocks if s.get("symbol") == self._symbol), {})

    @property
    def native_value(self) -> int | None:
        """Return the stock quantity."""
        return self._get_stock_data().get("quantity")


class FiftyOneAviationTemperatureSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Aviation OAT (Outside Air Temperature) sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_name = "LSZI Temperature"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_aviation_lszi_oat"

    @property
    def native_value(self) -> float | None:
        """Return the temperature."""
        aviation = self.coordinator.data.get("aviation", {})
        weather = aviation.get("weather", {})
        return weather.get("oat")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        aviation = self.coordinator.data.get("aviation", {})
        weather = aviation.get("weather", {})
        attrs = {}
        if weather.get("dew") is not None:
            attrs["dewpoint"] = weather["dew"]
        if weather.get("spread") is not None:
            attrs["spread"] = weather["spread"]
        if weather.get("timestamp"):
            attrs["data_timestamp"] = datetime.fromtimestamp(weather["timestamp"]).isoformat()
        if weather.get("age") is not None:
            attrs["data_age_seconds"] = weather["age"]
        return attrs


class FiftyOneAviationHumiditySensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Aviation humidity sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_name = "LSZI Humidity"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_aviation_lszi_humidity"

    @property
    def native_value(self) -> float | None:
        """Return the humidity."""
        aviation = self.coordinator.data.get("aviation", {})
        weather = aviation.get("weather", {})
        return weather.get("humidity")


class FiftyOneAviationPressureSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Aviation pressure (QNH) sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ATMOSPHERIC_PRESSURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPressure.HPA
    _attr_name = "LSZI Pressure"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_aviation_lszi_pressure"

    @property
    def native_value(self) -> float | None:
        """Return the pressure."""
        aviation = self.coordinator.data.get("aviation", {})
        weather = aviation.get("weather", {})
        return weather.get("hpa")


class FiftyOneAviationWindSpeedSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Aviation wind speed sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.WIND_SPEED
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfSpeed.KNOTS
    _attr_name = "LSZI Wind Speed"
    _attr_icon = "mdi:weather-windy"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_aviation_lszi_wind_speed"

    @property
    def native_value(self) -> float | None:
        """Return the wind speed in knots."""
        aviation = self.coordinator.data.get("aviation", {})
        weather = aviation.get("weather", {})
        return weather.get("wind_kt")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        aviation = self.coordinator.data.get("aviation", {})
        weather = aviation.get("weather", {})
        attrs = {}
        if weather.get("wind_kmh") is not None:
            attrs["wind_kmh"] = weather["wind_kmh"]
        if weather.get("gust_kt") is not None:
            attrs["gust_kt"] = weather["gust_kt"]
        if weather.get("gust_kmh") is not None:
            attrs["gust_kmh"] = weather["gust_kmh"]
        return attrs


class FiftyOneAviationWindDirectionSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Aviation wind direction sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = DEGREE
    _attr_name = "LSZI Wind Direction"
    _attr_icon = "mdi:compass"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_aviation_lszi_wind_dir"

    @property
    def native_value(self) -> int | None:
        """Return the wind direction in degrees."""
        aviation = self.coordinator.data.get("aviation", {})
        weather = aviation.get("weather", {})
        return weather.get("wind_dir")


class FiftyOneAviationCloudBaseSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Aviation cloud base sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "ft"
    _attr_name = "LSZI Cloud Base"
    _attr_icon = "mdi:cloud"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_aviation_lszi_cloud_base"

    @property
    def native_value(self) -> int | None:
        """Return the cloud base in feet."""
        aviation = self.coordinator.data.get("aviation", {})
        weather = aviation.get("weather", {})
        return weather.get("cloud_base")


class FiftyOneAviationDensityAltitudeSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Aviation density altitude sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "ft"
    _attr_name = "LSZI Density Altitude"
    _attr_icon = "mdi:altimeter"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_aviation_lszi_da"

    @property
    def native_value(self) -> float | None:
        """Return the density altitude."""
        aviation = self.coordinator.data.get("aviation", {})
        weather = aviation.get("weather", {})
        return weather.get("da")


class FiftyOneAviationPressureAltitudeSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Aviation pressure altitude sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "ft"
    _attr_name = "LSZI Pressure Altitude"
    _attr_icon = "mdi:altimeter"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_aviation_lszi_pa"

    @property
    def native_value(self) -> float | None:
        """Return the pressure altitude."""
        aviation = self.coordinator.data.get("aviation", {})
        weather = aviation.get("weather", {})
        return weather.get("pa")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        aviation = self.coordinator.data.get("aviation", {})
        weather = aviation.get("weather", {})
        return {
            "field_elevation": weather.get("alt"),
            "valid": weather.get("valid"),
        }


class FiftyOneRunwayStatusSensor(CoordinatorEntity[FiftyOneDataUpdateCoordinator], SensorEntity):
    """Aviation runway status sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_name = "LSZI Runway Status"
    _attr_icon = "mdi:runway"

    def __init__(
        self,
        coordinator: FiftyOneDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_aviation_lszi_runway"

    @property
    def native_value(self) -> str | None:
        """Return the runway status text."""
        aviation = self.coordinator.data.get("aviation", {})
        runway = aviation.get("runway", {})
        status = runway.get("status")
        if status is not None:
            # Map status codes to human-readable text
            status_map = {
                0: "Closed",
                1: "Open",
                2: "PPR",  # Prior Permission Required
            }
            return status_map.get(status, f"Status {status}")
        return runway.get("text")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        aviation = self.coordinator.data.get("aviation", {})
        runway = aviation.get("runway", {})
        return {
            "status_code": runway.get("status"),
            "altitude": runway.get("altitude"),
            "additional": runway.get("additional"),
            "text": runway.get("text"),
        }
