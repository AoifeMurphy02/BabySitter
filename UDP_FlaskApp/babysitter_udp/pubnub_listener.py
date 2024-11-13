import requests
import mysql.connector
import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from dotenv import load_dotenv
import time

load_dotenv()

# PubNub configuration
config = PNConfiguration()
config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
config.user_id = "laptop"
pubnub = PubNub(config)

app_channel = "babysitter"

# MySQL database connection setup
def save_video_to_db(file_path):
    connection = mysql.connector.connect(
        host="ec2-51-21-134-92.eu-north-1.compute.amazonaws.com",  
        user="root",
        password="Aoifetara02*", 
        database="babysitter"
    )
    cursor = connection.cursor()

    # Insert the file path into the database
    try:
        cursor.execute("INSERT INTO baby_data(id, baby_name, time, sound_pitch, motion_detected, temperature, humidity, camera_feed_path, audio) VALUES (%s,%s,%s,%s,%s,%s,%s,%s, %s)", 
                       (1, "Eve", "11:00", "22", "yes", "12", file_path, "11"))
        connection.commit()
        print("Video path successfully saved to the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

# Function to download the video from the Raspberry Pi
def download_video_from_pi(video_path):
    pi_ip = "192.168.183.28" 
    url = f"http://{pi_ip}:8000/{video_path.split('/')[-1]}"  # Extract video filename from path
    print(f"Attempting to download video from URL: {url}")

    try:
        response = requests.get(url, stream=True, timeout=60)
        if response.status_code == 200:
            local_path = "downloaded_video.h264"
            with open(local_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print("Video downloaded successfully.")
            save_video_to_db(local_path)
        else:
            print(f"Failed to download video. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading video: {e}")

        
# PubNub listener to handle video-ready notifications
class VideoListener(SubscribeListener):
    def message(self, pubnub, message):
        if 'video_ready' in message.message:
            video_path = message.message['video_ready']
            print(f"Video is ready for transfer: {video_path}")
            download_video_from_pi(video_path)

pubnub.add_listener(VideoListener())
pubnub.subscribe().channels(app_channel).execute()
