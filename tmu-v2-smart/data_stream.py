import mysql.connector

class DataStream:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="client",
            password="raspi",
            database="iot_trafo_client"
        )
        self.last_data_id = None

    def get_settings(self):
        self.conn.commit()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *
            FROM transformer_settings
            WHERE trafoId = 1
        """)
        row = cursor.fetchone()
        cursor.close()
        result = list(row)
        tempSet = [result[15], result[16]] #Alarm, Trip
        pressSet = [result[26], result[25]] #Alarm, Trip
        return tempSet, pressSet

    def get_latest_values(self):
        self.conn.commit()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *
            FROM reading_data
            ORDER BY data_id DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        cursor.close()
        if row:
            return row
        return None

    def get_status(self):
        self.conn.commit()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT *
            FROM transformer_status
            WHERE trafoId = 1
        """)
        row = cursor.fetchone()
        cursor.close()
        result = list(row)
        result.pop(0)
        print(result)
        return result

    def get_autoscroll(self):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT intervalDelay
            FROM transformer_data   
            WHERE trafoId = 1
        """)
        row = cursor.fetchone()
        cursor.close()
        if row and row["intervalDelay"] is not None:
            return row["intervalDelay"]
        return 0
    
    def get_pages(self, textPropVal, textPropStat, colorPropStat, keySettings, page):
        textPropVal.insert(0, 0)
        textPropStat.insert(0, 0)
        colorPropStat.insert(0, 0)
        pages = {0: ([textPropVal[1], False, False], #Timestamp
                     [textPropVal[41], False, False], #Oil Temp. Val
                     [textPropStat[19], colorPropStat[19], False], #Oil Temp. Stat
                     [keySettings[0], False, False], #Oil Temp. Settings
                     [textPropVal[45], False, False], #Oil Pressure Val
                     [textPropStat[23], colorPropStat[23], False], #Oil Pressure Stat
                     [keySettings[1], False, False], #Oil Pressure Settings
                     [textPropVal[46], False, False], #Oil Level Val
                     [textPropStat[24], colorPropStat[24], False], #Oil Level Stat
                     [textPropVal[53], False, False], #H2 Level Val
                     [textPropStat[25], colorPropStat[25], False], #H2 Level Stat
                     [textPropVal[54], False, False], #Moisture Level Val
                     [textPropStat[26], colorPropStat[26], False]), #Moisture Level Stat
                 1: ([textPropVal[1], False, False],
                     [textPropVal[8], False, False], #Current U Val
                     [textPropStat[4], colorPropStat[4], False], #Current U Stat
                     [textPropVal[9], False, False], #Current V Val
                     [textPropStat[5], colorPropStat[5], False], #Current V Stat
                     [textPropVal[10], False, False], #Current W Val
                     [textPropStat[6], colorPropStat[6], False], #Current W Stat
                     [textPropVal[12], False, False], #Neutral Current Val
                     [textPropStat[7], colorPropStat[7], False], #Neutral Current
                     [textPropVal[5], False, False], #Voltage U-V Val
                     [textPropStat[1], colorPropStat[1], False], #Voltage U-V Stat
                     [textPropVal[6], False, False], #Voltage V-W Val
                     [textPropStat[2], colorPropStat[2], False]), #Voltage V-W Stat,
                 2: ([textPropVal[1], False, False],
                     [textPropVal[7], False, False], #Voltage W-U Val
                     [textPropStat[3], colorPropStat[3], False], #Voltage W-U Stat
                     [textPropVal[11], False, False], #Average Current Val
                     [textPropVal[22], False, False], #Total Active Power Val
                     [textPropVal[34], False, False], #Total Power Factor Val
                     [textPropVal[35], False, False], #Frequency Val
                     [textPropVal[2], False, False], #Voltage U-N Val
                     [textPropVal[3], False, False], #Voltage V-N Val
                     [textPropVal[4], False, False], #Voltage W-N Val
                     [" ", False, False],
                     [" ", False, False],
                     [" ", False, False]),
                 3: ([textPropVal[1], False, False],
                     [textPropVal[42], False, False], #WTI U Val
                     [textPropStat[20], colorPropStat[20], False], #WTI U Stat
                     [textPropVal[43], False, False], #WTI V Val
                     [textPropStat[21], colorPropStat[21], False], #WTI V Stat
                     [textPropVal[44], False, False], #WTI W Val
                     [textPropStat[22], colorPropStat[22], False], #WTI W Stat
                     [textPropVal[38], False, False], #Busbar U Val
                     [textPropStat[16], colorPropStat[16], False], #Busbar U Stat
                     [textPropVal[39], False, False], #Busbar V Val
                     [textPropStat[17], colorPropStat[17], False], #Busbar V Stat
                     [textPropVal[40], False, False], #Busbar W Val
                     [textPropStat[18], colorPropStat[18], False]) #Busbar W Stat
                     }
        result = pages.get(page, pages[0])
        return result

    def get_snapshot(self, page = 0):
        values = self.get_latest_values()
        if not values or len(values) < 58:
            return None
        status = self.get_status()

        oilSettings, pressSettings = self.get_settings()
        oilSettingsTxt = f"Oil Temp. Alarm : {oilSettings[0]}°C, Trip : {oilSettings[1]}°C"
        pressSettingsTxt = f"Tank Pressure Alarm : {pressSettings[0]} bar, Trip : {pressSettings[1]} bar"
        keySettings = [oilSettingsTxt, pressSettingsTxt]

        keyVal = ["Timestamp : ", 
                         "Voltage U-N : ", "Voltage V-N : ", "Voltage W-N : ",
                         "Voltage U-V : ", "Voltage V-W : ", "Voltage U-W : ",
                         "Current U : ", "Current V : ", "Current W : ", 
                         "Total Current : ", "Neutral Current : ",
                         "THDv Phase U : ", "THDv Phase V : ", "THDv Phase W : ",
                         "THDi Phase U : ", "THDi Phase V : ", "THDi Phase W : ",
                         "Active Power Pu : ", "Active Power Pv : ", "Active Power Pw : ", "Active Power Total : ",
                         "Reactive Power Qu : ", "Reactive Power Qv : ", "Reactive Power Qw : ", "Reactive Power Total : ",
                         "Apparent Power Su : ", "Apparent Power Sv : ", "Apparent Power Sw : ", "Apparent Power Total : ",
                         "Power Factor U : ", "Power Factor V : ", "Power Factor W : ", "Power Factor Total : ",
                         "Frequency : ", "Energy kWh : ", "Energy kVARh : ", 
                         "Busbar Temp U : ", "Busbar Temp V : ", "Busbar Temp W : ",
                         "Oil Temperature : ", "Winding Temp U : ", "Winding Temp V : ", "Winding Temp W : ",
                         "Tank Pressure : ", "Oil Level : ", "K-Rated U : ", "Derating U : ", 
                         "K-Rated V : ", "Derating V : ",  "K-Rated W : ", "Derating W : ",
                         "H2 Level (ppm) : ", "Moisture Level (ppm) : ",
                         "Voltage Unbalance UV : ", "Voltage Unbalance VW : ", "Voltage Unbalance UW : "]
        textPropVal = [" "]*58
        for i, key in enumerate(keyVal):
            textPropVal[i] = key + str(values[i+1])

        textPropStat = [" "]*28
        keyStat = ["Voltage U-V stat : ", "Voltage V-W stat : ", "Voltage U-W stat : ", 
               "Current U stat : ", "Current V stat : ", "Current W stat : ", "Neutral Current stat : ",
               "THDv U stat : ", "THDv V stat : ", "THDv W stat : ", "THDi U stat : ", "THDi V stat : ", "THDi W stat : ", 
               "Total Power Factor stat : ", "Frequency stat : ", 
               "Busbar Temp. U stat : ", "Busbar Temp. V stat : ", "Busbar Temp. W stat : ", "Oil Temp. : ",
               "Winding Temp. U stat : ", "Winding Temp. V stat : ", "Winding Temp. W stat : ", "Tank Pressure : ",
               "H2 Level (ppm) stat : ", "Moisture Level (ppm) stat : ",
               "Unballance Voltage U-V stat: ", "Unballance Voltage V-W stat: ", "Unballance Voltage U-W stat: "]
        colorPropStat, blinkPropStat = [False]*28, [False]*28
        for i, stat in enumerate(status[:28]):
            if not status:
                return self.get_pages(textPropVal, textPropStat, colorPropStat, blinkPropStat, page)
            if stat == 1 or stat == 5:
                colorPropStat[i] = True
                if stat == 5:
                    textPropStat[i] = keyStat[i] + "Extreme High"
                elif stat == 1:
                    textPropStat[i] = keyStat[i] + "Extreme Low"
            elif stat == 2 or stat == 4:
                colorPropStat[i] = True
                if stat == 4:
                    textPropStat[i] = keyStat[i] + "High"
                elif stat == 2:
                    textPropStat[i] = keyStat[i] + "Low"
            elif stat == 3:
                colorPropStat[i] = False
                textPropStat[i] = keyStat[i] + "Normal"

        return self.get_pages(textPropVal, textPropStat, colorPropStat, keySettings, page)
