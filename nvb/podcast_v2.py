import sys
import time
import sounddevice as sd
import logging
import threading
import signal
import os
import numpy as np
import torch
import queue
from elmo_server import ElmoServer
from emoshow_logger import EmoShowLogger
from collections import Counter
from fastapi import FastAPI
from uvicorn import Config, Server


class LockedValue:
    def __init__(self, value=None):
        self._value = value
        self._lock = threading.Lock()

    def get(self, n=None):
        with self._lock:
            if n is None:
                import copy
                return copy.deepcopy(self._value)
            val = self._value[n]
            return val.copy() if isinstance(val, list) else val
    
    def set(self, n, value):
        with self._lock:
            self._value[n] = value.copy() if isinstance(value, list) else value

    def setAll(self, value):
        with self._lock:
            import copy
            self._value = copy.deepcopy(value)


# Audio parameters
SAMPLE_RATE = 16000
CHUNK = 512
PODCAST_ID = 0

# VAD threshold (0-1, higher = more strict)
VAD_THRESHOLD = 0.05

# Global variables
global elmo_ip, elmo_port, client_ip, robot_angles, rest_api_input, api_server
elmo_ip = None
elmo_port = None
client_ip = None

shutdown_event = threading.Event()
loudness_levels = LockedValue([0.0, 0.0, 0.0, 0.0])
speech_detected = LockedValue([False, False, False, False])
speech_probability = LockedValue([0.0, 0.0, 0.0, 0.0])
robot_angles = LockedValue({0: [-35, -3], 1: [-35, -3], 2: [None, None], 3: [35, -3]})

# Robot command queue
robot_command_queue = queue.Queue()

flag = LockedValue(True)
delay_mode = LockedValue(False)
rest_api_input = LockedValue([None, None, None, None, None, None])
api_server = None
app = FastAPI()

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutdown signal received...")
    shutdown_event.set()


