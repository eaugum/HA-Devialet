"""The Devialet IP Control integration."""
import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    SERVICE_SET_VOLUME,
    SERVICE_VOLUME_UP,
    SERVICE_VOLUME_DOWN,
    SERVICE_PLAY,
    SERVICE_PAUSE,
    SERVICE_MUTE,
    SERVICE_UNMUTE,
    SERVICE_NEXT,
    SERVICE_PREVIOUS,
    SERVICE_SET_NIGHT_MODE,
    SERVICE_SET_EQ_PRESET,
    SERVICE_SET_CUSTOM_EQ,
    SERVICE_POWER_OFF_SYSTEM,
    SERVICE_REBOOT_SYSTEM,
    ATTR_VOLUME,
    ATTR_SOURCE_ID,
    ATTR_NIGHT_MODE,
    ATTR_EQ_PRESET,
    ATTR_EQ_LOW,
    ATTR_EQ_HIGH,
    EQ_PRESET_FLAT,
    EQ_PRESET_VOICE,
    EQ_PRESET_CUSTOM,
)
from .devialet_api import DevialetAPI

_LOGGER = logging.getLogger(__name__)

# Supported platforms
PLATFORMS = [Platform.MEDIA_PLAYER, Platform.SENSOR, Platform.SWITCH]

# Volume service schema
VOLUME_SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_VOLUME): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
})

# Source service schema
SOURCE_SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_SOURCE_ID): cv.string,
})

# Night mode service schema
NIGHT_MODE_SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_NIGHT_MODE): cv.boolean,
})

# EQ preset service schema
EQ_PRESET_SERVICE_SCHEMA = vol.Schema({
    vol.Required(ATTR_EQ_PRESET): vol.In([
        EQ_PRESET_FLAT,
        EQ_PRESET_VOICE,
        EQ_PRESET_CUSTOM,
    ]),
})

# Custom EQ service schema
CUSTOM_EQ_SERVICE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_EQ_LOW, default=0.0): vol.All(
        vol.Coerce(float), vol.Range(min=-12.0, max=12.0)
    ),
    vol.Optional(ATTR_EQ_HIGH, default=0.0): vol.All(
        vol.Coerce(float), vol.Range(min=-12.0, max=12.0)
    ),
})

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Devialet IP Control component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Devialet IP Control from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Get config entry data
    host = entry.data[CONF_HOST]
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    
    # Create API instance
    api = DevialetAPI(host)
    
    # Store API instance and scan interval in hass.data
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "scan_interval": scan_interval,
    }
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register update listener for config entry changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

def register_services(hass: HomeAssistant) -> None:
    """Register services for the Devialet integration."""
    
    async def handle_set_volume(call: ServiceCall) -> None:
        """Handle the set_volume service."""
        volume = call.data[ATTR_VOLUME]
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.set_volume, volume)
    
    async def handle_reboot_system(call: ServiceCall) -> None:
        """Handle the reboot_system service."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.reboot_system)
    
    async def handle_volume_up(call: ServiceCall) -> None:
        """Handle the volume_up service."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.volume_up)
    
    async def handle_volume_down(call: ServiceCall) -> None:
        """Handle the volume_down service."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.volume_down)
    
    async def handle_play(call: ServiceCall) -> None:
        """Handle the play service."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.play)
    
    async def handle_pause(call: ServiceCall) -> None:
        """Handle the pause service."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.pause)
    
    async def handle_mute(call: ServiceCall) -> None:
        """Handle the mute service."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.mute)
    
    async def handle_unmute(call: ServiceCall) -> None:
        """Handle the unmute service."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.unmute)
    
    async def handle_next(call: ServiceCall) -> None:
        """Handle the next_track service."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.next_track)
    
    async def handle_previous(call: ServiceCall) -> None:
        """Handle the previous_track service."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.previous_track)
    
    async def handle_set_night_mode(call: ServiceCall) -> None:
        """Handle the set_night_mode service."""
        enabled = call.data[ATTR_NIGHT_MODE]
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.set_night_mode, enabled)

    async def handle_set_eq_preset(call: ServiceCall) -> None:
        """Handle the set_eq_preset service."""
        preset = call.data[ATTR_EQ_PRESET]
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.set_eq_preset, preset)

    async def handle_set_custom_eq(call: ServiceCall) -> None:
        """Handle the set_custom_eq service."""
        low = call.data[ATTR_EQ_LOW]
        high = call.data[ATTR_EQ_HIGH]
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.set_custom_eq, low, high)
    
    async def handle_power_off_system(call: ServiceCall) -> None:
        """Handle the power_off_system service."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            api = entry_data["api"]
            await hass.async_add_executor_job(api.power_off_system)
    
    # Register services if they don't already exist
    if not hass.services.has_service(DOMAIN, SERVICE_SET_VOLUME):
        hass.services.async_register(
            DOMAIN, SERVICE_SET_VOLUME, handle_set_volume, schema=VOLUME_SERVICE_SCHEMA
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_VOLUME_UP):
        hass.services.async_register(
            DOMAIN, SERVICE_VOLUME_UP, handle_volume_up
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_VOLUME_DOWN):
        hass.services.async_register(
            DOMAIN, SERVICE_VOLUME_DOWN, handle_volume_down
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_PLAY):
        hass.services.async_register(
            DOMAIN, SERVICE_PLAY, handle_play
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_PAUSE):
        hass.services.async_register(
            DOMAIN, SERVICE_PAUSE, handle_pause
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_MUTE):
        hass.services.async_register(
            DOMAIN, SERVICE_MUTE, handle_mute
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_UNMUTE):
        hass.services.async_register(
            DOMAIN, SERVICE_UNMUTE, handle_unmute
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_NEXT):
        hass.services.async_register(
            DOMAIN, SERVICE_NEXT, handle_next
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_PREVIOUS):
        hass.services.async_register(
            DOMAIN, SERVICE_PREVIOUS, handle_previous
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SET_NIGHT_MODE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_NIGHT_MODE,
            handle_set_night_mode,
            schema=NIGHT_MODE_SERVICE_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SET_EQ_PRESET):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_EQ_PRESET,
            handle_set_eq_preset,
            schema=EQ_PRESET_SERVICE_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SET_CUSTOM_EQ):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_CUSTOM_EQ,
            handle_set_custom_eq,
            schema=CUSTOM_EQ_SERVICE_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_POWER_OFF_SYSTEM):
        hass.services.async_register(
            DOMAIN,
            SERVICE_POWER_OFF_SYSTEM,
            handle_power_off_system,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_REBOOT_SYSTEM):
        hass.services.async_register(
            DOMAIN,
            SERVICE_REBOOT_SYSTEM,
            handle_reboot_system,
        )
