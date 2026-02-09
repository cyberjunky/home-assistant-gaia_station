"""Sensor platform for GAIA Station integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfTemperature,
    UnitOfTime,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GaiaStationDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class GaiaStationSensorEntityDescription(SensorEntityDescription):
    """Describes GAIA Station sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any] = lambda _: None


# ==============================================================================
# Static sensor descriptions for rolling averages, CO2, met, and system data.
# These are only created if their key exists in the flattened data.
# ==============================================================================

ROLLING_PM_SENSORS: tuple[GaiaStationSensorEntityDescription, ...] = (
    # --- Rolling PM2.5 ---
    GaiaStationSensorEntityDescription(
        key="rolling_pm25_latest",
        name="PM2.5 Rolling",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("rolling_pm25_latest"),
        icon="mdi:blur",
    ),
    GaiaStationSensorEntityDescription(
        key="rolling_pm25_mean",
        name="PM2.5 Rolling Mean",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("rolling_pm25_mean"),
        icon="mdi:blur",
    ),
    # --- Rolling PM1.0 ---
    GaiaStationSensorEntityDescription(
        key="rolling_pm1_latest",
        name="PM1.0 Rolling",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM1,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("rolling_pm1_latest"),
        icon="mdi:blur-linear",
    ),
    GaiaStationSensorEntityDescription(
        key="rolling_pm1_mean",
        name="PM1.0 Rolling Mean",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM1,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("rolling_pm1_mean"),
        icon="mdi:blur-linear",
    ),
    # --- Rolling PM10 ---
    GaiaStationSensorEntityDescription(
        key="rolling_pm10_latest",
        name="PM10 Rolling",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM10,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("rolling_pm10_latest"),
        icon="mdi:blur-radial",
    ),
    GaiaStationSensorEntityDescription(
        key="rolling_pm10_mean",
        name="PM10 Rolling Mean",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM10,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("rolling_pm10_mean"),
        icon="mdi:blur-radial",
    ),
)

CO2_SENSORS: tuple[GaiaStationSensorEntityDescription, ...] = (
    GaiaStationSensorEntityDescription(
        key="co2_latest",
        name="CO₂",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("co2_latest"),
        icon="mdi:molecule-co2",
    ),
    GaiaStationSensorEntityDescription(
        key="co2_mean",
        name="CO₂ Mean",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("co2_mean"),
        icon="mdi:molecule-co2",
    ),
    GaiaStationSensorEntityDescription(
        key="co2_min",
        name="CO₂ Min",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("co2_min"),
        icon="mdi:molecule-co2",
    ),
    GaiaStationSensorEntityDescription(
        key="co2_max",
        name="CO₂ Max",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("co2_max"),
        icon="mdi:molecule-co2",
    ),
    GaiaStationSensorEntityDescription(
        key="co2_median",
        name="CO₂ Median",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("co2_median"),
        icon="mdi:molecule-co2",
    ),
)

MET_SENSORS: tuple[GaiaStationSensorEntityDescription, ...] = (
    GaiaStationSensorEntityDescription(
        key="temperature_latest",
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("temperature_latest"),
        icon="mdi:thermometer",
    ),
    GaiaStationSensorEntityDescription(
        key="humidity_latest",
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("humidity_latest"),
        icon="mdi:water-percent",
    ),
)

