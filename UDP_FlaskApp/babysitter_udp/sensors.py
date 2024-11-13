from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from time import sleep
import RPi.GPIO as GPIO
import time
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from dotenv import load_dotenv
import os
import subprocess
import json
import subprocess  
import threading  

load_dotenv()

class Listener(SubscribeListener):
    def status(self, pubnub, status):
        print(f'Status: \n{status.category.name}')
    
config = PNConfiguration()
config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
config.user_id = "pi"

pubnub = PubNub(config)
pubnub.add_listener(Listener())

app_channel = "babysitter"

subscription = pubnub.channel(app_channel).subscription()
#subscription.on_message= lambda message: handle_message(message)
subscription.subscribe()

def notify_video_ready(file_path):
    pubnub.publish().channel(app_channel).message({"video_ready": file_path}).sync()
    print(f"Notification sent for video: {file_path}")

def start_http_server(directory, port=8000, ip_address="192.168.183.28"):
    """Start a simple HTTP server in the given directory, binding to a specific IP address."""
    os.chdir(directory)
    command = ["python3", "-m", "http.server", str(port), "--bind", ip_address]
    subprocess.Popen(command)
    print(f"HTTP server started at http://{ip_address}:{port}/")

def camera():
    # Initialize the camera
    picam2 = Picamera2()
    # Debugging: Print detected camera information
    camera_info = picam2.global_camera_info()
    print("Detected cameras:", camera_info)

    if not camera_info:
        print("No cameras detected. Exiting...")
        return

    # Set up video configuration
    video_config = picam2.create_video_configuration(main={"size": (1920, 1080)})
    picam2.configure(video_config)

    # Start the camera
    picam2.start()

    # Allow the camera to warm up
    sleep(2)

    # Capture an image and save it as 'image.jpg'
    picam2.capture_file('/home/aoife/img.jpg')
    print("Image captured and saved as 'img.jpg'")

    # Record a video
    video_file_path = '/home/aoife/Videos/video1.h264'
    encoder = H264Encoder(bitrate=1000000)
    picam2.start_recording(encoder, video_file_path)
    
    print("Recording video...")
    sleep(5)  # Record for 5 seconds
    picam2.stop_recording()
    print(f"Video recorded and saved as '{video_file_path}'")

    # Stop the camera
    picam2.stop()

    # Start the HTTP server to serve the video file
    video_directory = os.path.dirname(video_file_path)  # Get the directory where the video is stored
    http_server_thread = threading.Thread(target=start_http_server, args=(video_directory,))
    http_server_thread.daemon = True
    http_server_thread.start()

    # Notify laptop about the new video
    notify_video_ready(video_file_path)

if __name__ == "__main__":
    camera()
