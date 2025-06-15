"""Constants for the Devialet IP Control integration."""

DOMAIN = "devialet"

# Configuration
CONF_HOST = "host"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_NAME = "Devialet Speaker"
DEFAULT_SCAN_INTERVAL = 10

# Services
SERVICE_SET_VOLUME = "set_volume"
SERVICE_VOLUME_UP = "volume_up"
SERVICE_VOLUME_DOWN = "volume_down"
SERVICE_PLAY = "play"
SERVICE_PAUSE = "pause"
SERVICE_MUTE = "mute"
SERVICE_UNMUTE = "unmute"
SERVICE_NEXT = "next_track"
SERVICE_PREVIOUS = "previous_track"
SERVICE_SET_NIGHT_MODE = "set_night_mode"
SERVICE_SET_EQ_PRESET = "set_eq_preset"
SERVICE_SET_CUSTOM_EQ = "set_custom_eq"
SERVICE_POWER_OFF_SYSTEM = "power_off_system"

# Attributes
ATTR_VOLUME = "volume"
ATTR_SOURCE_ID = "source_id"
ATTR_NIGHT_MODE = "night_mode"
ATTR_EQ_PRESET = "preset"
ATTR_EQ_LOW = "low"
ATTR_EQ_HIGH = "high"

# API Endpoints
API_BASE = "/ipcontrol/v1"
API_DEVICES_CURRENT = f"{API_BASE}/devices/current"
API_SYSTEMS_CURRENT = f"{API_BASE}/systems/current"
API_VOLUME = f"{API_BASE}/systems/current/sources/current/soundControl/volume"
API_VOLUME_UP = f"{API_BASE}/systems/current/sources/current/soundControl/volumeUp"
API_VOLUME_DOWN = f"{API_BASE}/systems/current/sources/current/soundControl/volumeDown"
API_PLAY = f"{API_BASE}/groups/current/sources/current/playback/play"
API_PAUSE = f"{API_BASE}/groups/current/sources/current/playback/pause"
API_MUTE = f"{API_BASE}/groups/current/sources/current/playback/mute"
API_UNMUTE = f"{API_BASE}/groups/current/sources/current/playback/unmute"
API_NEXT = f"{API_BASE}/groups/current/sources/current/playback/next"
API_PREVIOUS = f"{API_BASE}/groups/current/sources/current/playback/previous"
API_SOURCES = f"{API_BASE}/groups/current/sources"
API_CURRENT_SOURCE = f"{API_BASE}/groups/current/sources/current"
API_PLAY_SOURCE = f"{API_BASE}/groups/current/sources/{{source_id}}/playback/play"
API_NIGHT_MODE = f"{API_BASE}/systems/current/settings/audio/nightMode"
API_EQUALIZER = f"{API_BASE}/systems/current/settings/audio/equalizer"
API_SYSTEM_POWER_OFF = f"{API_BASE}/systems/current/powerOff"

# EQ Presets
EQ_PRESET_FLAT = "flat"
EQ_PRESET_VOICE = "voice"
EQ_PRESET_CUSTOM = "custom"
