#!/usr/bin/env python3
from pymodbus.client import ModbusSerialClient

#init modbus device, db, gps
client = ModbusSerialClient(method='rtu', port='/dev/ttyUSB-RSM', baudrate=19200, timeout=1)
getTemp = client.read_holding_registers(0, 4, slave = 7)
getPLC = client.read_holding_registers(55, 4, slave = 1)
getElect1 = client.read_holding_registers(0, 29, slave = 2)
getElect2 = client.read_holding_registers(46, 5, slave = 2)
getElect3 = client.read_holding_registers(800, 6, slave = 2)
getHarmV = client.read_holding_registers(806, 90, slave = 2)
getHarmA = client.read_holding_registers(896, 90, slave = 2)
physical2 = client.write_register(502, 0, slave=1)
tempPT = ((round((getPLC.registers[0]/1000) * 25000))/100) - 50
print(tempPT)
print(getTemp)
print(getElect1)
print(getPLC.registers)
print(physical2)