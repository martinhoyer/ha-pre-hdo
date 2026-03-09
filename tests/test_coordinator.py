"""Tests for PRE Distribuce DataUpdateCoordinator."""

from datetime import date, datetime, time

from custom_components.pre_hdo.const import PRAGUE_TZ
from custom_components.pre_hdo.coordinator import process_periods
from custom_components.pre_hdo.parser import HdoDaySchedule, HdoPeriod

WEEKDAY_PERIODS = [
    HdoPeriod(tariff="VT", start=time(0, 0), end=time(1, 0)),
    HdoPeriod(tariff="NT", start=time(1, 0), end=time(6, 0)),
    HdoPeriod(tariff="VT", start=time(6, 0), end=time(13, 0)),
    HdoPeriod(tariff="NT", start=time(13, 0), end=time(16, 0)),
    HdoPeriod(tariff="VT", start=time(16, 0), end=time(0, 0)),
]

SATURDAY_PERIODS = [
    HdoPeriod(tariff="VT", start=time(0, 0), end=time(3, 0)),
    HdoPeriod(tariff="NT", start=time(3, 0), end=time(6, 0)),
    HdoPeriod(tariff="VT", start=time(6, 0), end=time(13, 0)),
    HdoPeriod(tariff="NT", start=time(13, 0), end=time(18, 0)),
    HdoPeriod(tariff="VT", start=time(18, 0), end=time(0, 0)),
]

SAMPLE_SCHEDULES = [
    HdoDaySchedule(
        date_label="pondělí 10.03. - pátek 14.03.",
        dates=[date(2026, 3, d) for d in range(10, 15)],
        periods=WEEKDAY_PERIODS,
    ),
    HdoDaySchedule(
        date_label="sobota 15.03.",
        dates=[date(2026, 3, 15)],
        periods=SATURDAY_PERIODS,
    ),
]


def _prague_dt(year, month, day, hour, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=PRAGUE_TZ)


class TestProcessPeriods:
    def test_during_low_tariff(self) -> None:
        now = _prague_dt(2026, 3, 10, 3, 0)
        data = process_periods(SAMPLE_SCHEDULES, now)
        assert data.current_tariff == "NT"
        assert data.is_low_tariff is True
        assert data.minutes_to_low_tariff == 0
        assert data.minutes_to_high_tariff == 180

    def test_during_high_tariff(self) -> None:
        now = _prague_dt(2026, 3, 10, 10, 0)
        data = process_periods(SAMPLE_SCHEDULES, now)
        assert data.current_tariff == "VT"
        assert data.is_low_tariff is False
        assert data.minutes_to_high_tariff == 0
        assert data.minutes_to_low_tariff == 180

    def test_next_low_tariff_start_during_high(self) -> None:
        now = _prague_dt(2026, 3, 10, 10, 0)
        data = process_periods(SAMPLE_SCHEDULES, now)
        assert data.next_low_tariff_start == _prague_dt(2026, 3, 10, 13, 0)

    def test_next_high_tariff_start_during_low(self) -> None:
        now = _prague_dt(2026, 3, 10, 3, 0)
        data = process_periods(SAMPLE_SCHEDULES, now)
        assert data.next_high_tariff_start == _prague_dt(2026, 3, 10, 6, 0)

    def test_next_low_start_skips_current_when_active(self) -> None:
        """When NT is active, next_low_tariff_start shows the NEXT NT period."""
        now = _prague_dt(2026, 3, 10, 3, 0)  # In NT 01:00-06:00
        data = process_periods(SAMPLE_SCHEDULES, now)
        assert data.next_low_tariff_start == _prague_dt(2026, 3, 10, 13, 0)

    def test_next_high_start_skips_current_when_active(self) -> None:
        """When VT is active, next_high_tariff_start shows the NEXT VT period."""
        now = _prague_dt(2026, 3, 10, 10, 0)  # In VT 06:00-13:00
        data = process_periods(SAMPLE_SCHEDULES, now)
        assert data.next_high_tariff_start == _prague_dt(2026, 3, 10, 16, 0)

    def test_cross_midnight_next_low(self) -> None:
        """At 20:00 VT (last period), next NT is tomorrow at 01:00."""
        now = _prague_dt(2026, 3, 10, 20, 0)  # In VT 16:00-00:00
        data = process_periods(SAMPLE_SCHEDULES, now)
        assert data.next_low_tariff_start == _prague_dt(2026, 3, 11, 1, 0)

    def test_cross_midnight_to_different_schedule(self) -> None:
        """Friday evening -> Saturday has different schedule."""
        now = _prague_dt(2026, 3, 14, 20, 0)  # Friday VT 16:00-00:00
        data = process_periods(SAMPLE_SCHEDULES, now)
        # Saturday NT starts at 03:00, not 01:00
        assert data.next_low_tariff_start == _prague_dt(2026, 3, 15, 3, 0)

    def test_minutes_to_next_change(self) -> None:
        now = _prague_dt(2026, 3, 10, 0, 30)
        data = process_periods(SAMPLE_SCHEDULES, now)
        assert data.minutes_to_next_change == 30

    def test_evening_minutes_to_next_change(self) -> None:
        now = _prague_dt(2026, 3, 10, 20, 0)
        data = process_periods(SAMPLE_SCHEDULES, now)
        assert data.minutes_to_next_change == 240

    def test_empty_schedules(self) -> None:
        now = _prague_dt(2026, 3, 10, 12, 0)
        data = process_periods([], now)
        assert data.current_tariff is None
        assert data.is_low_tariff is False
        assert data.next_low_tariff_start is None
        assert data.next_high_tariff_start is None

    def test_schedules_stored(self) -> None:
        now = _prague_dt(2026, 3, 10, 12, 0)
        data = process_periods(SAMPLE_SCHEDULES, now)
        assert data.schedules == SAMPLE_SCHEDULES
