"""Parser for PRE Distribuce HDO HTML responses."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import time

TARIFF_PATTERN = re.compile(r'class="hdo(nt|vt)"')
TIME_RANGE_PATTERN = re.compile(r'title="(\d{2}:\d{2}) - (\d{2}:\d{2})"')


@dataclass(frozen=True)
class HdoPeriod:
    """A single tariff period with start/end times."""

    tariff: str  # "NT" (low) or "VT" (high)
    start: time
    end: time


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
