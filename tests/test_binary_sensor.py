"""Tests for PRE Distribuce binary sensor."""

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


class TestCanApplianceRun:
    """Test the appliance time window logic."""

    def test_low_tariff_enough_time(self) -> None:
        """Appliance needs 30 min, 180 min of NT remain."""
        from custom_components.pre_hdo.binary_sensor import can_appliance_run

        data = HdoData(
            periods=SAMPLE_PERIODS,
            current_tariff="NT",
            is_low_tariff=True,
            minutes_to_next_change=180,
            minutes_to_low_tariff=0,
            minutes_to_high_tariff=180,
        )
        assert can_appliance_run(data, 30) is True

    def test_low_tariff_not_enough_time(self) -> None:
        """Appliance needs 200 min, only 120 min of NT remain."""
        from custom_components.pre_hdo.binary_sensor import can_appliance_run

        data = HdoData(
            periods=SAMPLE_PERIODS,
            current_tariff="NT",
            is_low_tariff=True,
            minutes_to_next_change=120,
            minutes_to_low_tariff=0,
            minutes_to_high_tariff=120,
        )
        assert can_appliance_run(data, 200) is False

    def test_high_tariff_cannot_run(self) -> None:
        """During high tariff, appliance cannot run."""
        from custom_components.pre_hdo.binary_sensor import can_appliance_run

        data = HdoData(
            periods=SAMPLE_PERIODS,
            current_tariff="VT",
            is_low_tariff=False,
            minutes_to_next_change=60,
            minutes_to_low_tariff=60,
            minutes_to_high_tariff=0,
        )
        assert can_appliance_run(data, 30) is False

    def test_no_data(self) -> None:
        """No data available."""
        from custom_components.pre_hdo.binary_sensor import can_appliance_run

        data = HdoData()
        assert can_appliance_run(data, 30) is False
