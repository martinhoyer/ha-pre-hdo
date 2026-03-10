"""Binary sensor platform for PRE Distribuce HDO."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, override

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_RECEIVER_COMMAND_ID, DOMAIN, PRAGUE_TZ
from .coordinator import HdoData, PreHdoCoordinator

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import PreHdoConfigEntry
    from .parser import HdoPeriod


def can_appliance_run(data: HdoData, minutes_needed: int) -> bool:
    """Check if an appliance can complete within the current low tariff window."""
    if not data.is_low_tariff or data.next_high_tariff_start is None:
        return False
    now = datetime.now(tz=PRAGUE_TZ)
    minutes_remaining = int((data.next_high_tariff_start - now).total_seconds() / 60)
    return minutes_needed < minutes_remaining


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


class HdoTariffBinarySensor(CoordinatorEntity[PreHdoCoordinator], BinarySensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
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
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, command_id)},
            name=f"PRE Distribuce HDO {command_id}",
            manufacturer="PREdistribuce, a.s.",
        )

    @property
    @override
    def is_on(self) -> bool | None:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Return True if low tariff is active."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.get_processed_data().is_low_tariff

    @staticmethod
    def _get_periods_today(data: HdoData) -> list[HdoPeriod]:
        today = datetime.now(tz=PRAGUE_TZ).date()
        for schedule in data.schedules:
            if today in schedule.dates:
                return schedule.periods
        return []

    @property
    @override
    def extra_state_attributes(self) -> dict[str, Any]:  # pyright: ignore[reportIncompatibleVariableOverride]
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}
        data = self.coordinator.get_processed_data()
        return {
            "current_tariff": data.current_tariff,
            "minutes_to_next_change": data.minutes_to_next_change,
            "periods_today": [
                {
                    "tariff": p.tariff,
                    "start": p.start.strftime("%H:%M"),
                    "end": p.end.strftime("%H:%M"),
                }
                for p in self._get_periods_today(data)
            ],
        }
