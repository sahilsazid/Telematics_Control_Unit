from Adafruit_IO import Client
import time

ADAFRUIT_IO_USERNAME = "Sahil122"
ADAFRUIT_IO_KEY = "aio_gcrO68MZPo6y2mRezhZaup4mjRPA"

aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Example coordinates (Delhi)
latitude = 26.788060000000005
longitude = 81.073905
print("Starting to send data to Adafruit IO... (Press Ctrl+C to stop)")

while(1):
    gps_data = f"{latitude},{longitude}"
    
    try:
        # 1. Use .send_data() instead of .send()
        aio.send_data('gps', gps_data)
        
        # 2. Print INSIDE the loop to confirm each send
        print(f"Sent: {gps_data}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

    # Your 10-second sleep is perfect for staying within the rate limits.
    time.sleep(10)

