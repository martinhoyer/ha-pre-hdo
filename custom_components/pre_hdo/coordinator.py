"""DataUpdateCoordinator for PRE Distribuce."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING, override

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import PreHdoApiClient, PreHdoApiError
from .const import DOMAIN, PRAGUE_TZ
from .parser import HdoDaySchedule, HdoPeriod, get_current_tariff, get_time_remaining

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

REFRESH_HOUR_START = 14
REFRESH_HOUR_END = 15


@dataclass
class HdoData:
    """Processed HDO data for entity consumption."""

    schedules: list[HdoDaySchedule] = field(default_factory=list)
    current_tariff: str | None = None
    is_low_tariff: bool = False
    next_low_tariff_start: datetime | None = None
    next_high_tariff_start: datetime | None = None
    minutes_to_next_change: int = 0


def _get_periods_for_date(
    schedules: list[HdoDaySchedule],
    target: date,
) -> list[HdoPeriod]:
    """Find the periods applicable to a specific date."""
    for schedule in schedules:
        if target in schedule.dates:
            return schedule.periods
    return []


def _time_in_period(now: time, period: HdoPeriod) -> bool:
    if period.end == time(0, 0):
        return now >= period.start
    return period.start <= now < period.end


def _build_timeline(
    schedules: list[HdoDaySchedule],
    now: datetime,
) -> list[tuple[datetime, str]]:
    """Build a forward-looking timeline of tariff switch points.

    Returns a list of (datetime, tariff) tuples representing the start
    of each tariff period from the current period onward, across days.
    """
    timeline: list[tuple[datetime, str]] = []
    current_date = now.date()

    for day_offset in range(14):
        target_date = current_date + timedelta(days=day_offset)
        periods = _get_periods_for_date(schedules, target_date)
        for period in periods:
            period_start = datetime.combine(
                target_date,
                period.start,
                tzinfo=PRAGUE_TZ,
            )
            if period_start >= now or (
                day_offset == 0 and _time_in_period(now.time(), period)
            ):
                timeline.append((period_start, period.tariff))

    return timeline


def process_periods(
    schedules: list[HdoDaySchedule],
    now: datetime,
) -> HdoData:
    """Process schedules into HdoData for the current datetime."""
    if not schedules:
        return HdoData()

    today_periods = _get_periods_for_date(schedules, now.date())
    current_tariff = get_current_tariff(today_periods, now.time())
    minutes_to_next_change = get_time_remaining(today_periods, now.time())

    timeline = _build_timeline(schedules, now)

    next_low: datetime | None = None
    next_high: datetime | None = None
    skip_first_match_low = current_tariff == "NT"
    skip_first_match_high = current_tariff == "VT"

    for switch_time, tariff in timeline:
        if tariff == "NT" and next_low is None:
            if skip_first_match_low:
                skip_first_match_low = False
                continue
            next_low = switch_time
        elif tariff == "VT" and next_high is None:
            if skip_first_match_high:
                skip_first_match_high = False
                continue
            next_high = switch_time

        if next_low is not None and next_high is not None:
            break

    return HdoData(
        schedules=schedules,
        current_tariff=current_tariff,
        is_low_tariff=current_tariff == "NT",
        next_low_tariff_start=next_low,
        next_high_tariff_start=next_high,
        minutes_to_next_change=minutes_to_next_change,
    )


def _get_daily_refresh_offset(command_id: str) -> int:
    """Get a stable random minute offset (0-59) for daily refresh."""
    h = hashlib.md5(command_id.encode(), usedforsecurity=False)
    return int.from_bytes(h.digest()[:2]) % 60


class PreHdoCoordinator(DataUpdateCoordinator[HdoData]):
    """Coordinator for fetching PRE Distribuce HDO data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: PreHdoApiClient,
        command_id: str,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,
        )
        self.client: PreHdoApiClient = client
        self.command_id: str = command_id
        self._refresh_minute: int = _get_daily_refresh_offset(command_id)

    def get_processed_data(self) -> HdoData:
        """Recompute derived data from stored schedules and current time.

        Entities should use this instead of self.data directly to get
        fresh tariff state that reflects the current time, not the
        last fetch time.
        """
        if self.data is None or not self.data.schedules:
            return self.data or HdoData()
        return process_periods(self.data.schedules, datetime.now(tz=PRAGUE_TZ))

    def _next_refresh_interval(self) -> timedelta:
        """Calculate timedelta until next daily refresh (14:xx Prague time)."""
        now = datetime.now(tz=PRAGUE_TZ)
        target = now.replace(
            hour=REFRESH_HOUR_START,
            minute=self._refresh_minute,
            second=0,
            microsecond=0,
        )
        if target <= now:
            target += timedelta(days=1)
        return target - now

    @override
    async def _async_update_data(self) -> HdoData:
        """Fetch and process HDO data."""
        try:
            schedules = await self.client.async_get_hdo_multi_day(self.command_id)
        except PreHdoApiError as err:
            msg = f"Error fetching HDO data: {err}"
            raise UpdateFailed(msg) from err

        self.update_interval = self._next_refresh_interval()

        now = datetime.now(tz=PRAGUE_TZ)
        return process_periods(schedules, now)
