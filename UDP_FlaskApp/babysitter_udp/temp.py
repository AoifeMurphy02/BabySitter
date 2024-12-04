import time
import board
import adafruit_dht

# Replace D4 with your GPIO pin
dht_device = adafruit_dht.DHT22(board.D4)

while True:
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        print(f"Temp: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
    except RuntimeError as error:
        # DHT sensors can fail sporadically, just retry
        print(f"Error reading sensor: {error}")
    time.sleep(2)
