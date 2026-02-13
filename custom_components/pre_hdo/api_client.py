"""Async API client for PRE Distribuce HDO data."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from aiohttp import ClientError, ClientSession

from .const import HDO_ONE_DAY_URL
from .parser import HdoPeriod, parse_hdo_periods

_LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30


class PreHdoApiError(Exception):
    """Error communicating with PRE Distribuce API."""


class PreHdoApiClient:
    """Async client for the PRE Distribuce HDO AJAX API."""

    def __init__(self, session: ClientSession) -> None:
        self._session = session

    async def async_get_hdo_periods(
        self, command_id: str, date_str: str | None = None
    ) -> list[HdoPeriod]:
        """Fetch HDO periods for a given receiver command ID and date.

        Args:
            command_id: The HDO receiver command code (e.g. "492").
            date_str: Date in DD.MM.YYYY format. Defaults to today.

        Returns:
            List of HdoPeriod for the requested day.

        Raises:
            PreHdoApiError: On HTTP or parsing errors.

        """
        if date_str is None:
            today = datetime.now(tz=UTC).date()
            date_str = today.strftime("%d.%m.%Y")

        data = {
            "datum": date_str,
            "povel": command_id,
            "povelTitle": command_id,
        }

        try:
            async with self._session.post(
                HDO_ONE_DAY_URL,
                data=data,
                timeout=REQUEST_TIMEOUT,
            ) as resp:
                resp.raise_for_status()
                result = await resp.json(content_type=None)
        except ClientError as err:
            msg = f"Error fetching HDO data: {err}"
            raise PreHdoApiError(msg) from err
        except (ValueError, KeyError) as err:
            msg = f"Invalid response from PRE Distribuce: {err}"
            raise PreHdoApiError(msg) from err

        html = result.get("html", "")
        return parse_hdo_periods(html)

    async def async_validate_command_id(self, command_id: str) -> bool:
        """Validate that a receiver command ID returns HDO data."""
        try:
            periods = await self.async_get_hdo_periods(command_id)
            return len(periods) > 0
        except PreHdoApiError:
            return False
