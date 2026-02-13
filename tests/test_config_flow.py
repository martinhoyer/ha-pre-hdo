"""Tests for PRE Distribuce config flow."""

from custom_components.pre_hdo.const import (
    CONF_RECEIVER_COMMAND_ID,
    DOMAIN,
)


class TestConfigFlowUnit:
    """Unit tests for config flow validation logic."""

    def test_domain_constant(self) -> None:
        assert DOMAIN == "pre_hdo"

    def test_config_keys(self) -> None:
        assert CONF_RECEIVER_COMMAND_ID == "receiver_command_id"
