# Fronius Wattpilot Integration for Home Assistant

Custom Home Assistant integration for monitoring and controlling Fronius Wattpilot EV chargers using a reverse-engineered WebSocket API.

## Features

- **Comprehensive Control**: Switch between charging modes (Default, Eco, Next Trip), start/stop charging, and configure charging behavior
- **Real-Time Monitoring**: Track charging status, power consumption, energy usage, and vehicle connection state
- **Multiple Connection Options**: Connect via local LAN (WebSocket) or Fronius Cloud
- **Device Compatibility**: Works with Wattpilot Home 11J, Wattpilot Home 22J, and Wattpilot Flex
- **Next Trip Planning**: Configure departure times via service calls with input_datetime synchronization
- **Automation Friendly**: Full integration with Home Assistant automations and scripts

## Installation

1. Install via HACS (recommended) or manually copy the wattpilot folder to custom_components/
2. Restart Home Assistant
3. Go to Settings, Devices and Services, Add Integration
4. Search for Fronius Wattpilot
5. Choose Local (IP + password) or Cloud (serial + credentials) connection

## Screenshots

### Device View
![screenshot of Wattpilot Device](doc/device_view1.jpg)
![screenshot of Wattpilot Device](doc/device_view2.jpg)
![screenshot of Wattpilot Device](doc/device_view3.jpg)

### Service Call
![screenshot of Next Trip service](doc/service_view1.jpg)

## Credits

Based on the excellent work by [@joscha82](https://github.com/joscha82) on the [wattpilot python module](https://github.com/joscha82/wattpilot).

Originally developed by [@mk-maddin](https://github.com/mk-maddin).

## Disclaimer

This integration is not officially associated with or endorsed by Fronius. It uses a reverse-engineered API and may stop working at any time. Use at your own risk.

## License

[MIT](LICENSE)
