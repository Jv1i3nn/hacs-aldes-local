"""Mode selectors for Aldes Local."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import AIR_MODES, WATER_MODES
from .coordinator import AldesLocalCoordinator
from .entity import AldesLocalEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[AldesLocalCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Create air and hot-water mode selectors."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            AldesAirModeSelect(coordinator, entry.entry_id),
            AldesWaterModeSelect(coordinator, entry.entry_id),
        ]
    )


class AldesModeSelect(AldesLocalEntity, SelectEntity):
    """Base selector for a mode represented by an Aldes index and command code."""

    _modes: dict[str, tuple[int, str]]

    def __init__(self, coordinator: AldesLocalCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_options = list(self._modes)

    @property
    def current_index(self) -> int | None:
        raise NotImplementedError

    @property
    def current_option(self) -> str | None:
        return next(
            (
                option
                for option, (index, _) in self._modes.items()
                if index == self.current_index
            ),
            None,
        )


class AldesAirModeSelect(AldesModeSelect):
    """Full-fidelity air mode selector."""

    _attr_name = "Air mode"
    _modes = AIR_MODES

    def __init__(self, coordinator: AldesLocalCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_air_mode"

    @property
    def current_index(self) -> int | None:
        return self.coordinator.data.air_mode

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.api.async_set_air_mode(self._modes[option][1])
        await self.coordinator.async_request_refresh()


class AldesWaterModeSelect(AldesModeSelect):
    """Hot-water mode selector."""

    _attr_name = "Hot water mode"
    _modes = WATER_MODES

    def __init__(self, coordinator: AldesLocalCoordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_water_mode"

    @property
    def current_index(self) -> int | None:
        return self.coordinator.data.water_mode

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.api.async_set_water_mode(self._modes[option][1])
        await self.coordinator.async_request_refresh()
