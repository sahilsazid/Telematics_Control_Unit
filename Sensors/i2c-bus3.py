import smbus2
from Adafruit_IO import Client, Feed, RequestError
import time
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1115 import ADS1115
import adafruit_ads1x15.ads1115 as ADS
import adafruit_ads1x15.analog_in as AnalogIn
import busio
import csv

# =======================
# I2C Configuration
# =======================
# Use the software I2C bus (created with dtoverlay)
I2C_BUS_NUMBER = 3   # corresponds to /dev/i2c-3

# Initialize hardware interfaces
bus = smbus2.SMBus(I2C_BUS_NUMBER)

# MPU6050 Registers and Address
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B

# =======================
# Adafruit IO Setup
# =======================
ADAFRUIT_AIO_USERNAME = "Sahil122"
ADAFRUIT_AIO_KEY      = "aio_gcrO68MZPo6y2mRezhZaup4mjRPA"

aio = Client(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)
myfeed = aio.feeds('acceleration')
myfeed_2 = aio.feeds('engine-temp')

# =======================
# Initialize Sensors
# =======================
# Wake up MPU6050
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

# Initialize ADS1115 using /dev/i2c-3
i2c_ads = busio.I2C(3, 3)  # Dummy values, we’ll fix below
import board
import adafruit_bus_device.i2c_device as i2c_device
import adafruit_ads1x15.ads1115 as ADS

# Use the I2C device directly from /dev/i2c-3
i2c_ads = busio.I2C(board.SCL, board.SDA)  # This line won't work for /dev/i2c-3
# Instead, open directly:
import os
import fcntl
import sys

# Helper for creating I2C device manually
import adafruit_bus_device.i2c_device as i2c_device
from adafruit_ads1x15.ads1x15 import ADS1x15

# Better approach: use Adafruit ADS1115 with smbus2 via low-level wrapper
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio

# You can access the same I2C bus as:
i2c_ads = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c_ads)
chan = AnalogIn(ads, ADS.P0)

# =======================
# Helper Functions
# =======================
def read_raw_data(addr):
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

def get_acceleration():
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_XOUT_H + 2)
    acc_z = read_raw_data(ACCEL_XOUT_H + 4)

    Ax = acc_x / 16384.0
    Ay = acc_y / 16384.0
    Az = acc_z / 16384.0

    return Ax, Ay, Az

def get_temperature_lm35():
    voltage = chan.voltage  # in Volts
    temperature_c = voltage * 100.0
    return temperature_c

# =======================
# CSV Setup
# =======================
with open("accl_data.csv", "w", newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Acceleration X", "Acceleration Y", "Acceleration Z", "Temperature (°C)"])

# =======================
# Main Loop
# =======================
try:
    while True:
        Ax, Ay, Az = get_acceleration()
        temperature = get_temperature_lm35()

        aio.send(myfeed.key, Ax)
        aio.send(myfeed_2.key, temperature)

        print(f"Accel (g): X={Ax:.2f}, Y={Ay:.2f}, Z={Az:.2f} | LM35 Temp: {temperature:.2f} °C")
        time.sleep(5)

except KeyboardInterrupt:
    print("\nExiting...")
    bus.close()

