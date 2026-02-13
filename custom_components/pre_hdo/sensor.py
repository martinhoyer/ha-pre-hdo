"""Sensor platform for PRE Distribuce HDO."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_RECEIVER_COMMAND_ID, DOMAIN
from .coordinator import PreHdoCoordinator

if TYPE_CHECKING:
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
            HdoMinutesToLowTariffSensor(coordinator, command_id),
            HdoMinutesToHighTariffSensor(coordinator, command_id),
            HdoCurrentTariffSensor(coordinator, command_id),
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


class HdoMinutesToLowTariffSensor(HdoBaseSensor):
    """Sensor showing minutes until low tariff starts."""

    _attr_icon = "mdi:clock-start"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "minutes_to_low_tariff"

    def __init__(self, coordinator: PreHdoCoordinator, command_id: str) -> None:
        super().__init__(coordinator, command_id)
        self._attr_unique_id = f"pre-hdo_{command_id}_minutes_to_low"

    @property
    def native_value(self) -> int | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.minutes_to_low_tariff


class HdoMinutesToHighTariffSensor(HdoBaseSensor):
    """Sensor showing minutes until high tariff starts."""

    _attr_icon = "mdi:clock-end"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_translation_key = "minutes_to_high_tariff"

    def __init__(self, coordinator: PreHdoCoordinator, command_id: str) -> None:
        super().__init__(coordinator, command_id)
        self._attr_unique_id = f"pre-hdo_{command_id}_minutes_to_high"

    @property
    def native_value(self) -> int | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.minutes_to_high_tariff


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
