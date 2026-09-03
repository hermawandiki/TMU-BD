import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.IN) #Oil Level Alarm
GPIO.setup(17, GPIO.IN) #Oil Level Trip
GPIO.setup(22, GPIO.IN) #Spare
GPIO.setup(27, GPIO.IN) #Spare

GPIO.setup(23, GPIO.OUT) #TMU Alarm Relay - DO0
GPIO.setup(24, GPIO.OUT) #TMU Trip Relay - DO1
GPIO.setup(25, GPIO.OUT) #Solenoid Relay - DO2
GPIO.setup(26, GPIO.OUT) #Spare - DO3

outStat = {
    'Alarm' : False,
    'Trip' : False,
    'Solenoid' : False,
    'Spare' : False
}
loop = False

def testBatch():
    print("** GPIO IN **")
    print("Oil Level Alarm DI0 - Terminal 10")
    print(GPIO.input(13))
    print("Oil Level Trip DI1 - Terminal 11")
    print(GPIO.input(17))
    print("Spare DI2")
    print(GPIO.input(22))
    print("Spare DI3")
    print(GPIO.input(27))
    print("** GPIO OUT **")
    print("TMU Alarm Relay DO0 K1 - Terminal 14-21")
    GPIO.output(23, GPIO.HIGH if outStat['Alarm'] else GPIO.LOW)
    print("TMU Trip Relay DO1 K2 - Terminal 14-22")
    GPIO.output(24, GPIO.HIGH if outStat['Trip'] else GPIO.LOW)
    print("TMU Trip Relay DO1 K2 - Terminal 1-4 (Hot Wire!)")
    GPIO.output(25, GPIO.HIGH if outStat['Solenoid'] else GPIO.LOW)
    print("Spare DO3")
    GPIO.output(26, GPIO.HIGH if outStat['Spare'] else GPIO.LOW)
    print("~~~")

if loop:
    while True:
        testBatch()
        sleep(2)
else:
    testBatch()
