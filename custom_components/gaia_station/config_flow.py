"""Config flow for GAIA Station integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GaiaStationApiClient, GaiaStationApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    client = GaiaStationApiClient(data[CONF_HOST], session)

    # Test connection by getting realtime data
    realtime_data = await client.async_get_system_info()

    # Verify it looks like a GAIA station response
    if "sys" not in realtime_data and "pms" not in realtime_data:
        raise GaiaStationApiError("Response does not look like a GAIA Station")

    return {
        "title": f"GAIA Station ({data[CONF_HOST]})",
    }


class GaiaStationConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GAIA Station."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip()
            try:
                info = await validate_input(self.hass, user_input)
            except GaiaStationApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
