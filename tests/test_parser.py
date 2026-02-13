"""Tests for HDO HTML parser."""

from datetime import time

from custom_components.pre_hdo.parser import (
    get_current_tariff,
    get_time_remaining,
    parse_hdo_periods,
)


class TestParseHdoPeriods:
    def test_parses_periods_from_html(self, sample_hdo_html) -> None:
        periods = parse_hdo_periods(sample_hdo_html)
        assert len(periods) == 5

    def test_first_period_is_high_tariff(self, sample_hdo_html) -> None:
        periods = parse_hdo_periods(sample_hdo_html)
        assert periods[0].tariff == "VT"
        assert periods[0].start == time(0, 0)
        assert periods[0].end == time(1, 0)

    def test_second_period_is_low_tariff(self, sample_hdo_html) -> None:
        periods = parse_hdo_periods(sample_hdo_html)
        assert periods[1].tariff == "NT"
        assert periods[1].start == time(1, 0)
        assert periods[1].end == time(6, 0)

    def test_last_period_ends_at_midnight(self, sample_hdo_html) -> None:
        periods = parse_hdo_periods(sample_hdo_html)
        assert periods[-1].tariff == "VT"
        assert periods[-1].start == time(16, 0)
        assert periods[-1].end == time(0, 0)

    def test_empty_html_returns_empty_list(self) -> None:
        assert parse_hdo_periods("") == []

    def test_malformed_html_returns_empty_list(self) -> None:
        assert parse_hdo_periods("<div>no data</div>") == []


class TestGetCurrentTariff:
    def test_during_high_tariff_morning(self, sample_hdo_html) -> None:
        periods = parse_hdo_periods(sample_hdo_html)
        tariff = get_current_tariff(periods, time(0, 30))
        assert tariff == "VT"

    def test_during_low_tariff_night(self, sample_hdo_html) -> None:
        periods = parse_hdo_periods(sample_hdo_html)
        tariff = get_current_tariff(periods, time(3, 0))
        assert tariff == "NT"

    def test_during_low_tariff_afternoon(self, sample_hdo_html) -> None:
        periods = parse_hdo_periods(sample_hdo_html)
        tariff = get_current_tariff(periods, time(14, 0))
        assert tariff == "NT"

    def test_during_high_tariff_evening(self, sample_hdo_html) -> None:
        periods = parse_hdo_periods(sample_hdo_html)
        tariff = get_current_tariff(periods, time(20, 0))
        assert tariff == "VT"

    def test_at_exact_boundary(self, sample_hdo_html) -> None:
        periods = parse_hdo_periods(sample_hdo_html)
        tariff = get_current_tariff(periods, time(6, 0))
        assert tariff == "VT"

    def test_empty_periods_returns_none(self) -> None:
        assert get_current_tariff([], time(12, 0)) is None


class TestGetTimeRemaining:
    def test_time_remaining_in_high_tariff(self, sample_hdo_html) -> None:
        """At 00:30, high tariff until 01:00 = 30 min remaining."""
        periods = parse_hdo_periods(sample_hdo_html)
        remaining = get_time_remaining(periods, time(0, 30))
        assert remaining == 30

    def test_time_remaining_in_low_tariff(self, sample_hdo_html) -> None:
        """At 03:00, low tariff until 06:00 = 180 min remaining."""
        periods = parse_hdo_periods(sample_hdo_html)
        remaining = get_time_remaining(periods, time(3, 0))
        assert remaining == 180

    def test_time_remaining_last_period_crosses_midnight(self, sample_hdo_html) -> None:
        """At 20:00, high tariff until 00:00 = 240 min remaining."""
        periods = parse_hdo_periods(sample_hdo_html)
        remaining = get_time_remaining(periods, time(20, 0))
        assert remaining == 240

    def test_empty_periods_returns_zero(self) -> None:
        assert get_time_remaining([], time(12, 0)) == 0
