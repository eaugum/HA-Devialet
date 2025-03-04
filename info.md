# Devialet

Control your Devialet speaker through Home Assistant using the Devialet IP Control API.

## Features

- 🎵 Media player entity with full playback controls
- 🔊 Volume control (set exact volume, volume up/down, mute/unmute)
- 📊 Detailed sensors for volume, current track, artist, album, and stream info
- 🎯 Source selection (Spotify Connect, AirPlay, UPnP/DLNA, Optical)
- 🌙 Night mode support (requires firmware DOS 2.16 or newer)
- 🎚️ Equalizer with presets (flat, voice, custom) and custom settings (-12.0 to 12.0 dB)
- ⚙️ Configuration via UI
- 🔄 Regular status updates
- 🔌 Night mode switch (if supported by firmware)

## Setup

1. Add the integration through the Home Assistant UI
2. Enter the IP address of your Devialet speaker
3. Configure the update interval if desired (default: 10 seconds)

## Services

Several services are available to control your Devialet speaker:

- Set specific volume (0-100)
- Volume up/down
- Playback control (play, pause, next, previous)
- Mute/unmute
- Night mode on/off
- Set EQ preset (flat, voice, custom)
- Set custom EQ settings (low and high frequencies, -12.0 to 12.0 dB)

## Requirements

- Devialet speaker (Phantom I, Phantom II, etc.) with firmware DOS 2.16 or newer
- Speaker must be on the same network as your Home Assistant instance
- Speaker must support the IP Control API
