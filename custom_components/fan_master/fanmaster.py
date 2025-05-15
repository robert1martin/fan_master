import logging
import threading
from typing import Optional
from datetime import timedelta, datetime

import pymodbus
from pymodbus.client import ModbusTcpClient

from homeassistant.core import callback
from homeassistant.helpers.event import async_track_time_interval
from .const import (
    MAX_DEVICES, DEFAULT_MODBUS_TIMEOUT
)
from .fandevice import FanDevice

_LOGGER = logging.getLogger(__name__)

def bitfield(value, size=None):
    """convert a int to a bitfield represented in a list"""    
    if size is not None:
            return [int(digit) for digit in bin(value)[2:].zfill(size)] # [2:] to chop off the "0b" part 
    else:
            return [int(digit) for digit in bin(value)[2:]]             # [2:] to chop off the "0b" part 

class FanMaster:
    """Thread safe wrapper class for pymodbus."""

    def __init__(self, hass, name, host, port, address, scan_interval, numberDevices=1):
        """Initialize the Modbus hub."""
        self._hass = hass
        self._client = ModbusTcpClient(host=host, port=port, timeout=max(3, (scan_interval - 1)))
        self._lock = threading.Lock()
        self._name = name
        self._address = address
        self._scan_interval = timedelta(seconds=scan_interval)        
        self._last_data_received_timestamp = datetime(year=2000, month=1, day=1)
        self._unsub_interval_method = None
        self._sensors = []
        self.slaves = []
        self.data = {}
        
        self.addDevices(numberDevices)        
    
    def addDevices(self, numberDevices):
        #Temp solution: create 2 Devices only
        for i in range(1, numberDevices+1):
            self.slaves.append(FanDevice(self, i))
            
    def addDevice(self, address):
        self.slaves.append(FanDevice(self, address))
        return True
        
    def removeDevice(self, address):
        self.slaves.remove(self.get_device(address))
        return True
        
    def get_device(self, address):
        for slave in self.slaves:
            if (slave._address == address):
                return slave
        return None
            
    def is_known_device(self, address):
        for slave in self.slaves:
            if (slave._address == address):
                return True
        return False
            
    def updateDeviceList(self):
        """Update the devices."""
        
        _LOGGER.debug("Updating Devices ...")
        if self.slaves is None:
            self.slaves = []
            
        codingList = self.data["mastercodinglist"]
        codingInvalid = self.data["codingInvalid"]
        index = 0
        if (not codingInvalid):
            for codingBit in codingList:
                index  = index + 1
                if (codingBit):
                    if (not self.is_known_device(index)):
                        _LOGGER.info(f"add address {index} to device list as its newly coded")
                        self.addDevice(index)
                else:
                    if (self.is_known_device(index)):
                        _LOGGER.info(f"remove address {index} from device list as its not part of coding anymore")
                        self.removeDevice(index)
        return True    
            
    @callback
    def async_add_fanmaster_sensor(self, update_callback):
        """Listen for data updates."""
        # This is the first sensor, set up interval.
        if not self._sensors:
           # self.connect()
            self._unsub_interval_method = async_track_time_interval(
                self._hass, self.async_refresh_modbus_data, self._scan_interval
            )

        self._sensors.append(update_callback)

    @callback
    def async_remove_fanmaster_sensor(self, update_callback):
        """Remove data update."""
        self._sensors.remove(update_callback)

        if not self._sensors:
            """stop the interval timer upon removal of last sensor"""
            self._unsub_interval_method()
            self._unsub_interval_method = None
            self.close()
                
    async def async_refresh_modbus_data(self, _now: Optional[int] = None) -> dict:
        """Time to update."""
        result : bool = await self._hass.async_add_executor_job(self._refresh_modbus_data)
        if result:
            self._last_data_received_timestamp = datetime.now()
            
        
        if (datetime.now() - self._last_data_received_timestamp).total_seconds() > DEFAULT_MODBUS_TIMEOUT:
            #set all data to None so entities get unavailable
            
            self.data = dict.fromkeys(self.data, None)
            
            for slave in self.slaves:
                slave.data = dict.fromkeys(slave.data, None)
            
            #for date in self.data:
            #    date = None
            #for slave in self.slaves:
            #    for date in slave.data:
            #        date = None
                    
        for update_callback in self._sensors:
            update_callback()


    def _refresh_modbus_data(self, _now: Optional[int] = None) -> bool:
        """Time to update."""
        if not self._sensors:
            return False

        if not self._check_and_reconnect():
            #if not connected, skip
            return False

        try:
            update_result = self.read_modbus_data()
        except Exception as e:
            _LOGGER.exception("Error reading modbus data", exc_info=True)
            update_result = False
        return update_result



    @property
    def name(self):
        """Return the name of this hub."""
        return self._name

    def close(self):
        """Disconnect client."""
        with self._lock:
            self._client.close()

    def _check_and_reconnect(self):
        if not self._client.connected:
            _LOGGER.info("modbus client is not connected, trying to reconnect")
            return self.connect()
        return self._client.connected

    def connect(self):
        """Connect client."""
        result = False
        with self._lock:
            result = self._client.connect()

        if result:
            _LOGGER.info("successfully connected to %s:%s",
                         self._client.comm_params.host, self._client.comm_params.port)
        else:
            _LOGGER.warning("not able to connect to %s:%s",
                            self._client.comm_params.host, self._client.comm_params.port)
        return result
    

    def read_holding_registers(self, unit, address, count):
        """Read holding registers."""
        try:
            with self._lock:
                return self._client.read_holding_registers(
                    address=address, count=count, slave=unit
                )
        except BrokenPipeError:
            self.close()

    def write_registers(self, unit, address, payload):
        """Write registers."""
        with self._lock:
            return self._client.write_registers(
                address=address, values=payload, slave=unit
            )
            
    def write_register(self, unit, address, payload):
        """Write register."""
        with self._lock:
            return self._client.write_register(
                address=address, value=payload, slave=unit
            )
            
    def read_modbus_data(self):
        _LOGGER.debug("Modbus read Start")
        result = False
        try:
            return (
                self.read_modbus_data_master_sw_Version()
                and self.read_modbus_data_master_dtc_active()
                and self.read_modbus_data_master_codingList()
                and self.updateDeviceList()
                and self.read_modbus_data_master_locations()
                and self.read_modbus_data_master_worst_dewpoint()
                and self.read_modbus_data_master_lowest_supply()
                and self.read_modbus_data_master_cooling_locked()
                and self.read_modbus_data_slaves()
            )
        except (BrokenPipeError, pymodbus.exceptions.ModbusIOException):
            self.close()

        _LOGGER.debug("Modbus read End")
        return result

    def read_modbus_data_slaves(self):
        """start reading data"""
        retval = True                    
        for fandevice in self.slaves:
            _LOGGER.debug(f'read Fan device data of {fandevice._name}')
            retval = retval and fandevice.read_modbus_data_device()
        
        return retval

    def read_modbus_data_master_sw_Version(self, start_address=0):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=4)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        
        
        
        value = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT64)
        
        fbl_sw_version_major = value >> 56
        fbl_sw_version_minor = (value >> 48) & 0xFF
        fbl_sw_version_patch = (value >> 40) & 0xFF
        appl_sw_version_major = (value >> 32) & 0xFF
        appl_sw_version_minor = (value >> 24) & 0xFF
        appl_sw_version_patch = (value >> 16) & 0xFF

        self.data["fbl_sw_version"] = f"{fbl_sw_version_major}.{fbl_sw_version_minor}.{fbl_sw_version_patch}"
        self.data["appl_sw_version"] = f"{appl_sw_version_major}.{appl_sw_version_minor}.{appl_sw_version_patch}"
        
        return True
    
    def read_modbus_data_master_dtc_active(self, start_address=3):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        
        value = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)
        
        dtc_active = (value != 0)
        
        self.data["dtcactive"] = dtc_active
        
        return True     
    
    def read_modbus_data_master_codingList(self, start_address=10):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=2) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False

        coding_value = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT32)
        _LOGGER.debug(f'coding_value: {coding_value}')
        
        coding_list = bitfield(coding_value, 32)
        coding_list.reverse()
        codingValid = coding_list[31]
        coding_list.pop() # remove element 32 (Valid bit)
        coding_list.pop() # remove element 31 (unused bit)
        
        _LOGGER.debug(f'coding_list: {coding_list}')
                
        self.data["codingInvalid"] = (codingValid != 1) #valid=1 --> set invalid variable if not 1
        self.data["mastercodinglist"] = coding_list
        
        return True    
    
    def read_modbus_data_master_locations(self, start_address=20, numberLocations=MAX_DEVICES, stringSize=20):
        retval = True
        for i in range(1,numberLocations+1):
            #parse through all locations
            try:
                if(self.data["mastercodinglist"][i-1]):
                    address = int(start_address + ( (i - 1)  * stringSize / 2))
                    retval = retval and self.read_modbus_data_master_location(i, address, stringSize)
                else:
                    self.data[f"location_{i}"] = "not coded"
            except IndexError:
                self.data[f"location_{i}"] = "out of mastercodinglist"
            
        return retval
    
    

    def read_modbus_data_master_location(self, index, start_address=20, stringSize=20):
        """start reading data"""
        
        length=int(stringSize/2)
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=length)
        
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        
        string_location = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.STRING)
        
        if (string_location == ""):
            self.data[f"location_{index}"] = "no location in Parameter"
        else:
            self.data[f"location_{index}"] = string_location
            
        #_LOGGER.debug(f'location {index} = {string_location}')     
             
        return True
    
    def read_modbus_data_master_worst_dewpoint(self, start_address=320):
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        temperature_raw = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.INT16)
        
        if (temperature_raw == 32767):
            self.data["masterworstdewpoint"] = "Error"
        else:
            self.data["masterworstdewpoint"] = temperature_raw/10
        
        return True
    
    def read_modbus_data_master_lowest_supply(self, start_address=321):
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        temperature_raw = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.INT16)
        if (temperature_raw == 32767):
            self.data["masterlowestsupply"] = "Error"
        else:
            self.data["masterlowestsupply"] = temperature_raw/10
        
        return True
    
    def read_modbus_data_master_cooling_locked(self, start_address=322):
        """start reading data"""
        data_package = self.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        value = self._client.convert_from_registers(data_package.registers, self._client.DATATYPE.UINT16)
        dtc_active = (value != 0)
        
        self.data["coolinglocked"] = dtc_active
        
        return True   
