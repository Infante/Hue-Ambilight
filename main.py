# Import modules
import time, json, threading
import numpy as np
import cv2 as cv
from phue import Bridge
from utils import utils
from app import emit_socket, start_server
from sklearn.cluster import KMeans

started = False

# Intialize utilities
utilities = utils.Utils()

# Gets all video inputs on current device
def get_inputs():
    try:
        inputs_list = []
        count = 0
        while True:
            capture = cv.VideoCapture(count)
            if capture.read()[0]:
                inputs_list.append(count)
            else:
                break
            count+=1
        return inputs_list
    except Exception as e:
        emit_socket(f"Error getting input devices: {e}")
        print(f"Error getting input devices: {e}")

# Listens to video streaming data (main function)
def listen_video(device, light, config):
    # Update config here as well incase user updated setup ??
    global started
    # Start watching video
    capture = cv.VideoCapture(device)
    # While the video is being streamed
    while capture.isOpened():
        try:
            time.sleep(.1)
            if light.on == True:
                # Captures each frame
                ret, frame = capture.read()
                # get image from current frame
                image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                # reshape the image to a 2D array of pixels and 3 color values (RGB)
                pixel_values = image.reshape((-1, 3))
                # convert to float
                pixel_values = np.float32(pixel_values)
                # define stopping criteria
                criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.2)
                k = 3
                _, labels, (colors) = cv.kmeans(pixel_values, k, None, criteria, 10, cv.KMEANS_RANDOM_CENTERS)
                # convert back to 8 bit values
                colors = np.uint8(colors)
                # Update light's colors
                utilities.update_light(light, colors)
                # Check if video streaming has ended
                if ret == False:
                    break
            else:
                print("User lights off")
                emit_socket("User lights off")
        except Exception as e:
            if ret == False:
                break
            else:
                print(f"Error streaming video: {e}")
                emit_socket(f"Error streaming video: {e}")
    # End streaming when loop is done
    print("Video stream ended")
    emit_socket("Video stream ended")
    capture.release()
    cv.destroyAllWindows()
    # Restart script to wait for video to start up again
    started = False
    main()

# Main function
def main():
    global started
    # Get config + setup HUE client
    with open("config.json", "r") as f:
      config = json.load(f)
    # Get users config for his HUE
    ip = config['ip']
    username = config["username"]
    # If user has no IP setup get him to input one
    if ip == "":
        emit_socket("Please enter in your HUE's IP. Found here: https://discovery.meethue.com/")
        print("Please enter in your HUE's IP. Found here: https://discovery.meethue.com/")
        time.sleep(10)
        # Return and check if user entered
        return main()
    # Connect to user's HUE
    try:
        hue = Bridge(ip)
        hue.connect()
        print("HUE connected")
        emit_socket("HUE connected")
    except:
        print("Please connect HUE")
        emit_socket("Please connect HUE")
        time.sleep(5)
        return main()
    # Update lights available and define the hue light
    lights = hue.get_light_objects('id')
    lights_object = []
    hue_light = ""
    for light in lights:
        # Select light based off user inputted light (defaults at 11)
        if light == config["light"]:
            hue_light = lights[light]
        lights_object.append({"name": lights[light].name, "id": light})
    config["lights"] = lights_object
    utilities.write_json("config.json", config)
    # Stop this loop when a video capture starts up
    while started == False:
        try:
            print("Waiting for video")
            time.sleep(3)
            # Get current inputs
            inputs = get_inputs()
            if len(inputs) > 0:
                # Start watching video / input
                started = True
                listen_video(0, hue_light, config)
                break
            else:
                print("No input available")
                emit_socket("No input available")
        except Exception as e:
            print(f"Error waiting for video: {e}")
            emit_socket(f"Error waiting for video: {e}")

if __name__ == '__main__':
    # Create two threads, one for running the server
    # The other thread for running the script
    event = threading.Event()
    thread1 = threading.Thread(target=main)
    thread2 = threading.Thread(target=start_server)
    thread2.start()
    time.sleep(10)
    thread1.start()
