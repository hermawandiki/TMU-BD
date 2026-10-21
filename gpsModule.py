import time
import serial
import logging

ts = time.strftime("%Y%m%d")
logName = r'/home/pi/tmu/tmu-app-client-deploy/assets/datalog/sysdata/syslog-' + ts + '.log'
logging.basicConfig(level=logging.INFO, filename=logName, format='%(asctime)s | %(levelname)s: %(message)s')

def initConnection():
    logging.info("init GPS")
    try:
        ser1 = serial.Serial('/dev/ttyUSB_GPS', 4800, timeout = 1, rtscts = True, dsrdtr = False)
    except serial.error as message:
        pass
    except Exception as message:
        pass
    while ser1.getDSR() == False:
        ser1.setDTR(False)
        time.sleep(0.7)
        ser1.setDTR(True)
        time.sleep(0.2)
        ser1.setDTR(False)
        time.sleep(0.7)
    ser1.setRTS(False)
    while ser1.getDSR() == True:
        ser1.setDTR(False)
        time.sleep(0.7)
        ser1.setDTR(True)
        time.sleep(0.2)
        ser1.setDTR(False)
        time.sleep(0.7)
    logging.info("init Done")
    return ser1

def getPosition(port):
    latitude = ""
    longitude = ""
    time.sleep(0.25)
    try:
        x = port.readline()
    except Exception as message:
        pass
    identifierStr = ""
    identifier = ""
    try:
        if len(x) > 6:
            for i in range (1,6):
                identifierStr = identifierStr + (hex(x[i]))[2:]
            identifier = bytes.fromhex(identifierStr).decode("ascii")
        if identifier == "GPGGA":
            if x[18] != 44:
                latitudeStr = ""
                for i in range(18,27):
                    latitudeStr = latitudeStr + (hex(x[i]))[2:]
                latitude = float(bytes.fromhex(latitudeStr[0:4]).decode("ascii")) + (float(bytes.fromhex(latitudeStr[4:]).decode("ascii")))/60
                latIndi = bytes.fromhex((hex(x[28]))[2:]).decode("ascii")            
                longitudeStr = ""
                for i in range(30,40):
                    longitudeStr = longitudeStr + (hex(x[i]))[2:]
                longitude = float(bytes.fromhex(longitudeStr[0:6]).decode("ascii")) + (float(bytes.fromhex(longitudeStr[6:]).decode("ascii")))/60
                lonIndi = bytes.fromhex((hex(x[41]))[2:]).decode("ascii")
                if latIndi == "S":
                    latitude = latitude * -1
                if lonIndi == "W":
                    longitude = longitude * -1
                return latitude, longitude
    except Exception as Message:
        return latitude, longitude
    
def updatePosition(port, maxTry, maxSample, lastPosition):
    currentPosition = None
    sampleNum = 0
    for i in range(0, maxTry):
        while currentPosition is None and sampleNum <= maxSample:
            sampleNum = sampleNum + 1
            try:
                currentPosition = getPosition(port)
            except Exception as Message:
                pass
        if currentPosition != None : lastPosition = currentPosition
        currentPosition = None
        sampleNum = 0
    return(lastPosition)