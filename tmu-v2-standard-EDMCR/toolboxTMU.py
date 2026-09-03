import tkinter as tk
from threading import Timer, Lock
import json
import math
import random
import struct

class parameter:
    def __init__(self, name, value, isWatched, highAlarm, lowAlarm, highTrip, lowTrip, status, trafoStat):
        self.name = name
        self.value = value
        self.isWatched = isWatched
        self.highAlarm = highAlarm
        self.lowAlarm = lowAlarm
        self.highTrip = highTrip
        self.lowTrip = lowTrip
        self.status = status
        self.trafoStat = trafoStat
        
    def toJson(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)
    
def find_tap(input_value, input_output_map):
    sorted_data = sorted(input_output_map.items(), reverse=True, key=lambda x: x[1])
    for output, max_input in sorted_data:
        if input_value >= max_input:
            return output
    return 0 

def initParameter(dataSet, inputData, trafoSetting, trafoData, tripSetting, dataLen):
    paramThreshold = [[None]*dataLen, [None]*dataLen, [None]*dataLen, [None]*dataLen]
    paramTrip = [None]*dataLen
    arrayString = ["Voltage UN", "Voltage VN", "Voltage WN", 
                    "Voltage UV", "Voltage VW", "Voltage UW",
                    "Current U", "Current V", "Current W", 
                    "Total Current", "Neutral Current",
                    "THDV U", "THDV V", "THDV W",
                    "THDI U", "THDI V", "THDI W",
                    "Active Power U", "Active Power V", 
                    "Active Power W", "Total Active Power",
                    "Reactive Power U", "Reactive Power V", 
                    "Reactive Power W", "Total Reactive Power",
                    "Apparent Power U", "Apparent Power V", 
                    "Apparent Power W", "Total Apparent Power",
                    "Power Factor U", "Power Factor V", "Power Factor W",
                    "Average Power Factor", "Frequency",
                    "Active Energy", "Reactive Energy",
                    "Busbar Temperature U", "Busbar Temperature V", 
                    "Busbar Temperature W", "Top Oil Temperature",
                    "Winding Temperature U", "Winding Temperature V", 
                    "Winding Temperature W",  "Tank Pressure", "Oil Level",
                    "KRated U", "Derating U", 
                    "KRated V", "Derating V", 
                    "KRated W", "Derating W",
                    "H2 ppm", "Water Content ppm",
                    "Gap Voltage U-V", "Gap Voltage V-W", "Gap Voltage U-W"]
    iswatchBool = [False, False, False, True, True, True,
                    True, True, True, False, True, 
                    True, True, True, True, True, True,
                    False, False, False, False,
                    False, False, False, False,
                    False, False, False, False,
                    False, False, False, True, True, False, False,
                    True, True, True, True, True, True, True, True, True,
                    False, False, False, False, False, False, 
                    True, True, True, True, True]
    
    trafoSetting = list(trafoSetting)
    trafoSetting.pop(23)
    trafoSetting.pop(23)
    
    for i in range(0, 3):
        paramThreshold[0][i+3] = trafoSetting[2] #low trip Voltage
        paramThreshold[1][i+3] = trafoSetting[4] #low alarm Voltage
        paramThreshold[2][i+3] = trafoSetting[8] #high alarm Voltage
        paramThreshold[3][i+3] = trafoSetting[6] #high trip Voltage
        paramThreshold[2][i+53] = (trafoSetting[9] * trafoData[4])/(100 * math.sqrt(3)) #high alarm gap Voltage
        paramThreshold[3][i+53] = (trafoSetting[10] * trafoData[4])/(100 * math.sqrt(3)) #high trip gap Voltage
        paramThreshold[2][i+6] = (trafoSetting[21] * trafoData[6])/100 #high alarm Current Profile
        paramThreshold[3][i+6] = (trafoSetting[22] * trafoData[6])/100 #high trip Current Profile
        paramThreshold[2][i+40] = trafoSetting[17] #high alarm WTI Temp
        paramThreshold[3][i+40] = trafoSetting[18] #high trip WTI Temp
        paramThreshold[2][i+36] = trafoSetting[25] #high alarm Busbar Temp
        
        paramThreshold[3][i+36] = trafoSetting[26] #high trip Busbar Temp
        paramThreshold[2][i + 11] = trafoSetting[29] #high alarm THD Voltage Alarm
        paramThreshold[3][i + 11] = trafoSetting[30] #high trip THD Voltage Trip
        paramThreshold[2][i + 14] = trafoSetting[27] #high alarm THD Current Alarm
        paramThreshold[3][i + 14] = trafoSetting[28] #high trip THD Current Trip

        paramTrip[i+3] = tripSetting[1] #trip setting Voltage
        paramTrip[i+53] = tripSetting[2] #trip setting gap Voltage
        paramTrip[i+6] = tripSetting[7] #trip setting Current Profile
        paramTrip[i+40] = tripSetting[10] #trip setting WTI
        paramTrip[i+36] = tripSetting[5] #trip setting Busbar Temp
        paramTrip[i+11] = tripSetting[12] #trip setting THD Voltage
        paramTrip[i+14] = tripSetting[11] #trip setting THD Current

    paramThreshold[0][33] = trafoData[7] - ((trafoSetting[11] * trafoData[7])/100) #low trip Frequency
    paramThreshold[1][33] = trafoData[7] - ((trafoSetting[12] * trafoData[7])/100) #low alarm Frequency
    paramThreshold[2][33] = trafoData[7] + ((trafoSetting[14] * trafoData[7])/100) #high alarm Frequency
    paramThreshold[3][33] = trafoData[7] + ((trafoSetting[13] * trafoData[7])/100) #high trip Frequency
    paramThreshold[2][39] = trafoSetting[15] #high alarm Top Oil Temp
    paramThreshold[3][39] = trafoSetting[16] #high trip Top Oil Temp
    paramThreshold[1][32] = trafoSetting[19] #low alarm PF
    paramThreshold[0][32] = trafoSetting[20] #low trip PF
    paramThreshold[2][43] = trafoSetting[24] #high alarm Pressure Tank
    paramThreshold[3][43] = trafoSetting[23] #high trip Pressure Tank
    paramThreshold[2][10] = trafoSetting[31] #high alarm Neutral Current
    paramThreshold[3][10] = trafoSetting[32] #high trip Neutral Current
    paramThreshold[1][44] = 2 #low alarm Oil Level
    paramThreshold[0][44] = 1 #low trip Oil Level
    paramThreshold[2][51] = trafoSetting[33] #high alarm H2 ppm
    paramThreshold[3][51] = trafoSetting[34] #high trip H2 ppm
    paramThreshold[2][52] = trafoSetting[35] #high alarm Water Content ppm
    paramThreshold[3][52] = trafoSetting[36] #high trip Water Content ppm

    paramTrip[33] = tripSetting[3] #trip setting Frequency
    paramTrip[39] = tripSetting[4] #trip setting Oil Temp
    paramTrip[32] = tripSetting[6] #trip setting PF
    paramTrip[43] = tripSetting[8] #trip setting Tank Pressure
    paramTrip[10] = tripSetting[13] #trip setting Neutral Current
    paramTrip[44] = tripSetting[9] #trip setting Oil Level
    paramTrip[51] = tripSetting[14] #trip setting H2 ppm
    paramTrip[52] = tripSetting[15] #trip setting Water Content ppm

    for i in range(0, dataLen):            
        dataSet[i].name = arrayString[i]
        dataSet[i].value = inputData[i]
        dataSet[i].isWatched = iswatchBool[i]
        if dataSet[i].isWatched:
            dataSet[i].highAlarm = paramThreshold[2][i]
            dataSet[i].lowAlarm = paramThreshold[1][i]
            dataSet[i].highTrip = paramThreshold[3][i]
            dataSet[i].lowTrip = paramThreshold[0][i]
            if dataSet[i].highAlarm and dataSet[i].lowAlarm:
                if dataSet[i].value <= dataSet[i].lowTrip:
                    dataSet[i].status = 1
                    if paramTrip[i] == 0:
                        dataSet[i].trafoStat = 1
                    elif paramTrip[i] == 1:
                        dataSet[i].trafoStat = 2
                    elif paramTrip[i] == 2:
                        dataSet[i].trafoStat = 3
                elif dataSet[i].value > dataSet[i].lowTrip and dataSet[i].value <= dataSet[i].lowAlarm:
                    dataSet[i].status = 2
                    dataSet[i].trafoStat = 1
                elif dataSet[i].value > dataSet[i].lowAlarm and dataSet[i].value < dataSet[i].highAlarm:
                    dataSet[i].status = 3
                    dataSet[i].trafoStat = 0
                elif dataSet[i].value >= dataSet[i].highAlarm and dataSet[i].value < dataSet[i].highTrip:
                    dataSet[i].status = 4
                    dataSet[i].trafoStat = 1
                elif dataSet[i].value >= dataSet[i].highTrip:
                    dataSet[i].status = 5
                    if paramTrip[i] == 0:
                        dataSet[i].trafoStat = 1
                    elif paramTrip[i] == 1:
                        dataSet[i].trafoStat = 2
                    elif paramTrip[i] == 2:
                        dataSet[i].trafoStat = 3
            elif dataSet[i].highAlarm:
                if dataSet[i].value < dataSet[i].highAlarm:
                    dataSet[i].status = 3
                    dataSet[i].trafoStat = 0
                elif dataSet[i].value >= dataSet[i].highAlarm and dataSet[i].value < dataSet[i].highTrip:
                    dataSet[i].status = 4
                    dataSet[i].trafoStat = 1
                elif dataSet[i].value >= dataSet[i].highTrip:
                    dataSet[i].status = 5
                    if paramTrip[i] == 0:
                        dataSet[i].trafoStat = 1
                    elif paramTrip[i] == 1:
                        dataSet[i].trafoStat = 2
                    elif paramTrip[i] == 2:
                        dataSet[i].trafoStat = 3
            elif dataSet[i].lowAlarm:
                if dataSet[i].value <= dataSet[i].lowTrip:
                    dataSet[i].status = 1
                    if paramTrip[i] == 0:
                        dataSet[i].trafoStat = 1
                    elif paramTrip[i] == 1:
                        dataSet[i].trafoStat = 2
                    elif paramTrip[i] == 2:
                        dataSet[i].trafoStat = 3
                elif dataSet[i].value > dataSet[i].lowTrip and dataSet[i].value <= dataSet[i].lowAlarm:
                    dataSet[i].status = 2
                    dataSet[i].trafoStat = 1
                elif dataSet[i].value > dataSet[i].lowAlarm:
                    dataSet[i].status = 3
                    dataSet[i].trafoStat = 0
    return(dataSet)

