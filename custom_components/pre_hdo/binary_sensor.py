"""Binary sensor platform for PRE Distribuce HDO."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_RECEIVER_COMMAND_ID, DOMAIN
from .coordinator import HdoData, PreHdoCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import PreHdoConfigEntry


def can_appliance_run(data: HdoData, minutes_needed: int) -> bool:
    """Check if an appliance can complete within the current low tariff window."""
    if not data.is_low_tariff:
        return False
    return minutes_needed < data.minutes_to_high_tariff


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PreHdoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors from a config entry."""
    coordinator = entry.runtime_data
    command_id = entry.data[CONF_RECEIVER_COMMAND_ID]

    async_add_entities(
        [
            HdoTariffBinarySensor(coordinator, command_id),
        ]
    )


class HdoTariffBinarySensor(CoordinatorEntity[PreHdoCoordinator], BinarySensorEntity):
    """Binary sensor showing whether low tariff is currently active."""

    _attr_device_class = BinarySensorDeviceClass.POWER
    _attr_icon = "mdi:flash"
    _attr_has_entity_name = True
    _attr_translation_key = "low_tariff"

    def __init__(
        self,
        coordinator: PreHdoCoordinator,
        command_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"pre-hdo_{command_id}_low_tariff"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, command_id)},
            "name": f"PRE Distribuce HDO {command_id}",
            "manufacturer": "PREdistribuce, a.s.",
        }

    @property
    def is_on(self) -> bool | None:
        """Return True if low tariff is active."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.is_low_tariff

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional state attributes."""
        data = self.coordinator.data
        if data is None:
            return {}
        return {
            "current_tariff": data.current_tariff,
            "minutes_to_next_change": data.minutes_to_next_change,
            "periods_today": [
                {
                    "tariff": p.tariff,
                    "start": p.start.strftime("%H:%M"),
                    "end": p.end.strftime("%H:%M"),
                }
                for p in data.periods
            ],
        }
