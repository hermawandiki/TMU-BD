import asyncio
import signal
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.server import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification
import logging
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import mysql.connector
import datetime, sys

debugMsg = False
infoMsg = True

db = mysql.connector.connect(
    host = "localhost",
    user = "client",
    passwd = "raspi",
    database= "iot_trafo_client")

if infoMsg == True: print("4D|Initialize program")

def unsigned32bit(value):
    high_register = (value >> 16) & 0xFFFF
    low_register = value & 0xFFFF
    return high_register, low_register

def signed32bit(value):
    if value < 0:
        value = (1 << 32) + value
    high_register = (value >> 16) & 0xFFFF
    low_register = value & 0xFFFF
    return high_register, low_register

def unsigned16bit(value):
    return value & 0xFFFF

def signed16bit(value):
    if not (-32768 <= value <= 32767):
        raise ValueError(f"Nilai {value} di luar rentang signed 16-bit (-32768 s.d. 32767)")
    if value < 0:
        value = (1 << 16) + value
    return value & 0xFFFF

def dataStore(data):
    storage = [0]*80
    # print(data)
    #Voltage
    for i in range(0, 6): 
        data[i] = round(data[i]*10)
        storage[i*2 + 1], storage[i*2] = unsigned32bit(data[i])
    #Current
    for i in range(6, 11):
        data[i] = round(data[i]*10)
        storage[i+6] = data[i]
    #THD V & I
    for i in range(11, 17):
        data[i] = round(data[i]*100)
        storage[i+6] = data[i]
    #P & Q
    for i in range(0, 8): 
        data[i+17] = round(data[i+17]*10)
        storage[i*2 + 24], storage[i*2 + 23] = signed32bit(data[i+17])    
    #S
    for i in range(0, 4): 
        data[i+25] = round(data[i+25]*10)
        storage[i*2 + 40], storage[i*2 + 39] = unsigned32bit(data[i+25])
    #PF
    for i in range(29, 33):
        data[i] = round(data[i]*100)
        storage[i + 18] = signed16bit(data[i])
    #Freq
    data[33] = round(data[33]*100)
    storage[51] = data[33]
    #KWH
    for i in range(0, 2): 
        data[i+34] = round(data[i+34]*10)
        storage[i*2 + 53], storage[i*2 + 52] = unsigned32bit(data[i+34])
    #Busbar
    for i in range(36, 43):
        data[i] = round(data[i]*100)
        storage[i + 20] = data[i]
    #Pressure
    data[43] = signed16bit(round(data[43]*1000))
    storage[63] = data[43]
    #Level
    storage[64] = data[44]
    #kRATED A
    storage[65] = data[45]
    #derating A
    data[46] = round(data[46]*100)
    storage[66] = data[46]
    #kRATED B
    storage[67] = data[47]
    #derating B
    data[48] = round(data[48]*100)
    storage[68] = data[48]
    #kRATED A
    storage[69] = data[49]
    #derating A
    data[50] = round(data[50]*100)
    storage[70] = data[50]
    #H2ppm
    storage[71] = data[51]
    #Moisture ppm
    storage[72] = data[52]
    #Gap Voltage
    for i in range(0, 3): 
        data[i+53] = round(data[i+53]*10)
        storage[i*2 + 74], storage[i*2 + 73] = unsigned32bit(data[i+53])
    return storage

def gatherValues():
    cursor = db.cursor()
    sql = "SELECT * FROM reading_data ORDER BY data_id DESC LIMIT 1"
    cursor.execute(sql)
    result = cursor.fetchall()
    listResult = list(result[0])
    listResult.pop(0)
    listResult.pop(0)
    db.commit()
    # print(listResult)
    return dataStore(listResult)

# Handler untuk menampilkan log di tkinter
class LogDisplayHandler(logging.Handler):
    def __init__(self, text_widget, max_lines=10):
        super().__init__()
        self.text_widget = text_widget
        self.max_lines = max_lines

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)  # Scroll otomatis ke baris terakhir

        # Batasi jumlah baris log agar tidak membebani memori
        num_lines = int(self.text_widget.index('end-1c').split('.')[0])
        if num_lines > self.max_lines:
            self.text_widget.delete('1.0', f'{num_lines - self.max_lines}.0')

# Fungsi untuk memulai tkinter dalam thread terpisah
def start_tkinter_loop():
    root = tk.Tk()
    root.title("Modbus Server Log")
    root.attributes("-topmost", False)
    text_area = ScrolledText(root, wrap=tk.WORD, state='disabled', height=20, width=80)
    text_area.pack(padx=10, pady=10)
    text_area.configure(state='normal')

    log_handler = LogDisplayHandler(text_area)
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    log.addHandler(log_handler)
    log.setLevel(logging.DEBUG)

    root.withdraw()
    root.mainloop()
    
# Jalankan tkinter di thread terpisah
# threading.Thread(target=start_tkinter_loop, daemon=True).start()

# Konfigurasi logging
logging.basicConfig()
log = logging.getLogger()

# Membuat blok data dengan 20 parameter acak
values = [0 for _ in range(99)]
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, values),
    co=ModbusSequentialDataBlock(0, values),
    hr=ModbusSequentialDataBlock(0, values),
    ir=ModbusSequentialDataBlock(0, values)
)
context = ModbusServerContext(slaves=store, single=True)

# Fungsi untuk memperbarui nilai register setiap 2 detik
async def update_register_values():
    if infoMsg == True: print("4D|Start Loop")
    while True:
        new_values = gatherValues()
        #print(new_values)
        store.setValues(3, 0, new_values)  # 3 = Holding Register
        log.debug(f"register values updated: {new_values}")
        log.debug(f"register values updated")

        print("4T|%s" % datetime.datetime.now())
        # print("4D|Still Running")
        sys.stdout.flush()

        await asyncio.sleep(2)

# Identifikasi perangkat
identity = ModbusDeviceIdentification()
identity.VendorName = 'CustomModbusServer'
identity.ProductCode = 'PYSERVER'
identity.ModelName = 'Modbus TCP Server'
identity.MajorMinorRevision = '1.0'

# Fungsi untuk menangani sinyal sistem dan menutup server dengan benar
def handle_exit(*args):
    log.info("Shutting down server...")
    exit(0)

# Tangkap sinyal sistem
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Fungsi untuk menjalankan server
async def run_server():
    # Jalankan fungsi pembaruan data dan server secara bersamaan
    await asyncio.gather(
        update_register_values(),
        StartAsyncTcpServer(context, identity=identity, address=("0.0.0.0", 1502), allow_reuse_address=True)
    )
    
# Menjalankan server
asyncio.run(run_server())