def dataParser(exhibitStat, getEnergy, getVI, getPower, getFPF, getTHD, getK, dataLen, CTratio, PTratio):
    outputData = [0]*dataLen
    fragment_1 = getattr(getEnergy, "registers", []) or [0]*10
    fragment_2 = getattr(getVI, "registers", []) or [0]*34
    fragment_3 = getattr(getPower, "registers", []) or [0]*24
    fragment_4 = getattr(getFPF, "registers", []) or [0]*42
    fragment_5 = getattr(getTHD, "registers", []) or [0]*36
    fragment_6 = getattr(getK, "registers", []) or [0]*6
    try:
        inputData = fp32Handler(fragment_1 + fragment_2 + fragment_3 + fragment_4 + fragment_5 + fragment_6, "AB")
    except:
        inputData = [0]*76

    for i in range(3):
        outputData[i] = inputData[i + 19] #Voltage Phase Neutral
        outputData[i + 3] = inputData[i + 15] #Voltage Phase Phase
        outputData[i + 6] = inputData[i + 5] #current
        outputData[i + 29] = inputData[i + 51] #PF
        outputData[i + 17] = inputData[i + 22] #P
        outputData[i + 21] = inputData[i + 26] #Q
        outputData[i + 25] = inputData[i + 30] #S
        outputData[i + 11] = inputData[i + 70] #THD Voltage
        outputData[i + 14] = inputData[i + 55] #THD Current
        outputData[i*2 + 45] = inputData[i + 73] #KRated
    outputData[10] = inputData[8] #Neutral Current
    outputData[20] = inputData[25] #Psig
    outputData[24] = inputData[29] #Qsig
    outputData[28] = inputData[33] #Ssig
    outputData[33] = inputData[34] #Frequency 
    outputData[34] = inputData[0] #kWh
    outputData[35] = inputData[4] #kVARh
    outputData[32] = inputData[54] #PF Total
    outputData[9] = (outputData[6] + outputData[7] + outputData[8])/3 #Average Current
    outputData[53] = abs(outputData[0] - outputData[1]) #Gap Voltage Un-Vn
    outputData[54] = abs(outputData[1] - outputData[2]) #Gap Voltage Vn-Wn
    outputData[55] = abs(outputData[0] - outputData[2]) #Gap Voltage Un-Wn
    
    #Exhibition only
    if exhibitStat:
        outputData = randomify(dataLen)

    return outputData

