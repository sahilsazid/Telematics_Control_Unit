from Adafruit_IO import MQTTClient
import RPi.GPIO as GPIO
import time

ADAFRUIT_AIO_USERNAME = "Sahil122"
ADAFRUIT_AIO_KEY      = "aio_gcrO68MZPo6y2mRezhZaup4mjRPA"

FEED_ID = "relay-control"

# Setup GPIO
RELAY_PIN = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Start OFF

def connected(client):
    print("Connected to Adafruit IO!")
    client.subscribe(FEED_ID)

def disconnected(client):
    print("Disconnected from Adafruit IO!")
    exit(1)

def message(client, feed_id, payload):
    print(f"Received: {payload}")
    if payload.lower() == "on":
        GPIO.output(RELAY_PIN, GPIO.HIGH)
    elif payload.lower() == "off":
        GPIO.output(RELAY_PIN, GPIO.LOW)

client = MQTTClient(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message

client.connect()
client.loop_background()

try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()

