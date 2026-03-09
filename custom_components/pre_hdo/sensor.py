"""Sensor platform for PRE Distribuce HDO."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_RECEIVER_COMMAND_ID, DOMAIN
from .coordinator import PreHdoCoordinator

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from . import PreHdoConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: PreHdoConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities from a config entry."""
    coordinator = entry.runtime_data
    command_id = entry.data[CONF_RECEIVER_COMMAND_ID]

    async_add_entities(
        [
            HdoCurrentTariffSensor(coordinator, command_id),
            HdoNextLowTariffStartSensor(coordinator, command_id),
            HdoNextHighTariffStartSensor(coordinator, command_id),
        ]
    )


class HdoBaseSensor(CoordinatorEntity[PreHdoCoordinator], SensorEntity):
    """Base class for HDO sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PreHdoCoordinator,
        command_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._command_id = command_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, command_id)},
            "name": f"PRE Distribuce HDO {command_id}",
            "manufacturer": "PREdistribuce, a.s.",
        }


class HdoCurrentTariffSensor(HdoBaseSensor):
    """Sensor showing the current tariff name."""

    _attr_icon = "mdi:lightning-bolt"
    _attr_translation_key = "current_tariff"

    def __init__(self, coordinator: PreHdoCoordinator, command_id: str) -> None:
        super().__init__(coordinator, command_id)
        self._attr_unique_id = f"pre-hdo_{command_id}_current_tariff"

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.current_tariff


class HdoNextLowTariffStartSensor(HdoBaseSensor):
    """Sensor showing when the next low tariff period starts."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-start"
    _attr_translation_key = "next_low_tariff_start"

    def __init__(self, coordinator: PreHdoCoordinator, command_id: str) -> None:
        super().__init__(coordinator, command_id)
        self._attr_unique_id = f"pre-hdo_{command_id}_next_low_tariff_start"

    @property
    def native_value(self) -> datetime | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.next_low_tariff_start


class HdoNextHighTariffStartSensor(HdoBaseSensor):
    """Sensor showing when the next high tariff period starts."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-end"
    _attr_translation_key = "next_high_tariff_start"

    def __init__(self, coordinator: PreHdoCoordinator, command_id: str) -> None:
        super().__init__(coordinator, command_id)
        self._attr_unique_id = f"pre-hdo_{command_id}_next_high_tariff_start"

    @property
    def native_value(self) -> datetime | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.next_high_tariff_start
