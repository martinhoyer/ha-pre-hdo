"""Tests for PRE Distribuce sensor entities."""

from datetime import time

from custom_components.pre_hdo.coordinator import HdoData
from custom_components.pre_hdo.parser import HdoPeriod

SAMPLE_PERIODS = [
    HdoPeriod(tariff="VT", start=time(0, 0), end=time(1, 0)),
    HdoPeriod(tariff="NT", start=time(1, 0), end=time(6, 0)),
    HdoPeriod(tariff="VT", start=time(6, 0), end=time(13, 0)),
    HdoPeriod(tariff="NT", start=time(13, 0), end=time(16, 0)),
    HdoPeriod(tariff="VT", start=time(16, 0), end=time(0, 0)),
]


class TestSensorValues:
    """Test sensor value extraction from HdoData."""

    def test_minutes_to_low_tariff_during_high(self) -> None:
        data = HdoData(
            periods=SAMPLE_PERIODS,
            current_tariff="VT",
            is_low_tariff=False,
            minutes_to_next_change=180,
            minutes_to_low_tariff=180,
            minutes_to_high_tariff=0,
        )
        assert data.minutes_to_low_tariff == 180

    def test_minutes_to_low_tariff_during_low(self) -> None:
        data = HdoData(
            periods=SAMPLE_PERIODS,
            current_tariff="NT",
            is_low_tariff=True,
            minutes_to_next_change=120,
            minutes_to_low_tariff=0,
            minutes_to_high_tariff=120,
        )
        assert data.minutes_to_low_tariff == 0

    def test_minutes_to_high_tariff_during_low(self) -> None:
        data = HdoData(
            periods=SAMPLE_PERIODS,
            current_tariff="NT",
            is_low_tariff=True,
            minutes_to_next_change=120,
            minutes_to_low_tariff=0,
            minutes_to_high_tariff=120,
        )
        assert data.minutes_to_high_tariff == 120

    def test_no_data(self) -> None:
        data = HdoData()
        assert data.minutes_to_low_tariff == 0
        assert data.minutes_to_high_tariff == 0
        assert data.current_tariff is None
