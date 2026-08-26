"""Helpers for Aldes telemetry diagnostics."""

from __future__ import annotations

import time


def telemetry_age(updated: float | None, now: float | None = None) -> float | None:
    """Return the non-negative age of the latest telemetry sample."""
    if updated is None:
        return None
    return max(0, (time.time() if now is None else now) - updated)


def telemetry_is_stale(
    updated: float | None, stale_after: float, now: float | None = None
) -> bool:
    """Return whether telemetry is missing or older than the diagnostic limit."""
    age = telemetry_age(updated, now)
    return age is None or age > stale_after
