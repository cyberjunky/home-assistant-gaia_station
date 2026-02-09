"""DataUpdateCoordinator for GAIA Station."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GaiaStationApiClient, GaiaStationApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class GaiaStationDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching GAIA Station data."""

    def __init__(self, hass: HomeAssistant, client: GaiaStationApiClient) -> None:
        """Initialize."""
        self.client = client
        self.raw_data: dict[str, Any] = {}
        super().__init__(
            hass,
            _LOGGER,
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

        # Individual PMS sensor groups (pms1, pms2, pms3, ...)
        for group_key, group_data in pms.items():
            if group_key in ("historic", "rolling"):
                continue
            if not isinstance(group_data, dict):
                continue
            # group_key is e.g. "pms1"
            for particle_type in ("pm25", "pm1", "pm10"):
                particle_data = group_data.get(particle_type)
                if not isinstance(particle_data, dict):
                    continue
                prefix = f"{group_key}_{particle_type}"
                for stat_key in ("latest", "mean", "median", "min", "max", "stddev", "samples"):
                    if stat_key in particle_data:
                        flat[f"{prefix}_{stat_key}"] = particle_data[stat_key]

        # Rolling averages for PMS
        rolling_pms = pms.get("rolling", {})
        if isinstance(rolling_pms, dict):
            for particle_type in ("pm25", "pm1", "pm10"):
                particle_data = rolling_pms.get(particle_type)
                if not isinstance(particle_data, dict):
                    continue
                prefix = f"rolling_{particle_type}"
                for stat_key in ("latest", "mean", "median", "min", "max", "stddev", "samples"):
                    if stat_key in particle_data:
                        flat[f"{prefix}_{stat_key}"] = particle_data[stat_key]

        # --- CO2 ---
        co2 = data.get("co2", {})
        if isinstance(co2, dict):
            co2_rolling = co2.get("rolling")
            if isinstance(co2_rolling, dict):
                for stat_key in ("latest", "mean", "median", "min", "max", "stddev", "samples"):
                    if stat_key in co2_rolling:
                        flat[f"co2_{stat_key}"] = co2_rolling[stat_key]

        # --- Meteorological ---
        met = data.get("met", {})
        if isinstance(met, dict):
            for met_type in ("temperature", "humidity"):
                met_data = met.get(met_type)
                if isinstance(met_data, dict):
                    for stat_key in ("latest", "mean", "median", "min", "max", "stddev", "samples"):
                        if stat_key in met_data:
                            flat[f"{met_type}_{stat_key}"] = met_data[stat_key]
                elif isinstance(met_data, (int, float)):
                    # Some models may return simple values
                    flat[f"{met_type}_latest"] = met_data

        # --- System ---
        sys_data = data.get("sys", {})
        if isinstance(sys_data, dict):
            for key in ("boot", "vpwr", "heap", "alive", "time"):
                if key in sys_data:
                    flat[f"sys_{key}"] = sys_data[key]

        _LOGGER.debug("Flattened %d keys from GAIA Station data", len(flat))
        return flat
