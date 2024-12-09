from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.number import NumberDeviceClass
from homeassistant.const import (
    UnitOfTemperature,
)

DOMAIN = "fan_master"
DEFAULT_NAME = "fanmaster"
DEFAULT_SCAN_INTERVAL = 5
DEFAULT_PORT = 502
DEFAULT_MODBUS_ADDRESS = 0
DEFAULT_ACTIVE_DEVICES = 2 #temporaty solution until auto detect works
MAX_DEVICES = 30

ATTR_STATUS_DESCRIPTION = "status_description"
ATTR_MANUFACTURER = "M Engineering"
CONF_MODBUS_ADDRESS = "modbus_address"
CONF_ACTIVE_DEVICES = "number_slaves" #temporary solution until auto detect works

#attributes: type(0=normal | 1=binary), name, key, unit, class, icon
FANMASTER_SENSOR_TYPES = {
    "Master_FBL_SW_Version": [0, "FBL Software Version", "fbl_sw_version", None, None, None],
    "Master_APPL_SW_Version": [0, "APPL Software Version", "appl_sw_version", None, None, None],
    "Master_DTC_Active": [1, "Master DTCs Active", "dtcactive", None, BinarySensorDeviceClass.PROBLEM, None],
    "Master_Coding_List": [0, "Master Coding List", "mastercodinglist", None, None, None],
    "Master_Coding_Invalid": [1, "Coding List Invalid", "codingInvalid", None, BinarySensorDeviceClass.PROBLEM, None],
    "Master_Worst_Dewpoint": [0, "Master Worst Dewpoint", "masterworstdewpoint", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None],
    "Master_Lowest_Supply": [0, "Master Lowest Supply ", "masterlowestsupply", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None],
    "Master_Cooling_Locked": [1, "Cooling Locked", "coolinglocked", None, BinarySensorDeviceClass.LOCK, None],
}


#attributes: type(0=normal | 1=binary), name, key, unit, class, icon
FANDEVICE_SENSOR_TYPES = {
    "Slave_SW_Version": [0, "Software Version", "appl_sw_version", None, None, None],
    "Slave_DTC_Active": [1, "DTCs Active", "dtcactive", None, BinarySensorDeviceClass.PROBLEM, None],
    "Slave_Comm_Timeout": [1, "Communication Timeout", "commtimeout", None, BinarySensorDeviceClass.PROBLEM, None],
    "Slave_Sleep": [1, "Sleep", "sleep", None, None, None],
    "Slave_RSSI_Last": [0, "RSSI last message", "rssilast", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, None],
    "Slave_RSSI_Filtered": [0, "RSSI filtered", "rssifiltered", "dBm", SensorDeviceClass.SIGNAL_STRENGTH, None],
    "Slave_LQI_Last": [0, "LQI last message", "lqilast", None, None, None],
    "Slave_Temp_Supply": [0, "Temperature Supply", "tempsupply", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None],
    "Slave_Temp_Supply_Raw": [0, "Temperature Supply Unfiltered", "tempsupplyraw", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None],
    "Slave_Temp_Return": [0, "Temperature Return", "tempreturn", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None],
    "Slave_Temp_Room": [0, "Temperature Room", "temproom", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None],
    "Slave_Humidity": [0, "Humidity", "humidity", "%", SensorDeviceClass.HUMIDITY, None],
    "Slave_Dewpoint": [0, "Dewpoint", "dewpoint", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, None],
    "Slave_Fan1_RPM": [0, "Fan 1 RPM", "fan1rpm", "RPM", SensorDeviceClass.SPEED, None],
    "Slave_Fan2_RPM": [0, "Fan 2 RPM", "fan2rpm", "RPM", SensorDeviceClass.SPEED, None],
    "Slave_Fan3_RPM": [0, "Fan 3 RPM", "fan3rpm", "RPM", SensorDeviceClass.SPEED, None],
    "Slave_Fan4_RPM": [0, "Fan 4 RPM", "fan4rpm", "RPM", SensorDeviceClass.SPEED, None],
    "Slave_Fan5_RPM": [0, "Fan 5 RPM", "fan5rpm", "RPM", SensorDeviceClass.SPEED, None],
    "Slave_Fan6_RPM": [0, "Fan 6 RPM", "fan6rpm", "RPM", SensorDeviceClass.SPEED, None],
    "Slave_Fan7_RPM": [0, "Fan 7 RPM", "fan7rpm", "RPM", SensorDeviceClass.SPEED, None],
    "Slave_Fan8_RPM": [0, "Fan 8 RPM", "fan8rpm", "RPM", SensorDeviceClass.SPEED, None],
    "Slave_Fan9_RPM": [0, "Fan 9 RPM", "fan9rpm", "RPM", SensorDeviceClass.SPEED, None],
    "Slave_Fan10_RPM": [0, "Fan 10 RPM", "fan10rpm", "RPM", SensorDeviceClass.SPEED, None],
    "Slave_Fan11_RPM": [0, "Fan 11 RPM", "fan11rpm", "RPM", SensorDeviceClass.SPEED, None],
    "Slave_Fan_Speed": [0, "Fan Speed", "fanspeed", "%", SensorDeviceClass.SPEED, None],
    "Slave_Active_Mode": [0, "Active Mode", "activemode", None, None, None],
    "Slave_Window_Open": [1, "Window Open", "window", None, BinarySensorDeviceClass.WINDOW, None],
}

#attributes: name, modbusadress, unit, keylist, operatingValues
FANDEVICE_CLIMATE_TYPES = [
    ["Operating Mode", 20, UnitOfTemperature.CELSIUS, {"roomtemp": "temproom", "hvac": "opmode"}, {"off": 0, "auto": 1, "heating": 2, "cooling": 3, "boost": 4}],
]

#attributes: name, key, modbusadress, datatype, unit, min, max, class
FANDEVICE_NUMBER_TYPES = [
    ["Boost Level", "boostlevel", 21, "u16", "%", 0, 100, NumberDeviceClass.SPEED],
]

#attributes: name, key, modbusadress,
FANDEVICE_SWITCH_TYPES = [
    ["Debug Mode", "debug", 22],
]
    