def randomify(dataLen):
    outputData = [0]*dataLen
    #randomify getTemp
    try:
        outputData[36] = (random.randint(3500, 4200))/100
        outputData[37] = (random.randint(3500, 4200))/100
        outputData[38] = (random.randint(3500, 4200))/100 #busbar Temp
    except:
        pass
    #randomify getElect1
    try:
        for i in range(0, 3):
            outputData[i] = (random.randint(21750, 23050))/100 #Voltage Phase Neutral
            outputData[i + 3] = math.pow(3, 0.5) * outputData[i] #Voltage Phase Phase
            outputData[i + 6] = (random.randint(400000, 750000))/1000 #Current
            outputData[i + 29] = (random.randint(900, 1000))/1000 #PF
            outputData[i + 17] = outputData[i + 3] * outputData[i + 6] * outputData[i + 29] #P
            outputData[i + 21] = outputData[i + 3] * outputData[i + 6] * math.sin(math.acos(outputData[i + 29])) #Q
        #outputData[10] = math.sqrt(math.pow(outputData[6], 2) + math.pow(outputData[7], 2) + math.pow(outputData[8], 2) - outputData[6]*outputData[7] - outputData[7]*outputData[8] - outputData[6]*outputData[8]) #Neutral Current
        outputData[10] = (random.randint(4920, 10000))/1000
        outputData[20] = outputData[17] + outputData[18] + outputData[19] #Psig
        outputData[24] = outputData[21] + outputData[22] + outputData[23]  #Qsig
        outputData[33] = (random.randint(4920, 5000))/100 #Frequency 
        outputData[34] = 43516251 #kWh
        outputData[35] = 3562 #kVARh
        outputData[32] = (outputData[29] + outputData[30] + outputData[31])/3 #Average PF
        outputData[9] = outputData[6] + outputData[7] + outputData[8] #Total Current
        outputData[53] = abs(outputData[0] - outputData[1]) #Gap Voltage Un-Vn
        outputData[54] = abs(outputData[1] - outputData[2]) #Gap Voltage Vn-Wn
        outputData[55] = abs(outputData[0] - outputData[2]) #Gap Voltage Un-Wn
    except:
        pass
    #parse getElect2
    try:
        for i in range(0, 3):
            outputData[i + 25] = outputData[i + 6] * outputData[i + 3] #S
        outputData[28] = outputData[25] + outputData[26] + outputData[27] #Ssig
    except:
        pass
    #parse getElect3
    try:
        for i in range(0, 3):
            outputData[i + 11] = (random.randint(12, 40))/10 #THD Voltage
            outputData[i + 14] = (random.randint(10, 100))/10 #THD Current
    except:
        pass
    #parse getH2 and getMoist
    try:
        outputData[51] = random.randint(0, 9) #H2 ppm
        outputData[52] = random.randint(0, 9) #Water Content ppm
    except:
        pass
    return outputData

