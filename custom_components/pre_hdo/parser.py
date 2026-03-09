"""Parser for PRE Distribuce HDO HTML responses."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, time, timedelta

TARIFF_PATTERN = re.compile(r'class="hdo(nt|vt)"')
TIME_RANGE_PATTERN = re.compile(r'title="(\d{2}:\d{2}) - (\d{2}:\d{2})"')
DATE_LABEL_PATTERN = re.compile(r'class="blue-text pull-left">([^<]+)</div>')
DATE_RANGE_PATTERN = re.compile(r"(\d{2})\.(\d{2})\.")
HDO_BAR_PATTERN = re.compile(
    r'<div class="hdo-bar">(.*?)</div>\s*(?=<div class="hdo-bar">|<script|$)',
    re.DOTALL,
)


@dataclass(frozen=True)
class HdoPeriod:
    """A single tariff period with start/end times."""

    tariff: str  # "NT" (low) or "VT" (high)
    start: time
    end: time


@dataclass(frozen=True)
class HdoDaySchedule:
    """A schedule group covering one or more days with identical tariff periods."""

    date_label: str
    dates: list[date]
    periods: list[HdoPeriod]


def parse_hdo_periods(html: str) -> list[HdoPeriod]:
    """Parse HDO periods from the AJAX HTML response.

    Returns list of HdoPeriod sorted by start time.
    """
    tariffs = TARIFF_PATTERN.findall(html)
    time_ranges = TIME_RANGE_PATTERN.findall(html)

    if not tariffs or not time_ranges or len(tariffs) != len(time_ranges):
        return []

    periods: list[HdoPeriod] = []
    for tariff_code, (start_str, end_str) in zip(tariffs, time_ranges, strict=False):
        tariff = "NT" if tariff_code == "nt" else "VT"
        start = time.fromisoformat(start_str)
        end = time.fromisoformat(end_str)
        periods.append(HdoPeriod(tariff=tariff, start=start, end=end))

    return periods


def get_current_tariff(periods: list[HdoPeriod], now: time) -> str | None:
    """Return the current tariff code ("NT" or "VT") at the given time."""
    if not periods:
        return None

    for period in periods:
        if period.end == time(0, 0):
            # Period crosses midnight: active from start until 23:59:59
            if now >= period.start:
                return period.tariff
        elif period.start <= now < period.end:
            return period.tariff

    return periods[-1].tariff


def get_time_remaining(periods: list[HdoPeriod], now: time) -> int:
    """Return minutes remaining in the current tariff period."""
    if not periods:
        return 0

    for period in periods:
        in_period = False
        if period.end == time(0, 0):
            in_period = now >= period.start
        else:
            in_period = period.start <= now < period.end

        if in_period:
            if period.end == time(0, 0):
                # Minutes until midnight
                now_minutes = now.hour * 60 + now.minute
                return 24 * 60 - now_minutes
            end_minutes = period.end.hour * 60 + period.end.minute
            now_minutes = now.hour * 60 + now.minute
            return end_minutes - now_minutes

    return 0


def _expand_date_range(label: str, year: int) -> list[date]:
    """Expand a date label into a list of dates.

    Handles both single dates ("sobota 14.03.") and ranges
    ("pondělí 09.03. - pátek 13.03.").
    """
    matches = DATE_RANGE_PATTERN.findall(label)
    if not matches:
        return []

    if len(matches) == 1:
        day, month = int(matches[0][0]), int(matches[0][1])
        return [date(year, month, day)]

    start_day, start_month = int(matches[0][0]), int(matches[0][1])
    end_day, end_month = int(matches[1][0]), int(matches[1][1])

    end_year = year
    if end_month < start_month:
        end_year = year + 1

    start_date = date(year, start_month, start_day)
    end_date = date(end_year, end_month, end_day)

    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates


def parse_hdo_multi_day(html: str, year: int) -> list[HdoDaySchedule]:
    """Parse multi-day HDO response into a list of day schedules."""
    bars = HDO_BAR_PATTERN.findall(html)
    if not bars:
        return []

    schedules: list[HdoDaySchedule] = []
    for bar_html in bars:
        label_match = DATE_LABEL_PATTERN.search(bar_html)
        if not label_match:
            continue

        label = label_match.group(1).strip()
        dates = _expand_date_range(label, year)
        periods = parse_hdo_periods(bar_html)

        if dates and periods:
            schedules.append(
                HdoDaySchedule(date_label=label, dates=dates, periods=periods)
            )

    return schedules
