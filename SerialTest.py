#!/usr/bin/env python3
from pymodbus.client import ModbusSerialClient

#init modbus device, db, gps
client = ModbusSerialClient(method='rtu', port='/dev/ttyUSB-RSM', baudrate=19200, timeout=1)
getTemp = client.read_holding_registers(0, 4, slave = 7)
getPLC = client.read_holding_registers(55, 4, slave = 1)
getElect = client.read_holding_registers(0, 29, slave = 2)
physical2 = client.write_register(502, 0, slave=1)
print(getTemp)
print(getElect)
print(getPLC.registers)
print(physical2)