# Devialet for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

This custom integration for Home Assistant allows you to control your Devialet speaker via IP Control API. It provides full control of your speaker's playback, volume, source selection, and sound settings.

## Features

- Media player entity with playback controls (play, pause, next, previous)
- Volume control (set volume, volume up/down, mute/unmute)
- Source selection (Spotify Connect, AirPlay, UPnP/DLNA, Optical)
- Media information display (artist, album, track)
- Night mode support (requires firmware DOS 2.16 or newer)
- Equalizer with presets (flat, voice, custom) and custom settings
- Additional sensors for detailed status
- Stream information display (codec, lossless status)

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

The integration provides several services to control your Devialet speaker:

- `devialet.set_volume`: Set volume level (0-100)
- `devialet.volume_up`: Increase volume
- `devialet.volume_down`: Decrease volume
- `devialet.play`: Start or resume playback
- `devialet.pause`: Pause playback
- `devialet.mute`: Mute sound
- `devialet.unmute`: Unmute sound
- `devialet.next_track`: Skip to next track
- `devialet.previous_track`: Skip to previous track
- `devialet.set_night_mode`: Enable or disable night mode
- `devialet.set_eq_preset`: Set equalizer preset (flat, voice, custom)
- `devialet.set_custom_eq`: Set custom equalizer settings for low and high frequencies (-12.0 to 12.0 dB)

## Entities Created

### Media Player

- `media_player.devialet`: Main media player entity with volume and playback controls

### Sensors

- `sensor.devialet_volume`: Current volume level
- `sensor.devialet_playback_state`: Current playback state (playing/paused)
- `sensor.devialet_artist`: Current artist
- `sensor.devialet_track`: Current track
- `sensor.devialet_album`: Current album
- `sensor.devialet_stream_info`: Stream information (codec, lossless status)

### Switches

- `switch.devialet_night_mode`: Night mode toggle (if supported by firmware)

## Example Automations

```yaml
# Automatically set volume to 5% when Home Assistant starts
automation:
  - alias: "Set Devialet volume at startup"
    trigger:
      - platform: homeassistant
        event: start
    action:
      - service: devialet.set_volume
        data:
          volume: 5

# Enable night mode at 22:00
automation:
  - alias: "Enable night mode in the evening"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: devialet.set_night_mode
        data:
          night_mode: true

# Set voice EQ preset for TV source
automation:
  - alias: "Set voice EQ for TV"
    trigger:
      - platform: state
        entity_id: media_player.devialet
        to: "tv"
    action:
      - service: devialet.set_eq_preset
        data:
          preset: "voice"
```

## Troubleshooting

- If the integration cannot connect to your Devialet speaker, make sure:
  - The IP address is correct
  - The speaker is powered on and connected to your network
  - Your Home Assistant instance can reach the speaker on your network
- Night mode and EQ features require firmware DOS 2.16 or newer
- Check the 'availableFeatures' list in the system-info response to verify supported features

## Supported Devices

This integration has been tested with:
- Phantom I
- Phantom II

It should work with any Devialet device that supports the IP Control API.

## API Documentation

This integration is based on the official Devialet IP Control API documentation:
- Devialet IP Control - Reference API Documentation (Revision 1 - December 2021)

## Contributions

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
