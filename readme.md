# Devialet for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This custom integration for Home Assistant allows you to control your Devialet speaker via IP Control API. It provides full control of your speaker's playback, volume, source selection, and sound settings.

## Features

- Media playback control (play, pause, stop)
- Volume control
- Source selection
- Equalizer control with presets and custom settings
- Night mode control
- System reboot (requires DOS >= 2.16)
- System power off
- Device information (firmware version, serial number, local IP)

## Installation

### HACS (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Add this repository as a custom repository in HACS:
   - Go to HACS > Integrations
   - Click the three dots in the upper right corner
   - Select "Custom repositories"
   - Add the URL of this repository and select "Integration" as the category
3. Search for "Devialet" in HACS and install it
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/devialet` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

After installation:

1. Go to Home Assistant > Settings > Devices & Services
2. Click "+ Add Integration" and search for "Devialet"
3. Enter the IP address of your Devialet speaker
4. Complete the setup

## Services

The integration provides the following services:

- `devialet_play`: Start playback
- `devialet_pause`: Pause playback
- `devialet_stop`: Stop playback
- `devialet_volume_set`: Set volume level (0-100)
- `devialet_volume_mute`: Mute/unmute
- `devialet_volume_up`: Increase volume
- `devialet_volume_down`: Decrease volume
- `devialet_select_source`: Select input source
- `devialet_set_equalizer`: Set equalizer preset or custom settings
- `devialet_set_night_mode`: Enable/disable night mode
- `devialet_reboot_system`: Reboot the Devialet system (requires DOS >= 2.16)
- `devialet_power_off_system`: Power off the Devialet system

## Media Player Card

The integration adds a media player card to Home Assistant with the following features:

- Play/pause/stop controls
- Volume control
- Source selection
- Equalizer control
- Night mode toggle
- Reboot button (if firmware version >= 2.16)
- Power off button
- Device information display (firmware version, serial number, local IP)

## Requirements

- Home Assistant 2024.1.0 or later
- Devialet speaker with DOS firmware
- For reboot functionality: DOS firmware version 2.16.0 or later

## Limitations

- The speaker cannot be powered on via the API after using the power off function
- Reboot functionality requires DOS firmware version 2.16.0 or later

## Entities Created

### Media Player

- `