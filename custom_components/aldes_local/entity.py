"""Shared entity behavior for Aldes Local."""

from __future__ import annotations

import time
from datetime import UTC, datetime

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TELEMETRY_STALE_AFTER
from .coordinator import AldesLocalCoordinator


class AldesLocalEntity(CoordinatorEntity[AldesLocalCoordinator]):
    """Entity backed by fresh telemetry from Aldes Bridge."""

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
        updated = self.coordinator.data.last_updated
        return max(0, time.time() - updated) if updated is not None else None

    @property
    def available(self) -> bool:
        age = self.telemetry_age
        return (
            super().available
            and self.coordinator.data.connected
            and age is not None
            and age <= TELEMETRY_STALE_AFTER
        )

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
        }
