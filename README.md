[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
![Project Maintenance][maintenance-shield]

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-blue.svg?style=for-the-badge&logo=paypal)](https://www.paypal.me/cyberjunkynl/)
[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-GitHub-red.svg?style=for-the-badge&logo=github)](https://github.com/sponsors/cyberjunky)

# GAIA Station Air Quality Monitor

A Home Assistant custom integration that monitors [GAIA air quality stations](https://aqicn.org/gaia/) (A08, A12, A18) over your local network. Get real-time insights into particulate matter, CO₂ levels, and more — no cloud required.

## Supported Features

Monitor your GAIA station with these sensors (created dynamically based on your model):

### Air Quality (per PMS sensor group)

- **PM2.5** - Fine particulate matter (µg/m³)
- **PM1.0** - Ultra-fine particulate matter (µg/m³)
- **PM10** - Coarse particulate matter (µg/m³)
- Plus mean, min, max, median statistics for each

### Rolling Averages

- **PM2.5 Rolling / Mean** - Smoothed PM2.5 values (µg/m³)
- **PM1.0 Rolling / Mean** - Smoothed PM1.0 values (µg/m³)
- **PM10 Rolling / Mean** - Smoothed PM10 values (µg/m³)

### CO₂ (if your model supports it)

- **CO₂** - Carbon dioxide concentration (ppm)
- **CO₂ Mean / Min / Max / Median** - Statistical values

### Meteorological (if your model supports it)

- **Temperature** - Ambient temperature (°C)
- **Humidity** - Relative humidity (%)

### System Diagnostics (disabled by default)

- **Supply Voltage** - Power supply voltage (mV)
- **Free Heap Memory** - Available memory (bytes)
- **Uptime** - Time since last restart (seconds)
- **Boot Count** - Number of reboots

All sensors are created automatically based on what data your specific station model provides and grouped under a single device for easy management.

## Supported Models

| Model | PM Sensors | CO₂ | Temperature/Humidity |
|-------|-----------|-----|---------------------|
| GAIA A08 | 1–2x PMS 5003 | Optional (SCD-41) | AHT-20 |
| GAIA A12 | 3x PMS 5003 | Sensirion SCD4x | Yes |
| GAIA A18 | 3x PMS 5003 | Sensirion SCD4x | Yes |

## Requirements

- **GAIA air quality station** (A08, A12, or A18) with WiFi connectivity
- **Station IP address** accessible from Home Assistant

## Installation

### HACS (Recommended)

This integration is not yet in the default HACS repository. You need to add it as a custom repository first:

1. Install [HACS](https://hacs.xyz) if not already installed
2. Open HACS in Home Assistant
3. Click the **⋮** menu (top right) → **Custom repositories**
4. Add `https://github.com/cyberjunky/home-assistant-gaia_station` with category **Integration**
5. Search for "GAIA Station" in HACS
6. Click **Download**
7. Restart Home Assistant
8. Add via Settings → Devices & Services

### Manual Installation

1. Copy the `custom_components/gaia_station` folder to your `<config>/custom_components/` directory
2. Restart Home Assistant
3. Add via Settings → Devices & Services

## Configuration

### Adding the Integration

1. Navigate to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **"GAIA Station"**
4. Enter your configuration:
   - **Host**: Your station's IP address (e.g., `192.168.2.154`)

The integration connects to your station's local `/realtime/` endpoint, validates the connection and creates all sensors automatically. Disable sensors you don't need via **Settings** → **Devices & Services** → **GAIA Station** → click a sensor → cogwheel icon → "Enable entity" toggle.

## Advanced Usage

### Automation Examples

Alert on poor air quality:

```yaml
automation:
  - alias: "PM2.5 Air Quality Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.gaia_station_192_168_2_154_pm2_5_rolling
        above: 50
        for:
          minutes: 10
    action:
      - service: notify.mobile_app
        data:
          message: "Warning: PM2.5 level is {{ states('sensor.gaia_station_192_168_2_154_pm2_5_rolling') }} µg/m³!"
```

Monitor CO₂ levels:

```yaml
automation:
  - alias: "High CO2 Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.gaia_station_192_168_2_154_co2
        above: 1000
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          message: >
            CO₂ level is high: {{ states('sensor.gaia_station_192_168_2_154_co2') }} ppm.
            Consider ventilating the room.
```

## Troubleshooting

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.gaia_station: debug
```

Alternatively, enable debug logging via the UI in **Settings** → **Devices & Services** → **GAIA Station** → **Enable debug logging**:

![Enable Debug Logging](screenshots/enabledebug.png)

Then perform any steps to reproduce the issue and disable debug logging again. It will download the relevant log file automatically.

### Common Issues

**Integration won't connect:**

- Verify your station's IP address is correct
- Ensure the station is powered on and connected to your WiFi network
- Try accessing `http://YOUR_IP/realtime/` in a browser to verify the station is responding

**Sensors show "Unavailable":**

- Check network connectivity to the station
- Verify the station's WiFi connection is stable
- Check debug logs for error messages

**Missing sensors (CO₂, temperature, humidity):**

- This is expected if your station model doesn't include those sensors
- The integration only creates sensors for data your station actually provides
- For example, the `met` section may be empty on some models

## Development

Quick-start (from project root):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements_lint.txt
./scripts/lint    # runs pre-commit + vulture
# or: ruff check .
# to auto-fix: ruff check . --fix
```

## 💖 Support This Project

If you find this integration useful, please consider supporting its continued development:

### 🌟 Ways to Support

- **⭐ Star this repository** - Help others discover the project
- **💰 Financial Support** - Contribute to development and hosting costs
- **🐛 Report Issues** - Help improve stability and compatibility
- **📖 Spread the Word** - Share with other air quality enthusiasts

### 💳 Financial Support Options

[![Donate via PayPal](https://img.shields.io/badge/Donate-PayPal-blue.svg?style=for-the-badge&logo=paypal)](https://www.paypal.me/cyberjunkynl/)
[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-GitHub-red.svg?style=for-the-badge&logo=github)](https://github.com/sponsors/cyberjunky)

## Links

- [GAIA Station Product Page](https://aqicn.org/gaia/)
- [GAIA A12 Setup Guide](https://aqicn.org/gaia/setup/A12/)
- [GAIA A08 Arduino Source](https://github.com/aqicn/gaia-a08-arduino)
- [Report an Issue](https://github.com/cyberjunky/home-assistant-gaia_station/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

[releases-shield]: https://img.shields.io/github/release/cyberjunky/home-assistant-gaia_station.svg?style=for-the-badge
[releases]: https://github.com/cyberjunky/home-assistant-gaia_station/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/cyberjunky/home-assistant-gaia_station.svg?style=for-the-badge
[commits]: https://github.com/cyberjunky/home-assistant-gaia_station/commits/main
[license-shield]: https://img.shields.io/github/license/cyberjunky/home-assistant-gaia_station.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-cyberjunky-blue.svg?style=for-the-badge
