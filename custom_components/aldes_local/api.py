"""Client for the authenticated local API exposed by Aldes Bridge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiohttp import ClientError, ClientSession


class AldesLocalError(Exception):
    """Base API error."""


class AldesLocalAuthenticationError(AldesLocalError):
    """Raised when Aldes Bridge rejects the configured token."""


class AldesLocalConnectionError(AldesLocalError):
    """Raised when Aldes Bridge cannot be reached."""


@dataclass(frozen=True, slots=True)
class AldesZone:
    """State of one Aldes temperature zone."""

    zone_id: int
    current_temperature: float | None
    target_temperature: float | None


@dataclass(frozen=True, slots=True)
class AldesDevice:
    """State returned by Aldes Bridge."""

    connected: bool
    client_id: str | None
    air_mode: int | None
    water_mode: int | None
    zones: tuple[AldesZone, ...]


class AldesLocalApi:
    """Small asynchronous Aldes Bridge API client."""

    def __init__(self, session: ClientSession, base_url: str, token: str) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {token}"}

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            async with self._session.request(
                method,
                f"{self._base_url}{path}",
                headers=self._headers,
                **kwargs,
            ) as response:
                if response.status == 401:
                    raise AldesLocalAuthenticationError("Invalid cloud2cloud token")
                response.raise_for_status()
                return await response.json()
        except AldesLocalAuthenticationError:
            raise
        except (ClientError, TimeoutError) as err:
            raise AldesLocalConnectionError(str(err)) from err

    async def async_get_device(self) -> AldesDevice:
        """Fetch the current local device state."""
        payload = await self._request("GET", "/api/local/device")
        zones = tuple(
            AldesZone(
                zone_id=int(zone["id"]),
                current_temperature=zone.get("current_temperature"),
                target_temperature=zone.get("target_temperature"),
            )
            for zone in payload.get("zones", [])
            if zone.get("current_temperature") not in (None, 0)
        )
        return AldesDevice(
            connected=bool(payload.get("connected")),
            client_id=payload.get("client_id"),
            air_mode=payload.get("air_mode"),
            water_mode=payload.get("water_mode"),
            zones=zones,
        )

    async def async_set_zone_temperature(
        self, zone_id: int, temperature: float
    ) -> None:
        """Send a target temperature to Aldes Bridge."""
        if not float(temperature).is_integer():
            raise ValueError("Aldes only accepts whole-degree setpoints")
        await self._request(
            "POST",
            f"/api/local/zones/{zone_id}/setpoint",
            json={"temperature": int(temperature)},
        )
