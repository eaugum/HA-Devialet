"""Support for Devialet IP Control switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .media_player import DevialetDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Devialet IP Control switches based on config_entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id].get("coordinator")
    
    if coordinator and coordinator.data:
        system_info = coordinator.data.get("system_info", {})
        if "availableFeatures" in system_info and "nightMode" in system_info["availableFeatures"]:
            async_add_entities([DevialetNightModeSwitch(coordinator, entry)], True)

class DevialetNightModeSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of Devialet Night Mode switch."""

    def __init__(
        self,
        coordinator: DevialetDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the night mode switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = "Night Mode"
        self._attr_unique_id = f"{entry.entry_id}_night_mode"
        self._attr_icon = "mdi:weather-night"

    @property
    def device_info(self):
        """Return device information about this Devialet device."""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
        }

    @property
    def is_on(self) -> bool | None:
        """Return true if night mode is on."""
        if not self.coordinator.data or not self.coordinator.data.get("night_mode"):
            return None
        
        night_mode = self.coordinator.data["night_mode"]
        return night_mode.get("nightMode") == "on"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on night mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_night_mode, True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off night mode."""
        await self.hass.async_add_executor_job(
            self.coordinator.api.set_night_mode, False
        )
        await self.coordinator.async_request_refresh() 