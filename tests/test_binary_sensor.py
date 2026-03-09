"""Tests for PRE Distribuce binary sensor."""

from datetime import date, datetime, time
from unittest.mock import patch

from custom_components.pre_hdo.const import PRAGUE_TZ
from custom_components.pre_hdo.coordinator import HdoData
from custom_components.pre_hdo.parser import HdoDaySchedule, HdoPeriod

SAMPLE_PERIODS = [
    HdoPeriod(tariff="VT", start=time(0, 0), end=time(1, 0)),
    HdoPeriod(tariff="NT", start=time(1, 0), end=time(6, 0)),
    HdoPeriod(tariff="VT", start=time(6, 0), end=time(13, 0)),
    HdoPeriod(tariff="NT", start=time(13, 0), end=time(16, 0)),
    HdoPeriod(tariff="VT", start=time(16, 0), end=time(0, 0)),
]

SAMPLE_SCHEDULES = [
    HdoDaySchedule(
        date_label="pondělí 10.03.",
        dates=[date(2026, 3, 10)],
        periods=SAMPLE_PERIODS,
    ),
]


class TestCanApplianceRun:
    """Test the appliance time window logic."""

    def test_low_tariff_enough_time(self) -> None:
        """Appliance needs 30 min, 180 min of NT remain."""
        from custom_components.pre_hdo.binary_sensor import can_appliance_run

        now = datetime(2026, 3, 10, 3, 0, tzinfo=PRAGUE_TZ)
        data = HdoData(
            schedules=[],
            current_tariff="NT",
            is_low_tariff=True,
            next_high_tariff_start=datetime(2026, 3, 10, 6, 0, tzinfo=PRAGUE_TZ),
            minutes_to_next_change=180,
        )
        with patch("custom_components.pre_hdo.binary_sensor.datetime") as mock_dt:
            mock_dt.now.return_value = now
            assert can_appliance_run(data, 30) is True

    def test_low_tariff_not_enough_time(self) -> None:
        """Appliance needs 200 min, only 120 min of NT remain."""
        from custom_components.pre_hdo.binary_sensor import can_appliance_run

        now = datetime(2026, 3, 10, 14, 0, tzinfo=PRAGUE_TZ)
        data = HdoData(
            schedules=[],
            current_tariff="NT",
            is_low_tariff=True,
            next_high_tariff_start=datetime(2026, 3, 10, 16, 0, tzinfo=PRAGUE_TZ),
            minutes_to_next_change=120,
        )
        with patch("custom_components.pre_hdo.binary_sensor.datetime") as mock_dt:
            mock_dt.now.return_value = now
            assert can_appliance_run(data, 200) is False

    def test_high_tariff_cannot_run(self) -> None:
        """During high tariff, appliance cannot run."""
        from custom_components.pre_hdo.binary_sensor import can_appliance_run

        data = HdoData(
            schedules=[],
            current_tariff="VT",
            is_low_tariff=False,
            minutes_to_next_change=60,
        )
        assert can_appliance_run(data, 30) is False

    def test_no_data(self) -> None:
        """No data available."""
        from custom_components.pre_hdo.binary_sensor import can_appliance_run

        data = HdoData()
        assert can_appliance_run(data, 30) is False


class TestBinarySensorAttributes:
    def test_periods_today_from_schedules(self) -> None:
        data = HdoData(
            schedules=SAMPLE_SCHEDULES,
            current_tariff="NT",
            is_low_tariff=True,
            minutes_to_next_change=120,
        )
        assert len(data.schedules) == 1
        assert len(data.schedules[0].periods) == 5
