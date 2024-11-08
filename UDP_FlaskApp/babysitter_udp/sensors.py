from picamera2 import Picamera2
from time import sleep

def main():
    camera()

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

    # Record a video
    video_file_path = '/home/aoife/Videos/video1.h264'
    picam2.start_recording(video_file_path)
    print("Recording video...")
    sleep(5)  # Record for 5 seconds
    picam2.stop_recording()
    print(f"Video recorded and saved as '{video_file_path}'")

    # Stop the camera
    picam2.stop()

if __name__ == "__main__":
    main()
