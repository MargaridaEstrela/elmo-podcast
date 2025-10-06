import os
import sys
import time
import socket
import multiprocessing
import webrtcvad
import collections
import sounddevice as sd
import logging
import threading





# Audio recording parameters
RATE = 16000
FRAME_DURATION = 10  # 10ms
CHUNK = int(RATE * FRAME_DURATION / 1000)  # 10ms frames
TIMEOUT = 0.8  # Timeout period in seconds to determine end of speech
PODCAST_ID = 0

robot_angles = {0: None, 1: -40, 2: 0 , 3: 40}

speakers = {0: False, 1: False, 2: False, 3:False}



def setup_logger(process_name):

    directory = str(PODCAST_ID)

    #if not os.path.exists(directory):
    #   os.makedirs(directory)

    # Define the directory and log file path
    log_dir = os.path.join("logs", directory)
    log_file = os.path.join(log_dir, process_name + ".log")
    
    # Ensure the directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a logger
    logger = logging.getLogger(process_name)
    logger.setLevel(logging.INFO)  # Set the log level

    # Prevent duplicate handlers if logger already exists
    if not logger.handlers:
        # Create a file handler for each process based on process name
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.INFO)

        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(file_handler)
    
    return logger

def find_input_device_index(device):
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if device.lower() in dev["name"].lower():
            return i
    return None

def vb_control(input_device_index, speaker):
    logger = setup_logger(f"vb_{speaker}")
    vad = webrtcvad.Vad(1)  # Change for more aggressive filtering
    print(f"Listening on channel {speaker}...")

    def callback(indata, frames, callback_time, status):
        if status:
            print(status)

        # Extract the specific channel
        mono_frame = indata[:, speaker + 2].copy()
        mono_frame_bytes = mono_frame.tobytes()

        # Voice Activity Detection
        speakers[speaker] = vad.is_speech(mono_frame_bytes, RATE)
        #print(f"{channel}__{speakers[channel]}") 
       
    try:
        stream = sd.InputStream(
            samplerate=RATE,
            device=input_device_index,
            channels=6,
            dtype="int16",
            callback=callback,
            blocksize=CHUNK,
        )

        with stream:
            while True:
                time.sleep(0.1)

    except Exception as e:
        print(f"Error during listening: {e}")


def nvb_autonomous_control():
    while True:
        active_angles = [robot_angles[k] for k, v in speakers.items() if v]



def main():
    """print(sys.argv)
    if len(sys.argv) != 4:
        print("Usage: python ___.py <host_ip> <robot_ip>")
        sys.exit(1)
    else:
        HOST_IP = sys.argv[1]
        ROBOT_IP = sys.argv[2]
        PORT = sys.argv[3]"""

    logger = setup_logger("main")

    # Get a list of all available devices
    devices = sd.query_devices()

    # Filter and list only input devices (microphones)
    input_devices = [device for device in devices if device["max_input_channels"] > 0]

    # Display the input devices
    for idx, device in enumerate(input_devices):
        print(f"Device {idx}: {device['name']} -> {device['max_input_channels']}")

    device_name = "H6"
    input_device_index = find_input_device_index(device_name)
    if input_device_index is None:
        print(f"Input device '{device_name}' not found.")
        sys.exit(1)

    #channel = 3  # Skip L and R channels
    
    for speaker in range(4):
        threading.Thread(target=vb_control, args=(input_device_index, speaker, )).start()
        logger.info(f'START: {str(speaker)}')

    threading.Thread(target=nvb_autonomous_control, args=( )).start()

if __name__ == "__main__":
    main()
