"""Tests for the GAIA Station sensors."""

from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant.common import MockConfigEntry
from pytest_homeassistant.test_util.aiohttp import AiohttpClientMocker

from custom_components.gaia_station.const import DOMAIN

from .conftest import REALTIME_URL, realtime_data


async def _setup(
    hass: HomeAssistant, entry: MockConfigEntry, aioclient_mock: AiohttpClientMocker, data
) -> None:
    aioclient_mock.get(REALTIME_URL, json=data)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


def _keys(hass: HomeAssistant, entry: MockConfigEntry) -> set[str]:
    return {
        e.unique_id.removeprefix(f"{entry.entry_id}_")
        for e in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    }


def _entity_id(hass: HomeAssistant, entry: MockConfigEntry, key: str) -> str:
    entity_id = er.async_get(hass).async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_{key}")
    assert entity_id is not None, key
    return entity_id


async def test_sensors_created_from_data(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Sensors exist only for keys present in the station data."""
    await _setup(hass, mock_config_entry, aioclient_mock, realtime_data())

    keys = _keys(hass, mock_config_entry)
    pms1 = {
        f"pms1_{pm}_{stat}"
        for pm in ("pm25", "pm1", "pm10")
        for stat in ("latest", "mean", "min", "max", "median")
    }
    pms2 = {f"pms2_pm25_{stat}" for stat in ("latest", "mean", "min", "max", "median")}
    rolling = {
        f"rolling_{pm}_{stat}" for pm in ("pm25", "pm1", "pm10") for stat in ("latest", "mean")
    }
    co2 = {f"co2_{stat}" for stat in ("latest", "mean", "min", "max", "median")}
    met = {"temperature_latest", "humidity_latest"}
    system = {"sys_vpwr", "sys_heap", "sys_alive", "sys_boot"}
    assert keys == pms1 | pms2 | rolling | co2 | met | system


async def test_sensor_values(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Flattened values are exposed on the sensors."""
    await _setup(hass, mock_config_entry, aioclient_mock, realtime_data())

    def value(key: str) -> str:
        return hass.states.get(_entity_id(hass, mock_config_entry, key)).state

    assert value("pms1_pm25_latest") == "8"
    assert value("pms1_pm10_max") == "13"
    assert value("pms2_pm25_mean") == "8.5"
    assert value("rolling_pm25_latest") == "8.5"
    assert value("co2_latest") == "612"
    assert value("co2_min") == "611"
    assert value("temperature_latest") == "21.3"
    # Plain numeric met values are supported too
    assert value("humidity_latest") == "45"


async def test_diagnostic_sensors_disabled_by_default(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """System sensors are registered but disabled."""
    await _setup(hass, mock_config_entry, aioclient_mock, realtime_data())

    registry = er.async_get(hass)
    for key in ("sys_vpwr", "sys_heap", "sys_alive", "sys_boot"):
        entry = registry.async_get(_entity_id(hass, mock_config_entry, key))
        assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION


async def test_minimal_station(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Malformed sections are skipped without failing setup."""
    data = {"pms": {"pms1": {"pm25": {"latest": 3}}, "pms9": "bogus"}, "co2": "n/a", "met": None}
    await _setup(hass, mock_config_entry, aioclient_mock, data)

    assert _keys(hass, mock_config_entry) == {"pms1_pm25_latest"}


async def test_sensor_unavailable_after_failed_update(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Sensors become unavailable when the station stops responding."""
    await _setup(hass, mock_config_entry, aioclient_mock, realtime_data())
    entity_id = _entity_id(hass, mock_config_entry, "co2_latest")

    aioclient_mock.clear_requests()
    aioclient_mock.get(REALTIME_URL, status=500)
    await hass.data[DOMAIN][mock_config_entry.entry_id].async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == STATE_UNAVAILABLE
