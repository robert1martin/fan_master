import logging

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

_LOGGER = logging.getLogger(__name__)

class FanDevice:
    def __init__(self, fanmaster, slave_address):
        """Initialize the FanDevice"""
        self._name = f"slave_{slave_address}"
        self._fanmaster = fanmaster
        self._address = slave_address
        self._sensors = []
        self.data = {}  

    def read_modbus_data_device(self):
        return (
            self.read_modbus_data_sw_Version()
            and self.read_modbus_data_dtc_active()
            and self.read_modbus_data_communication_timeout()
            and self.read_modbus_data_sleep()
            and self.read_modbus_data_rssi_last()
            and self.read_modbus_data_rssi_filtered()
            and self.read_modbus_data_lqi()
            and self.read_modbus_data_operating_mode()
            and self.read_modbus_data_boost_level()
            and self.read_modbus_data_debug_mode()
            and self.read_modbus_data_temperature_supply()
            and self.read_modbus_data_temperature_supply_raw()
            and self.read_modbus_data_temperature_return()
            and self.read_modbus_data_temperature_room()
            and self.read_modbus_data_humidity()
            and self.read_modbus_data_dewpoint()
            and self.read_modbus_data_fan_rpm(36,1)
            and self.read_modbus_data_fan_rpm(37,2)
            and self.read_modbus_data_fan_rpm(38,3)
            and self.read_modbus_data_fan_rpm(39,4)
            and self.read_modbus_data_fan_rpm(40,5)
            and self.read_modbus_data_fan_rpm(41,6)
            and self.read_modbus_data_fan_rpm(42,7)
            and self.read_modbus_data_fan_rpm(43,8)
            and self.read_modbus_data_fan_rpm(44,9)
            and self.read_modbus_data_fan_rpm(45,10)
            and self.read_modbus_data_fan_rpm(46,11)
            and self.read_modbus_data_fan_speed()
            and self.read_modbus_data_active_mode()
            and self.read_modbus_data_window()
        )
        
    def read_modbus_data_sw_Version(self, start_address=0):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=2)      
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)
        
        appl_sw_version_major = decoder.decode_8bit_uint()
        appl_sw_version_minor = decoder.decode_8bit_uint()
        appl_sw_version_patch = decoder.decode_8bit_uint()

        #_LOGGER.debug(f'read sw_Version of {self._name} : {appl_sw_version_major}.{appl_sw_version_minor}.{appl_sw_version_patch}')
        self.data["appl_sw_version"] = f"{appl_sw_version_major}.{appl_sw_version_minor}.{appl_sw_version_patch}"
        
        return True
        
    
    def read_modbus_data_dtc_active(self, start_address=2):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        dtc_active = (decoder.decode_16bit_uint() != 0)
        
        #_LOGGER.debug(f'read dtc status of {self._name} : {dtc_active}')
        self.data["dtcactive"] = dtc_active
        
        return True  
    
    def read_modbus_data_communication_timeout(self, start_address=3):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        commtimeout = (decoder.decode_16bit_uint() != 0)
        
        #_LOGGER.debug(f'read dtc status of {self._name} : {dtc_active}')
        self.data["commtimeout"] = commtimeout
        
        return True 
    
    def read_modbus_data_sleep(self, start_address=4):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        sleep = (decoder.decode_16bit_uint() != 0)
        
        #_LOGGER.debug(f'read dtc status of {self._name} : {dtc_active}')
        self.data["sleep"] = sleep
        
        return True  
        
    
    def read_modbus_data_rssi_last(self, start_address=5):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["rssilast"] = decoder.decode_16bit_int()
        
        return True  
    
    def read_modbus_data_rssi_filtered(self, start_address=6):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["rssifiltered"] = decoder.decode_16bit_int()
        
        return True  
    
    def read_modbus_data_lqi(self, start_address=7):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["lqilast"] = decoder.decode_16bit_uint()
        
        return True 
    
    def read_modbus_data_operating_mode(self, start_address=20):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        self.data["opmode"] = decoder.decode_16bit_int()
            
        return True
    
    def read_modbus_data_boost_level(self, start_address=21):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        boostlevel = decoder.decode_16bit_uint()
        if (boostlevel == 0):
            self.data["boostlevel"] = "Default"
        elif (boostlevel  > 100):
            self.data["boostlevel"] = "Error"
        else:
            self.data["boostlevel"] = boostlevel
        
        return True 
    
    
    def read_modbus_data_debug_mode(self, start_address=22):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        debug = (decoder.decode_16bit_uint() != 0)
        self.data["debug"] = debug
        
        return True  
    
    def read_modbus_data_temperature_supply(self, start_address=30):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        temperature_raw = decoder.decode_16bit_int()
        if (temperature_raw == 32767):
            self.data["tempsupply"] = "Error"
        else:
            self.data["tempsupply"] = temperature_raw/10
        
        return True 
    
    def read_modbus_data_temperature_supply_raw(self, start_address=31):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        temperature_raw = decoder.decode_16bit_int()
        if (temperature_raw == 32767):
            self.data["tempsupplyraw"] = "Error"
        else:
            self.data["tempsupplyraw"] = temperature_raw/10
        
        return True 
    
    def read_modbus_data_temperature_return(self, start_address=32):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        temperature_raw = decoder.decode_16bit_int()
        if (temperature_raw == 32767):
            self.data["tempreturn"] = "Error"
        else:
            self.data["tempreturn"] = temperature_raw/10
        
        return True  
    
    def read_modbus_data_temperature_room(self, start_address=33):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        temperature_raw = decoder.decode_16bit_int()
        if (temperature_raw == 32767):
            self.data["temproom"] = "Error"
        else:
            self.data["temproom"] = temperature_raw/10
        
        return True 
    
    def read_modbus_data_humidity(self, start_address=34):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        humidity_raw = decoder.decode_16bit_uint()
        if (humidity_raw >= 65533):
            self.data["humidity"] = "Error"
        else:
            self.data["humidity"] = humidity_raw/10
        
        return True  
    
    def read_modbus_data_dewpoint(self, start_address=35):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        temperature_raw = decoder.decode_16bit_int()
        if (temperature_raw == 32765 or temperature_raw == 32767):
            self.data["dewpoint"] = "Error"
        else:
            self.data["dewpoint"] = temperature_raw/10
        
        return True
    
    def read_modbus_data_fan_rpm(self, start_address=36, fan=1):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  
        
        speed = decoder.decode_16bit_uint()
        if (speed == 65534):
            self.data[f"fan{fan}rpm"] = "NotAttached"
        elif (speed == 65535):
            self.data[f"fan{fan}rpm"] = "Error"
        else:
            self.data[f"fan{fan}rpm"] = speed
        
        return True
    
    def read_modbus_data_fan_speed(self, start_address=47):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  

        speed = decoder.decode_16bit_uint()
        if (speed == 65535):
            self.data[f"fanspeed"] = "Error"
            
        self.data["fanspeed"] = speed
        
        return True
    
    def read_modbus_data_active_mode(self, start_address=48):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  

        mode = decoder.decode_16bit_uint()
        modeString = ""
        if (mode == 0): modeString  = "Off"
        elif (mode == 1): modeString  = "Boost"
        elif (mode == 2): modeString  = "Heating"
        elif (mode == 3): modeString  = "Cooling"
        else: modeString = "Error"
        self.data["activemode"] = modeString
        
        return True
    
    def read_modbus_data_window(self, start_address=49):
        data_package = self._fanmaster.read_holding_registers(unit=self._address, address=start_address, count=1) 
        if data_package.isError():
            _LOGGER.debug(f'data Error at start address {start_address}')
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(data_package.registers, byteorder=Endian.BIG)  

        window = (decoder.decode_16bit_uint() != 0)
        self.data["window"] = window
        
        return True
    
    
    
    