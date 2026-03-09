"""Tests for HDO HTML parser."""

from datetime import date, time

from custom_components.pre_hdo.parser import (
    HdoDaySchedule,
    get_current_tariff,
    get_time_remaining,
    parse_hdo_multi_day,
    parse_hdo_periods,
)

SAMPLE_MULTI_DAY_HTML = (
    '<div class="hdo-bar">'
    '<div class="blue-text pull-left">pondělí 09.03. - pátek 13.03.</div>'
    '<div class="overflow-bar"></div>'
    '<span style="left: 0.00%;" class="hdovt"></span>'
    '<span style="left: 0.00%;" class="span-overflow" title="00:00 - 01:00"></span>'
    '<span style="left: 4.17%;" class="hdont"></span>'
    '<span style="left: 4.17%;" class="span-overflow" title="01:00 - 06:00"></span>'
    '<span style="left: 25.00%;" class="hdovt"></span>'
    '<span style="left: 25.00%;" class="span-overflow" title="06:00 - 13:00"></span>'
    '<span style="left: 54.17%;" class="hdont"></span>'
    '<span style="left: 54.17%;" class="span-overflow" title="13:00 - 16:00"></span>'
    '<span style="left: 66.67%;" class="hdovt"></span>'
    '<span style="left: 66.67%;" class="span-overflow" title="16:00 - 00:00"></span>'
    "</div>"
    '<div class="hdo-bar">'
    '<div class="blue-text pull-left">sobota 14.03.</div>'
    '<div class="overflow-bar"></div>'
    '<span style="left: 0.00%;" class="hdovt"></span>'
    '<span style="left: 0.00%;" class="span-overflow" title="00:00 - 03:00"></span>'
    '<span style="left: 12.50%;" class="hdont"></span>'
    '<span style="left: 12.50%;" class="span-overflow" title="03:00 - 06:00"></span>'
    '<span style="left: 25.00%;" class="hdovt"></span>'
    '<span style="left: 25.00%;" class="span-overflow" title="06:00 - 13:00"></span>'
    '<span style="left: 54.17%;" class="hdont"></span>'
    '<span style="left: 54.17%;" class="span-overflow" title="13:00 - 18:00"></span>'
    '<span style="left: 75.00%;" class="hdovt"></span>'
    '<span style="left: 75.00%;" class="span-overflow" title="18:00 - 00:00"></span>'
    "</div>"
)


class TestParseHdoMultiDay:
    def test_parses_two_groups(self) -> None:
        schedules = parse_hdo_multi_day(SAMPLE_MULTI_DAY_HTML, 2026)
        assert len(schedules) == 2

    def test_weekday_range_expands_dates(self) -> None:
        schedules = parse_hdo_multi_day(SAMPLE_MULTI_DAY_HTML, 2026)
        weekday_schedule = schedules[0]
        assert weekday_schedule.dates == [
            date(2026, 3, 9),
            date(2026, 3, 10),
            date(2026, 3, 11),
            date(2026, 3, 12),
            date(2026, 3, 13),
        ]

    def test_single_day_has_one_date(self) -> None:
        schedules = parse_hdo_multi_day(SAMPLE_MULTI_DAY_HTML, 2026)
        saturday_schedule = schedules[1]
        assert saturday_schedule.dates == [date(2026, 3, 14)]

    def test_weekday_periods(self) -> None:
        schedules = parse_hdo_multi_day(SAMPLE_MULTI_DAY_HTML, 2026)
        periods = schedules[0].periods
        assert len(periods) == 5
        assert periods[0].tariff == "VT"
        assert periods[1].tariff == "NT"
        assert periods[1].start == time(1, 0)
        assert periods[1].end == time(6, 0)

    def test_saturday_periods_differ(self) -> None:
        schedules = parse_hdo_multi_day(SAMPLE_MULTI_DAY_HTML, 2026)
        periods = schedules[1].periods
        assert len(periods) == 5
        assert periods[1].tariff == "NT"
        assert periods[1].start == time(3, 0)
        assert periods[1].end == time(6, 0)

    def test_preserves_date_label(self) -> None:
        schedules = parse_hdo_multi_day(SAMPLE_MULTI_DAY_HTML, 2026)
        assert "09.03" in schedules[0].date_label
        assert "13.03" in schedules[0].date_label
        assert "14.03" in schedules[1].date_label

    def test_empty_html_returns_empty(self) -> None:
        assert parse_hdo_multi_day("", 2026) == []

    def test_year_end_boundary(self) -> None:
        """Schedule spanning Dec into Jan uses correct years."""
        html = (
            '<div class="hdo-bar">'
            '<div class="blue-text pull-left">pondělí 30.12. - pátek 03.01.</div>'
            '<div class="overflow-bar"></div>'
            '<span style="left: 0.00%;" class="hdovt"></span>'
            '<span style="left: 0.00%;" class="span-overflow" title="00:00 - 06:00"></span>'
            '<span style="left: 25.00%;" class="hdont"></span>'
            '<span style="left: 25.00%;" class="span-overflow" title="06:00 - 00:00"></span>'
            "</div>"
        )
        schedules = parse_hdo_multi_day(html, 2026)
        dates = schedules[0].dates
        assert dates[0] == date(2026, 12, 30)
        assert dates[-1] == date(2027, 1, 3)


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
