"""Config flow for Aldes Local."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AldesLocalApi, AldesLocalAuthenticationError, AldesLocalConnectionError
from .const import CONF_TOKEN, DEFAULT_NAME, DOMAIN


class AldesLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure an Aldes Bridge connection."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial configuration step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            url = user_input[CONF_URL].rstrip("/")
            api = AldesLocalApi(
                async_get_clientsession(self.hass), url, user_input[CONF_TOKEN]
            )
            try:
                device = await api.async_get_device()
            except AldesLocalAuthenticationError:
                errors["base"] = "invalid_auth"
            except AldesLocalConnectionError:
                errors["base"] = "cannot_connect"
            else:
                unique_id = device.client_id or url
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={CONF_URL: url, CONF_TOKEN: user_input[CONF_TOKEN]},
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_URL, default="http://homeassistant.local:8080"): str,
                vol.Required(CONF_TOKEN): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
