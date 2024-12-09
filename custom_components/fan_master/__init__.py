"""The Fan Master Modbus Integration."""
import asyncio
import logging
from typing import Optional

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant

from .fanmaster import FanMaster

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_MODBUS_ADDRESS,
    DEFAULT_ACTIVE_DEVICES,
    CONF_MODBUS_ADDRESS,
    CONF_ACTIVE_DEVICES,
)

_LOGGER = logging.getLogger(__name__)

FAN_MASTER_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.string,
        vol.Optional(CONF_MODBUS_ADDRESS, default=DEFAULT_MODBUS_ADDRESS): cv.positive_int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
        vol.Optional(CONF_ACTIVE_DEVICES, default=DEFAULT_ACTIVE_DEVICES): cv.positive_int,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({cv.slug: FAN_MASTER_SCHEMA})}, extra=vol.ALLOW_EXTRA
)

PLATFORMS = ["number", "switch", "sensor", "binary_sensor", "climate"]


async def async_setup(hass, config):
    """Set up the Fan Master modbus component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a Fan Master modbus."""
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    port = entry.data[CONF_PORT]
    address = entry.data.get(CONF_MODBUS_ADDRESS, 1)
    scan_interval = entry.data[CONF_SCAN_INTERVAL]
    devices = entry.data.get(CONF_ACTIVE_DEVICES, DEFAULT_ACTIVE_DEVICES)

    _LOGGER.debug("Setup %s.%s", DOMAIN, name)

    hub = FanMaster(
        hass,
        name,
        host,
        port,
        address,
        scan_interval,
        devices
    )
    """Register the hub."""
    hass.data[DOMAIN][name] = {"hub": hub}

    #for component in PLATFORMS:
    #    hass.async_create_task(
    #        hass.config_entries.async_forward_entry_setup(entry, component)
    #    )
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass, entry):
    """Unload Fan Master mobus entry."""
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    #unload_ok = all(
    #    await asyncio.gather(
    #        *[
    #            hass.config_entries.async_forward_entry_unload(entry, component)
    #            for component in PLATFORMS
    #        ]
    #    )
    #)
    if not unload_ok:
        return False

    hass.data[DOMAIN].pop(entry.data["name"])
    return True