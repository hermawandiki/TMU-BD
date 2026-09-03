from toolboxTMU import TimerEx
from time import sleep
import RPi.GPIO as GPIO
import Adafruit_ADS1x15
import mysql.connector
import json
import time, datetime, sys

GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.IN) #Oil Level Alarm
GPIO.setup(17, GPIO.IN) #Oil Level Trip

GPIO.setup(23, GPIO.OUT) #TMU Alarm Relay - DO0
GPIO.setup(24, GPIO.OUT) #TMU Trip Relay - DO1
GPIO.setup(25, GPIO.OUT) #Solenoid Relay - DO2

adc = Adafruit_ADS1x15.ADS1115(address = 0x48, busnum = 1)

valveStat = 0
gasEnabler = False
openValveDuration = 10
debugMsg = False
infoMsg = True

db = mysql.connector.connect(
    host = "localhost",
    user = "client",
    passwd = "raspi",
    database = "iot_trafo_client")

def gasRelease():
    global valveStat
    valveStat = 0

def updateJson(name, val):
    try:
        with open("module_IO.json", "r") as jsonFile:
            data = json.load(jsonFile)
        data[name] = val
        with open("module_IO.json", "w") as jsonFile:
            json.dump(data, jsonFile)
    except json.JSONDecodeError:
        if infoMsg == True: print("2D|JSON File corrupt, rewrite")
        data = {
            "resetValve" : False,
            "prevStatOil" : 0
            }
        data[name] = val
        with open("module_IO.json", "w") as jsonFile:
            json.dump(data, jsonFile)        

def main():
    if infoMsg == True: print("2D|Initialize program")
    global valveStat
    timer = TimerEx(interval_sec = openValveDuration, function = gasRelease)
    try:
        with open("module_IO.json", "r") as jsonFile:
            data = json.load(jsonFile)
    except json.JSONDecodeError:
        if infoMsg == True: print("2D|JSON File corrupt at main, use default value")
        data = {
            "resetValve" : False,
            "prevStatOil" : 0
            }
    
    cursor = db.cursor()
    sqlReadStat = "SELECT * FROM transformer_data"
    sqlUpdateDO = "UPDATE do_scan SET state = %s WHERE number = %s"
    sqlUpdateDI = "UPDATE di_scan SET state = %s WHERE number = %s"
    if infoMsg == True: print("2D|Start loop")
    while True:
        start_time = time.time()
        if debugMsg == True: print("2D|1 Stat Oil Level")
        oilLevelAlarm = GPIO.input(13)
        oilLevelTrip = GPIO.input(17)
        if (oilLevelAlarm and oilLevelTrip) or oilLevelTrip:
            oilStat = 1
        elif oilLevelAlarm:
            oilStat = 2
        elif oilLevelAlarm == 0 and oilLevelTrip == 0:
            oilStat = 3
            
        if debugMsg == True: print("2D|2 Gas Fault logic")
        if gasEnabler:
            try:
                with open("module_IO.json", "r") as jsonFile:
                    data = json.load(jsonFile)
            except json.JSONDecodeError:
                if infoMsg == True: print("2D|JSON File corrupt at gas Enabler, use default value")
                data = {
                    "resetValve" : False,
                    "prevStatOil" : 0
                    }
            resetValve = data["resetValve"]
            prevStatOil = data["prevStatOil"]
            if timer.is_alive() == False and resetValve == False:
                if oilStat < prevStatOil:
                    timer.start()
                    valveStat = 1
                    updateJson("resetValve", True)
                else:
                    updateJson("prevStatOil", oilStat)
            elif timer.is_alive() or resetValve:
                if oilStat >= prevStatOil:
                    timer.cancel()
                    valveStat = 0
                    updateJson("resetValve", False)
                elif valveStat == 0:
                    updateJson("prevStatOil", oilStat)
        
        if debugMsg == True: print("2D|3 Input definition, Update DB")
        analogIn1 = 0 if adc.read_adc(1, gain = 1) < 0 else adc.read_adc(1, gain = 1)
        analogIn2 = 0 if adc.read_adc(0, gain = 1) < 0 else adc.read_adc(0, gain = 1)
        
        cursor.execute(sqlUpdateDI, [oilLevelAlarm, 4])
        cursor.execute(sqlUpdateDI, [oilLevelTrip, 5])
        cursor.execute(sqlUpdateDI, [analogIn1, 6])
        cursor.execute(sqlUpdateDI, [analogIn2, 7])
        cursor.execute(sqlReadStat)
        trafoStat = cursor.fetchall()[0][28]
        db.commit()
        
        if debugMsg == True: print("2D|4 Update DO based on Trafo stat & Gas Fault stat")
        if trafoStat == 1:
            cursor.execute(sqlUpdateDO, [1, 0])
            GPIO.output(23, GPIO.HIGH)
            cursor.execute(sqlUpdateDO, [0, 1])
            GPIO.output(24, GPIO.LOW)
            cursor.execute(sqlUpdateDO, [0, 2])
        elif trafoStat == 2:
            cursor.execute(sqlUpdateDO, [0, 0])
            GPIO.output(23, GPIO.LOW)
            cursor.execute(sqlUpdateDO, [1, 1])
            GPIO.output(24, GPIO.HIGH)
            cursor.execute(sqlUpdateDO, [0, 2])
        elif trafoStat == 3:
            cursor.execute(sqlUpdateDO, [0, 0])
            cursor.execute(sqlUpdateDO, [0, 1])
            cursor.execute(sqlUpdateDO, [1, 2])
        else:
            cursor.execute(sqlUpdateDO, [0, 0])
            GPIO.output(23, GPIO.LOW)
            cursor.execute(sqlUpdateDO, [0, 1])
            GPIO.output(24, GPIO.LOW)
            cursor.execute(sqlUpdateDO, [0, 2])
        cursor.execute(sqlUpdateDO, [valveStat, 4])
        GPIO.output(25, GPIO.HIGH if valveStat else GPIO.LOW)
        db.commit()

        sleep(0.5)
        cycleTime = (round(10000 * (time.time() - start_time)))/10000
        if debugMsg == True: print("2D|Cycle time %s" % cycleTime)
        print("2T|%s" % datetime.datetime.now())
        sys.stdout.flush()
    
if __name__ == "__main__":
    main()