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

        cursor.execute("""
            SELECT impedance
            FROM transformer_data
            ORDER BY trafoId DESC
            LIMIT 1
        """)
        row1 = cursor.fetchone()

        cursor.execute("""
            SELECT * 
            FROM di_scan
            WHERE number BETWEEN 0 AND 3
            ORDER BY number ASC
        """)
        row2 = cursor.fetchall()

        cursor.close()
        if row:
            result = list(row)
            result.append(row1[0] if row1 else None)  # Append impedance value
            for data in row2:
                state = data[2]  # index 2 adalah kolom state
                result.append(bool(state))
            return result
            # print(result)
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
        #print(result)
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

        pages = {
            0: ([textPropVal[1], False, False], # Timestamp
                [textPropVal[2], False, False], # Voltage U-N Val
                [textPropVal[3], False, False], # Voltage V-N Val
                [textPropVal[4], False, False], # Voltage W-N Val
                [textPropVal[5], False, False], # Voltage U-V Val
                [textPropStat[1], colorPropStat[1], False], # Voltage U-V Stat
                [textPropVal[6], False, False], # Voltage V-W Val
                [textPropStat[2], colorPropStat[2], False], # Voltage V-W Stat
                [textPropVal[7], False, False], # Voltage U-W Val
                [textPropStat[3], colorPropStat[3], False], # Voltage U-W Stat
                [textPropVal[8], False, False], # Current U Val
                [textPropStat[4], colorPropStat[4], False], # Current U Stat
                [" ", False, False]
                ),
            1: ([textPropVal[1], False, False], # Timestamp
                [textPropVal[9], False, False], # Current V Val
                [textPropStat[5], colorPropStat[5], False], # Current V Stat
                [textPropVal[10], False, False], # Current W Val
                [textPropStat[6], colorPropStat[6], False], # Current W Stat
                [textPropVal[11], False, False], # Total Current Val
                [textPropVal[12], False, False], # Current N Val
                [textPropStat[7], colorPropStat[7], False], # Current N Stat
                [textPropVal[13], False, False], # THDv Phase U Val
                [textPropStat[8], colorPropStat[8], False], # THDv Phase U Stat
                [textPropVal[14], False, False], # THDv Phase V Val
                [textPropStat[9], colorPropStat[9], False], # THDv Phase V Stat
                [" ", False, False]
                ),
            2: ([textPropVal[1], False, False], # Timestamp
                [textPropVal[15], False, False], # THDv Phase W Val
                [textPropStat[10], colorPropStat[10], False], # THDv Phase W Stat
                [textPropVal[16], False, False], # THDi Phase U Val
                [textPropStat[11], colorPropStat[11], False], # THDi Phase U Stat
                [textPropVal[17], False, False], # THDi Phase V Val
                [textPropStat[12], colorPropStat[12], False], # THDi Phase V Stat
                [textPropVal[18], False, False], # THDi Phase W Val
                [textPropStat[13], colorPropStat[13], False],  # THDi Phase W Stat
                [textPropVal[19], False, False], # Active Power Pu Val
                [textPropVal[20], False, False], # Active Power Pv Val
                [textPropVal[21], False, False], # Active Power Pw Val
                [textPropVal[22], False, False]  # Active Power Total Val
                ),
            3: ([textPropVal[1], False, False], # Timestamp
                [textPropVal[23], False, False], # Reactive Power Qu Val
                [textPropVal[24], False, False], # Reactive Power Qv Val
                [textPropVal[25], False, False], # Reactive Power Qw Val
                [textPropVal[26], False, False], # Reactive Power Total Val
                [textPropVal[27], False, False], # Apparent Power Su Val
                [textPropVal[28], False, False], # Apparent Power Sv Val
                [textPropVal[29], False, False], # Apparent Power Sw Val
                [textPropVal[30], False, False], # Apparent Power Total Val
                [textPropVal[31], False, False], # Power Factor U Val
                [textPropVal[32], False, False], # Power Factor V Val
                [textPropVal[33], False, False], # Power Factor W Val
                [" ", False, False]
                ),
            4: ([textPropVal[1], False, False], # Timestamp
                [textPropVal[34], False, False], # Power Factor Total Val
                [textPropStat[14], colorPropStat[14], False], # Power Factor Total Stat
                [textPropVal[35], False, False], # Frequency Val
                [textPropStat[15], colorPropStat[15], False], # Frequency Stat
                [textPropVal[36], False, False], # Energy kWh Val
                [textPropVal[37], False, False], # Energy kVARh Val
                [textPropVal[38], False, False], # Busbar Temp U Val
                [textPropStat[16], colorPropStat[16], False], # Busbar Temp U Stat
                [textPropVal[39], False, False], # Busbar Temp V Val
                [textPropStat[17], colorPropStat[17], False], # Busbar Temp V Stat
                [textPropVal[40], False, False],  # Busbar Temp W Val
                [textPropStat[18], colorPropStat[18], False]  # Busbar Temp W Stat
                ),
            5: ([textPropVal[1], False, False], # Timestamp
                [textPropVal[41], False, False], # Oil Temperature Val
                [textPropStat[19], colorPropStat[19], False], # Oil Temperature Stat
                [keySettings[0], False, False], # Oil Temp. Settings
                [textPropVal[42], False, False], # Winding Temp U Val
                [textPropStat[20], colorPropStat[20], False], # Winding Temp U Stat
                [textPropVal[43], False, False], # Winding Temp V Val
                [textPropStat[21], colorPropStat[21], False], # Winding Temp V Stat
                [textPropVal[44], False, False], # Winding Temp W Val
                [textPropStat[22], colorPropStat[22], False], # Winding Temp W Stat
                [textPropVal[45], False, False], # Oil Pressure Val
                [textPropStat[23], colorPropStat[23], False], # Oil Pressure Stat
                [keySettings[1], False, False], # Oil Pressure Settings
                ),
            6: ([textPropVal[1], False, False], # Timestamp
                [textPropVal[46], False, False], # Oil Level Val
                [textPropStat[24], colorPropStat[24], False], # Oil Level Stat
                [textPropVal[47], False, False], # K-Rated U Val
                [textPropVal[48], False, False], # Derating U Val
                [textPropVal[49], False, False], # K-Rated V Val
                [textPropVal[50], False, False], # Derating V Val
                [textPropVal[51], False, False], # K-Rated W Val
                [textPropVal[52], False, False], # Derating W Val
                [textPropVal[53], False, False], # H2 Level (ppm) Val
                [textPropStat[25], colorPropStat[25], False], # H2 Level (ppm) Stat
                [textPropVal[54], False, False], # Moisture Level Val
                [textPropStat[26], colorPropStat[26], False], # Moisture Level Stat
                ),
            7: ([textPropVal[1], False, False], # Timestamp
                [textPropVal[55], False, False], # Unbalance UV Val
                [textPropStat[27], colorPropStat[27], False], # Unbalance UV Stat
                [textPropVal[56], False, False], # Unbalance VW Val
                [textPropStat[28], colorPropStat[28], False], # Unbalance VW Stat
                [textPropVal[57], False, False], # Unbalance UW Val
                [textPropStat[29], colorPropStat[29], False], # Unbalance UW Stat
                [textPropVal[58], False, False], # OLTC Tap Pos Val
                [textPropVal[59], False, False], # Reset Buzzer Status Val
                [textPropVal[60], False, False], # PRD Trigger Status Val
                [textPropVal[61], False, False], # Bucholz Alarm Status Val
                [textPropVal[62], False, False], # Bucholz Trip Status Val
                [" ", False, False]
                )
        }

        result = pages.get(page, pages[0])
        return result

    def get_snapshot(self, page = 0):
        values = self.get_latest_values()
        # print(values)
        if not values or len(values) < 63:
            return None
        status = self.get_status()

        oilSettings, pressSettings = self.get_settings()
        oilSettingsTxt   = f"    Oil Temp. Alarm        : {oilSettings[0]} °C, Trip : {oilSettings[1]} °C"
        pressSettingsTxt = f"    Oil Pres. Alarm        : {pressSettings[0]} bar, Trip : {pressSettings[1]} bar"
        keySettings = [oilSettingsTxt, pressSettingsTxt]

        keyVal = ["Timestamp : ", 
                "01. Voltage U-N            : ",
                "02. Voltage V-N            : ",
                "03. Voltage W-N            : ",
                "04. Voltage U-V            : ",
                "05. Voltage V-W            : ",
                "06. Voltage U-W            : ",
                "07. Current U              : ",
                "08. Current V              : ",
                "09. Current W              : ", 
                "10. Total Current          : ",
                "11. Current N              : ",
                "12. THDv Phase U           : ",
                "13. THDv Phase V           : ",
                "14. THDv Phase W           : ",
                "15. THDi Phase U           : ",
                "16. THDi Phase V           : ", 
                "17. THDi Phase W           : ",
                "18. Active Power Pu        : ", 
                "19. Active Power Pv        : ", 
                "20. Active Power Pw        : ", 
                "21. Active Power Total     : ",
                "22. Reactive Power Qu      : ", 
                "23. Reactive Power Qv      : ",
                "24. Reactive Power Qw      : ", 
                "25. Reactive Power Total   : ",
                "26. Apparent Power Su      : ", 
                "27. Apparent Power Sv      : ", 
                "28. Apparent Power Sw      : ", 
                "29. Apparent Power Total   : ",
                "30. Power Factor U         : ", 
                "31. Power Factor V         : ", 
                "32. Power Factor W         : ", 
                "33. Power Factor Total     : ",
                "34. Frequency              : ", 
                "35. Energy kWh             : ", 
                "36. Energy kVARh           : ", 
                "37. Busbar Temp U          : ", 
                "38. Busbar Temp V          : ", 
                "39. Busbar Temp W          : ",
                "40. Oil Temperature        : ", 
                "41. Winding Temp U         : ", 
                "42. Winding Temp V         : ", 
                "43. Winding Temp W         : ",
                "44. Oil Pressure           : ", 
                "45. Oil Level              : ", 
                "46. K-Rated U              : ", 
                "47. Derating U             : ", 
                "48. K-Rated V              : ", 
                "49. Derating V             : ", 
                "50. K-Rated W              : ", 
                "51. Derating W             : ",
                "52. H2 Level (ppm)         : ", 
                "53. Moisture Level         : ",
                "54. Unbalance UV           : ", 
                "55. Unbalance VW           : ", 
                "56. Unbalance UW           : ",
                "57. OLTC Tap Position      : ",
                "58. Reset Buzzer Status    : ",
                "59. PRD Trigger Status     : ",
                "60. Bucholz Alarm Status   : ",
                "61. Bucholz Trip Status    : "]

        keyStat = ["    Voltage U-V status     : ",
                "    Voltage V-W status     : ", 
                "    Voltage U-W status     : ", 
                "    Current U status       : ", 
                "    Current V status       : ", 
                "    Current W status       : ", 
                "    Current N status       : ",
                "    THDv U status          : ", 
                "    THDv V status          : ", 
                "    THDv W status          : ", 
                "    THDi U status          : ", 
                "    THDi V status          : ", 
                "    THDi W status          : ", 
                "    Power Factor status    : ", 
                "    Frequency status       : ", 
                "    Busbar U status        : ", 
                "    Busbar V status        : ", 
                "    Busbar W status        : ", 
                "    Oil Temp. status       : ",
                "    WTI U status           : ", 
                "    WTI V status           : ", 
                "    WTI W status           : ", 
                "    Oil Pres. status       : ",
                "    Oil Level status       : ", 
                "    H2 Level status        : ", 
                "    Moisture status        : ",
                "    Unbalance UV status    : ", 
                "    Unbalance VW status    : ", 
                "    Unbalance UW status    : "]
        
        textPropVal = [" "]*63
        for i, key in enumerate(keyVal):
            textPropVal[i] = key + str(values[i+1])

        textPropStat = [" "]*29
        colorPropStat, blinkPropStat = [False]*29, [False]*29
        for i, stat in enumerate(status[:29]):
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
