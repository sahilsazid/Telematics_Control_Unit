from time import sleep
from machine import UART
import time
import network


uart = UART(2, baudrate=115200, tx=17, rx=16)
uart.write("AT+CGDCONT=1,\"IP\",\"jionet\"\r\n")
sleep(1.5)
uart.write("ATD*99#\r\n")
sleep(1.5)
uart.write("AT+CGDATA=\"PPP\",1\r\n")
sleep(1.5)
ppp = network.PPP(uart)
ppp.active(True)
ppp.connect()
sleep(3)
print(ppp.ifconfig())
print(ppp.isconnected())
import urequests as rt

print(rt.get("https://cyberfly.io/").text)
