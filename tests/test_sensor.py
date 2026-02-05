"""Tests for the FiftyOne sensor platform."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.fiftyone.sensor import (
    FiftyOneAviationCloudBaseSensor,
    FiftyOneAviationDensityAltitudeSensor,
    FiftyOneAviationHumiditySensor,
    FiftyOneAviationPressureAltitudeSensor,
    FiftyOneAviationPressureSensor,
    FiftyOneAviationTemperatureSensor,
    FiftyOneAviationWindDirectionSensor,
    FiftyOneAviationWindSpeedSensor,
    FiftyOneRunwayStatusSensor,
    FiftyOneStockPriceSensor,
    FiftyOneStockQuantitySensor,
    FiftyOneStockValueSensor,
)


@pytest.fixture
def mock_coordinator(
    mock_stocks_response: list[dict],
    mock_aviation_response: dict,
) -> MagicMock:
    """Return a mock coordinator with data."""
    coordinator = MagicMock()
    coordinator.data = {
        "stocks": mock_stocks_response,
        "aviation": mock_aviation_response,
    }
    return coordinator


@pytest.fixture
def mock_entry() -> MagicMock:
    """Return a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry"
    return entry


class TestStockSensors:
    """Tests for stock sensors."""

    def test_stock_price_sensor(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test stock price sensor."""
        sensor = FiftyOneStockPriceSensor(mock_coordinator, mock_entry, "AAPL")

        assert sensor.native_value == 150.00
        assert sensor.name == "AAPL Price"
        assert sensor.unique_id == "test_entry_stock_AAPL_price"

    def test_stock_value_sensor(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test stock value sensor."""
        sensor = FiftyOneStockValueSensor(mock_coordinator, mock_entry, "AAPL")

        assert sensor.native_value == 1500.00
        assert sensor.name == "AAPL Value"

        attrs = sensor.extra_state_attributes
        assert attrs["name"] == "Apple Inc."
        assert attrs["symbol"] == "AAPL"
        assert attrs["quantity"] == 10
        assert attrs["price"] == 150.00

    def test_stock_quantity_sensor(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test stock quantity sensor."""
        sensor = FiftyOneStockQuantitySensor(mock_coordinator, mock_entry, "AAPL")

        assert sensor.native_value == 10
        assert sensor.name == "AAPL Quantity"

    def test_stock_sensor_unknown_symbol(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test stock sensor with unknown symbol."""
        sensor = FiftyOneStockPriceSensor(mock_coordinator, mock_entry, "UNKNOWN")

        assert sensor.native_value is None


class TestAviationSensors:
    """Tests for aviation sensors."""

    def test_temperature_sensor(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test aviation temperature sensor."""
        sensor = FiftyOneAviationTemperatureSensor(mock_coordinator, mock_entry)

        assert sensor.native_value == 15.5
        assert sensor.name == "LSZI Temperature"

        attrs = sensor.extra_state_attributes
        assert attrs["dewpoint"] == 8.0
        assert attrs["spread"] == 7.5

    def test_humidity_sensor(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test aviation humidity sensor."""
        sensor = FiftyOneAviationHumiditySensor(mock_coordinator, mock_entry)

        assert sensor.native_value == 65.0
        assert sensor.name == "LSZI Humidity"

    def test_pressure_sensor(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test aviation pressure sensor."""
        sensor = FiftyOneAviationPressureSensor(mock_coordinator, mock_entry)

        assert sensor.native_value == 1013.25
        assert sensor.name == "LSZI Pressure"

    def test_wind_speed_sensor(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test aviation wind speed sensor."""
        sensor = FiftyOneAviationWindSpeedSensor(mock_coordinator, mock_entry)

        assert sensor.native_value == 8.1
        assert sensor.name == "LSZI Wind Speed"

        attrs = sensor.extra_state_attributes
        assert attrs["wind_kmh"] == 15.0
        assert attrs["gust_kt"] == 13.5
        assert attrs["gust_kmh"] == 25.0

    def test_wind_direction_sensor(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test aviation wind direction sensor."""
        sensor = FiftyOneAviationWindDirectionSensor(mock_coordinator, mock_entry)

        assert sensor.native_value == 270
        assert sensor.name == "LSZI Wind Direction"

    def test_cloud_base_sensor(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test aviation cloud base sensor."""
        sensor = FiftyOneAviationCloudBaseSensor(mock_coordinator, mock_entry)

        assert sensor.native_value == 3500
        assert sensor.name == "LSZI Cloud Base"

    def test_density_altitude_sensor(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test aviation density altitude sensor."""
        sensor = FiftyOneAviationDensityAltitudeSensor(mock_coordinator, mock_entry)

        assert sensor.native_value == 2100
        assert sensor.name == "LSZI Density Altitude"

    def test_pressure_altitude_sensor(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test aviation pressure altitude sensor."""
        sensor = FiftyOneAviationPressureAltitudeSensor(mock_coordinator, mock_entry)

        assert sensor.native_value == 1650
        assert sensor.name == "LSZI Pressure Altitude"

        attrs = sensor.extra_state_attributes
        assert attrs["field_elevation"] == 1575
        assert attrs["valid"] is True


class TestRunwaySensor:
    """Tests for runway status sensor."""

    def test_runway_status_open(
        self, mock_coordinator: MagicMock, mock_entry: MagicMock
    ) -> None:
        """Test runway status sensor when open."""
        sensor = FiftyOneRunwayStatusSensor(mock_coordinator, mock_entry)

        assert sensor.native_value == "Open"
        assert sensor.name == "LSZI Runway Status"

        attrs = sensor.extra_state_attributes
        assert attrs["status_code"] == 1
        assert attrs["altitude"] == 1575
        assert attrs["text"] == "Runway open"

    def test_runway_status_closed(self, mock_entry: MagicMock) -> None:
        """Test runway status sensor when closed."""
        coordinator = MagicMock()
        coordinator.data = {
            "aviation": {
                "runway": {"status": 0, "altitude": 1575},
            }
        }

        sensor = FiftyOneRunwayStatusSensor(coordinator, mock_entry)

        assert sensor.native_value == "Closed"

    def test_runway_status_ppr(self, mock_entry: MagicMock) -> None:
        """Test runway status sensor when PPR."""
        coordinator = MagicMock()
        coordinator.data = {
            "aviation": {
                "runway": {"status": 2, "altitude": 1575},
            }
        }

        sensor = FiftyOneRunwayStatusSensor(coordinator, mock_entry)

        assert sensor.native_value == "PPR"

    def test_runway_status_unknown(self, mock_entry: MagicMock) -> None:
        """Test runway status sensor with unknown status code."""
        coordinator = MagicMock()
        coordinator.data = {
            "aviation": {
                "runway": {"status": 99, "altitude": 1575},
            }
        }

        sensor = FiftyOneRunwayStatusSensor(coordinator, mock_entry)

        assert sensor.native_value == "Status 99"

    def test_runway_status_empty_data(self, mock_entry: MagicMock) -> None:
        """Test runway status sensor with empty data."""
        coordinator = MagicMock()
        coordinator.data = {"aviation": {}}

        sensor = FiftyOneRunwayStatusSensor(coordinator, mock_entry)

        assert sensor.native_value is None
