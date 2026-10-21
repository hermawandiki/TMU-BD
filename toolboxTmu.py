import math
import time
import logging
import binascii, struct

ts = time.strftime("%Y%m%d")
logName = r'/home/pi/tmu/tmu-app-client-deploy/assets/datalog/sysdata/syslog-' + ts + '.log'
logging.basicConfig(level=logging.INFO, filename=logName, format='%(asctime)s | %(levelname)s: %(message)s')

def floatToDec(data_hex, data_num):
    rawData = [[" "]*4] * data_num  
    processData = [0] * data_num    
    for i in range(0, data_num):
        rawData[i] = [data_hex[(i*4)+10], data_hex[(i*4)+9], data_hex[(i*4)+8], data_hex[(i*4)+7]]  
        for j in range(0, len(rawData[i])):
            if len(rawData[i][j]) == 1:
                rawData[i][j] = '0' + rawData[i][j] 
            else:
                rawData[i][j] = rawData[i][j]       
        stringData = "".join(map(str, rawData[i])) 
        fdata = struct.unpack('<f', binascii.unhexlify(stringData))[0] 
        processData[i] = (round(fdata*100))/100
    return processData

def splitData(dataset):
    try:
        posList = []
        for i in range(0, len(dataset)):
            if dataset[i] == 98 and (dataset[i+1] == 16 or dataset[i+1] == 3):
                posList.append(i)
        separatedList = []
        for i in range(0, len(posList)):
            try:
                separatedList.append(dataset[posList[i]:posList[i+1]])
            except:
                separatedList.append(dataset[posList[i]:])
        if len(dataset) == 512 and separated:
            separatedList.pop(len(separatedList)-1)
        filteredList = []
        filteredList.append(separatedList[0])
        if len(separatedList) > 1 and len(filteredList) > 0:
            for i in range(0, len(separatedList)-1):
                if separatedList[i] != separatedList[i+1]:
                    filteredList.append(separatedList[i+1])
        return filteredList
    except Exception as Argument:
        logging.debug("Splitting Data Error Occured")
        logging.debug(dataset)
        logging.exception("Error splitting Data")
        logging.debug(filteredList)
        return filteredList
        
def checkDataHealthness(data_dec, healthThreshold):
    dataHealth = 0
    for i in range(0, len(data_dec)):
        if data_dec[i] == 0:
            dataHealth = dataHealth
        else:
            dataHealth = dataHealth + 1
    if (dataHealth/len(data_dec))*100 < healthThreshold:
        logging.warning("Data Health Bad : " + str((dataHealth/len(data_dec))*100))
        logging.info("Dataset : " + str(data_dec))
        return False
    else :
        logging.info("Data Passed : " + str((dataHealth/len(data_dec))*100))
        return True

def gatherSetting(trafoSetting, trafoData, paramNum):
    paramThreshold = [[0]*paramNum, [0]*paramNum, [0]*paramNum, [0]*paramNum]
    for i in range(0,3):
        #Setting Threshold V phase to neutral (0 - 2)
        paramThreshold[0][i] = trafoSetting[2]/1.73 #low trip
        paramThreshold[1][i] = trafoSetting[4]/1.73 #low alarm
        paramThreshold[2][i] = trafoSetting[8]/1.73 #high alarm
        paramThreshold[3][i] = trafoSetting[6]/1.73 #high trip
        #Setting Threshold V phase to phase (3 - 5)
        paramThreshold[0][i+3] = trafoSetting[2]
        paramThreshold[1][i+3] = trafoSetting[4]
        paramThreshold[2][i+3] = trafoSetting[8]
        paramThreshold[3][i+3] = trafoSetting[6]
        #Setting Unbalance Threshold (6 - 8)
        paramThreshold[2][i+6] = (trafoSetting[9] * trafoData[4]) / 173 #Unbalance 
        paramThreshold[3][i+6] = (trafoSetting[10] * trafoData[4]) / 173  #Unbalance
    paramThreshold[0][9] = trafoData[7] - ((trafoSetting[11] * trafoData[7])/100) #Frequency Low Trip
    paramThreshold[1][9] = trafoData[7] - ((trafoSetting[12] * trafoData[7])/100) #Frequency Low Alarm
    paramThreshold[2][9] = trafoData[7] + ((trafoSetting[14] * trafoData[7])/100)  #Frequency High Alarm
    paramThreshold[3][9] = trafoData[7] + ((trafoSetting[13] * trafoData[7])/100)  #Frequency High Trip
    paramThreshold[2][10] = trafoSetting[15] #Top Oil Alarm
    paramThreshold[3][10] = trafoSetting[16] #Top Oil Trip
    paramThreshold[2][11] = paramThreshold[2][12] = paramThreshold[2][13] = trafoSetting[17] #WTI Alarm
    paramThreshold[3][11] = paramThreshold[3][12] = paramThreshold[3][13] = trafoSetting[18] #WTI Trip
    paramThreshold[2][14] = paramThreshold[2][15] = paramThreshold[2][16] = trafoSetting[27] #Bus Temp Alarm
    paramThreshold[3][14] = paramThreshold[3][15] = paramThreshold[3][16] = trafoSetting[28] #Bus Temp Trip
    paramThreshold[1][17] = trafoSetting[19] #PF Alarm
    paramThreshold[0][17] = trafoSetting[20] #PF Trip
    paramThreshold[2][18] = paramThreshold[2][19] = paramThreshold[2][20] = (trafoSetting[21] * trafoData[6])/100 #Current Alarm
    paramThreshold[3][18] = paramThreshold[3][19] = paramThreshold[3][20] = (trafoSetting[22] * trafoData[6])/100 #Current Trip
    paramThreshold[3][21] = trafoSetting[23] #ambient Trip
    paramThreshold[2][21] = trafoSetting[24] #ambient Alarm
    paramThreshold[3][22] = trafoSetting[25] #Pressure Trip
    paramThreshold[2][22] = trafoSetting[26] #Pressure Alarm
    paramThreshold[0][23] = 4 #Level Trip
    paramThreshold[1][23] = 8 #Level Alarm
    for i in range(0, 3):
        paramThreshold[2][i + 24] = trafoSetting[29]    #THD Current Alarm
        paramThreshold[3][i + 24] = trafoSetting[30]    #THD Current Trip
        paramThreshold[2][i + 27] = trafoSetting[31]    #THD Voltage Alarm
        paramThreshold[3][i + 27] = trafoSetting[32]    #THD Voltage Trip
    paramThreshold[3][30] = trafoSetting[33]    #I Neutral Trip
    paramThreshold[2][30] = trafoSetting[34]    #I Neutral Alarm
    return paramThreshold

