import sys
import time
import socket
import multiprocessing
import webrtcvad
import collections
import sounddevice as sd
import logging
import threading
import random
import signal
import os
from elmo_server import ElmoServer
from emoshow_logger import EmoShowLogger
from fastapi import FastAPI
from uvicorn import Config, Server
import torch



# Audio recording parameters
SAMPLE_RATE = 16000
FRAME_DURATION = 10  # 10ms
CHUNK = 512 # must be 512 samples for VAD at 16kHz
SILENCE_FRAMES_THRESHOLD = 30
PODCAST_ID = 0

MAX_CHUNK_DURATION = 5  # seconds
MAX_CHUNK_SAMPLES = SAMPLE_RATE * MAX_CHUNK_DURATION

# Global variables
elmo = None
elmo_ip = None
elmo_port = None
client_ip = None
shutdown_event = threading.Event()


robot_angles = {0: [None, None], 1: [35, -7], 2: [0, -7], 3: [-35, -7]}
speakers = {0: False, 1: False, 2: False, 3: False}

global flag, robot_position, api_server
flag = True
robot_position = [None,None,None,None]
api_server = None
app = FastAPI()

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutdown signal received, stopping all threads...")
    shutdown_event.set()

def setup_logger(process_name):
    directory = str(PODCAST_ID)
    log_dir = os.path.join("logs", directory)
    log_file = os.path.join(log_dir, process_name + ".log")
    
    # Ensure the directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a logger
    logger = logging.getLogger(process_name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if logger already exists
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def find_input_device_index(device):
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if device.lower() in dev["name"].lower():
            return i
    return None

"""def vb_control(input_device_index, speaker):
    global speakers, shutdown_event
    logger = setup_logger(f"vb_{speaker}")
    vad = webrtcvad.Vad(1)  # Change for more aggressive filtering
    logger.info(f"Listening on channel {speaker}...")
    print(f"Listening on channel {speaker}...")

    def callback(indata, frames, callback_time, status):
        if status:
            logger.warning(f"Audio callback status: {status}")

        # Extract the specific channel
        mono_frame = indata[:, speaker + 2].copy()
        mono_frame_bytes = mono_frame.tobytes()

        # Voice Activity Detection
        try:
            speakers[speaker] = vad.is_speech(mono_frame_bytes, RATE)
        except Exception as e:
            logger.error(f"VAD error: {e}")
       
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
            # Check shutdown_event instead of infinite loop
            while not shutdown_event.is_set():
                time.sleep(0.1)
        
        logger.info(f"Speaker {speaker} stream closed")

    except Exception as e:
        logger.error(f"Error during listening on speaker {speaker}: {e}")
    finally:
        logger.info(f"Speaker {speaker} control thread cleaned up")"""

def detect_speech(audio, accumulated_audio, vad_model):
    """Detects speech segments using Silero VAD."""
    accumulated_audio.extend(audio)
    if len(accumulated_audio) < 512:
        return False

    audio_tensor = torch.tensor(accumulated_audio[-512:], dtype=torch.float32)
    
    # Normalize audio
    if torch.max(torch.abs(audio_tensor)) > 0:
        audio_tensor /= torch.max(torch.abs(audio_tensor))
    
    audio_tensor = audio_tensor.unsqueeze(0)

    speech_prob = vad_model(audio_tensor, SAMPLE_RATE).item()

    return speech_prob > 0.2  # Adjust threshold (lower = more sensitive)


def vb_control(input_device_index, speaker):
    logger = setup_logger(f"vb_{speaker}")
    print("Loading VAD model...")
    vad_model, _ = torch.hub.load("snakers4/silero-vad", "silero_vad")
    logger.info("VAD model loaded.")
    
    chunk_buffer = []  # Stores speech audio
    recording = False  # Flag to track when we are recording speech
    silence_counter = 0  # Tracks silence duration
    accumulated_audio = []  # Collects audio for VAD
    
    logger.info("Listening...")
    
    def callback(indata, frames, time, status):
        """Real-time audio callback function."""
        nonlocal speaker, chunk_buffer, recording, silence_counter, accumulated_audio, vad_model
        if status:
            print(f"Audio error: {status}")

        audio_chunk = indata[:, speaker+2]  # Take mono channel

        if detect_speech(audio_chunk, accumulated_audio, vad_model):
            if not recording:
                recording = True           
            
            silence_counter = 0  # Reset silence counter when voice is detected
            speakers[speaker] = True
        else:
            silence_counter += 1

            # Only stop recording if silence is detected for multiple frames
            if recording and silence_counter > SILENCE_FRAMES_THRESHOLD:                
                accumulated_audio.clear()
                silence_counter = 0
                speakers[speaker] = False

    with sd.InputStream(device=input_device_index, samplerate=SAMPLE_RATE, channels=6, dtype="float32", 
                        callback=callback, blocksize=CHUNK):
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Stopping listening.")



def nvb_autonomous_control():
    global robot_position, flag
    logger = setup_logger(f"nvd_autonomous")
    debug_mode = False
    connect_mode = False

    # Start logger
    log_path = "logs/elmo-app.log"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Create the file only if it does not exist
    if not os.path.exists(log_path):
        with open(log_path, "w") as f:
            f.write("")

    elmo_logger = EmoShowLogger(log_file=log_path)
    
    # Start server
    elmo = ElmoServer(
        elmo_ip, int(elmo_port), client_ip, elmo_logger, debug_mode, connect_mode
    )
    #elmo.toggle_motors()
    #elmo.toggle_behaviour()
    elmo.set_image("blink.gif")
    elmo.move_tilt(-7)

    logger.info("Autonomous control initialized")
    print("Autonomous control initialized")

    time.sleep(5)
    #elmo.move_pan(-40)
    time_listening = 0
    time_count = 0
    s_talking = None
    current_position = [0, -7]
    #print("pan")
    
    try:
        while not shutdown_event.is_set():
            try:
                    
                if flag:    
                    # find the persons that are talking
                    active_angles = [[k, robot_angles[k]] for k, v in speakers.items() if v]
                    print(active_angles)
                    
                    # if theres more that one 
                    # TODO: gaze detection
                    if len(active_angles) > 1:

                        if 0 in [k for k, v in active_angles]:
                            print("elmo is talking")
                            elmo.set_icon("speaking.png")

                        #if the person that was talking previously is stil talking look at that person                     
                        elif s_talking != None and s_talking in [k for k, v in active_angles]:
                            print("kip looking")
                            elmo.set_icon("listening.png") 
                        # else choose a rondom person
                        else:
                            active_angles = [random.choice(active_angles)]
                            print("choose random")
                            elmo.set_icon("listening.png")


                    #print(f"{s_talking} {active_angles[0][0]}")
                    # if one person is speaking and it is not the robot
                    if len(active_angles) == 1 and active_angles[0][0] != 0:
                        elmo.set_icon("listening.png")
                        print(time.time() - time_listening)
                        #start talking
                        if (time_listening == 0 and s_talking == None) or (time_listening != 0 and s_talking != active_angles[0][0]):
                            
                            s_talking = active_angles[0][0]
                            elmo.move_pan(active_angles[0][1][0])
                            elmo.move_tilt(active_angles[0][1][1])

                            if current_position != [active_angles[0][1][0],active_angles[0][1][1]]:
                                time_listening = time.time()
                                current_position = [active_angles[0][1][0],active_angles[0][1][1]]
                            
                            time.sleep(2)
                            print("start talking")
                    
                
                        # if is still talking
                        elif time_listening != 0 and s_talking == active_angles[0][0] and time.time() - time_listening >= 5:
                                elmo.set_icon("listening.png")
                                elmo.toggle_behaviour()
                                print(elmo.get_control_behaviour())
                                #elmo.move_tilt(active_angles[0][1][1]+10)    
                                time.sleep(2)   
                                #elmo.move_tilt(active_angles[0][1][1])  
                                #time.sleep(2)
                                elmo.toggle_behaviour()
                                print(elmo.get_control_behaviour())
                                elmo.move_pan(active_angles[0][1][0])
                                elmo.move_tilt(active_angles[0][1][1]) 
                                current_position = [active_angles[0][1][0],active_angles[0][1][1]] 
                                print("backchanneling")
                                time_listening = time.time()
                        
                    elif len(active_angles) == 1 and active_angles[0][0] == 0:
                        elmo.set_icon("speaking.png")
                        if s_talking != 0:
                            time_listening = time.time()
                            s_talking = active_angles[0][0]
                            print("robot star talking")
                            
                    
                    elif len(active_angles) == 0:
                        print("nada")
                        #time_listening = 0
                        s_talking = None
                        elmo.set_icon("black.png")
                    
                    #TODO: WHAT ROBO DO WHEN TALKING
                
                if not flag:
                    if robot_position[0] != None:
                        elmo.move_pan(robot_position[0])
                        current_position[0] = robot_position[0]
                    if robot_position[1] != None:
                        elmo.move_tilt(robot_position[1])
                        current_position[1] = robot_position[1]
                    if robot_position[2] != None:
                        elmo.set_image(robot_position[2])
                    if robot_position[3] != None:
                        elmo.set_icon(robot_position[3])
                    if robot_position == [None,None,None,None]:
                        elmo.move_tilt(current_position[1]+10)
                        time.sleep(2)
                        elmo.move_tilt(current_position[1])
                    time.sleep(2)
                    flag = True
                
            except Exception as e:
                logger.error(f"Error in autonomous control loop: {e}")
                if shutdown_event.is_set():
                    break
            
            time.sleep(1)
        
        logger.info("Autonomous control stopping...")
        
    except Exception as e:
        logger.error(f"Fatal error in autonomous control: {e}")


@app.get("/action/{command}")
def action(command: str):
    global robot_position, flag
    print(f"Received command: {command}")
    flag = False
    if command == "s1":
        robot_position = [40, -7, None, None]
    elif command == "s2":
        robot_position = [0, -7, None, None]
    elif command == "s3":
        robot_position = [-40, -7, None, None]
    elif command == "backchanneling":
        robot_position = [None, None, None, None]
    elif command == "listening":
        robot_position = [None, None, None, "listening.png"]
    elif command == "speaking":
        robot_position = [None, None, None, "speaking.png"]
    elif command == "blush":
        robot_position = [None, None, "blush.png", None]
    elif command == "cry":
        robot_position = [None, None, "cry.png", None]
    elif command == "effort":
        robot_position = [None, None, "effort.png", None]
    elif command == "love":
        robot_position = [None, None, "love.png", None]
    elif command == "normal":
        robot_position = [None, None, "blink.gif", None]
    elif command == "sad":
        robot_position = [None, None, "sad.png", None]
    elif command == "star":
        robot_position = [None, None, "star.png", None]
    elif command == "thinking":
        robot_position = [None, None, "thinking.png", None]
    elif command == "idle":
        robot_position = [0, -7, "blink.gif", "black.png"]
    else:
        pass
    return {"status": "ok", "command": command}

@app.get("/stop")
def stop():
    shutdown_event.set()
    global api_server
    if api_server is not None:
        api_server.should_exit = True
    return {"status": "stopping"}

def run_rest_api(host="0.0.0.0", port=8000, log_level="warning"):
    global api_server
    config = Config(app=app, host=host, port=port, log_level=log_level, loop="asyncio")
    api_server = Server(config=config)
    # this call blocks until server.should_exit becomes True
    api_server.run()


def main():
    """Main function with graceful shutdown"""
    global elmo, elmo_ip, elmo_port, client_ip, robot_angles, speakers, shutdown_event

    # Parse command line arguments
    if len(sys.argv) != 4:
        print("Usage: python3 podcast.py <elmo_ip> <elmo_port> <my_ip>")
        return 1

    elmo_ip = sys.argv[1]
    try:
        elmo_port = int(sys.argv[2])
    except ValueError:
        print(f"Error: elmo_port must be an integer, got '{sys.argv[2]}'")
        return 1
    client_ip = sys.argv[3]

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Setup main logger
    logger = setup_logger("main")
    logger.info("=== Application Starting ===")
    logger.info(f"Elmo: {elmo_ip}:{elmo_port}")
    logger.info(f"Client: {client_ip}")

    try:
        # Get a list of all available devices
        devices = sd.query_devices()

        # Filter and list only input devices (microphones)
        input_devices = [device for device in devices if device["max_input_channels"] > 0]

        # Display the input devices
        print("\nAvailable Input Devices:")
        for idx, device in enumerate(input_devices):
            print(f"Device {idx}: {device['name']} -> {device['max_input_channels']}")

        device_name = "H6"
        input_device_index = find_input_device_index(device_name)
        if input_device_index is None:
            print(f"\nInput device '{device_name}' not found.")
            logger.error(f"Input device '{device_name}' not found.")
            return 1

        print(f"\nUsing input device: {device_name} (index: {input_device_index})")
        logger.info(f"Using input device: {device_name} (index: {input_device_index})")

        # Start voice-based control threads
        threads = []
        for speaker in range(4):
            t = threading.Thread(
                target=vb_control,
                args=(input_device_index, speaker),
                name=f"VB_Control_{speaker}"
            )
            t.start()
            threads.append(t)
            logger.info(f"Started voice control thread for speaker {speaker}")

        # Start autonomous control thread
        nvb_thread = threading.Thread(
            target=nvb_autonomous_control,
            args=(),
            name="NVB_Autonomous"
        )
        nvb_thread.start()
        threads.append(nvb_thread)
        logger.info("Started autonomous control thread")

        #Start interface thread
        rest_api_thread = threading.Thread(
            target=run_rest_api,
            args=(),
            name="interface"
        )
        rest_api_thread .start()
        threads.append(rest_api_thread)
        logger.info("Started interface control thread")

        print("\nAll threads started. Press Ctrl+C to stop.\n")

        # Wait for all threads to complete
        for t in threads:
            t.join()

        logger.info("=== All threads stopped cleanly ===")
        print("\nApplication shut down successfully.")
        return 0

    except KeyboardInterrupt:
        print("\nKeyboard interrupt in main...")
        shutdown_event.set()
        return 0
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        shutdown_event.set()
        return 1
    finally:
        # Ensure all threads are stopped
        if not shutdown_event.is_set():
            shutdown_event.set()
        
        # Give threads time to finish
        print("Waiting for threads to finish...")
        for t in threading.enumerate():
            if t != threading.current_thread() and t.is_alive():
                logger.info(f"Waiting for thread: {t.name}")
                t.join(timeout=5)
                if t.is_alive():
                    logger.warning(f"Thread {t.name} did not stop in time")
        
        logger.info("=== Application Terminated ===")

if __name__ == "__main__":
    sys.exit(main())