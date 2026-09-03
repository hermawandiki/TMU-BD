import requests
from time import sleep
from requests.models import StreamConsumedError
from requests.exceptions import Timeout, RequestException

teleURL = 'http://192.168.8.113:1444/api/transformer/sendNotificationToTelegramGroup'
API_URL = "https://tmu.bambangdjaja.com/triggerAlarmNotification"

def testTele(messages):
    payload = {'message':messages}
    print("Sending message : " + messages)
    r = requests.post(teleURL, data = pload, timeout = 5, verify = False)
    print(r)

def testAPI():
    payload = {
    "companyKey": "P66geqk4bYQuetarke2Z", # baca dari folder tmu-app-client-deploy baca file .env ada variable COMPANY_KEY
    "raspiSerialNo": "1000000024b2178e",  #baca dari folder tmu-app-client-deploy baca file .serialno
    "time_start": "2025-10-22 08:05:00", # sesuai data insert di failure_log
    "failure_type": "Regular Test",  # sesuai data insert di failure_log
    "parameter": "Regular Test", # sesuai data insert di failure_log
    "parameterValue": "999", # sesuai data insert di failure_log
    "duration": 0, # sesuai data insert di failure_log
    "event_type": "alarm" # Nilainya "alarm" atau "trip"
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        response.raise_for_status()
        print("Success:", response.json())
    except Timeout:
        print("Request timeout — server tidak merespons dalam 5 detik.")
    except RequestException as e:
        print("Gagal mengirim request:", e)

testTele("Test")
sleep(1)
testAPI()