def gatherTripSetting(tripSetting, paramNum):
    allTripSetting = [0]*paramNum
    for i in range (0, 6):
        allTripSetting[i] = tripSetting[1] #Voltage Value
    allTripSetting[6] = allTripSetting[7] = allTripSetting[8] = tripSetting[2] #Voltage Unbalance
    allTripSetting[9] = tripSetting[3] #Freq
    allTripSetting[10] = tripSetting[4] #OilTemp
    allTripSetting[11] = allTripSetting[12] = allTripSetting[13] = tripSetting[11] #WTI
    allTripSetting[14] = allTripSetting[15] = allTripSetting[16] = tripSetting[5] #BusTemp
    allTripSetting[17] = tripSetting[6] #PF
    allTripSetting[18] = allTripSetting[19] = allTripSetting[20] = tripSetting[7] #I
    allTripSetting[21] = tripSetting[8] #Ambient
    allTripSetting[22] = tripSetting[9] #Pressure
    allTripSetting[23] = tripSetting[10] #Level
    allTripSetting[22] = tripSetting[9] #Pressure
    allTripSetting[23] = tripSetting[10] #Level
    allTripSetting[24] = allTripSetting[25] = allTripSetting[26] = tripSetting[12]
    allTripSetting[27] = allTripSetting[28] = allTripSetting[29] = tripSetting[13]
    allTripSetting[30] = tripSetting[14]
    return allTripSetting

def gatherParamValue(current_result, paramNum, gasFault):
    paramValue = [0]*paramNum #arrange data from currentResult
    paramValue[0] = current_result[6]
    paramValue[1] = current_result[15]
    paramValue[2] = current_result[24]
    paramValue[3] = current_result[7]
    paramValue[4] = current_result[16]
    paramValue[5] = current_result[25]
    paramValue[6] = abs(paramValue[0] - paramValue[1]) #Unbalance
    paramValue[7] = abs(paramValue[1] - paramValue[2])
    paramValue[8] = abs(paramValue[0] - paramValue[2])
    paramValue[9] = current_result[38] #Frequency
    paramValue[10] = current_result[0] #Oil Temp
    paramValue[11] = current_result[50] #WTITemp1
    paramValue[12] = current_result[51] #WTITemp2
    paramValue[13] = current_result[52] #WTITemp3
    paramValue[14] = current_result[1] #BusTemp1
    paramValue[15] = current_result[2] #BusTemp2
    paramValue[16] = current_result[3] #BusTemp3
    paramValue[17] = current_result[34] #PowerFactor
    paramValue[18] = current_result[8] #I1
    paramValue[19] = current_result[17] #I2
    paramValue[20] = current_result[26] #I3
    paramValue[21] = 0.0 #AmbTemp
    paramValue[22] = current_result[4] #Pressure
    if current_result[5] == 3:
        #print("Gas Fault")
        logging.info("Gas Fault Event")
        gasFault = True
        paramValue[23] = 6
    else:
        paramValue[23] = 10 - (current_result[5] * 4) #Level
    paramValue[24] = current_result[14]
    paramValue[25] = current_result[23]
    paramValue[26] = current_result[32]
    paramValue[27] = current_result[13]
    paramValue[28] = current_result[22]
    paramValue[29] = current_result[31]
    paramValue[30] = current_result[39]
    return paramValue, gasFault