def harmonicParser(inputArg):
    try:
        inputList = [inputArg.registers[0:30], inputArg.registers[30:60], inputArg.registers[60:]]
        outputList = [[0]*15, [0]*15, [0]*15]
        harmIndex = 0
        for i in range(0, 3):
            for j in range(0, len(outputList[i])):
                if j % 2 == 1:
                    outputList[i][harmIndex] = (inputList[i][j])/10
                    harmIndex = harmIndex + 1
            harmIndex = 0
            outputList[i].insert(0, 100)
    except:
        outputList = [[0]*16, [0]*16, [0]*16]
    return outputList

def signedInt16Handler(data):
    if data > (math.pow(2, 16))/2:
        data = data - math.pow(2, 16)
    else:
        data = data
    return data

def signedInt32Handler(dataset):
    hexData = [hex(member)[2:] for member in dataset]
    idata = [0]*int(len(dataset)/2)
    for i in range(0, len(hexData)): 
        while len(hexData[i]) < 4: hexData[i] = "0" + hexData[i]
    for i in range(0, int(len(hexData)/2)):
        tempData = int((hexData[i*2+1] + hexData[i*2]),16)
        if tempData > (math.pow(2, 32))/2:
            idata[i] = tempData - math.pow(2, 32)
        else:
            idata[i] = tempData
    return idata

