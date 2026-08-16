import Adafruit_ADS1x15
from time import sleep
adc = Adafruit_ADS1x15.ADS1115(address = 0x48, busnum = 1)

while True:
    ANcurrent3 = adc.read_adc(3, gain = 2)    #Temperature
    ANcurrent2 = adc.read_adc(2, gain = 2)    #Pressure
    ANvoltage1 = adc.read_adc(1, gain = 2)    #OIL Level Alarm
    ANvoltage0 = adc.read_adc(0, gain = 2)    #OIL Level Trip
    print("Temperature ADC0 - Terminal 11")
    print(ANcurrent3)
    print("Pressure ADC1 - Terminal 12")
    print(ANcurrent2)
    print("Oil Level Trip ADC2 - Terminal 22")
    print(ANvoltage1)
    print("Oil Level Alarm ADC3 - Terminal 21")
    print(ANvoltage0)
    print("~~")
    sleep(1)