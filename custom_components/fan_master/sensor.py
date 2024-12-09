import logging
from typing import Optional, Dict, Any
from .const import (
    MAX_DEVICES,
    FANMASTER_SENSOR_TYPES,
    FANDEVICE_SENSOR_TYPES,
    DOMAIN,
    ATTR_MANUFACTURER,
)
from datetime import datetime
from homeassistant.helpers.entity import Entity
from homeassistant.const import CONF_NAME, UnitOfEnergy, UnitOfPower
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass
)

from homeassistant.core import callback
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    conf_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][conf_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, conf_name)},
        "name": conf_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities = []
    for sensor_info in FANMASTER_SENSOR_TYPES.values():
        if (sensor_info[0] == 0):
            sensor = FanMasterSensor(
                conf_name,
                hub,
                device_info,
                sensor_info[1],
                sensor_info[2],
                sensor_info[3],
                sensor_info[4],
                sensor_info[5],
            )
            entities.append(sensor)
    
    for i in range(1,MAX_DEVICES+1):
        sensor = FanMasterSensor(conf_name, hub, device_info, f"Location {i}", f"location_{i}", None, None, None)
        entities.append(sensor)
        
    #Temp solution: create sensors as configured
    for slave in hub.slaves:
        slave_name = f"fan_slave_{slave._address}"
        slave_device_info = {
            "identifiers": {(DOMAIN, conf_name, slave_name)},
            "name": slave_name,
            "manufacturer": ATTR_MANUFACTURER,
        }
        
        for slave_sensor_info in FANDEVICE_SENSOR_TYPES.values():
            if (slave_sensor_info[0] == 0):
                sensor = FanDeviceSensor(
                    conf_name,
                    hub,
                    slave._address,
                    slave_device_info,
                    slave_sensor_info[1],
                    slave_sensor_info[2],
                    slave_sensor_info[3],
                    slave_sensor_info[4],
                    slave_sensor_info[5],
                )
                entities.append(sensor)
    
    async_add_entities(entities)
    return True

class SensorBase(SensorEntity):
    """Representation of an Fan Master sensor."""

    def __init__(self, platform_name, hub, device_info, name, key, unit, sensorclass, icon):
        """Initialize the sensor."""
        self._platform_name = platform_name
        self._hub = hub
        self._key = key
        self._name = name
        self._unit_of_measurement = unit
        self._attr_device_class = sensorclass
        self._icon = icon
        self._device_info = device_info
        self._attr_state_class = SensorStateClass.MEASUREMENT

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_fanmaster_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_fanmaster_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self):
        self.async_write_ha_state()

    @callback
    def _update_state(self):
        if self._key in self._hub.data:
            self._state = self._hub.data[self._key]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the sensor icon."""
        return self._icon

    @property
    def should_poll(self) -> bool:
        """Data is delivered by the hub"""
        return False

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._device_info


class FanMasterSensor(SensorBase):
    def __init__(self, platform_name, hub, device_info, name, key, unit, sensorclass, icon):
        super().__init__(platform_name, hub, device_info, name, key, unit, sensorclass, icon)
        """Initialize the sensor."""
        
    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} ({self._name})"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self._key}"
    
    @property
    def state(self):
        """Return the state of the sensor."""
        if self._key in self._hub.data:
            if (self._hub.data[self._key] == "Error"):
                return None
            return self._hub.data[self._key]
            
        
        
        
class FanDeviceSensor(SensorBase):
    def __init__(self, platform_name, hub, device_id, device_info, name, key, unit, sensorclass, icon):
        super().__init__(platform_name, hub, device_info, name, key, unit, sensorclass, icon)
        """Initialize the sensor."""
        self._deviceID = device_id
        
    @property
    def name(self):
        """Return the name."""
        location_key = f"location_{self._deviceID}"
        if location_key in self._hub.data:
            return f"{self._hub.data[location_key]} ({self._name})"

    @property
    def unique_id(self) -> Optional[str]:
        """return the identifier."""
        return f"fan_location_{self._deviceID}_{self._key}"
    
    @property
    def state(self):
        """Return the state of the sensor."""
        try: 
            if self._key in self._hub.slaves[self._deviceID-1].data:
                if (self._hub.slaves[self._deviceID-1].data[self._key] == "Error"):
                    return None
                return self._hub.slaves[self._deviceID-1].data[self._key]
        except IndexError:
            return None