def unsignedInt32Handler(dataset):
    hexData = [hex(member)[2:] for member in dataset]
    for i in range(0, len(hexData)): 
        while len(hexData[i]) < 4: hexData[i] = "0" + hexData[i]
    tempData = int((hexData[1] + hexData[0]),16)
    return tempData

def fp32Handler(dataset, word_order="AB"):
    """
    Convert list of 16-bit registers to list of FP32 values.

    word_order:
        "AB" = High word first (ABCD)  [Commonly Used]
        "BA" = Low word first  (CDAB)
    """
    if len(dataset) % 2 != 0:
        raise ValueError("FP32 requires even number of registers")

    result = []
    for i in range(0, len(dataset), 2):
        hi, lo = dataset[i], dataset[i + 1]

        if word_order == "AB":
            packed = struct.pack(">HH", hi, lo)
        elif word_order == "BA":
            packed = struct.pack(">HH", lo, hi)
        else:
            raise ValueError("word_order must be 'AB' or 'BA'")

        value = struct.unpack(">f", packed)[0]
        result.append(round(value, 3))
    return result

def binaryToDecimal(binaryList):
    decimal = 0
    i = 0
    for bit in binaryList:
        decimal = decimal + bit * math.pow(2, i)
        i += 1
    return int(decimal)

def convertBinList(stateDI, stateDO, tripStatus):
    binList = [0, 0, 0, 0, 0]

    binDI = [0]*6
    for i in range(0, 6):
        binDI[i] = stateDI[i][2]
    binList[0] = binaryToDecimal(binDI)

    binDO = [0]*5
    for i in range(0, 5):
        binDO[i] = stateDO[i][2]
    binList[1] = binaryToDecimal(binDO)

    binAlarm = [0]*len(tripStatus)
    binTrip1 = [0]*len(tripStatus)
    binTrip2 = [0]*len(tripStatus)
    for i in range(0, len(tripStatus)):
        if tripStatus[i] == 0:
            binAlarm[i] = 0
            binTrip1[i] = 0
            binTrip2[i] = 0
        elif tripStatus[i] == 1:
            binAlarm[i] = 1
            binTrip1[i] = 0
            binTrip2[i] = 0
        elif tripStatus[i] == 2:
            binAlarm[i] = 0
            binTrip1[i] = 1
            binTrip2[i] = 0
        elif tripStatus[i] == 3:
            binAlarm[i] = 0
            binTrip1[i] = 0
            binTrip2[i] = 1
        else:
            pass
    binList[2] = binaryToDecimal(binAlarm)
    binList[3] = binaryToDecimal(binTrip1)
    binList[4] = binaryToDecimal(binTrip2)

    return binList

