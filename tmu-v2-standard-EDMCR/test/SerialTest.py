#!/usr/bin/env python3
from pymodbus.client import ModbusSerialClient
from time import sleep

client = ModbusSerialClient(method='rtu', port='/dev/ttyACM0', baudrate=9600)
loop = False

def signedInt16Handler(data):
    if data > (math.pow(2, 16))/2:
        data = data - math.pow(2, 16)
    else:
        data = data
    return data

def testBatch():
    getDMCR = client.read_holding_registers(0x1301, 4, slave = 1)
    try:
        DMCRval = getDMCR.registers()
    except:
        DMCRval = [0, 0, 0, 4]

    oilLevelAlarm = 1 if DMCRval[3]<=3 else 0
    oilLevelTrip = 1 if DMCRval[3]==1 else 0
    analogIn1 = (signedInt16Handler(DMCRval[1]))/10
    analogIn2 = (signedInt16Handler(DMCRval[0]))/1000

    oilStat = 3
    if (oilLevelAlarm and oilLevelTrip) or oilLevelTrip:
        oilStat = 1
    elif oilLevelAlarm:
        oilStat = 2
    elif oilLevelAlarm == 0 and oilLevelTrip == 0:
        oilStat = 3

    print(f"Oil Level Alarm  = {oilLevelAlarm}")
    print(f"Oil Level Trip   = {oilLevelTrip}")
    print(f"Oil Level Status = {oilStat}")
    print(f"Oil Temperature  = {analogIn1}")
    print(f"Oil Pressure     = {analogIn2}")
    print("~~~")

if loop:
    while True:
        testBatch()
        sleep(2)
else:
    testBatch()
