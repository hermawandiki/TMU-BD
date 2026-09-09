import Adafruit_ADS1x15
from time import sleep
adc = Adafruit_ADS1x15.ADS1115(address = 0x48, busnum = 1)

source = {
    16: 862,
    15: 817,
    14: 773,
    13: 728,
    12: 683,
    11: 639,
    10: 594,
    9: 548,
    8: 503,
    7: 458,
    6: 413,
    5: 367,
    4: 321,
    3: 276,
    2: 230,
    1: 184,
    0: 0
}

def find_tap(input_value, input_output_map):
    sorted_data = sorted(input_output_map.items(), reverse=True, key=lambda x: x[1])
    for output, max_input in sorted_data:
        if input_value >= max_input:
            return output
    return 0 

while True:
    ANcurrent3 = adc.read_adc(3, gain = 2)    #Temperature
    ANcurrent2 = adc.read_adc(2, gain = 2)    #Pressure
    ANvoltage1 = adc.read_adc(1, gain = 2)    #OIL Level Alarm
    ANvoltage0 = adc.read_adc(0, gain = 2)    #OIL Level Trip

    voltage = ANcurrent2 / 32767 * 2.048 * 2.5
    current = voltage * 1000 / 250 

    # tapPos = find_tap(round(ANcurrent2 * 0.0269375), source) + 1
    # tapPos = round((17-1) * ((voltage-1.0)/4.0) + 1)
    # tapPos = round(4 * voltage - 3.0)
    # tapPos = round((17-1) * ((current-4.0)/16.0) + 1)
    tapPos = round(current - 3.0)

    print("ADC     : ", ANcurrent2)
    print("Voltage : ", voltage)
    print("Current : ", current)
    print("Tap Pos : ", tapPos)
    print()

    # print("Temperature ADC0 - Terminal 11")
    # print(ANcurrent3)
    # print("Pressure ADC1 - Terminal 12")
    # print(ANcurrent2)
    # print("Oil Level Trip ADC2 - Terminal 22")
    # print(ANvoltage1)
    # print("Oil Level Alarm ADC3 - Terminal 21")
    # print(ANvoltage0)
    # print("~~")
    sleep(1)