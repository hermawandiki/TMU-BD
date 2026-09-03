import Adafruit_ADS1x15
from time import sleep
adc = Adafruit_ADS1x15.ADS1115(address = 0x48, busnum = 1)
loop = False

def testADC():
    adcRead3 = adc.read_adc(3, gain = 1)    #Spare
    adcRead2 = adc.read_adc(2, gain = 1)    #Spare
    adcRead1 = adc.read_adc(1, gain = 1)    #Temperature
    adcRead0 = adc.read_adc(0, gain = 1)    #Pressure
    print("Pressure ADC0 - Terminal 12")
    print(adcRead0)
    print("Temperature ADC1 - Terminal 13")
    print(adcRead1)
    print("Spare ADC2")
    print(adcRead2)
    print("Spare ADC3")
    print(adcRead3)
    print("~~")

if loop:
    while True:
        testADC()
        sleep(1)
else:
    testADC()