"""Tests for the GAIA Station config flow."""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant.common import MockConfigEntry
from pytest_homeassistant.test_util.aiohttp import AiohttpClientMocker

from custom_components.gaia_station.const import DOMAIN

from .conftest import HOST, REALTIME_URL, realtime_data


@pytest.fixture(autouse=True)
async def mock_setup_entry(hass: HomeAssistant) -> AsyncGenerator[AsyncMock]:
    """Prevent created entries from actually being set up."""
    with (
        patch(
            "custom_components.gaia_station.async_setup_entry", AsyncMock(return_value=True)
        ) as mock,
        patch("custom_components.gaia_station.async_unload_entry", AsyncMock(return_value=True)),
    ):
        yield mock
        # Unload while patched; the real unload expects state the mock never set up
        for entry in hass.config_entries.async_entries(DOMAIN):
            await hass.config_entries.async_unload(entry.entry_id)


async def test_user_flow_success(hass: HomeAssistant, aioclient_mock: AiohttpClientMocker) -> None:
    """A reachable station is added; surrounding whitespace is stripped."""
    aioclient_mock.get(REALTIME_URL, json=realtime_data())

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: f"  {HOST} "}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"GAIA Station ({HOST})"
    assert result["data"] == {CONF_HOST: HOST}
    assert result["result"].unique_id == HOST


@pytest.mark.parametrize(
    "mock_kwargs",
    [
        {"exc": aiohttp.ClientConnectionError()},
        {"exc": aiohttp.ClientError()},
        {"exc": TimeoutError()},
        {"status": 500},
        {"text": "not json"},
        {"json": [1, 2]},
        {"json": {"something": "else"}},
    ],
)
async def test_user_flow_cannot_connect(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, mock_kwargs: dict
) -> None:
    """Unreachable hosts and non-GAIA responses show cannot_connect."""
    aioclient_mock.get(REALTIME_URL, **mock_kwargs)

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_HOST: HOST})

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    aioclient_mock.clear_requests()
    aioclient_mock.get(REALTIME_URL, json=realtime_data())
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_HOST: HOST})
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_unknown_error(hass: HomeAssistant) -> None:
    """Unexpected exceptions are reported as unknown."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    with patch(
        "custom_components.gaia_station.config_flow.validate_input",
        side_effect=RuntimeError,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_HOST: HOST}
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}


async def test_user_flow_already_configured(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """The same host cannot be added twice."""
    mock_config_entry.add_to_hass(hass)
    aioclient_mock.get(REALTIME_URL, json=realtime_data())

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_HOST: HOST})

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
