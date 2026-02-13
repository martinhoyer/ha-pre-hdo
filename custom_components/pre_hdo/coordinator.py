"""DataUpdateCoordinator for PRE Distribuce."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, time, timedelta
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import PreHdoApiClient, PreHdoApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .parser import HdoPeriod, get_current_tariff, get_time_remaining

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


@dataclass
class HdoData:
    """Processed HDO data for entity consumption."""

    periods: list[HdoPeriod] = field(default_factory=list)
    current_tariff: str | None = None
    is_low_tariff: bool = False
    minutes_to_next_change: int = 0
    minutes_to_low_tariff: int = 0
    minutes_to_high_tariff: int = 0


def process_periods(periods: list[HdoPeriod], now: time) -> HdoData:
    """Process raw periods into HdoData for the current time."""
    if not periods:
        return HdoData()

    current_tariff = get_current_tariff(periods, now)
    remaining = get_time_remaining(periods, now)

    if current_tariff == "NT":
        minutes_to_low = 0
        minutes_to_high = remaining
    elif current_tariff == "VT":
        minutes_to_high = 0
        current_idx = _find_current_index(periods, now)
        minutes_to_low = remaining
        for i in range(current_idx + 1, len(periods)):
            if periods[i].tariff == "NT":
                break
            minutes_to_low += _period_duration(periods[i])
    else:
        minutes_to_low = 0
        minutes_to_high = 0

    return HdoData(
        periods=periods,
        current_tariff=current_tariff,
        is_low_tariff=current_tariff == "NT",
        minutes_to_next_change=remaining,
        minutes_to_low_tariff=minutes_to_low,
        minutes_to_high_tariff=minutes_to_high,
    )


def _find_current_index(periods: list[HdoPeriod], now: time) -> int:
    """Find the index of the period containing the given time."""
    for i, period in enumerate(periods):
        if period.end == time(0, 0):
            if now >= period.start:
                return i
        elif period.start <= now < period.end:
            return i
    return -1


def _period_duration(period: HdoPeriod) -> int:
    """Return duration of a period in minutes."""
    if period.end == time(0, 0):
        return 24 * 60 - (period.start.hour * 60 + period.start.minute)
    return (period.end.hour * 60 + period.end.minute) - (
        period.start.hour * 60 + period.start.minute
    )


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
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client
        self.command_id = command_id

    async def _async_update_data(self) -> HdoData:
        """Fetch and process HDO data."""
        try:
            periods = await self.client.async_get_hdo_periods(self.command_id)
        except PreHdoApiError as err:
            msg = f"Error fetching HDO data: {err}"
            raise UpdateFailed(msg) from err

        now = datetime.now(tz=UTC).time()
        return process_periods(periods, now)
