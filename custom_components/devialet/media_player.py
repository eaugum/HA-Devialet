"""Support for Devialet IP Control media players."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import timedelta

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    BrowseMedia,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
import homeassistant.util.dt as dt_util

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    EQ_PRESET_FLAT,
    EQ_PRESET_VOICE,
    EQ_PRESET_CUSTOM,
)
from .devialet_api import DevialetAPI

_LOGGER = logging.getLogger(__name__)

# Supported features
SUPPORT_DEVIALET = (
    MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.STOP  # Using pause as stop
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.SELECT_SOUND_MODE  # For EQ presets
    | MediaPlayerEntityFeature.BROWSE_MEDIA  # Add browse media support
    | MediaPlayerEntityFeature.TURN_ON  # Using this for reboot button
)

# Custom feature for reboot
SUPPORT_REBOOT = MediaPlayerEntityFeature.TURN_ON << 1

# Night mode feature flag
SUPPORT_NIGHT_MODE = MediaPlayerEntityFeature.SELECT_SOUND_MODE << 1

# Sound modes (EQ presets)
SOUND_MODES = [
    EQ_PRESET_FLAT,
    EQ_PRESET_VOICE,
    EQ_PRESET_CUSTOM,
]

# Sound mode mapping
SOUND_MODE_MAPPING = {
    EQ_PRESET_FLAT: "Flat",
    EQ_PRESET_VOICE: "Voice",
    EQ_PRESET_CUSTOM: "Custom",
    "night_mode": "Night Mode",  # Add night mode to sound modes
}

# Night mode options
NIGHT_MODE_OPTIONS = ["Normal", "Night Mode"]

# Night mode mapping
NIGHT_MODE_MAPPING = {
    "Normal": False,
    "Night Mode": True,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Devialet IP Control media player based on config_entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    api = entry_data["api"]
    scan_interval = entry_data["scan_interval"]
    
    # Create coordinator for updating data
    coordinator = DevialetDataUpdateCoordinator(
        hass,
        api=api,
        name=f"{DOMAIN}_{entry.entry_id}",
        update_interval=timedelta(seconds=scan_interval),
    )
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator in hass.data for sensor.py to use
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator
    
    # Add media player entity
    async_add_entities([DevialetMediaPlayer(coordinator, entry)], True)


class DevialetDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Devialet data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: DevialetAPI,
        name: str,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=update_interval,
        )
        self.api = api

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the Devialet API."""
        data = {}
        
        # Get device info first for serial number and firmware version
        data["device_info"] = await self.hass.async_add_executor_job(
            self.api.get_device_info
        )
        
        # Get system info
        data["system_info"] = await self.hass.async_add_executor_job(
            self.api.get_system_info
        )
        
        # Get current playback state and volume
        data["playback"] = await self.hass.async_add_executor_job(
            self.api.get_current_source
        )
        data["volume"] = await self.hass.async_add_executor_job(
            self.api.get_volume
        )
        data["sources"] = await self.hass.async_add_executor_job(
            self.api.get_sources
        )
        data["night_mode"] = await self.hass.async_add_executor_job(
            self.api.get_night_mode
        )
        data["equalizer"] = await self.hass.async_add_executor_job(
            self.api.get_equalizer
        )
        
        return data


class DevialetMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """Representation of a Devialet media player."""

    def __init__(
        self,
        coordinator: DevialetDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the Devialet media player."""
        super().__init__(coordinator)
        self.api = coordinator.api
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_name = DEFAULT_NAME
        self._attr_supported_features = SUPPORT_DEVIALET
        self._source_mapping = {}
        self._night_mode_available = False

    @property
    def device_info(self):
        """Return device information about this Devialet device."""
        device_name = None
        model = None
        firmware_version = None
        serial_number = None
        
        if self.coordinator.data:
            # Get device info
            device_info = self.coordinator.data.get("device_info", {})
            if device_info:
                firmware_version = device_info.get("release", {}).get("canonicalVersion")
                serial_number = device_info.get("serial")
                device_name = device_info.get("deviceName", "Devialet Speaker")
                model = device_info.get("model", "Phantom")

        info = {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": device_name or self._attr_name,
            "manufacturer": "Devialet",
            "model": model,
            "sw_version": firmware_version,
            "serial_number": serial_number,
        }
        return info

    @property
    def available(self) -> bool:
        """Return if the media player is available."""
        return self.coordinator.last_update_success

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the state of the media player."""
        if not self.coordinator.data or not self.coordinator.data.get("playback"):
            return MediaPlayerState.IDLE

        playback = self.coordinator.data["playback"]
        playing_state = playback.get("playingState")
        
        if playing_state == "playing":
            return MediaPlayerState.PLAYING
        elif playing_state == "paused":
            return MediaPlayerState.PAUSED
        return MediaPlayerState.IDLE

    @property
    def volume_level(self) -> float | None:
        """Return the volume level."""
        if not self.coordinator.data or not self.coordinator.data.get("volume"):
            return None
        
        volume_data = self.coordinator.data["volume"]
        volume = volume_data.get("volume")
        
        if volume is not None:
            return volume / 100.0
        return None

    @property
    def is_volume_muted(self) -> bool | None:
        """Return whether the media player is muted."""
        if not self.coordinator.data or not self.coordinator.data.get("playback"):
            return None
        
        playback = self.coordinator.data["playback"]
        mute_state = playback.get("muteState")
        
        return mute_state == "muted"

    @property
    def media_title(self) -> str | None:
        """Return the title of current playing media."""
        if not self.coordinator.data or not self.coordinator.data.get("playback"):
            return None
        
        playback = self.coordinator.data["playback"]
        metadata = playback.get("metadata", {})
        
        return metadata.get("title")

    @property
    def media_artist(self) -> str | None:
        """Return the artist of current playing media."""
        if not self.coordinator.data or not self.coordinator.data.get("playback"):
            return None
        
        playback = self.coordinator.data["playback"]
        metadata = playback.get("metadata", {})
        
        return metadata.get("artist")

    @property
    def media_album_name(self) -> str | None:
        """Return the album of current playing media."""
        if not self.coordinator.data or not self.coordinator.data.get("playback"):
            return None
        
        playback = self.coordinator.data["playback"]
        metadata = playback.get("metadata", {})
        
        return metadata.get("album")

    @property
    def media_content_type(self) -> str | None:
        """Return the content type of current playing media."""
        return "music"

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        if not self.coordinator.data or not self.coordinator.data.get("playback"):
            return None
        
        playback = self.coordinator.data["playback"]
        source = playback.get("source", {})
        
        if source:
            source_type = source.get("type")
            if source_type:
                return self._format_source_name(source_type)
        return None

    def _format_source_name(self, source_type: str) -> str:
        """Format source type to a more readable name."""
        source_mapping = {
            "spotifyconnect": "Spotify Connect",
            "airplay2": "AirPlay",
            "upnp": "UPnP/DLNA",
            "optical": "Optical"
        }
        
        return source_mapping.get(source_type.lower(), source_type)

    @property
    def source_list(self) -> list[str] | None:
        """List of available input sources."""
        if not self.coordinator.data or not self.coordinator.data.get("sources"):
            return None
        
        sources = self.coordinator.data["sources"]
        source_list = sources.get("sources", [])
        
        if source_list:
            # Create a mapping of source types to readable names
            source_types = {}
            for source in source_list:
                source_type = source.get("type")
                if source_type and source_type.lower() not in ["bluetooth", "raat"]:  # Filter out Bluetooth and Roon
                    # Store mapping of source ID to type for select_source
                    formatted_name = self._format_source_name(source_type)
                    self._source_mapping[formatted_name] = source.get("sourceId")
                    source_types[formatted_name] = True
            
            return list(source_types.keys())
        return None

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        if source not in self._source_mapping:
            _LOGGER.error("Source %s not found in available sources", source)
            return
        
        source_id = self._source_mapping[source]
        await self.hass.async_add_executor_job(self.api.play_source, source_id)
        await self.coordinator.async_request_refresh()

    async def async_volume_up(self) -> None:
        """Increase volume level."""
        await self.hass.async_add_executor_job(self.api.volume_up)
        await self.coordinator.async_request_refresh()

    async def async_volume_down(self) -> None:
        """Decrease volume level."""
        await self.hass.async_add_executor_job(self.api.volume_down)
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        volume_percent = int(volume * 100)
        await self.hass.async_add_executor_job(self.api.set_volume, volume_percent)
        await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        if mute:
            await self.hass.async_add_executor_job(self.api.mute)
        else:
            await self.hass.async_add_executor_job(self.api.unmute)
        await self.coordinator.async_request_refresh()

    async def async_media_play(self) -> None:
        """Send play command."""
        await self.hass.async_add_executor_job(self.api.play)
        await self.coordinator.async_request_refresh()

    async def async_media_pause(self) -> None:
        """Send pause command."""
        await self.hass.async_add_executor_job(self.api.pause)
        await self.coordinator.async_request_refresh()

    async def async_media_previous_track(self) -> None:
        """Send previous track command."""
        await self.hass.async_add_executor_job(self.api.previous_track)
        await self.coordinator.async_request_refresh()

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self.hass.async_add_executor_job(self.api.next_track)
        await self.coordinator.async_request_refresh()

    async def async_media_stop(self) -> None:
        """Send stop command."""
        await self.hass.async_add_executor_job(self.api.pause)  # Using pause as stop if no dedicated stop function
        await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs = {}
        
        # Add firmware version
        if self.coordinator.data and self.coordinator.data.get("device_info"):
            device_info = self.coordinator.data["device_info"]
            if "release" in device_info:
                attrs["firmware_version"] = device_info["release"].get("canonicalVersion")
        
        # Add reboot support status
        if self.coordinator.data and self.coordinator.data.get("device_info"):
            device_info = self.coordinator.data["device_info"]
            firmware_version = device_info.get("release", {}).get("canonicalVersion", "0.0.0")
            attrs["reboot_supported"] = firmware_version >= "2.16.0"
        
        # Add EQ settings
        if self.coordinator.data and self.coordinator.data.get("equalizer"):
            eq_data = self.coordinator.data["equalizer"]
            attrs["eq_preset"] = eq_data.get("preset", EQ_PRESET_FLAT)
            if eq_data.get("customEqualization"):
                attrs["eq_low"] = eq_data["customEqualization"].get("low", {}).get("gain", 0.0)
                attrs["eq_high"] = eq_data["customEqualization"].get("high", {}).get("gain", 0.0)
        
        # Add stream info (codec and lossless status)
        if self.coordinator.data and self.coordinator.data.get("playback"):
            playback = self.coordinator.data["playback"]
            if "streamInfo" in playback:
                stream_info = playback["streamInfo"]
                attrs["audio_codec"] = stream_info.get("codec")
                attrs["audio_lossless"] = stream_info.get("lossless", False)
                attrs["stream_supported"] = stream_info.get("supported", True)
            
            # Add peer device name if available
            if "peerDeviceName" in playback and playback["peerDeviceName"]:
                attrs["source_device"] = playback["peerDeviceName"]
        
        return attrs

    def _format_sound_mode(self, mode: str) -> str:
        """Format sound mode to a more readable name."""
        return SOUND_MODE_MAPPING.get(mode, mode)

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag media player features that are supported."""
        features = SUPPORT_DEVIALET
        
        # Check if night mode is available
        if self.coordinator.data and self.coordinator.data.get("system_info"):
            system_info = self.coordinator.data["system_info"]
            if "availableFeatures" in system_info and "nightMode" in system_info["availableFeatures"]:
                self._night_mode_available = True
        
        # Add reboot support if firmware version is >= 2.16
        if self.coordinator.data and self.coordinator.data.get("device_info"):
            device_info = self.coordinator.data["device_info"]
            firmware_version = device_info.get("release", {}).get("canonicalVersion", "0.0.0")
            if firmware_version >= "2.16.0":
                features |= SUPPORT_REBOOT
        
        return features

    @property
    def sound_mode(self) -> str | None:
        """Return the current sound mode (EQ preset) or night mode."""
        if not self.coordinator.data:
            return None

        # Check night mode first
        if self._night_mode_available and self.coordinator.data.get("night_mode"):
            night_mode = self.coordinator.data["night_mode"]
            if night_mode.get("nightMode") == "on":
                return "Night Mode"

        # Then check EQ preset
        if self.coordinator.data.get("equalizer"):
            eq_data = self.coordinator.data["equalizer"]
            mode = eq_data.get("preset", EQ_PRESET_FLAT)
            return self._format_sound_mode(mode)

        return None

    @property
    def sound_mode_list(self) -> list[str] | None:
        """Return a list of available sound modes."""
        if not self.coordinator.data:
            return None
            
        modes = [self._format_sound_mode(mode) for mode in SOUND_MODES]
        
        # Add night mode if available
        if self._night_mode_available:
            modes.append("Night Mode")
            
        return modes

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        """Select sound mode (EQ preset) or night mode."""
        if not self.coordinator.data:
            return

        # Handle night mode
        if self._night_mode_available and sound_mode == "Night Mode":
            await self.hass.async_add_executor_job(
                self.api.set_night_mode, True
            )
            return

        # Handle EQ preset
        if sound_mode in [self._format_sound_mode(mode) for mode in SOUND_MODES]:
            # Reverse lookup the internal mode name from the formatted name
            internal_mode = None
            for mode, formatted in SOUND_MODE_MAPPING.items():
                if formatted == sound_mode:
                    internal_mode = mode
                    break
            
            if internal_mode:
                # Turn off night mode when selecting an EQ preset
                if self._night_mode_available:
                    await self.hass.async_add_executor_job(
                        self.api.set_night_mode, False
                    )
                await self.hass.async_add_executor_job(
                    self.api.set_eq_preset, internal_mode
                )

        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn on the media player (used for reboot)."""
        await self.hass.async_add_executor_job(self.api.reboot_system)
        await self.coordinator.async_request_refresh()

