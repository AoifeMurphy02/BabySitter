from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import time
from time import sleep
import os
import subprocess
import pyaudio
import wave
import numpy as np
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from pubnub.callbacks import SubscribeCallback
from dotenv import load_dotenv
import threading
import signal
import sys
import adafruit_dht
import board
import RPi.GPIO as GPIO
import http.server
import socketserver
import threading
import pygame


httpd = None

last_notification_time = 0
notification_interval = 60
GPIO.cleanup() 

load_dotenv()

class Listener(SubscribeListener):
    def status(self, pubnub, status):
        print(f'Status: {status.category.name}')

# PubNub configuration
config = PNConfiguration()
config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
config.secret_key =os.getenv("PUBNUB_SECRET")   
config.user_id = "pi"

pubnub = PubNub(config)
pubnub.add_listener(Listener())

app_channel = "babysitter"

class MySubscribeCallback(SubscribeCallback):
    def message(self, pubnub, message):
        """Handle incoming messages."""
        if message.message == "play_music":
            print("Received 'play_music' message. (No speakers)")
            file_path = "/home/aoife/Videos/music.wav"
            play_audio(file_path)

# Global flag to control the sound detection loop
sound_detection_active = True

def detect_loud_sound_continuous(threshold=2000, rate=44100, channels=1, chunk_size=1024):
    """Continuously detect loud sounds."""
    global sound_detection_active

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size)

    print("Listening for loud sounds (continuous)... Press Ctrl+C to stop.")

    try:
        while sound_detection_active:
            data = stream.read(chunk_size, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)
            max_amplitude = np.max(np.abs(audio_data))

            if max_amplitude > threshold:
                print(f"Loud sound detected! Amplitude: {max_amplitude}")
                send_sound_notification()
    except KeyboardInterrupt:
        print("Sound detection stopped by user.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Stopped listening.")

def start_sound_detection():
    """Start the sound detection in a separate thread."""
    sound_thread = threading.Thread(target=detect_loud_sound_continuous, kwargs={"threshold": 1000})
    sound_thread.daemon = True  # Ensure the thread exits when the main program exits
    sound_thread.start()
    return sound_thread


def handle_exit_signal(signal, frame):
    """Handle exit signals (e.g., Ctrl+C) to stop sound detection."""
    global sound_detection_active
    print("Shutting down...")
    sound_detection_active = False
    sys.exit(0)

# Attach the signal handler
signal.signal(signal.SIGINT, handle_exit_signal)

def notify_file_ready(video_url, audio_url):
    """Notify the app with video and audio URLs."""
    pubnub.publish().channel(app_channel).message({
        "video_ready": video_url,
        "audio_ready": audio_url,
    }).sync()
    print(f"Notification sent for video: {video_url} and audio: {audio_url}")

def start_http_server(directory, port=8000, ip_address="192.168.219.28"):
    """Start an HTTP server to serve files."""
    global httpd
    os.chdir(directory)

    # Define the request handler
    handler = http.server.SimpleHTTPRequestHandler
    
    # Create the server instance
    httpd = socketserver.TCPServer((ip_address, port), handler)
    
    print(f"HTTP server started at http://{ip_address}:{port}/")
    threading.Thread(target=httpd.serve_forever).start()
def convert_to_mp4(h264_path, mp4_path):
    """Convert H.264 video to MP4."""
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", h264_path, "-c:v", "copy", mp4_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode == 0:
        print(f"Video converted to MP4: {mp4_path}")
    else:
        print(f"Video conversion failed: {result.stderr.decode()}")

def camera():
    """Capture video and save it."""
    try:
        picam2 = Picamera2(camera_num=0)  # Ensure the correct camera index
        video_config = picam2.create_video_configuration(main={"size": (1920, 1080)})
        picam2.configure(video_config)
        picam2.start()
        sleep(2)

        video_h264_path = '/home/aoife/Videos/video1.h264'
        video_mp4_path = '/home/aoife/Videos/video1.mp4'
        encoder = H264Encoder(bitrate=1000000)
        picam2.start_recording(encoder, video_h264_path)
        print("Recording video...")
        sleep(5)  # Record for 5 seconds
        picam2.stop_recording()
        picam2.stop()

        convert_to_mp4(video_h264_path, video_mp4_path)
        return video_mp4_path
    except Exception as e:
        print(f"Error in camera function: {e}")
        return None


