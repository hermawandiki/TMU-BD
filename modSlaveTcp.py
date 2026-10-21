#!/usr/modSlave/myEnv/bin/env python3
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_tcp
import random
import time
import math
import mysql.connector
import datetime

db = mysql.connector.connect(
    host = "localhost",
    user = "client",
    passwd = "raspi",
    database= "iot_trafo_client")

CTratio = 1

def gatherValues():
    cursor = db.cursor()
    sql = "SELECT * FROM reading_data ORDER BY data_id DESC LIMIT 1"
    cursor.execute(sql)
    result = cursor.fetchall()
    listResult = list(result[0])
    listResult.pop(0)
    listResult.pop(0)
    print(listResult)
    sql = "SELECT * FROM current_harmonic"
    cursor.execute(sql)
    resultIHarm = cursor.fetchall()
    sql = "SELECT * FROM voltage_harmonic"
    cursor.execute(sql)
    resultVHarm = cursor.fetchall()
    db.commit()
    IHarm = []
    VHarm = []
    for i in range(0, 3):
        resultIHarm[i] = list(resultIHarm[i])
        resultVHarm[i] = list(resultVHarm[i])
        resultIHarm[i].pop(0)
        resultVHarm[i].pop(0)
        for member in resultIHarm[i]:
            IHarm.append(member)
        for member in resultVHarm[i]:
            VHarm.append(member)
    inputList = listResult + VHarm + IHarm
    inputList.pop(35)
    inputList.pop(36)
    for i in range(0, 6):
        inputList[i] = int(inputList[i] * 100)
    for i in range(6, 11):
        inputList[i] = int(1000 * (inputList[i])/CTratio)
    for i in range(11, 17):
        inputList[i] = int(10 * inputList[i])
    for i in range(17, 20):
        inputList[i] = int(10 * (inputList[i])/CTratio)
        if inputList[i] < 0:
            inputList[i] = int(inputList[i] + math.pow(2, 16))
    target = int(10 * (inputList[20])/CTratio)
    if target < 0: target = int(target + math.pow(2, 32))
    targetStr = hex(target)[2:]
    while len(targetStr) < 8 : targetStr = "0" + targetStr
    lowWord = int(targetStr[0:4], 16)
    highWord = int(targetStr[4:], 16)
    inputList[20] = lowWord
    inputList.insert(21, highWord)
    for i in range(22, 25):
        inputList[i] = int(10 * (inputList[i])/CTratio)
        if inputList[i] < 0:
            inputList[i] = int(inputList[i] + math.pow(2, 16))
    target = int(10 * (inputList[25])/CTratio)
    if target < 0: target = int(target + math.pow(2, 32))
    targetStr = hex(target)[2:]
    while len(targetStr) < 8 : targetStr = "0" + targetStr
    lowWord = int(targetStr[0:4], 16)
    highWord = int(targetStr[4:], 16)
    inputList[25] = lowWord
    inputList.insert(26, highWord)
    for i in range(27, 30):
        inputList[i] = inputList[i] * 10
    target = int(10 * inputList[30])
    targetStr = hex(target)[2:]
    while len(targetStr) < 8 : targetStr = "0" + targetStr
    lowWord = int(targetStr[0:4], 16)
    highWord = int(targetStr[4:], 16)
    inputList[30] = lowWord
    inputList.insert(31, highWord)
    for i in range(32, 36):
        inputList[i] = int(1000 * inputList[i])
        if inputList[i] < 0:
            inputList[i] = int(inputList[i] + math.pow(2, 16))
    target = int(10 * inputList[37])
    targetStr = hex(target)[2:]
    while len(targetStr) < 8 : targetStr = "0" + targetStr
    lowWord = int(targetStr[0:4], 16)
    highWord = int(targetStr[4:], 16)
    inputList[37] = lowWord
    inputList.insert(38, highWord)
    target = int(10 * inputList[39])
    targetStr = hex(target)[2:]
    while len(targetStr) < 8 : targetStr = "0" + targetStr
    lowWord = int(targetStr[0:4], 16)
    highWord = int(targetStr[4:], 16)
    inputList[39] = lowWord
    inputList.insert(40, highWord)
    for i in range(41, 45):
        inputList[i] = int(10 * inputList[i])
    for i in range(45, 48):
        inputList[i] = int(100 * inputList[i])
    inputList[48] = int(1000 * inputList[48])
    inputList[51] = int(100 * inputList[51])
    inputList[53] = int(100 * inputList[53])    
    for i in range(55, len(inputList)):
        inputList[i] = int(100 * inputList[i])
    return inputList
    
def main():
    try:
        server = modbus_tcp.TcpServer()
        server.start()
        print("Server Started")
        values = [0] * 200
        print(values)
        slave_1 = server.add_slave(1)
        slave_1.add_block('0', cst.HOLDING_REGISTERS, 0, 200)
        slave = server.get_slave(1)
        slave.set_values('0', 0, values)
        while True:
            print("Server Running")
            values = gatherValues()
            slave = server.get_slave(1)
            slave.set_values('0', 0, values)
            print("Data Updated")
            print(datetime.datetime.now())
            print(values[0])
            time.sleep(3)
    finally:
        server.stop()

if __name__ == "__main__":
    main()
