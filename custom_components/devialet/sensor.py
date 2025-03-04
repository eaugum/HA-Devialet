"""Support for Devialet IP Control sensors."""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional
from datetime import timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .media_player import DevialetDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Devialet IP Control sensors based on config_entry."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator = (
        entry_data.get("coordinator")
        or hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("coordinator")
    )
    
    if not coordinator:
        coordinator = DevialetDataUpdateCoordinator(
            hass,
            api=entry_data["api"],
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=entry_data["scan_interval"]),
        )
        await coordinator.async_config_entry_first_refresh()
    
    async_add_entities([
        DevialetVolumeSensor(coordinator, entry),
        DevialetPlaybackSensor(coordinator, entry),
        DevialetArtistSensor(coordinator, entry),
        DevialetTrackSensor(coordinator, entry),
        DevialetAlbumSensor(coordinator, entry),
        DevialetStreamInfoSensor(coordinator, entry),
    ], True)


class DevialetSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Devialet sensors."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
        name: str,
        icon: str = None,
        device_class: str = None,
        state_class: str = None,
        unit_of_measurement: str = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"

    def _get_metadata_value(self, key: str) -> StateType:
        """Get metadata value from playback data."""
        playback = self.coordinator.data and self.coordinator.data.get("playback")
        if not playback:
            return None
        
        metadata = playback.get("metadata", {})
        return metadata.get(key, "Unknown")

    @property
    def device_info(self):
        """Return device information about this Devialet device."""
        device_info = self.coordinator.data and self.coordinator.data.get("device_info")
        if not device_info:
            return None
            
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": device_info.get("deviceName", "Devialet Speaker"),
            "manufacturer": "Devialet",
            "model": device_info.get("model", "Phantom"),
            "sw_version": device_info.get("release", {}).get("canonicalVersion"),
            "serial_number": device_info.get("serial"),
        }


class DevialetVolumeSensor(DevialetSensorBase):
    """Sensor for Devialet volume level."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the volume sensor."""
        super().__init__(
            coordinator,
            entry,
            "volume",
            "Devialet Volume",
            "mdi:volume-high",
            None,
            SensorStateClass.MEASUREMENT,
            PERCENTAGE,
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        volume_data = self.coordinator.data and self.coordinator.data.get("volume")
        if not volume_data:
            return None
        
        return volume_data.get("volume")


class DevialetPlaybackSensor(DevialetSensorBase):
    """Sensor for Devialet playback state."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the playback sensor."""
        super().__init__(
            coordinator,
            entry,
            "playback_state",
            "Devialet Playback State",
            "mdi:play-circle-outline",
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        playback = self.coordinator.data and self.coordinator.data.get("playback")
        if not playback:
            return None
        
        return playback.get("playingState")

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes."""
        playback = self.coordinator.data and self.coordinator.data.get("playback")
        if not playback:
            return {}
        
        attributes = {}
        if "muteState" in playback:
            attributes["mute_state"] = playback["muteState"]
        
        if "source" in playback and playback["source"]:
            attributes["source_type"] = playback["source"].get("type")
        
        return attributes


class DevialetArtistSensor(DevialetSensorBase):
    """Sensor for Devialet current artist."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the artist sensor."""
        super().__init__(
            coordinator,
            entry,
            "artist",
            "Devialet Artist",
            "mdi:account-music",
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._get_metadata_value("artist")


class DevialetTrackSensor(DevialetSensorBase):
    """Sensor for Devialet current track."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the track sensor."""
        super().__init__(
            coordinator,
            entry,
            "track",
            "Devialet Track",
            "mdi:music-note",
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._get_metadata_value("title")


class DevialetAlbumSensor(DevialetSensorBase):
    """Sensor for Devialet current album."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the album sensor."""
        super().__init__(
            coordinator,
            entry,
            "album",
            "Devialet Album",
            "mdi:album",
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._get_metadata_value("album")


class DevialetStreamInfoSensor(DevialetSensorBase):
    """Sensor for Devialet stream information."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the stream info sensor."""
        super().__init__(
            coordinator,
            entry,
            "stream_info",
            "Devialet Stream Info",
            "mdi:information",
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        playback = self.coordinator.data and self.coordinator.data.get("playback")
        if not playback or "streamInfo" not in playback:
            return None
            
        stream_info = playback["streamInfo"]
        codec = stream_info.get("codec", "").lower()
        
        if not codec:
            return None
            
        return f"{codec} (Lossless)" if stream_info.get("lossless", False) else codec

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes."""
        playback = self.coordinator.data and self.coordinator.data.get("playback")
        if not playback or "streamInfo" not in playback:
            return {}
            
        stream_info = playback["streamInfo"]
        if not stream_info.get("codec"):
            return {}
            
        return {
            "codec": stream_info.get("codec", "").lower(),
            "lossless": stream_info.get("lossless", False),
            "supported": stream_info.get("supported", True),
        }
