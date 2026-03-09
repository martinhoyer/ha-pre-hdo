"""Tests for PRE Distribuce sensor entities."""

from datetime import date, datetime, time

from custom_components.pre_hdo.const import PRAGUE_TZ
from custom_components.pre_hdo.coordinator import HdoData
from custom_components.pre_hdo.parser import HdoDaySchedule, HdoPeriod

WEEKDAY_PERIODS = [
    HdoPeriod(tariff="VT", start=time(0, 0), end=time(1, 0)),
    HdoPeriod(tariff="NT", start=time(1, 0), end=time(6, 0)),
    HdoPeriod(tariff="VT", start=time(6, 0), end=time(13, 0)),
    HdoPeriod(tariff="NT", start=time(13, 0), end=time(16, 0)),
    HdoPeriod(tariff="VT", start=time(16, 0), end=time(0, 0)),
]

SAMPLE_SCHEDULES = [
    HdoDaySchedule(
        date_label="pondělí 10.03. - pátek 14.03.",
        dates=[date(2026, 3, d) for d in range(10, 15)],
        periods=WEEKDAY_PERIODS,
    ),
]


class TestSensorValues:
    """Test sensor value extraction from HdoData."""

    def test_minutes_to_low_tariff_during_high(self) -> None:
        data = HdoData(
            schedules=SAMPLE_SCHEDULES,
            current_tariff="VT",
            is_low_tariff=False,
            next_low_tariff_start=datetime(2026, 3, 10, 13, 0, tzinfo=PRAGUE_TZ),
            next_high_tariff_start=datetime(2026, 3, 10, 16, 0, tzinfo=PRAGUE_TZ),
            minutes_to_next_change=180,
            minutes_to_low_tariff=180,
            minutes_to_high_tariff=0,
        )
        assert data.minutes_to_low_tariff == 180

    def test_minutes_to_low_tariff_during_low(self) -> None:
        data = HdoData(
            schedules=SAMPLE_SCHEDULES,
            current_tariff="NT",
            is_low_tariff=True,
            next_low_tariff_start=datetime(2026, 3, 10, 13, 0, tzinfo=PRAGUE_TZ),
            next_high_tariff_start=datetime(2026, 3, 10, 6, 0, tzinfo=PRAGUE_TZ),
            minutes_to_next_change=120,
            minutes_to_low_tariff=0,
            minutes_to_high_tariff=120,
        )
        assert data.minutes_to_low_tariff == 0

    def test_next_low_tariff_start(self) -> None:
        expected = datetime(2026, 3, 10, 13, 0, tzinfo=PRAGUE_TZ)
        data = HdoData(
            schedules=SAMPLE_SCHEDULES,
            current_tariff="VT",
            is_low_tariff=False,
            next_low_tariff_start=expected,
            next_high_tariff_start=datetime(2026, 3, 10, 16, 0, tzinfo=PRAGUE_TZ),
            minutes_to_next_change=180,
            minutes_to_low_tariff=180,
            minutes_to_high_tariff=0,
        )
        assert data.next_low_tariff_start == expected

    def test_next_high_tariff_start(self) -> None:
        expected = datetime(2026, 3, 10, 6, 0, tzinfo=PRAGUE_TZ)
        data = HdoData(
            schedules=SAMPLE_SCHEDULES,
            current_tariff="NT",
            is_low_tariff=True,
            next_low_tariff_start=datetime(2026, 3, 10, 13, 0, tzinfo=PRAGUE_TZ),
            next_high_tariff_start=expected,
            minutes_to_next_change=180,
            minutes_to_low_tariff=0,
            minutes_to_high_tariff=180,
        )
        assert data.next_high_tariff_start == expected

    def test_no_data(self) -> None:
        data = HdoData()
        assert data.minutes_to_low_tariff == 0
        assert data.minutes_to_high_tariff == 0
        assert data.current_tariff is None
        assert data.next_low_tariff_start is None
        assert data.next_high_tariff_start is None
