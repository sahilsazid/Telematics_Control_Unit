import smbus2
from  Adafruit_IO import Client, Feed, RequestError
import time
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1115 import ADS1115
import board
import busio
import csv

# MPU6050 Registers and Address
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B

gravity =9.80665 

ADAFRUIT_AIO_USERNAME = "Sahil122"
ADAFRUIT_AIO_KEY      = "aio_gcrO68MZPo6y2mRezhZaup4mjRPA"

aio = Client(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)

myfeed=aio.feeds('acceleration')
myfeed_2=aio.feeds('engine-temp')

# Initialize I2C for MPU6050 using smbus2
bus = smbus2.SMBus(1)

# Wake up MPU6050
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)
time.sleep(1)

# Initialize I2C for ADS1115
i2c_ads = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c_ads)
ads.gain = 4
chan = AnalogIn(ads, 0)   # A0 channel connected to LM35

def read_raw_data(addr):
    # Reads two bytes of data and combines them
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr+1)
    value = ((high << 8) | low)
    if value > 32768:
        value = value - 65536
    return value

def get_acceleration():
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_XOUT_H + 2)
    acc_z = read_raw_data(ACCEL_XOUT_H + 4)
    
    # Scale: 16384 LSB/g for ±2g
    Ax = acc_x / 16384.0
    Ay = acc_y / 16384.0
    Az = acc_z / 16384.0
    
    return Ax, Ay, Az

def get_temperature_lm35():
    # LM35 gives 10mV per °C, ADS1115 default gain = 1 => 4.096V range
    voltage = chan.voltage  # in Volts
    temperature_c =(voltage) * 100.0  # (10mV/°C → 0.01V/°C)
    return temperature_c


#csv file

with open("accl_data.csv","w",newline='') as file:
    writer = csv.writer(file)
    writer.writerow("Acceleration in X")


# Main loop
try:
    while True:
        Ax, Ay, Az = get_acceleration()
        axmss=Ax*gravity
        aymss=Ay*gravity
        azmss=Az*gravity
        temperature = get_temperature_lm35()
        aio.send(myfeed.key,axmss)
        aio.send(myfeed_2.key,temperature)

        
        print(f"Accel (ms2): X={axmss:.2f}, Y={aymss:.2f}, Z={azmss:.2f} | LM35 Temp: {temperature:.2f} °C")
        time.sleep(3)

except KeyboardInterrupt:
    print("\nExiting...")
    bus.close()