def detect_loud_sound(threshold=2000, duration=10, rate=44100, channels=1, chunk_size=1024):
    """Detect loud sounds from the microphone."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size)

    print("Listening for loud sounds...")

    for _ in range(0, int(rate / chunk_size * duration)):
        data = stream.read(chunk_size, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)
        max_amplitude = np.max(np.abs(audio_data))

        if max_amplitude > threshold:
            print(f"Loud sound detected! Amplitude: {max_amplitude}")
            send_sound_notification()
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Stopped listening.")


def send_sound_notification():
    """Notify the app that a loud sound has been detected."""
    global last_notification_time

    current_time = time.time()
    if current_time - last_notification_time > notification_interval:
        last_notification_time = current_time
        pubnub.publish().channel('babysitter').message({'sound_alert': 'Baby is crying!'}).sync()
        print("Notification sent: Baby is crying!")
    else:
        print("Notification suppressed: Too soon since the last one.")

def record_audio(file_path, duration=5, rate=44100, channels=1, chunk_size=1024):
    """Record audio from the microphone."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=chunk_size,input_device_index=3)
    print("Recording audio...")

    frames = [stream.read(chunk_size) for _ in range(0, int(rate / chunk_size * duration))]
    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    print(f"Audio saved: {file_path}")


def current_temperature(interval=2):
    """Monitor the temperature and humidity."""
    dht_device = adafruit_dht.DHT22(board.D4)

    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        print(f"Temperature: {temperature}°C")
        print(f"Humidity: {humidity}%")
        
        pubnub.publish().channel('babysitter').message({'current_temp': f'{temperature}°C'}).sync()
        pubnub.publish().channel('babysitter').message({'current_humidity': f'{humidity}%'}).sync()

        # Send alert if temperature exceeds 26°C
        if temperature and temperature > 26:
            alert_message = f"Alert! High temperature detected: {temperature}°C"
            print(alert_message)
            pubnub.publish().channel('babysitter').message({'high_alert': alert_message}).sync()
        # If temperature is less than 16°C (too cold)
        if temperature and temperature < 16:
            alert_message = f"Alert! Low temperature detected: {temperature}°C"
            print(alert_message)
            pubnub.publish().channel('babysitter').message({'low_alert': alert_message}).sync()

    except RuntimeError as e:
        print(f"Error reading sensor: {e}")


sound_thread = start_sound_detection()
def stop_http_server():
    """Stop the HTTP server."""
    if httpd:
        httpd.shutdown()
        print("HTTP server stopped.")

def play_audio(file_path):
    """Play an audio file through the speakers."""
    try:
        print(f"Playing audio: {file_path}")
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        # Wait for the audio to finish
        while pygame.mixer.music.get_busy():
            time.sleep(5)
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        pygame.mixer.music.stop() 


def main():
    """Main loop for the system."""
    # Temperature and humidity monitoring
    current_temperature()

    # Video and audio recording
    video_path = '/home/aoife/Videos/video1.mp4'
    audio_path = "/home/aoife/Videos/sound1.wav"
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    record_audio(audio_path)

    # Start HTTP server
    start_http_server("/home/aoife/Videos")

    # Construct URLs for video and audio
    ip_address = "192.168.219.28"
    video_url = f"http://{ip_address}:8000/{os.path.basename(video_path)}"
    audio_url = f"http://{ip_address}:8000/{os.path.basename(audio_path)}"

    # Notify app
    notify_file_ready(video_url, audio_url)

    # Keep the main loop running
    while True:
        try:
            print("Main application running... (Press Ctrl+C to stop)")
            sleep(10) 
        except KeyboardInterrupt:
            break
        except KeyboardInterrupt:
            print("Main loop interrupted. Cleaning up...")
        finally:
            time.sleep(10)
            stop_http_server()  
        handle_exit_signal(None, None)

  #  handle_exit_signal(None, None)

if __name__ == "__main__":
    pubnub.add_listener(MySubscribeCallback())
    main()
