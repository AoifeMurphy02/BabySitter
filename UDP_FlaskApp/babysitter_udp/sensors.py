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
#import pyaudio

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

def convert_to_mp4(h264_path, mp4_path):
    """Converts H.264 file to MP4 using ffmpeg."""
    print("Converting video to .mp4 format...")
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", h264_path, "-c:v", "copy", mp4_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode == 0:
        print(f"Conversion successful. Video saved as '{mp4_path}'")
    else:
        print(f"Conversion failed: {result.stderr.decode()}")

def camera():
    # Initialize the camera
    picam2 = Picamera2()

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

    # Record a video and save it as '.h264'
    video_h264_path = '/home/aoife/Videos/video1.h264'
    video_mp4_path = '/home/aoife/Videos/video1.mp4'
    encoder = H264Encoder(bitrate=1000000)
    picam2.start_recording(encoder, video_h264_path)

    print("Recording video...")
    sleep(5)  # Record for 5 seconds
    picam2.stop_recording()
    print(f"Video recorded and saved as '{video_h264_path}'")

    # Stop the camera
    picam2.stop()

    # Convert the recorded video to MP4
    convert_to_mp4(video_h264_path, video_mp4_path)

    # Start the HTTP server to serve the video file
    video_directory = os.path.dirname(video_mp4_path)
    start_http_server(video_directory)

    # Notify the app about the new video
    notify_video_ready(video_mp4_path)

#def microphone():
    # Initialize PyAudio
 #   p = pyaudio.PyAudio()



if __name__ == "__main__":
    camera()
#   microphone()
