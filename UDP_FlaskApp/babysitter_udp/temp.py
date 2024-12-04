import pulseio
from adafruit_dht import DHT22
import board
import time

# Initialize the DHT device using GPIO4
dht_device = DHT22(board.D4)  # D4 corresponds to GPIO4 on the Raspberry Pi

while True:
    try:
        humidity = dht_device.humidity
        temperature = dht_device.temperature
        if humidity is not None and temperature is not None:
            print(f"Temp: {temperature}°C, Humidity: {humidity}%")
        else:
            print("Failed to retrieve data from sensor.")
    except RuntimeError as error:
        print(f"Error reading sensor: {error}")
    time.sleep(2)
