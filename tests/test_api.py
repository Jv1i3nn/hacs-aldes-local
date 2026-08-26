"""Unit tests for the Aldes Bridge API client."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
from aiohttp import ClientConnectionError


@dataclass
class FakeResponse:
    payload: dict[str, Any]
    status: int = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    def raise_for_status(self):
        if self.status >= 400:
            raise AssertionError(f"Unexpected HTTP status {self.status}")

    async def json(self):
        return self.payload


@dataclass
class FakeSession:
    response: FakeResponse | None = None
    error: Exception | None = None
    calls: list[tuple[str, str, dict[str, Any]]] = field(default_factory=list)

    def request(self, method: str, url: str, **kwargs):
        self.calls.append((method, url, kwargs))
        if self.error:
            raise self.error
        assert self.response is not None
        return self.response


async def test_get_device_parses_local_state(api_module):
    session = FakeSession(
        FakeResponse(
            {
                "connected": True,
                "client_id": "box-123",
                "air_mode": 1,
                "water_mode": 0,
                "zones": [
                    {
                        "id": 2,
                        "current_temperature": 20.5,
                        "target_temperature": 21.0,
                    }
                ],
            }
        )
    )
    api = api_module.AldesLocalApi(session, "http://bridge:8080/", "secret")

    device = await api.async_get_device()

    assert device.connected is True
    assert device.client_id == "box-123"
    assert device.zones == (api_module.AldesZone(2, 20.5, 21.0),)
    assert session.calls[0][0:2] == ("GET", "http://bridge:8080/api/local/device")
    assert session.calls[0][2]["headers"] == {"Authorization": "Bearer secret"}


async def test_set_zone_temperature_posts_expected_payload(api_module):
    session = FakeSession(FakeResponse({"ok": True, "status": "sent"}))
    api = api_module.AldesLocalApi(session, "http://bridge:8080", "secret")

    await api.async_set_zone_temperature(3, 21.5)

    method, url, kwargs = session.calls[0]
    assert method == "POST"
    assert url == "http://bridge:8080/api/local/zones/3/setpoint"
    assert kwargs["json"] == {"temperature": 21.5}


async def test_invalid_token_raises_authentication_error(api_module):
    session = FakeSession(FakeResponse({}, status=401))
    api = api_module.AldesLocalApi(session, "http://bridge:8080", "wrong")

    with pytest.raises(api_module.AldesLocalAuthenticationError):
        await api.async_get_device()


async def test_connection_failure_is_wrapped(api_module):
    session = FakeSession(error=ClientConnectionError("unreachable"))
    api = api_module.AldesLocalApi(session, "http://bridge:8080", "secret")

    with pytest.raises(api_module.AldesLocalConnectionError, match="unreachable"):
        await api.async_get_device()
