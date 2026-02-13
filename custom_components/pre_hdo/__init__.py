"""The PRE Distribuce HDO integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import PreHdoApiClient
from .const import CONF_RECEIVER_COMMAND_ID
from .coordinator import PreHdoCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]

type PreHdoConfigEntry = ConfigEntry[PreHdoCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: PreHdoConfigEntry) -> bool:
    """Set up PRE Distribuce HDO from a config entry."""
    session = async_get_clientsession(hass)
    client = PreHdoApiClient(session=session)
    command_id = entry.data[CONF_RECEIVER_COMMAND_ID]

    coordinator = PreHdoCoordinator(hass, client, command_id)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: PreHdoConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
