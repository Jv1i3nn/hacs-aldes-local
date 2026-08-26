"""Shared entity behavior for Aldes Local."""

from __future__ import annotations

from datetime import UTC, datetime

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TELEMETRY_STALE_AFTER
from .coordinator import AldesLocalCoordinator
from .telemetry import telemetry_age, telemetry_is_stale


class AldesLocalEntity(CoordinatorEntity[AldesLocalCoordinator]):
    """Entity backed by telemetry from Aldes Bridge."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AldesLocalCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Aldes",
            "manufacturer": "Aldes",
            "model": "Local bridge",
        }

    @property
    def telemetry_age(self) -> float | None:
        """Return telemetry age in seconds."""
        return telemetry_age(self.coordinator.data.last_updated)

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data.connected

    @property
    def extra_state_attributes(self):
        updated = self.coordinator.data.last_updated
        return {
            "telemetry_last_updated": (
                datetime.fromtimestamp(updated, UTC).isoformat()
                if updated is not None
                else None
            ),
            "telemetry_age_seconds": (
                round(self.telemetry_age) if self.telemetry_age is not None else None
            ),
            "telemetry_stale": telemetry_is_stale(updated, TELEMETRY_STALE_AFTER),
        }
