"""API client for Devialet IP Control."""
import logging
import requests
from urllib.parse import urljoin
import json

from .const import (
    API_DEVICES_CURRENT,
    API_SYSTEMS_CURRENT,
    API_VOLUME,
    API_VOLUME_UP,
    API_VOLUME_DOWN,
    API_PLAY,
    API_PAUSE,
    API_MUTE,
    API_UNMUTE,
    API_NEXT,
    API_PREVIOUS,
    API_SOURCES,
    API_CURRENT_SOURCE,
    API_PLAY_SOURCE,
    API_NIGHT_MODE,
    API_EQUALIZER,
    EQ_PRESET_FLAT,
    EQ_PRESET_VOICE,
    EQ_PRESET_CUSTOM,
)

_LOGGER = logging.getLogger(__name__)

class DevialetAPI:
    """API Client for Devialet IP Control."""

    def __init__(self, host):
        """Initialize the API client."""
        self.host = host
        self.base_url = f"http://{host}"
        self.headers = {"Content-Type": "application/json"}
        self.timeout = 5

    def _get_url(self, endpoint):
        """Get full URL for endpoint."""
        return urljoin(self.base_url, endpoint)

    def _handle_response(self, response):
        """Handle the API response and check for errors."""
        if response.status_code != 200:
            _LOGGER.error(
                "API request failed with status code %s: %s",
                response.status_code,
                response.text,
            )
            return None

        try:
            data = response.json()
            if "error" in data:
                _LOGGER.error(
                    "API returned error: %s", 
                    json.dumps(data["error"])
                )
                return None
            return data
        except ValueError as exc:
            _LOGGER.error("Failed to parse response as JSON: %s", exc)
            return None

    def get(self, endpoint):
        """Make a GET request to the API."""
        try:
            url = self._get_url(endpoint)
            response = requests.get(url, timeout=self.timeout)
            return self._handle_response(response)
        except requests.RequestException as exc:
            _LOGGER.error("Failed to make GET request to %s: %s", endpoint, exc)
            return None

    def post(self, endpoint, data=None):
        """Make a POST request to the API."""
        if data is None:
            data = {}
            
        try:
            url = self._get_url(endpoint)
            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.RequestException as exc:
            _LOGGER.error("Failed to make POST request to %s: %s", endpoint, exc)
            return None

    def get_device_info(self):
        """Get device information including serial number and firmware version."""
        return self.get(API_DEVICES_CURRENT)

    def get_system_info(self):
        """Get system information including firmware version."""
        return self.get(API_SYSTEMS_CURRENT)

    def get_firmware_version(self):
        """Get firmware version from system info."""
        system_info = self.get_system_info()
        if system_info and "firmwareVersion" in system_info:
            return system_info.get("firmwareVersion")
        return None

    def get_volume(self):
        """Get current volume."""
        return self.get(API_VOLUME)

    def set_volume(self, volume):
        """Set volume (0-100)."""
        volume = max(0, min(100, volume))
        return self.post(API_VOLUME, {"volume": volume})

    def volume_up(self):
        """Increase volume."""
        return self.post(API_VOLUME_UP)

    def volume_down(self):
        """Decrease volume."""
        return self.post(API_VOLUME_DOWN)

    def play(self):
        """Play current source."""
        return self.post(API_PLAY)

    def pause(self):
        """Pause current source."""
        return self.post(API_PAUSE)

    def mute(self):
        """Mute current source."""
        return self.post(API_MUTE)

    def unmute(self):
        """Unmute current source."""
        return self.post(API_UNMUTE)

    def next_track(self):
        """Skip to next track."""
        return self.post(API_NEXT)

    def previous_track(self):
        """Skip to previous track."""
        return self.post(API_PREVIOUS)

    def get_sources(self):
        """Get available sources."""
        return self.get(API_SOURCES)

    def get_current_source(self):
        """Get current playback state."""
        return self.get(API_CURRENT_SOURCE)

    def play_source(self, source_id):
        """Play a specific source."""
        endpoint = API_PLAY_SOURCE.format(source_id=source_id)
        return self.post(endpoint)

    def get_night_mode(self):
        """Get night mode status."""
        return self.get(API_NIGHT_MODE)

    def set_night_mode(self, enabled: bool):
        """Set night mode on or off."""
        return self.post(API_NIGHT_MODE, {"nightMode": "on" if enabled else "off"})

    def get_equalizer(self):
        """Get equalizer settings."""
        return self.get(API_EQUALIZER)

    def set_eq_preset(self, preset: str):
        """Set equalizer preset."""
        if preset not in [EQ_PRESET_FLAT, EQ_PRESET_VOICE, EQ_PRESET_CUSTOM]:
            _LOGGER.error("Invalid EQ preset: %s", preset)
            return None
        return self.post(API_EQUALIZER, {"preset": preset})

    def set_custom_eq(self, low: float = 0.0, high: float = 0.0):
        """Set custom equalizer settings."""
        data = {
            "preset": EQ_PRESET_CUSTOM,
            "customEqualization": {
                "low": {"gain": low},
                "high": {"gain": high}
            }
        }
        return self.post(API_EQUALIZER, data)
