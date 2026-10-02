import mysql.connector

db = mysql.connector.connect(
    host = "localhost",
    user = "client",
    passwd = "raspi",
    database= "iot_trafo_client")
cursor = db.cursor()

sql = "SELECT * FROM transformer_data"

cursor.execute(sql)
trafoSetting = cursor.fetchall()[0]
print(trafoSetting)