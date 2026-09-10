import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.IN)
GPIO.setup(22, GPIO.IN)
GPIO.setup(17, GPIO.IN)
GPIO.setup(27, GPIO.IN)
loop = False

def testBatch():
    print("Push Button - GPIO0")
    print(GPIO.input(13))
    print("Push Button - GPIO1")
    print(GPIO.input(17))
    print("Push Button - GPIO2")
    print(GPIO.input(22))
    print("Push Button - GPIO3")
    print(GPIO.input(27))
    print("~~~")

if loop:
    while True:
        testBatch()
        time.sleep(2)
else:
    testBatch()