class sqlLibrary():
    sqlTrafoSetting = "SELECT * FROM transformer_settings"
    sqlTrafoData = "SELECT * FROM transformer_data"
    sqlTrafoStatus = "SELECT * FROM transformer_status"
    sqlTripStatus = "SELECT * FROM trip_status"
    sqlTripSetting = "SELECT * FROM trip_settings"
    sqlDIscan = "SELECT * FROM di_scan"
    sqlDOscan = "SELECT * FROM do_scan"
    sqlConstantWTI = "SELECT WindingExponent, K21, K22, T0, Tw FROM constanta_value WHERE typeCooling = %s"
    sqlFailure = "SELECT * FROM failure_log"
    sqlLastFailure = "SELECT * FROM failure_log ORDER BY failure_id DESC LIMIT 1"
    sqlResolveFailure = "UPDATE failure_log SET duration = %s WHERE failure_id = %s"
    sqlUpdateTrafoStat = "UPDATE transformer_data SET status = %s WHERE trafoId = 1"
    sqlUpdateTapPos = "UPDATE transformer_data SET impedance = %s WHERE trafoId = 1"
    sqlUpdateTransformerStatus = """UPDATE transformer_status SET 
                    Vab = %s , Vbc = %s , Vca = %s ,
                    Current1 = %s , Current2 = %s , Current3 = %s , Ineutral = %s ,
                    THDVoltage1 = %s, THDVoltage2 = %s , THDVoltage3 = %s , 
                    THDCurrent1 = %s, THDCurrent2 = %s , THDCurrent3 = %s ,                
                    PF = %s , Freq = %s , BusTemp1 = %s , BusTemp2 = %s , BusTemp3 = %s ,
                    OilTemp = %s , WTITemp1 = %s , WTITemp2 = %s , WTITemp3 = %s ,
                    Pressure = %s , OilLevel = %s , H2ppm = %s , Moistureppm = %s ,
                    Uab = %s , Ubc = %s , Uca = %s WHERE trafoId = 1"""
    sqlUpdateTripStatus = """UPDATE trip_status SET 
                    Vab = %s , Vbc = %s , Vca = %s ,
                    Current1 = %s , Current2 = %s , Current3 = %s , Ineutral = %s ,
                    THDVoltage1 = %s, THDVoltage2 = %s , THDVoltage3 = %s , 
                    THDCurrent1 = %s, THDCurrent2 = %s , THDCurrent3 = %s ,                
                    PF = %s , Freq = %s , BusTemp1 = %s , BusTemp2 = %s , BusTemp3 = %s ,
                    OilTemp = %s , WTITemp1 = %s , WTITemp2 = %s , WTITemp3 = %s ,
                    Pressure = %s , OilLevel = %s , H2ppm = %s , Moistureppm = %s ,
                    Uab = %s , Ubc = %s , Uca = %s WHERE trafoId = 1"""
    sqlUpdateVHarm1 = """UPDATE voltage_harmonic SET 
                    1st = %s , 3rd = %s , 5th = %s , 7th = %s , 9th = %s , 11th = %s , 
                    13th = %s , 15th = %s , 17th = %s , 19th = %s , 21th = %s , 23th = %s , 
                    25th = %s , 27th = %s , 29th = %s , 31th = %s WHERE Phase = 1"""
    sqlUpdateVHarm2 = """UPDATE voltage_harmonic SET 
                    1st = %s , 3rd = %s , 5th = %s , 7th = %s , 9th = %s , 11th = %s , 
                    13th = %s , 15th = %s , 17th = %s , 19th = %s , 21th = %s , 23th = %s , 
                    25th = %s , 27th = %s , 29th = %s , 31th = %s WHERE Phase = 2"""
    sqlUpdateVHarm3 = """UPDATE voltage_harmonic SET 
                    1st = %s , 3rd = %s , 5th = %s , 7th = %s , 9th = %s , 11th = %s , 
                    13th = %s , 15th = %s , 17th = %s , 19th = %s , 21th = %s , 23th = %s , 
                    25th = %s , 27th = %s , 29th = %s , 31th = %s WHERE Phase = 3"""
    sqlUpdateIHarm1 = """UPDATE current_harmonic SET 
                    1st = %s , 3rd = %s , 5th = %s , 7th = %s , 9th = %s , 11th = %s , 
                    13th = %s , 15th = %s , 17th = %s , 19th = %s , 21th = %s , 23th = %s , 
                    25th = %s , 27th = %s , 29th = %s , 31th = %s WHERE Phase = 1"""
    sqlUpdateIHarm2 = """UPDATE current_harmonic SET 
                    1st = %s , 3rd = %s , 5th = %s , 7th = %s , 9th = %s , 11th = %s , 
                    13th = %s , 15th = %s , 17th = %s , 19th = %s , 21th = %s , 23th = %s , 
                    25th = %s , 27th = %s , 29th = %s , 31th = %s WHERE Phase = 2"""
    sqlUpdateIHarm3 = """UPDATE current_harmonic SET 
                    1st = %s , 3rd = %s , 5th = %s , 7th = %s , 9th = %s , 11th = %s , 
                    13th = %s , 15th = %s , 17th = %s , 19th = %s , 21th = %s , 23th = %s , 
                    25th = %s , 27th = %s , 29th = %s , 31th = %s WHERE Phase = 3"""
    sqlInsertData = """INSERT INTO reading_data (timestamp,
                    Van, Vbn, Vcn, Vab, Vbc, Vca, Ia, Ib, Ic, Iavg, Ineutral,
                    THDV1, THDV2, THDV3, THDI1, THDI2, THDI3,
                    Pa, Pb, Pc, Psig, Qa, Qb, Qc, Qsig, Sa, Sb, Sc, Ssig,
                    PFa, PFb, PFc, PFsig, Freq, kWh, kVARh, 
                    BusTemp1, BusTemp2, BusTemp3, OilTemp,
                    WTITemp1, WTITemp2, WTITemp3, Press, Level,
                    KRateda, deRatinga, KRatedb, deRatingb, KRatedc, deRatingc,
                    H2ppm, Moistureppm, UnbalanceUV, UnbalanceVW, UnbalanceUW) VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s)"""
    sqlInsertFailure = "INSERT INTO failure_log (time_start, failure_type, parameter, parameterValue) VALUES (%s, %s, %s, %s)"


