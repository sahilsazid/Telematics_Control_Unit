#!/usr/bin/env python3
"""
Read LM35 temperature (°C) from ADS1115 channel 0 on Raspberry Pi Zero 2W.
Requires: adafruit-circuitpython-ads1x15
"""

import time
import sys
import board
import busio
from adafruit_ads1x15.ads1x15 import ADS1x15 as ADS
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

def setup_ads(gain=4):
    """Return initialized ADS1115 object and AnalogIn for channel 0."""
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS1115(i2c)
    ads.gain = gain
    chan0 = AnalogIn(ads,0)  # <-- use ADS.P0 instead of ADS1115.P0
    return ads, chan0

def voltage_to_celsius(voltage_v):
    """LM35 outputs 10 mV per °C → °C = V * 100"""
    return voltage_v * 100.0

def main(poll_interval=1.0, gain=1):
    try:
        ads, chan0 = setup_ads(gain=gain)
    except Exception as e:
        print("Failed to initialize ADS1115:", e)
        sys.exit(1)

    print("ADS1115 initialized. Gain =", ads.gain)
    print("Reading LM35 on A0. Press Ctrl+C to stop.\n")

    window = []
    window_size = 5

    try:
        while True:
            voltage = chan0.voltage
            temp_c = voltage_to_celsius(voltage)
            temp_f = temp_c * 9.0/5.0 + 32.0

            window.append(temp_c)
            if len(window) > window_size:
                window.pop(0)
            avg_c = sum(window) / len(window)

            print(f"Voltage: {voltage:0.4f} V  Temp: {temp_c:0.2f} °C  ({temp_f:0.2f} °F)  Avg: {avg_c:0.2f} °C")
            time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()

