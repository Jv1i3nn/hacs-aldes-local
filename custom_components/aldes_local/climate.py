"""Climate entities for Aldes Local zones."""

from __future__ import annotations

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .api import AldesZone
from .const import DOMAIN
from .coordinator import AldesLocalCoordinator
from .entity import AldesLocalEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[AldesLocalCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Create one climate entity for each zone reported by Aldes Bridge."""
    coordinator = entry.runtime_data
    entities = [
        AldesZoneClimate(coordinator, entry.entry_id, zone.zone_id)
        for zone in coordinator.data.zones
    ]
    valid_unique_ids = {entity.unique_id for entity in entities}
    registry = er.async_get(hass)
    for registry_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if (
            registry_entry.domain == "climate"
            and registry_entry.platform == DOMAIN
            and registry_entry.unique_id.startswith(f"{entry.entry_id}_zone_")
            and registry_entry.unique_id not in valid_unique_ids
        ):
            registry.async_remove(registry_entry.entity_id)
    async_add_entities(entities)


class AldesZoneClimate(AldesLocalEntity, ClimateEntity):
    """A locally controlled Aldes temperature zone."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 1
    _attr_min_temp = 5
    _attr_max_temp = 30
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(
        self, coordinator: AldesLocalCoordinator, entry_id: str, zone_id: int
    ) -> None:
        super().__init__(coordinator, entry_id)
        self._zone_id = zone_id
        self._attr_unique_id = f"{entry_id}_zone_{zone_id}"

    @property
    def _zone(self) -> AldesZone | None:
        return next(
            (
                zone
                for zone in self.coordinator.data.zones
                if zone.zone_id == self._zone_id
            ),
            None,
        )

    @property
    def current_temperature(self) -> float | None:
        return self._zone.current_temperature if self._zone else None

    @property
    def target_temperature(self) -> float | None:
        return self._zone.target_temperature if self._zone else None

    @property
    def available(self) -> bool:
        return super().available and self._zone is not None

    @property
    def hvac_mode(self) -> HVACMode:
        mode = self.coordinator.data.air_mode
        if mode == 0:
            return HVACMode.OFF
        if mode is not None and mode >= 5:
            return HVACMode.COOL
        return HVACMode.HEAT

    @property
    def hvac_modes(self) -> list[HVACMode]:
        return [self.hvac_mode]

    async def async_set_temperature(self, **kwargs: float) -> None:
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        await self.coordinator.api.async_set_zone_temperature(
            self._zone_id, temperature
        )
        await self.coordinator.async_request_refresh()
