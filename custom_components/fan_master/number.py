import logging
from typing import Optional, Any

from .const import (
    DOMAIN,
    ATTR_MANUFACTURER,
    FANDEVICE_NUMBER_TYPES,
)

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder

from homeassistant.const import CONF_NAME
from homeassistant.components.number import (
    PLATFORM_SCHEMA,
    NumberEntity,
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
    
    #no numbers to be added for Master
    
    #Temp solution: create sensors as configured
    for slave in hub.slaves:
        slave_name = f"fan_slave_{slave._address}"
        slave_device_info = {
            "identifiers": {(DOMAIN, conf_name, slave_name)},
            "name": slave_name,
            "manufacturer": ATTR_MANUFACTURER,
        }
        
        for number_info in FANDEVICE_NUMBER_TYPES:
            number = FanDeviceNumber(
                conf_name,
                hub,
                slave._address,
                slave_device_info,
                number_info[0], #name
                number_info[1], #key
                number_info[2], #modbusadress
                number_info[3], #datatype
                number_info[4], #unit
                number_info[5], #min
                number_info[6], #max
                number_info[7], #class
            )
            entities.append(number)

    async_add_entities(entities)
    return True

class FanDeviceNumber(NumberEntity):
    """Representation of an Fan Master number."""

    def __init__(self, platform_name, hub, device_id, device_info, name, key, address, fmt, unit, minValue, maxValue, numberclass) -> None:
        """Initialize the selector."""
        self._platform_name = platform_name
        self._hub = hub
        self._deviceID = device_id
        self._device_info = device_info
        self._name = name
        self._key = key
        self._address = address
        self._fmt = fmt
        self._attr_native_min_value = minValue
        self._attr_native_max_value = maxValue
        self._attr_native_unit_of_measurement = unit

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
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Change the selected value."""
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
        payloadData = None
        if self._fmt == "u32":
            #builder.add_32bit_uint(int(value))
            payloadData = int(value)
        elif self._fmt =="u16":
            #builder.add_16bit_uint(int(value))
            payloadData = int(value)
        #elif self._fmt == "f":
        #    builder.add_32bit_float(float(value))
        else:
            _LOGGER.error(f"Invalid encoding format {self._fmt} for {self._key}")
            return

        #_LOGGER.debug(f"try to write '{builder.to_registers()}' to location_{self._deviceID} {self._key}")
            
        response = self._hub.write_register(unit=self._deviceID, address=self._address, payload=payloadData)
        if response.isError():
            _LOGGER.error(f"Could not write value {value} to location_{self._deviceID} {self._key}")
            return

        self._hub.slaves[self._deviceID-1].data[self._key] = value
        self.async_write_ha_state()