def setup_logger(process_name):
    directory = str(PODCAST_ID)
    log_dir = os.path.join("logs", directory)
    log_file = os.path.join(log_dir, process_name + ".log")
    
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(process_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def select_device():
    """Let user choose between Zoom H6 and L-8"""
    devices = sd.query_devices()
    input_devices = [d for d in devices if d["max_input_channels"] > 0]
    
    print("\n" + "="*60)
    print("Available Input Devices:")
    print("="*60)
    
    zoom_devices = []
    for idx, device in enumerate(input_devices):
        device_name = device['name']
        channels = device['max_input_channels']
        print(f"Device {idx}: {device_name} -> {channels} channels")
        
        if "h6" in device_name.lower():
            device_type = "H6"
            zoom_devices.append((idx, device_name, device_type, channels))
        if "zoom" in device_name.lower():
            device_type = "L8"
            zoom_devices.append((idx, device_name, device_type, channels))
    
    if not zoom_devices:
        print("\nNo Zoom devices found!")
        return None, None, None
    
    print("\n" + "="*60)
    print("Zoom Devices Found:")
    print("="*60)
    for i, (idx, name, dtype, channels) in enumerate(zoom_devices):
        print(f"{i}: {name} ({dtype}) - {channels} channels (device index: {idx})")
    
    if len(zoom_devices) == 1:
        choice = 0
        print(f"\nOnly one Zoom device found, auto-selecting: {zoom_devices[0][1]}")
    else:
        while True:
            try:
                choice = int(input(f"\nSelect device (0-{len(zoom_devices)-1}): "))
                if 0 <= choice < len(zoom_devices):
                    break
                print("Invalid choice, please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    device_index, device_name, device_type, num_channels = zoom_devices[choice]
    print(f"\nSelected: {device_name} ({device_type})\n")
    return device_index, device_type, num_channels


def detect_speech_vad(audio_chunk, vad_model):
    """Detect if audio contains speech using Silero VAD"""
    try:
        audio_tensor = torch.tensor(audio_chunk, dtype=torch.float32)
        
        # Normalize audio
        max_val = torch.max(torch.abs(audio_tensor))
        if max_val > 0:
            audio_tensor = audio_tensor / max_val
        
        audio_tensor = audio_tensor.unsqueeze(0)
        
        # Get speech probability (0-1)
        speech_prob = vad_model(audio_tensor, SAMPLE_RATE).item()
        return speech_prob
    except Exception as e:
        return 0.0


def audio_callback(indata, frames, time_info, status, vad_model, channel_offset=2):
    """Callback to calculate loudness and detect speech for each speaker"""
    if status:
        print(f"Audio error: {status}")
    
    levels = []
    detections = []
    probabilities = []
    
    # Process each of 4 speakers
    for speaker in range(4):
        ch = channel_offset + speaker
        if ch < indata.shape[1]:
            audio = indata[:, ch]
            
            # Calculate loudness
            rms = np.sqrt(np.mean(audio ** 2))
            if rms > 0:
                db = 20 * np.log10(rms)
            else:
                db = -100
            levels.append(db)
            
            # Detect speech using VAD
            speech_prob = detect_speech_vad(audio, vad_model)
            probabilities.append(speech_prob)
            detections.append(speech_prob > VAD_THRESHOLD)
        else:
            levels.append(-100)
            probabilities.append(0.0)
            detections.append(False)
    
    loudness_levels.setAll(levels)
    speech_detected.setAll(detections)
    speech_probability.setAll(probabilities)


def robot_command_executor(elmo, logger):
    """Execute robot commands from the queue with delays"""
    while not shutdown_event.is_set():
        try:
            # Get command from queue (timeout to check shutdown_event)
            command_data = robot_command_queue.get(timeout=0.5)
            #
            command_type = command_data.get('type')
            delay_after = command_data.get('delay_after', 0)
            
            if command_type == 'set_icon':
                icon = command_data.get('icon')
                elmo.set_icon(icon)
                logger.info(f"Set icon: {icon}")
                print(f"Set icon: {icon}")
            
            elif command_type == 'move_pan':
                angle = command_data.get('angle')
                elmo.move_pan(angle)
                logger.info(f"Move pan: {angle}")
                print(f"Move pan: {angle}")
            
            elif command_type == 'move_tilt':
                angle = command_data.get('angle')
                
                elmo.move_tilt(angle)
                logger.info(f"Move tilt: {angle}")
                print(f"Move tilt: {angle}")
            
            elif command_type == 'toggle_behaviour':
                elmo.toggle_behaviour()
                logger.info(f"Toggle behaviour")
                print(f"Toggle behaviour")
            
            elif command_type == 'set_image':
                image = command_data.get('image')
                elmo.set_image(image)
                logger.info(f"Set image: {image}")
                print(f"Set image: {image}")    
                if image == "wink-2.gif":
                    time.sleep(2)
                    elmo.set_image("blink.gif")
                
            elif command_type == 'toggle_motors':
                elmo.toggle_motors()
                logger.info(f"Toggle motors")
                print(f"Toggle motors")
            
            if delay_after > 0:
                time.sleep(delay_after)
                    
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"Error executing robot command: {e}")


def add_robot_command(command_type, delay_after=2, **kwargs):
    """Add a command to the robot queue
    
    Args:
        command_type: Type of command ('set_icon', 'move_pan', 'move_tilt', 'toggle_behaviour', 'set_image')
        delay_after: Delay in seconds AFTER executing this command before processing the next one
        **kwargs: Additional arguments specific to the command
    """
    command_data = {
        'type': command_type,
        'delay_after': delay_after,
        **kwargs
    }
    robot_command_queue.put(command_data)

def delay_mode_loop(elmo, logger):
    """Loop that sets delay.gif every 2 seconds while delay_mode is active"""
    global delay_mode
    while not shutdown_event.is_set():
        if delay_mode.get():
            try:
                elmo.set_icon("loading.gif")
                logger.info("Delay mode: setting loading.gif")
                print("Delay mode: setting loading.gif")
                time.sleep(1.8)
            except Exception as e:
                logger.error(f"Error in delay mode loop: {e}")
                time.sleep(0.5)
        else:
            time.sleep(0.5)

def nvb_autonomous_control(elmo):
    global elmo_ip, elmo_port, client_ip, robot_angles, flag, rest_api_input, delay_mode
    logger = setup_logger(f"nvd_autonomous")
    
    logger.info("Autonomous control initialized")
    print("Autonomous control initialized")

    # Initialize robot

    time.sleep(5)

    loudest_speaker = -1
    robot_speaking = False
    previous = -1
    current_speaker_start_time = None
    do_nothing = False
    tiny_memory = []
    last_backchannel_time = 0
    backchannel_interval = 7  # seconds between backchannels
    

    try:
        while not shutdown_event.is_set():

            if delay_mode.get():
                time.sleep(0.5)
                continue

            if flag.get():
                levels = loudness_levels.get()
                detections = speech_detected.get()
                probabilities = speech_probability.get()
                
                # Find loudest speaker among those speaking
                speaking_speakers = [i for i in range(4) if detections[i]]
                
                if speaking_speakers:
                    loudest_speaker = max(speaking_speakers, key=lambda i: levels[i])
                else:
                    loudest_speaker = -1

                tiny_memory = (tiny_memory[-7:] if len(tiny_memory) >= 7 else tiny_memory) + [loudest_speaker]
                #print(f"Memory: {tiny_memory}, Current: {loudest_speaker}, Time talking: {current_speaker_start_time}")
                
                loudest_speaker = Counter(tiny_memory).most_common(1)[0][0]
                print(Counter(tiny_memory).most_common(1))
                #print(loudest_speaker)

                # Robot is speaking (speaker 2)
                if loudest_speaker == 2:
                    if not robot_speaking:
                        do_nothing = False
                        add_robot_command('set_icon', delay_after=2, icon='speaking.png')
                        logger.info(f"Robot start talking")
                        print(f"Robot start talking")
                        robot_speaking = True
                        current_speaker_start_time = None
                
                # Someone else is speaking (not robot, not silence)
                elif loudest_speaker != -1 and loudest_speaker != 2:
                    robot_speaking = False
                    do_nothing = False
                    
                    # NEW SPEAKER DETECTED
                    if loudest_speaker != previous or current_speaker_start_time is None:
                        current_speaker_start_time = time.time()
                        add_robot_command('set_icon', delay_after=2, icon='listening.png')
                        logger.info(f"Start Talking: {loudest_speaker}")
                        print(f"Start Talking: {loudest_speaker}")
                        add_robot_command('move_pan', delay_after=2, angle=robot_angles.get(loudest_speaker)[0])
                        add_robot_command('move_tilt', delay_after=2, angle=robot_angles.get(loudest_speaker)[1])
                        logger.info(f"Move to: {robot_angles.get(loudest_speaker)}")
                        #print(f"Move to: {robot_angles.get(loudest_speaker)}")
                        last_backchannel_time = time.time()
                    
                    # SAME SPEAKER TALKING - Check for backchannel after 7 seconds
                    elif current_speaker_start_time is not None:
                        time_talking = time.time() - current_speaker_start_time
                        time_since_last_backchannel = time.time() - last_backchannel_time
                        
                        if time_talking >= 5 and time_since_last_backchannel >= backchannel_interval:
                            add_robot_command('toggle_behaviour', delay_after=4)
                            add_robot_command('toggle_behaviour', delay_after=1)
                            logger.info(f"Backchanneling to: {robot_angles.get(loudest_speaker)}")
                            #print(f"Backchanneling to speaker {loudest_speaker} after {time_talking:.1f}s")
                            last_backchannel_time = time.time()
                
                # SILENCE
                if loudest_speaker == -1 and previous == -1:
                    robot_speaking = False
                    if not do_nothing:
                        robot_speaking = False
                        add_robot_command('set_icon', delay_after=2, icon='black.png')
                        do_nothing = True
                        logger.info(f"No one talking")
                        current_speaker_start_time = None
                    
                previous = loudest_speaker
                time.sleep(0.2)

            if not flag.get():
                flag.setAll(True)
                print(rest_api_input.get(0))
                if rest_api_input.get(4) == True:
                    add_robot_command('toggle_motors', delay_after=2)
                    logger.info(f"Toggle Motors")

                if rest_api_input.get(5) == True:
                    add_robot_command('toggle_behaviour', delay_after=2)
                    logger.info(f"Toggle Behaviour")

                if rest_api_input.get(0) != None:
                    add_robot_command('move_pan', delay_after=2, angle=rest_api_input.get(0))
                    logger.info(f"Move pan to: {rest_api_input.get(0)}")

                if rest_api_input.get(1) != None:
                    add_robot_command('move_tilt', delay_after=2, angle=rest_api_input.get(1))
                    logger.info(f"Move tilt to: {rest_api_input.get(1)}")

                if rest_api_input.get(2) != None:
                    add_robot_command('set_image', delay_after=2, image=rest_api_input.get(2))
                    logger.info(f"Set image to: {rest_api_input.get(2)}")

                if rest_api_input.get(3) != None:
                    add_robot_command('set_icon', delay_after=2, icon=rest_api_input.get(3))
                    logger.info(f"Set icon to: {rest_api_input.get(3)}")

                if rest_api_input.get() == [None, None, None, None, None, None]:
                    add_robot_command('toggle_behaviour', delay_after=4)
                    add_robot_command('toggle_behaviour', delay_after=2)  
                    logger.info(f"Backchanneling")
                   

    except KeyboardInterrupt:
        pass



@app.get("/action/{command}/{args}")
def action(command: str, args:str):
    global rest_api_input, flag, robot_angles, delay_mode
    print(f"Received command: {command} / {args}")

    if command == "delay":
        current_delay_state = delay_mode.get()
        delay_mode.setAll(not current_delay_state)
        flag.setAll(False)
        if not current_delay_state:
            print("Delay mode ACTIVATED")
            return {"status": "ok", "command": "delay", "state": "activated"}
        else:
            print("Delay mode DEACTIVATED")
            flag.setAll(True)
            return {"status": "ok", "command": "delay", "state": "deactivated"}
    

    flag.setAll(False)
    if command == "s1":
        rest_api_input.setAll([robot_angles.get(0)[0], robot_angles.get(0)[1], None, None, None, None])
    elif command == "s2":
        rest_api_input.setAll([robot_angles.get(1)[0], robot_angles.get(1)[1], None, None, None, None])
    elif command == "s3":
        rest_api_input.setAll([robot_angles.get(3)[0], robot_angles.get(3)[1], None, None, None, None])
    elif command == "backchanneling":
        rest_api_input.setAll([None, None, None, None, None, None])
    elif command == "listening":
        rest_api_input.setAll([None, None, None, "listening.png", None, None])
    elif command == "speaking":
        rest_api_input.setAll([None, None, None, "speaking.png", None, None])
    elif command == "cry":
        rest_api_input.setAll([None, None, "cry.png", None, None, None])
    elif command == "effort":
        rest_api_input.setAll([None, None, "effort.png", None, None, None])
    elif command == "normal":
        rest_api_input.setAll([None, None, "blink.gif", None, None, None])
    elif command == "sad":
        rest_api_input.setAll([None, None, "sad.png", None, None, None])
    elif command == "wink":
        rest_api_input.setAll([None, None, "wink-2.gif", None, None, None])
    elif command == "idle":
        rest_api_input.setAll([0, -7, "blink.gif", "black.png", None, None])
    elif command == "sets1":
        robot_angles.set(1, [int(args.split(",")[0]), int(args.split(",")[1])])
        rest_api_input.setAll([robot_angles.get(0)[0], robot_angles.get(0)[1], None, None, None, None])
    elif command == "sets2":
        robot_angles.set(2, [int(args.split(",")[0]), int(args.split(",")[1])])
        rest_api_input.setAll([robot_angles.get(1)[0], robot_angles.get(1)[1], None, None, None, None])
    elif command == "sets3":
        robot_angles.set(3, [int(args.split(",")[0]), int(args.split(",")[1])])
        rest_api_input.setAll([robot_angles.get(3)[0], robot_angles.get(3)[1], None, None, None, None])
    elif command == "toggle_motors":
        rest_api_input.setAll([None, None, None, None, True, None])
    elif command == "toggle_behaviour":
        rest_api_input.setAll([None, None, None, None, None, True])
    elif command == "front":
        rest_api_input.setAll([0, -3, None, None, None, None])
    else:
        pass
    return {"status": "ok", "command": command, "args": args}

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
    global elmo_ip, elmo_port, client_ip

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

    logger = setup_logger("main")
    logger.info("=== Application Starting ===")

    signal.signal(signal.SIGINT, signal_handler)

    try:
        print("Loading VAD model...")
        vad_model, _ = torch.hub.load("snakers4/silero-vad", "silero_vad")
        print("VAD model loaded!\n")
        logger.info("VAD model loaded")
        
        # Display available devices
        devices = sd.query_devices()
        input_devices = [device for device in devices if device["max_input_channels"] > 0]

        print("Available Input Devices:")
        for idx, device in enumerate(input_devices):
            print(f"Device {idx}: {device['name']} -> {device['max_input_channels']}")

        # Select device (H6 or L8)
        input_device_index, device_type, num_total_channels = select_device()
        
        if input_device_index is None:
            print("No device selected.")
            logger.error("No device selected.")
            return 1

        print(f"Using: {device_type} (index: {input_device_index}, channels: {num_total_channels})")
        logger.info(f"Using: {device_type} (index: {input_device_index}, channels: {num_total_channels})")
        print("Monitoring speech activity... Press Ctrl+C to stop.\n")

        # Initialize Elmo server
        debug_mode = False
        connect_mode = False
        log_path = "logs/elmo-app.log"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        if not os.path.exists(log_path):
            with open(log_path, "w") as f:
                f.write("")
        
        elmo_logger = EmoShowLogger(log_file=log_path)
        elmo = ElmoServer(
            elmo_ip, int(elmo_port), client_ip, elmo_logger, debug_mode, connect_mode
        )

        elmo.set_image("blink.gif")
        elmo.move_tilt(-3)
        time.sleep(2)

        # Start robot command executor thread
        executor_thread = threading.Thread(target=robot_command_executor, args=(elmo, logger), daemon=True)
        executor_thread.start()

        delay_thread = threading.Thread(target=delay_mode_loop, args=(elmo, logger), daemon=True)
        delay_thread.start()
        logger.info("Started delay mode loop thread")

        # Start autonomous control thread
        control_thread = threading.Thread(target=nvb_autonomous_control, args=(elmo,), daemon=True)
        control_thread.start()

        #Start interface thread
        rest_api_thread = threading.Thread(target=run_rest_api, args=(), daemon=True)
        rest_api_thread.start()
        logger.info("Started interface control thread")

        # Start audio stream
        with sd.InputStream(
            device=input_device_index,
            samplerate=SAMPLE_RATE,
            channels=num_total_channels,
            blocksize=CHUNK,
            callback=lambda indata, frames, time_info, status: audio_callback(indata, frames, time_info, status, vad_model, channel_offset=2)
        ):
            while not shutdown_event.is_set():
                time.sleep(0.1)

        print("\n\nApplication shut down successfully.")
        logger.info("=== Application Terminated ===")
        return 0

    except KeyboardInterrupt:
        print("\nShutting down...")
        shutdown_event.set()
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        shutdown_event.set()
        return 1


if __name__ == "__main__":
    sys.exit(main())