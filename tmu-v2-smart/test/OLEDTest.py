import smbus2
import time
from PIL import Image, ImageDraw, ImageFont

I2C_BUS = 1
I2C_ADDR = 0x3C

bus = smbus2.SMBus(I2C_BUS)

def oled_cmd(cmd):
    bus.write_byte_data(I2C_ADDR, 0x00, cmd)

def oled_init():
    for c in [0xAE, 0x00, 0x10, 0x40, 0x81, 0xCF, 0xA1, 0xC8, 0xA6,
              0xA8, 0x3F, 0xD3, 0x00, 0xD5, 0x80, 0xD9, 0xF1, 0xDA,
              0x12, 0xDB, 0x40, 0x20, 0x00, 0x8D, 0x14, 0xAF]:
        oled_cmd(c)

def oled_show(image):
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
        bus.write_i2c_block_data(I2C_ADDR, 0x40, buf[i:i+16])

def oled_print(teks: str):
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 10)
    except:
        font = ImageFont.load_default()
    img = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(img)
    for i, row in enumerate(teks.splitlines()):
        draw.text((0, i * 12), row, font=font, fill=255)
    oled_show(img)

if __name__ == "__main__":
    oled_init()
    oled_print("TMU MODBUS GATEWAY\nOLED TEST OK\nHello, DH!")
    time.sleep(5)