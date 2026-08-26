"""Test helpers for Aldes Local."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def api_module():
    """Load the API module without importing the Home Assistant package."""
    path = Path(__file__).parents[1] / "custom_components" / "aldes_local" / "api.py"
    spec = importlib.util.spec_from_file_location("aldes_local_api", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
