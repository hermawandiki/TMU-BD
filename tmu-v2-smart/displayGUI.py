import tkinter as tk
from data_stream import DataStream
import time, datetime, sys
import smbus2
from PIL import Image, ImageDraw, ImageFont

debugMsg = False
infoMsg = True

I2C_BUS = 1
I2C_ADDR = 0x3C
TMU_IP = "192.168.4.120"

try:
    oled_bus = smbus2.SMBus(I2C_BUS)
except Exception:
    oled_bus = None

def oled_cmd(cmd):
    if oled_bus: oled_bus.write_byte_data(I2C_ADDR, 0x00, cmd)

def oled_init():
    if not oled_bus: return
    for c in [0xAE, 0x00, 0x10, 0x40, 0x81, 0xCF, 0xA1, 0xC8, 0xA6,
              0xA8, 0x3F, 0xD3, 0x00, 0xD5, 0x80, 0xD9, 0xF1, 0xDA,
              0x12, 0xDB, 0x40, 0x20, 0x00, 0x8D, 0x14, 0xAF]:
        oled_cmd(c)

def oled_show(image):
    if not oled_bus: return
    image = image.rotate(180)
    oled_cmd(0x21); oled_cmd(0); oled_cmd(127)
    oled_cmd(0x22); oled_cmd(0); oled_cmd(7)
    pix = list(image.getdata())
    buf = []
    for page in range(8):
        for col in range(128):
            byte = 0
            for bit in range(8):
                if pix[(page * 8 + bit) * 128 + col]:
                    byte |= (1 << bit)
            buf.append(byte)
    for i in range(0, len(buf), 16):
        oled_bus.write_i2c_block_data(I2C_ADDR, 0x40, buf[i:i+16])

def oled_print(teks: str):
    if not oled_bus: return
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 10)
    except:
        font = ImageFont.load_default()
    img = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(img)
    for i, row in enumerate(teks.splitlines()):
        draw.text((0, i * 12), row, font=font, fill=255)
    oled_show(img)

class DisplayGUI:
    def __init__(self, root):
        if infoMsg == True: print("3D|Initialize program")
        self.root = root
        self.root.title("Data Stream")

        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', self.exitEsc)

        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f"{width}x{height}+0+0")
        self.root.attributes("-topmost", True)
        self.ds = DataStream()

        self.pageNow = 0
        self.timeThen = time.time()

        oled_init()
        oled_print(f"TMU FAJAR PAPER\nIP ETH: {TMU_IP}")

        self.btn_exit = tk.Button(
            self.root,
            text="Exit",
            font=("Arial", 11, "bold"),
            bg="#AF3F3E",
            command=self.exitEsc
        )
        self.btn_exit.pack(pady=10)

        self.data_labels = []
        for i in range(13):
            lbl = tk.Label(
                root,
                text=f"Data{i+1} = Null",
                font=("Consolas", 13),
                anchor="w",
                width=50
            )
            lbl.pack()
            self.data_labels.append(lbl)

        self.autoscrollLbl = tk.Label(
            root,
            text="Autoscroll : 0s",
            font=("Arial", 10, "bold")
        )
        self.autoscrollLbl.pack(pady=10)
        if infoMsg == True: print("3D|Start Loop")
        self.update_loop()

    def exitEsc(self, event=None):
        self.root.attributes('-fullscreen', False)
        self.root.destroy()

    def updatePages(self, snapshot):
        data, colorProp, blinkProp = map(list, zip(*snapshot))
        for i in range(13):
            self.data_labels[i]["text"] = data[i]
            if colorProp[i]:
                self.data_labels[i]["fg"] = "red"
            else:
                self.data_labels[i]["fg"] = "#0F3057"

    def update_loop(self):
        timeNow = time.time()
        autoscroll = (self.ds.get_autoscroll())/10
        self.autoscrollLbl["text"] = f"Autoscroll : {autoscroll}s"
        if autoscroll > 0:
            if timeNow - self.timeThen > autoscroll:
                if self.pageNow == 6:
                    self.pageNow = 0
                else:
                    self.pageNow += 1
                self.timeThen = timeNow
        else:
            self.pageNow = 0
            
        snapshot = self.ds.get_snapshot(self.pageNow)
        if snapshot:
            self.updatePages(snapshot)

        print("3T|%s" % datetime.datetime.now())
        # print("3D|Still Running")
        sys.stdout.flush()
        
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(1000, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = DisplayGUI(root)
    root.mainloop()
