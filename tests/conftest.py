"""Fixtures for GAIA Station tests."""

from typing import Any

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant.common import MockConfigEntry

from custom_components.gaia_station.const import DOMAIN

HOST = "192.168.1.60"
REALTIME_URL = f"http://{HOST}/realtime/"


def _stats(latest: float, mean: float) -> dict[str, Any]:
    return {
        "latest": latest,
        "mean": mean,
        "median": mean,
        "min": latest - 1,
        "max": latest + 1,
        "stddev": 0.5,
        "samples": 60,
    }


def realtime_data() -> dict[str, Any]:
    """Return a /realtime/ response with two PMS sensors."""
    return {
        "pms": {
            "pms1": {"pm25": _stats(8, 7.5), "pm1": _stats(5, 4.5), "pm10": _stats(12, 11)},
            "pms2": {"pm25": _stats(9, 8.5)},
            "rolling": {"pm25": _stats(8.5, 8), "pm1": _stats(5.5, 5), "pm10": _stats(12.5, 12)},
            "historic": {"pm25": _stats(100, 100)},
        },
        "co2": {"rolling": _stats(612, 600)},
        "met": {"temperature": _stats(21.3, 21), "humidity": 45},
        "sys": {"boot": 7, "vpwr": 5012, "heap": 123456, "alive": 86400, "time": 1700000000},
    }


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable loading of the custom integration in all tests."""
    return


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a mocked config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=f"GAIA Station ({HOST})",
        data={CONF_HOST: HOST},
        unique_id=HOST,
    )