class TimerEx(object):
    """
    A reusable thread safe timer implementation
    """

    def __init__(self, interval_sec, function, *args, **kwargs):
        """
        Create a timer object which can be restarted

        :param interval_sec: The timer interval in seconds
        :param function: The user function timer should call once elapsed
        :param args: The user function arguments array (optional)
        :param kwargs: The user function named arguments (optional)
        """
        self._interval_sec = interval_sec
        self._function = function
        self._args = args
        self._kwargs = kwargs
        # Locking is needed since the '_timer' object might be replaced in a different thread
        self._timer_lock = Lock()
        self._timer = None

    def start(self, restart_if_alive=True):
        """
        Starts the timer and returns this object [e.g. my_timer = TimerEx(10, my_func).start()]

        :param restart_if_alive: 'True' to start a new timer if current one is still alive
        :return: This timer object (i.e. self)
        """
        with self._timer_lock:
            # Current timer still running
            if self._timer is not None:
                if not restart_if_alive:
                    # Keep the current timer
                    return self
                # Cancel the current timer
                self._timer.cancel()
            # Create new timer
            self._timer = Timer(self._interval_sec, self.__internal_call)
            self._timer.start()
        # Return this object to allow single line timer start
        return self

    def cancel(self):
        """
        Cancels the current timer if alive
        """
        with self._timer_lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None

    def is_alive(self):
        """
        :return: True if current timer is alive (i.e not elapsed yet)
        """
        with self._timer_lock:
            if self._timer is not None:
                return self._timer.is_alive()
        return False

    def __internal_call(self):
        # Release timer object
        with self._timer_lock:
            self._timer = None
        # Call the user defined function
        self._function(*self._args, **self._kwargs)

