import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)           # Bus 0, CE0
spi.max_speed_hz = 500000
spi.mode = 0b00

def read_gps():
    # Send 32 dummy bytes, receive GPS string
    resp = spi.xfer2([0x00]*32)
    text = ''.join(chr(b) for b in resp if 32 <= b < 127)
    return text.strip()

try:
    while True:
        data = read_gps()
        if data:
            print("GPS Data:", data)
        time.sleep(1)
except KeyboardInterrupt:
    spi.close()

