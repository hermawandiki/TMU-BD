#!/usr/bin/env python3
from pymodbus.client import ModbusSerialClient
import time

client = ModbusSerialClient(method='rtu', port='/dev/ttyACM0', baudrate=9600)
client2 = ModbusSerialClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600)
loop = False
relayTest = True
relayState = False
doubleMeter = False
dryType = False
gasState = False

def testBatch():
    if relayTest:
        writeRly = client.write_coil(0, relayState, slave = 1)
        print("Write " + str(relayState) + " to Relay CH0")
        print(writeRly)
        writeRly = client.write_coil(1, relayState, slave = 1)
        print("Write " + str(relayState) + " to Relay CH1")
        print(writeRly)
        writeRly = client.write_coil(2, relayState, slave = 1)
        print("Write " + str(relayState) + " to Relay CH2")
        print(writeRly)
        writeRly = client.write_coil(3, relayState, slave = 1)
        print("Write " + str(relayState) + " to Relay CH3")
        print(writeRly)
        writeRly = client.write_coil(4, relayState, slave = 1)
        print("Write " + str(relayState) + " to Relay CH4")
        print(writeRly)
    
    getTemp = client.read_holding_registers(4, 3, slave = 3)
    print("Read Wireless Temperature Sensor")  
    print(getTemp.registers)
    getElect1 = client.read_holding_registers(0, 29, slave = 2)
    print("Read Power Meter 1")
    print(getElect1.registers) 
    if doubleMeter:
        getElect2 = client.read_holding_registers(0, 29, slave = 6)
        print("Read Power Meter 2")
        print(getElect2.registers) 
    if dryType:
        getWinding = client.read_holding_registers(0, 3, slave = 7)
        print("Read Winding Temperature")
        print(getWinding.registers) 
    if gasState:

        getH2 = client2.read_holding_registers(0, 10, slave = 4)
        print(getH2.registers)
        getMoist = client2.read_input_registers(0, 3, slave = 5)
        print(getMoist.registers)
    print("~~~")

if loop:
    while True:
        testBatch()
        time.sleep(2)
else:   
    testBatch()