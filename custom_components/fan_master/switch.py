import logging
from typing import Optional, Dict, Any

from .const import (
    DOMAIN,
    ATTR_MANUFACTURER,
    FANDEVICE_SWITCH_TYPES,
)

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder

from homeassistant.const import CONF_NAME
from homeassistant.components.switch import (
    PLATFORM_SCHEMA,
    SwitchEntity,
)

from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities) -> None:
    conf_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][conf_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, conf_name)},
        "name": conf_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities = []
    
    #no switches to be added for Master
    
    #Temp solution: create sensors as configured
    for slave in hub.slaves:
        slave_name = f"fan_slave_{slave._address}"
        slave_device_info = {
            "identifiers": {(DOMAIN, conf_name, slave_name)},
            "name": slave_name,
            "manufacturer": ATTR_MANUFACTURER,
        }
        
        for switch_info in FANDEVICE_SWITCH_TYPES:
            switch = FanDeviceSwitch(
                conf_name,
                hub,
                slave._address,
                slave_device_info,
                switch_info[0], #name
                switch_info[1], #key
                switch_info[2], #modbusadress
            )
            entities.append(switch)

    async_add_entities(entities)
    return True

class FanDeviceSwitch(SwitchEntity):
    """Representation of an Fan Master number."""

    def __init__(self, platform_name, hub, device_id, device_info, name, key, address) -> None:
        """Initialize the selector."""
        self._platform_name = platform_name
        self._hub = hub
        self._deviceID = device_id
        self._device_info = device_info
        self._name = name
        self._key = key
        self._address = address
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        self._hub.async_add_fanmaster_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_fanmaster_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self) -> None:
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Return the name."""
        location_key = f"location_{self._deviceID}"
        if location_key in self._hub.data:
            return f"{self._hub.data[location_key]} ({self._name})"

    @property
    def unique_id(self) -> Optional[str]:
        """return the identifier."""
        return f"fan_location_{self._deviceID}_{self._key}"

    @property
    def should_poll(self) -> bool:
        """Data is delivered by the hub"""
        return False

    @property
    def native_value(self) -> float:
        try: 
            if self._key in self._hub.slaves[self._deviceID-1].data:
                return self._hub.slaves[self._deviceID-1].data[self._key]
        except IndexError:
            return 
        
    
    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        """Change the selected value."""
        value = 1
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        builder.add_16bit_uint(int(value))
        
        _LOGGER.debug(f"try to write '{builder.to_registers()}' to location_{self._deviceID} {self._key}")
            
        response = self._hub.write_registers(unit=self._deviceID, address=self._address, payload=builder.to_registers())
        if response.isError():
            _LOGGER.error(f"Could not write value {value} to location_{self._deviceID} {self._key}")
            return

        self._hub.slaves[self._deviceID-1].data[self._key] = True
        self.async_write_ha_state()
        
        
    async def async_turn_off(self) -> None:
        """Turn the entity on."""
        """Change the selected value."""
        value = 0
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        builder.add_16bit_uint(int(value))
        
        _LOGGER.debug(f"try to write '{builder.to_registers()}' to location_{self._deviceID} {self._key}")
            
        response = self._hub.write_registers(unit=self._deviceID, address=self._address, payload=builder.to_registers())
        if response.isError():
            _LOGGER.error(f"Could not write value {value} to location_{self._deviceID} {self._key}")
            return

        self._hub.slaves[self._deviceID-1].data[self._key] = False
        self.async_write_ha_state()