SYSTEM_SENSORS: tuple[GaiaStationSensorEntityDescription, ...] = (
    GaiaStationSensorEntityDescription(
        key="sys_vpwr",
        name="Supply Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("sys_vpwr"),
        icon="mdi:flash",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GaiaStationSensorEntityDescription(
        key="sys_heap",
        name="Free Heap Memory",
        native_unit_of_measurement="B",
        device_class=SensorDeviceClass.DATA_SIZE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("sys_heap"),
        icon="mdi:memory",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GaiaStationSensorEntityDescription(
        key="sys_alive",
        name="Uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("sys_alive"),
        icon="mdi:clock-outline",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GaiaStationSensorEntityDescription(
        key="sys_boot",
        name="Boot Count",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("sys_boot"),
        icon="mdi:restart",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

# All static sensor descriptions combined
ALL_STATIC_SENSORS = (
    ROLLING_PM_SENSORS + CO2_SENSORS + MET_SENSORS + SYSTEM_SENSORS
)


def _build_dynamic_pms_sensors(
    data: dict[str, Any],
) -> list[GaiaStationSensorEntityDescription]:
    """Build sensor descriptions for dynamically discovered PMS sensor groups.

    The GAIA station can have pms1, pms2, pms3, etc. We scan the flattened
    data for keys like 'pms1_pm25_latest' and create appropriate sensors.
    """
    sensors: list[GaiaStationSensorEntityDescription] = []
    discovered_groups: set[str] = set()

    # Find all PMS group names from flattened keys
    for key in data:
        for prefix_candidate in ("pms1", "pms2", "pms3"):
            if key.startswith(f"{prefix_candidate}_"):
                discovered_groups.add(prefix_candidate)

    for group in sorted(discovered_groups):
        group_label = group.upper()  # e.g. "PMS1"

        pm_configs = [
            ("pm25", "PM2.5", SensorDeviceClass.PM25, "mdi:blur"),
            ("pm1", "PM1.0", SensorDeviceClass.PM1, "mdi:blur-linear"),
            ("pm10", "PM10", SensorDeviceClass.PM10, "mdi:blur-radial"),
        ]

        for pm_key, pm_label, device_class, icon in pm_configs:
            latest_key = f"{group}_{pm_key}_latest"
            mean_key = f"{group}_{pm_key}_mean"
            min_key = f"{group}_{pm_key}_min"
            max_key = f"{group}_{pm_key}_max"
            median_key = f"{group}_{pm_key}_median"

            if latest_key in data:
                sensors.append(
                    GaiaStationSensorEntityDescription(
                        key=latest_key,
                        name=f"{group_label} {pm_label}",
                        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                        device_class=device_class,
                        state_class=SensorStateClass.MEASUREMENT,
                        value_fn=lambda d, k=latest_key: d.get(k),
                        icon=icon,
                    )
                )
            if mean_key in data:
                sensors.append(
                    GaiaStationSensorEntityDescription(
                        key=mean_key,
                        name=f"{group_label} {pm_label} Mean",
                        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                        device_class=device_class,
                        state_class=SensorStateClass.MEASUREMENT,
                        value_fn=lambda d, k=mean_key: d.get(k),
                        icon=icon,
                    )
                )
            if min_key in data:
                sensors.append(
                    GaiaStationSensorEntityDescription(
                        key=min_key,
                        name=f"{group_label} {pm_label} Min",
                        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                        device_class=device_class,
                        state_class=SensorStateClass.MEASUREMENT,
                        value_fn=lambda d, k=min_key: d.get(k),
                        icon=icon,
                    )
                )
            if max_key in data:
                sensors.append(
                    GaiaStationSensorEntityDescription(
                        key=max_key,
                        name=f"{group_label} {pm_label} Max",
                        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                        device_class=device_class,
                        state_class=SensorStateClass.MEASUREMENT,
                        value_fn=lambda d, k=max_key: d.get(k),
                        icon=icon,
                    )
                )
            if median_key in data:
                sensors.append(
                    GaiaStationSensorEntityDescription(
                        key=median_key,
                        name=f"{group_label} {pm_label} Median",
                        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
                        device_class=device_class,
                        state_class=SensorStateClass.MEASUREMENT,
                        value_fn=lambda d, k=median_key: d.get(k),
                        icon=icon,
                    )
                )

    return sensors


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up GAIA Station sensors based on a config entry."""
    coordinator: GaiaStationDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data or {}

    entities: list[GaiaStationSensor] = []

    # Add static sensors only if their key exists in the flattened data
    for description in ALL_STATIC_SENSORS:
        if description.key in data:
            entities.append(GaiaStationSensor(coordinator, description, entry))

    # Add dynamically discovered PMS sensor group sensors
    dynamic_pms = _build_dynamic_pms_sensors(data)
    for description in dynamic_pms:
        entities.append(GaiaStationSensor(coordinator, description, entry))

    async_add_entities(entities)


class GaiaStationSensor(
    CoordinatorEntity[GaiaStationDataUpdateCoordinator], SensorEntity
):
    """Representation of a GAIA Station sensor."""

    entity_description: GaiaStationSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GaiaStationDataUpdateCoordinator,
        description: GaiaStationSensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "AQICN",
            "model": "GAIA Station",
        }

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
