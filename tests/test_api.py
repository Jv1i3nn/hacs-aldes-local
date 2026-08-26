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
                "last_updated": 1770000000.5,
                "zones": [
                    {
                        "id": 2,
                        "current_temperature": 20.5,
                        "target_temperature": 21.0,
                    },
                    {
                        "id": 9,
                        "current_temperature": 0,
                        "target_temperature": 0,
                    },
                ],
            }
        )
    )
    api = api_module.AldesLocalApi(session, "http://bridge:8080/", "secret")

    device = await api.async_get_device()

    assert device.connected is True
    assert device.client_id == "box-123"
    assert device.zones == (api_module.AldesZone(2, 20.5, 21.0),)
    assert device.air_mode == 1
    assert device.water_mode == 0
    assert device.last_updated == 1770000000.5
    assert session.calls[0][0:2] == ("GET", "http://bridge:8080/api/local/device")
    assert session.calls[0][2]["headers"] == {"Authorization": "Bearer secret"}


async def test_set_zone_temperature_posts_whole_degree_payload(api_module):
    session = FakeSession(FakeResponse({"ok": True, "status": "sent"}))
    api = api_module.AldesLocalApi(session, "http://bridge:8080", "secret")

    await api.async_set_zone_temperature(3, 21.0)

    method, url, kwargs = session.calls[0]
    assert method == "POST"
    assert url == "http://bridge:8080/api/local/zones/3/setpoint"
    assert kwargs["json"] == {"temperature": 21}


async def test_set_zone_temperature_rejects_half_degree(api_module):
    session = FakeSession(FakeResponse({"ok": True, "status": "sent"}))
    api = api_module.AldesLocalApi(session, "http://bridge:8080", "secret")

    with pytest.raises(ValueError, match="whole-degree"):
        await api.async_set_zone_temperature(3, 21.5)

    assert session.calls == []


@pytest.mark.parametrize(
    ("method_name", "path", "code"),
    [
        ("async_set_air_mode", "/api/local/modes/air", "F"),
        ("async_set_water_mode", "/api/local/modes/water", "N"),
    ],
)
async def test_set_mode_posts_expected_code(api_module, method_name, path, code):
    session = FakeSession(FakeResponse({"ok": True, "status": "sent"}))
    api = api_module.AldesLocalApi(session, "http://bridge:8080", "secret")

    await getattr(api, method_name)(code)

    method, url, kwargs = session.calls[0]
    assert method == "POST"
    assert url == f"http://bridge:8080{path}"
    assert kwargs["json"] == {"mode": code}


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
