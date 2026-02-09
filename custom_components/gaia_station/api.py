"""API client for GAIA Station air quality monitor."""
import json
import logging

import aiohttp
import async_timeout

_LOGGER = logging.getLogger(__name__)


class GaiaStationApiError(Exception):
    """Base exception for GAIA Station API errors."""


class GaiaStationConnectionError(GaiaStationApiError):
    """Exception for connection errors."""


class GaiaStationTimeoutError(GaiaStationApiError):
    """Exception for timeout errors."""


class GaiaStationApiClient:
    """API client for GAIA Station air quality monitor."""

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self.host = host
        self.session = session
        self._base_url = f"http://{host}"

    async def async_get_data(self, endpoint: str) -> dict:
        """Get data from the API."""
        url = f"{self._base_url}{endpoint}"
        try:
            async with async_timeout.timeout(10):
                async with self.session.get(url, allow_redirects=False) as response:
                    response.raise_for_status()

                    text = await response.text()

                    _LOGGER.debug(
                        "Response from %s (first 200 chars): %s", url, text[:200]
                    )

                    try:
                        data = json.loads(text)
                        if not isinstance(data, dict):
                            raise ValueError(f"Expected dict, got {type(data)}")
                        return data
                    except json.JSONDecodeError as err:
                        _LOGGER.error(
                            "Invalid JSON from %s. Content-Type: %s, Response: %s",
                            url,
                            response.content_type,
                            text[:500],
                        )
                        raise GaiaStationApiError(
                            f"Invalid JSON response from {url}: {err}"
                        ) from err

        except TimeoutError as err:
            _LOGGER.error("Timeout fetching data from %s after 10 seconds", url)
            raise GaiaStationTimeoutError(
                f"Timeout connecting to {self.host}"
            ) from err
        except aiohttp.ClientConnectionError as err:
            _LOGGER.error("Connection error to %s: %s", url, err)
            raise GaiaStationConnectionError(
                f"Cannot connect to {self.host}: {err}"
            ) from err
        except aiohttp.ClientResponseError as err:
            _LOGGER.error("HTTP %s error from %s: %s", err.status, url, err)
            raise GaiaStationApiError(
                f"HTTP {err.status} error from {url}"
            ) from err
        except aiohttp.ClientError as err:
            _LOGGER.error("HTTP client error from %s: %s", url, err)
            raise GaiaStationConnectionError(
                f"HTTP error connecting to {self.host}: {err}"
            ) from err

    async def async_get_realtime_data(self) -> dict:
        """Get realtime data from the station."""
        return await self.async_get_data("/realtime/")

    async def async_get_system_info(self) -> dict:
        """Get system information - used for validation during setup."""
        return await self.async_get_data("/realtime/")
