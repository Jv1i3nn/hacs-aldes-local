"""Data coordinator for Aldes Local."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AldesDevice, AldesLocalApi, AldesLocalError
from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class AldesLocalCoordinator(DataUpdateCoordinator[AldesDevice]):
    """Poll Aldes Bridge and share its state with entities."""

    def __init__(self, hass: HomeAssistant, api: AldesLocalApi) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="Aldes Local",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> AldesDevice:
        try:
            return await self.api.async_get_device()
        except AldesLocalError as err:
            raise UpdateFailed(str(err)) from err
