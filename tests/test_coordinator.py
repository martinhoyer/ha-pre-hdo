"""Tests for PRE Distribuce DataUpdateCoordinator."""

from datetime import time

from custom_components.pre_hdo.coordinator import process_periods
from custom_components.pre_hdo.parser import HdoPeriod

SAMPLE_PERIODS = [
    HdoPeriod(tariff="VT", start=time(0, 0), end=time(1, 0)),
    HdoPeriod(tariff="NT", start=time(1, 0), end=time(6, 0)),
    HdoPeriod(tariff="VT", start=time(6, 0), end=time(13, 0)),
    HdoPeriod(tariff="NT", start=time(13, 0), end=time(16, 0)),
    HdoPeriod(tariff="VT", start=time(16, 0), end=time(0, 0)),
]


class TestProcessPeriods:
    def test_during_low_tariff(self) -> None:
        data = process_periods(SAMPLE_PERIODS, time(3, 0))
        assert data.current_tariff == "NT"
        assert data.is_low_tariff is True
        assert data.minutes_to_next_change == 180

    def test_during_high_tariff(self) -> None:
        data = process_periods(SAMPLE_PERIODS, time(10, 0))
        assert data.current_tariff == "VT"
        assert data.is_low_tariff is False
        assert data.minutes_to_next_change == 180

    def test_evening_high_tariff_to_midnight(self) -> None:
        data = process_periods(SAMPLE_PERIODS, time(20, 0))
        assert data.current_tariff == "VT"
        assert data.minutes_to_next_change == 240

    def test_today_periods_stored(self) -> None:
        data = process_periods(SAMPLE_PERIODS, time(12, 0))
        assert data.periods == SAMPLE_PERIODS
        assert len(data.periods) == 5

    def test_empty_periods(self) -> None:
        data = process_periods([], time(12, 0))
        assert data.current_tariff is None
        assert data.is_low_tariff is False
        assert data.minutes_to_next_change == 0
        assert data.periods == []

    def test_low_tariff_remaining_minutes(self) -> None:
        data = process_periods(SAMPLE_PERIODS, time(14, 0))
        assert data.current_tariff == "NT"
        assert data.minutes_to_low_tariff == 0
        assert data.minutes_to_high_tariff == 120

    def test_high_tariff_remaining_minutes(self) -> None:
        data = process_periods(SAMPLE_PERIODS, time(10, 0))
        assert data.current_tariff == "VT"
        assert data.minutes_to_low_tariff == 180
        assert data.minutes_to_high_tariff == 0
