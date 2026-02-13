"""Config flow for PRE Distribuce integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import PreHdoApiClient
from .const import CONF_RECEIVER_COMMAND_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_RECEIVER_COMMAND_ID): str,
    }
)


class PreHdoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PRE Distribuce."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            command_id = user_input[CONF_RECEIVER_COMMAND_ID].strip()

            # Check if already configured with this command ID
            await self.async_set_unique_id(f"pre-hdo_{command_id}")
            self._abort_if_unique_id_configured()

            # Validate the command ID against the API
            session = async_get_clientsession(self.hass)
            client = PreHdoApiClient(session=session)
            valid = await client.async_validate_command_id(command_id)

            if valid:
                return self.async_create_entry(
                    title=f"PRE Distribuce HDO {command_id}",
                    data={CONF_RECEIVER_COMMAND_ID: command_id},
                )
            errors["base"] = "invalid_command_id"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
