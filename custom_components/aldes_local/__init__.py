"""Aldes Local integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AldesLocalApi
from .const import CONF_TOKEN
from .coordinator import AldesLocalCoordinator

PLATFORMS = [Platform.CLIMATE]
type AldesLocalConfigEntry = ConfigEntry[AldesLocalCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AldesLocalConfigEntry) -> bool:
    """Set up Aldes Local from a config entry."""
    api = AldesLocalApi(
        async_get_clientsession(hass),
        entry.data[CONF_URL],
        entry.data[CONF_TOKEN],
    )
    coordinator = AldesLocalCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AldesLocalConfigEntry) -> bool:
    """Unload Aldes Local."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
