# GAIA Station Air Quality Monitor

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/cyberjunky/home-assistant-gaia_station.svg)](https://github.com/cyberjunky/home-assistant-gaia_station/releases)
[![License](https://img.shields.io/github/license/cyberjunky/home-assistant-gaia_station.svg)](LICENSE)

Home Assistant integration for [GAIA air quality monitoring stations](https://aqicn.org/gaia/) (A08, A12, A18).

Monitor your local air quality directly from your GAIA station over your local network — no cloud required.

## Features

- **Particulate Matter**: PM2.5, PM1.0, PM10 readings from each PMS sensor (latest, mean, min, max, median)
- **Rolling Averages**: PM2.5, PM1.0, PM10 rolling average values
- **CO₂ Monitoring**: CO₂ concentration (latest, mean, min, max, median) — if your station model has a CO₂ sensor
- **Meteorological**: Temperature and humidity — if your station model has a weather sensor
- **System Diagnostics**: Supply voltage, free memory, uptime, boot count (disabled by default)
- **Dynamic Sensor Discovery**: Only sensors for data your specific station model provides are created

## Supported Models

| Model | PM Sensors | CO₂ | Temperature/Humidity |
|-------|-----------|-----|---------------------|
| GAIA A08 | 1–2x PMS 5003 | Optional (SCD-41) | AHT-20 |
| GAIA A12 | 3x PMS 5003 | Sensirion SCD4x | Yes |
| GAIA A18 | 3x PMS 5003 | Sensirion SCD4x | Yes |

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click **Integrations** → **⋮** → **Custom repositories**
3. Add `https://github.com/cyberjunky/home-assistant-gaia_station` as an **Integration**
4. Search for "GAIA Station" and install it
5. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/gaia_station` directory to your Home Assistant `custom_components` folder
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **GAIA Station**
3. Enter the IP address of your GAIA station (e.g., `192.168.2.154`)
4. The integration will automatically detect available sensors based on your station model

## How It Works

The integration polls your GAIA station's local `/realtime/` HTTP endpoint at 60-second intervals. The station returns a JSON response containing all sensor readings. The integration dynamically creates Home Assistant sensor entities for whatever data your specific station model provides.

## Available Sensors

### Air Quality (per PMS sensor group)
- **PM2.5** — Fine particulate matter (µg/m³)
- **PM1.0** — Ultra-fine particulate matter (µg/m³)
- **PM10** — Coarse particulate matter (µg/m³)
- Plus mean, min, max, median statistics for each

### Rolling Averages
- **PM2.5 Rolling / Mean** — Smoothed PM2.5 values
- **PM1.0 Rolling / Mean** — Smoothed PM1.0 values
- **PM10 Rolling / Mean** — Smoothed PM10 values

### CO₂ (if your model supports it)
- **CO₂** — Carbon dioxide concentration (ppm)
- **CO₂ Mean / Min / Max / Median** — Statistical values

### Meteorological (if your model supports it)
- **Temperature** — Ambient temperature (°C)
- **Humidity** — Relative humidity (%)

### System Diagnostics (disabled by default)
- **Supply Voltage** — Power supply voltage (mV)
- **Free Heap Memory** — Available memory (bytes)
- **Uptime** — Time since last restart (seconds)
- **Boot Count** — Number of reboots

## Requirements

- A GAIA air quality station (A08, A12, or A18) connected to your local network
- The station must be accessible via HTTP on your network

## Links

- [GAIA Station Product Page](https://aqicn.org/gaia/)
- [GAIA A12 Setup Guide](https://aqicn.org/gaia/setup/A12/)
- [GAIA A08 Arduino Source](https://github.com/aqicn/gaia-a08-arduino)
- [Report an Issue](https://github.com/cyberjunky/home-assistant-gaia_station/issues)

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
