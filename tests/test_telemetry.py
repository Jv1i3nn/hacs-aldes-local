"""Unit tests for telemetry diagnostics."""


def test_twenty_minute_old_telemetry_is_stale_but_remains_usable(telemetry_module):
    """Staleness is diagnostic and must not imply entity unavailability."""
    updated = 1_000.0
    now = updated + 20 * 60

    assert telemetry_module.telemetry_age(updated, now) == 1_200
    assert telemetry_module.telemetry_is_stale(updated, 300, now)


def test_recent_telemetry_is_not_stale(telemetry_module):
    assert not telemetry_module.telemetry_is_stale(1_000.0, 300, 1_299.0)


def test_missing_telemetry_is_stale(telemetry_module):
    assert telemetry_module.telemetry_age(None, 1_000.0) is None
    assert telemetry_module.telemetry_is_stale(None, 300, 1_000.0)