def initTkinter():
    class MyScreen:
        screen = tk.Tk()
        screen.title("TMU Gateway")
        width= screen.winfo_screenwidth() 
        height= screen.winfo_screenheight()
        screen.geometry("%dx%d" % (width, height))
        screen.attributes('-topmost', True)
        screen.configure(background='#17C0EB')

        restartBtn = tk.Button(
            screen,
            text = "Restart",
            font = ("Helvetica",16),
            height = 1,
            width = 7)
        stopBtn1 = tk.Button(
            screen,
            text = "Stop",
            font = ("Helvetica",16),
            height = 1,
            width = 7)
        prog1Txt = tk.Label(
                screen,
                font = ("Helvetica",16),
                text = "Data Handler Status"
                )
        prog1Lbl = tk.Label(
                screen,
                font = ("Helvetica",16)
                )
        lastHB1Txt = tk.Label(
                screen,
                font = ("Helvetica",16),
                text = "Last Heartbeat"
                )
        lastHB1Lbl = tk.Label(
                screen,
                font = ("Helvetica",16)
                )
        stopBtn2 = tk.Button(
            screen,
            text = "Stop",
            font = ("Helvetica",16),
            height = 1,
            width = 7)
        prog2Txt = tk.Label(
                screen,
                font = ("Helvetica",16),
                text = "Module IO Status"
                )
        prog2Lbl = tk.Label(
                screen,
                font = ("Helvetica",16)
                )
        lastHB2Txt = tk.Label(
                screen,
                font = ("Helvetica",16),
                text = "Last Heartbeat"
                )
        lastHB2Lbl = tk.Label(
                screen,
                font = ("Helvetica",16)
                )
        stopBtn3 = tk.Button(
            screen,
            text = "Stop",
            font = ("Helvetica",16),
            height = 1,
            width = 7)
        prog3Txt = tk.Label(
                screen,
                font = ("Helvetica",16),
                text = "Modbus TCP Status"
                )
        prog3Lbl = tk.Label(
                screen,
                font = ("Helvetica",16)
                )
        lastHB3Txt = tk.Label(
                screen,
                font = ("Helvetica",16),
                text = "Last Heartbeat"
                )
        lastHB3Lbl = tk.Label(
                screen,
                font = ("Helvetica",16)
                )
        debug1Txt = tk.Label(
                screen,
                font = ("Helvetica",16),
                text = "Debug message 1"
                )
        debug1Lbl = tk.Label(
                screen,
                font = ("Helvetica",16)
                )
        debug2Txt = tk.Label(
                screen,
                font = ("Helvetica",16),
                text = "Debug message 2"
                )
        debug2Lbl = tk.Label(
                screen,
                font = ("Helvetica",16)
                )
    mainScreen = MyScreen()
    mainScreen.prog1Txt.place(x = 10, y = 50)
    mainScreen.lastHB1Txt.place(x = 10, y = 105)
    mainScreen.prog2Txt.place(x = 10, y = 200)
    mainScreen.lastHB2Txt.place(x = 10, y = 255)
    mainScreen.prog3Txt.place(x = 10, y = 350)
    mainScreen.lastHB3Txt.place(x = 10, y = 405)
    mainScreen.debug1Txt.place(x = 10, y = 500)
    mainScreen.debug2Txt.place(x = 10, y = 555)

    mainScreen.prog1Lbl.place(x = 225, y = 50)
    mainScreen.lastHB1Lbl.place(x = 225, y = 105)
    mainScreen.prog2Lbl.place(x = 225, y = 200)
    mainScreen.lastHB2Lbl.place(x = 225, y = 255)
    mainScreen.prog3Lbl.place(x = 225, y = 350)
    mainScreen.lastHB3Lbl.place(x = 225, y = 405)
    mainScreen.debug1Lbl.place(x = 225, y = 500)
    mainScreen.debug2Lbl.place(x = 225, y = 555)

    mainScreen.restartBtn.place(x = 10, y = 625)
    mainScreen.stopBtn1.place(x = 325, y = 45)
    mainScreen.stopBtn2.place(x = 325, y = 195)
    mainScreen.stopBtn3.place(x = 325, y = 345)
    return mainScreen