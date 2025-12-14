# Fronius Wattpilot Integration for Home Assistant

[![HACS Integration](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/release/ruaan-deysel/ha-wattpilot.svg)](https://github.com/ruaan-deysel/ha-wattpilot/releases)
[![License](https://img.shields.io/github/license/ruaan-deysel/ha-wattpilot.svg)](LICENSE)

Custom Home Assistant integration for monitoring and controlling Fronius Wattpilot EV chargers using a reverse-engineered WebSocket API.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ruaan-deysel&repository=ha-wattpilot&category=integration)

## Features

- **Comprehensive Control**: Switch between charging modes (Default, Eco, Next Trip), start/stop charging, and configure charging behavior
- **Real-Time Monitoring**: Track charging status, power consumption, energy usage, and vehicle connection state
- **Multiple Connection Options**: Connect via local LAN (WebSocket) or Fronius Cloud
- **Device Compatibility**: Works with Wattpilot Home 11J, Wattpilot Home 22J, and Wattpilot Flex
- **Next Trip Planning**: Configure departure times via service calls with input_datetime synchronization
- **Automation Friendly**: Full integration with Home Assistant automations and scripts

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ruaan-deysel&repository=ha-wattpilot&category=integration)

**Manual HACS Installation:**

1. Open HACS in Home Assistant
2. Go to Integrations
3. Click the ⋮ menu → Custom repositories
4. Add this repository: `https://github.com/ruaan-deysel/ha-wattpilot`
5. Category: Integration
6. Click Add
7. Search for "Fronius Wattpilot"
8. Click Download
9. Restart Home Assistant

### Manual

1. Download the latest release from the [Releases](https://github.com/ruaan-deysel/ha-wattpilot/releases) page
2. Extract the `wattpilot` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click + Add Integration
3. Search for "Fronius Wattpilot"
4. Choose your connection type:
   - **Local**: Enter your charger's IP address and password
   - **Cloud**: Enter your Wattpilot serial number and Fronius account credentials

## Entities

### Controls
- **Charging Mode**: Switch between Default, Eco, and Next Trip modes
- **Force State**: Control charging (Neutral, Off, On)
- **Cable Lock**: Lock/unlock the charging cable

### Sensors
- **Car State**: Vehicle connection and charging status
- **Power**: Current charging power (W/kW)
- **Current**: Charging current per phase (A)
- **Voltage**: Voltage per phase (V)
- **Energy**: Session energy and total energy counters
- **Temperature**: Charger temperature readings

### Diagnostics
- **Connection Status**: Online/offline state
- **Firmware Version**: Current firmware information
- **Error Codes**: Active error states

## Services

The integration provides several services for advanced control:

- `wattpilot.set_next_trip` - Set departure time for Next Trip mode
- `wattpilot.set_go_current` - Set charging current for portable chargers
- `wattpilot.connect` - Manually connect to the charger
- `wattpilot.disconnect` - Manually disconnect from the charger

### Example: Next Trip Automation

```yaml
automation:
  - alias: "Set Wattpilot Next Trip"
    trigger:
      - platform: state
        entity_id: input_datetime.wattpilot_departure
    action:
      - service: wattpilot.set_next_trip
        data:
          device_id: !input wattpilot_device
          departure_time: "{{ states('input_datetime.wattpilot_departure') }}"
```

See [packages/wattpilot/](packages/wattpilot/) for complete automation examples.

## Troubleshooting

### Common Issues

**Cannot Connect (Local)**
- Verify the charger's IP address is correct
- Ensure Home Assistant can reach the charger on your network
- Check that the password matches (found in the Wattpilot app)

**Cannot Connect (Cloud)**
- Verify your Fronius account credentials
- Ensure the serial number is correct
- Check your internet connection

**Entities Not Updating**
- Check connection status in logs
- Verify WebSocket connection is active
- Try reloading the integration

### Debug Logging

Enable debug logging by adding to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.wattpilot: debug
```

## Screenshots

### Device View
![screenshot of Wattpilot Device](doc/device_view1.jpg)
![screenshot of Wattpilot Device](doc/device_view2.jpg)
![screenshot of Wattpilot Device](doc/device_view3.jpg)

### Service Call
![screenshot of Next Trip service](doc/service_view1.jpg)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run linting: `./scripts/lint`
5. Submit a pull request

### Development Setup

```bash
git clone https://github.com/ruaan-deysel/ha-wattpilot.git
cd ha-wattpilot
./scripts/setup    # Install dependencies
./scripts/develop  # Start Home Assistant dev instance
```

## Credits

Based on the excellent work by [@joscha82](https://github.com/joscha82) on the [wattpilot python module](https://github.com/joscha82/wattpilot).

Originally developed by [@mk-maddin](https://github.com/mk-maddin).

## Disclaimer

This integration is not officially associated with or endorsed by Fronius. Fronius trademarks belong to Fronius International GmbH. This integration is independently developed using a reverse-engineered API and may stop working at any time.

**Use at your own risk.** Neither the contributors nor maintainers are responsible for any damage caused by this integration.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2023 Martin Dagarin (@mk-maddin) - Original Author  
Copyright (c) 2024-2025 Ruaan Deysel (@ruaan-deysel) - Current Maintainer

See [NOTICE](NOTICE) file for additional attribution information.
