import logging
from typing import Optional, Dict, Any

from .const import (
    DOMAIN,
    ATTR_MANUFACTURER,
    FANDEVICE_CLIMATE_TYPES,
)

from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    PRESET_COMFORT,
    PRESET_ECO,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    ATTR_TEMPERATURE,
    PRECISION_HALVES,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback


OPERATION_LIST = [HVACMode.HEAT, HVACMode.OFF, HVACMode.AUTO, HVACMode.COOL, HVACMode.FAN_ONLY]

MIN_TEMPERATURE = 14
MAX_TEMPERATURE = 30

PRESET_MANUAL = "manual"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the FRITZ!SmartHome thermostat from ConfigEntry."""
    # = get_coordinator(hass, entry.entry_id)

    #@callback
    #def _add_entities(devices: set[str] | None = None) -> None:
    #    """Add devices."""
    #    if devices is None:
    #        devices = coordinator.new_devices
    #    if not devices:
    #        return
    #    async_add_entities(
    #        FritzboxThermostat(coordinator, ain)
    #        for ain in devices
    #        if coordinator.data.devices[ain].has_thermostat
    #    )

    #entry.async_on_unload(coordinator.async_add_listener(_add_entities))

    #(set(coordinator.data.devices))
    
    conf_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][conf_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, conf_name)},
        "name": conf_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities = []
    
    for slave in hub.slaves:
        slave_name = f"fan_slave_{slave._address}"
        slave_device_info = {
            "identifiers": {(DOMAIN, conf_name, slave_name)},
            "name": slave_name,
            "manufacturer": ATTR_MANUFACTURER,
        }
        
        for climate_info in FANDEVICE_CLIMATE_TYPES:
            climate = FanDeviceClimate(
                conf_name,
                hub,
                slave._address,
                slave_device_info,
                climate_info[0], #name
                climate_info[1], #modbusadress
                climate_info[2], #unit
                dict(hvac=climate_info[3]['hvac'],
                     roomtemp=climate_info[3]['roomtemp'],
                ),
                dict(off=climate_info[4]['off'],
                     auto=climate_info[4]['auto'],
                     heating=climate_info[4]['heating'],
                     cooling=climate_info[4]['cooling'],
                     boost=climate_info[4]['boost']
                )
            )
            entities.append(climate)

    async_add_entities(entities)
    return True


class FanDeviceClimate(ClimateEntity):
    """Representation of an Fan Master Climate."""
    _attr_supported_features = (ClimateEntityFeature.TURN_OFF | ClimateEntityFeature.TURN_ON)
    _enable_turn_on_off_backwards_compatibility = False
    
    def __init__(self, platform_name, hub, device_id, device_info, name, address, unit, keyList, states) -> None:
        """Initialize the selector."""
        self._platform_name = platform_name
        self._hub = hub
        self._deviceID = device_id
        self._device_info = device_info
        self._name = name
        self._address = address
        self._keyList = keyList
        self._stateValues = states
        self._attr_temperature_unit = unit

        self._attr_precision = PRECISION_HALVES
       
    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_fanmaster_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_fanmaster_sensor(self._modbus_data_updated)
         
    @callback
    def _modbus_data_updated(self):
        self.async_write_ha_state()
        
    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._device_info
    
    @property
    def name(self):
        """Return the name."""
        location_key = f"location_{self._deviceID}"
        if location_key in self._hub.data:
            return f"{self._hub.data[location_key]} ({self._name})"

    @property
    def unique_id(self) -> Optional[str]:
        """return the identifier."""
        return f"fan_location_{self._deviceID}_{self._keyList['hvac']}"
    
    @property
    def current_temperature(self) -> float:
        """Return the current room temperature."""
        try: 
            if self._keyList["roomtemp"] in self._hub.slaves[self._deviceID-1].data:
                temp = self._hub.slaves[self._deviceID-1].data[self._keyList["roomtemp"]]
                if (temp == "Error"):   return None
                else:                   return temp
        except IndexError:
            return None

    #@property
    #def target_temperature(self) -> float:
    #    """Return the temperature we try to reach."""
    #    if self.data.target_temperature == ON_API_TEMPERATURE:
    #        return ON_REPORT_SET_TEMPERATURE
    #    if self.data.target_temperature == OFF_API_TEMPERATURE:
    #        return OFF_REPORT_SET_TEMPERATURE
    #    return self.data.target_temperature  # type: ignore [no-any-return]

    #async def async_set_temperature(self, **kwargs: Any) -> None:
    #    """Set new target temperature."""
    #    if kwargs.get(ATTR_HVAC_MODE) is not None:
    #        hvac_mode = kwargs[ATTR_HVAC_MODE]
    #        await self.async_set_hvac_mode(hvac_mode)
    #    elif kwargs.get(ATTR_TEMPERATURE) is not None:
    #        temperature = kwargs[ATTR_TEMPERATURE]
    #        await self.hass.async_add_executor_job(
    #            self.data.set_target_temperature, temperature
    #        )
    #    await self.coordinator.async_refresh()

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current operation mode."""
        try: 
            if self._keyList["hvac"] in self._hub.slaves[self._deviceID-1].data:
                hvacValue = self._hub.slaves[self._deviceID-1].data[self._keyList["hvac"]]
                if (hvacValue == self._stateValues["auto"]): return HVACMode.AUTO
                elif (hvacValue == self._stateValues["boost"]): return HVACMode.FAN_ONLY
                elif (hvacValue == self._stateValues["cooling"]): return HVACMode.COOL
                elif (hvacValue == self._stateValues["heating"]): return HVACMode.HEAT
                elif (hvacValue == self._stateValues["off"]): return HVACMode.OFF
                return None
        except IndexError:
            return None

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available operation modes."""
        return OPERATION_LIST

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        hvacValue = 0
        if   (hvac_mode == HVACMode.AUTO):      hvacValue = self._stateValues["auto"]
        elif (hvac_mode == HVACMode.FAN_ONLY):  hvacValue = self._stateValues["boost"] 
        elif (hvac_mode == HVACMode.COOL):      hvacValue = self._stateValues["cooling"] 
        elif (hvac_mode == HVACMode.HEAT):      hvacValue = self._stateValues["heating"] 
        elif (hvac_mode == HVACMode.OFF):       hvacValue = self._stateValues["off"] 
        
        response = self._hub.write_register(unit=self._deviceID, address=self._address, payload=hvacValue)
        if response.isError():
            _LOGGER.error(f"Could not write value {value} to location_{self._deviceID} {self._key}")
            return
        

    @property
    def min_temp(self) -> int:
        """Return the minimum temperature."""
        return MIN_TEMPERATURE

    @property
    def max_temp(self) -> int:
        """Return the maximum temperature."""
        return MAX_TEMPERATURE
    
    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.HEATING)
