"""DataUpdateCoordinator for GAIA Station."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GaiaStationApiClient, GaiaStationApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

PARTICLE_TYPES = ("pm25", "pm1", "pm10")
STAT_KEYS = ("latest", "mean", "median", "min", "max", "stddev", "samples")


def _copy_stats(flat: dict[str, Any], prefix: str, source: Any) -> None:
    """Copy the statistics of one measurement into the flat dict."""
    if not isinstance(source, dict):
        return
    for stat_key in STAT_KEYS:
        if stat_key in source:
            flat[f"{prefix}_{stat_key}"] = source[stat_key]


class GaiaStationDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching GAIA Station data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: GaiaStationApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        self.raw_data: dict[str, Any] = {}
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API and flatten for sensor consumption."""
        try:
            self.raw_data = await self.client.async_get_realtime_data()
            return self._flatten_data(self.raw_data)
        except GaiaStationApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def _flatten_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Flatten nested GAIA Station JSON into a flat dict for sensors.

        The GAIA JSON has deeply nested data. This method produces a flat dict
        with descriptive keys so sensors can easily look up values.
        """
        flat: dict[str, Any] = {}

        # --- Particulate Matter Sensors ---
        pms = data.get("pms", {})
        if isinstance(pms, dict):
            # Individual PMS sensor groups (pms1, pms2, pms3, ...) and rolling averages
            for group_key, group_data in pms.items():
                if group_key == "historic" or not isinstance(group_data, dict):
                    continue
                for particle_type in PARTICLE_TYPES:
                    _copy_stats(
                        flat, f"{group_key}_{particle_type}", group_data.get(particle_type)
                    )

        # --- CO2 ---
        co2 = data.get("co2", {})
        if isinstance(co2, dict):
            _copy_stats(flat, "co2", co2.get("rolling"))

        # --- Meteorological ---
        met = data.get("met", {})
        if isinstance(met, dict):
            for met_type in ("temperature", "humidity"):
                met_data = met.get(met_type)
                if isinstance(met_data, (int, float)):
                    # Some models may return simple values
                    flat[f"{met_type}_latest"] = met_data
                else:
                    _copy_stats(flat, met_type, met_data)

        # --- System ---
        sys_data = data.get("sys", {})
        if isinstance(sys_data, dict):
            for key in ("boot", "vpwr", "heap", "alive", "time"):
                if key in sys_data:
                    flat[f"sys_{key}"] = sys_data[key]

        _LOGGER.debug("Flattened %d keys from GAIA Station data", len(flat))
        return flat
