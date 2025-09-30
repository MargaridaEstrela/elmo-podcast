import os
import sys
import time
import cv2
import FreeSimpleGUI as sg

from elmo_server import ElmoServer
from emoshow_logger import EmoShowLogger

elmo = None
elmo_ip = None
logger = None
window = None
debug_mode = False
connect_mode = False

# Load the Haar Cascade model
face_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def create_layout():
    """
    Creates the layout for the Emo-Show game interface.

    Returns:
        list: The layout of the interface as a list of elements.
    """

    sg.theme("LightBlue3")

    settings_layout = [
        [sg.Text("", size=(1, 1))],
        [
            sg.Text("", size=(8, 1)),
            sg.Button("Toggle Behaviour", size=(15, 1), button_color=("white", "red")),
            sg.Button("Toggle Motors", size=(15, 1), button_color=("white", "green")),
            sg.Text("", size=(9, 1)),
            sg.Text("Speakers", size=(10, 1)),
            sg.Text("", size=(11, 1)),
        ],
        [
            sg.Text("", size=(8, 1)),
            sg.Text("Pan", size=(3, 1)),
            sg.InputText(key="pan_value", size=(18, 1)),
            sg.Button("Set", key="SetPan", size=(8, 1)),
            sg.Text("", size=(9, 1)),
            sg.Button("⬆", size=(5, 1)),
            sg.Text("", size=(15, 1)),
            sg.Button("Default Screen", size=(15, 1)),
        ],
        [
            sg.Text("", size=(8, 1)),
            sg.Text("Tilt", size=(3, 1)),
            sg.InputText(key="tilt_value", size=(18, 1)),
            sg.Button("Set", key="SetTilt", size=(8, 1)),
            sg.Text("", size=(9, 1)),
            sg.Button("⬇", size=(5, 1)),
            sg.Text("", size=(15, 1)),
            sg.Button("Default Icon", size=(15, 1)),
        ],
        [
            sg.Text("", size=(8, 1)),
            sg.Button("Toggle Blush", size=(15, 1), button_color=("white", "red")),
            sg.Button("Check Speakers", size=(15, 1)),
            sg.Text("", size=(35, 1)),
        ],
        [sg.Text("", size=(1, 2))],
        [
            sg.Text("", size=(9, 1)),
            sg.Button("Move Left", size=(22, 1)),
            sg.Text("", size=(5, 1)),
            sg.Button("Move Right", size=(22, 1)),
            sg.Text("", size=(5, 1)),
            sg.Button("Idle", size=(22, 1)),
            sg.Text("", size=(1, 1)),
        ],
        [sg.Text("", size=(1, 1))],
        [sg.Text("", size=(2, 1)), sg.Image(filename="", key="image")],
        [sg.Text("", size=(1, 1))],
    ]

    layout = [
        [
            sg.TabGroup(
                [[sg.Tab("Settings", settings_layout)]],
                key="-TAB GROUP-",
                expand_x=True,
                expand_y=True,
            ),
        ]
    ]

    return layout

def set_pan(value):
    elmo.move_pan(value)
    default_pan = int(value)
    elmo.set_default_pan_left(-default_pan)
    elmo.set_default_pan_right(default_pan)
    
def set_tilt(value):
    elmo.move_tilt(value)
    default_tilt = int(value)
    elmo.set_default_tilt_left(default_tilt)
    elmo.set_default_tilt_right(default_tilt)

def call_gemini():
    # Call Gemini API to get a response (TODO: implement)
    return

def center_player(self, side):
    """
    Centers the player's face in the frame by adjusting the robot's pan and
    tilt angles. If no faces detected, returns and continues the game.
    """
    frame = self.elmo.grab_image()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))

    if len(faces) == 0:
        print("Cannot center player. No faces detected.")
        return

    # Get frame center and dimensions
    frame_width, frame_height = frame.shape[1], frame.shape[0]
    frame_center_x = frame_width / 2
    frame_center_y = frame_height / 2

    # Extract face bounding box
    x, y, w, h = faces[0]
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Compute offsets
    face_center_x = x + w / 2
    face_center_y = y + h / 2
    horizontal_offset = face_center_x - frame_center_x
    vertical_offset = frame_center_y - face_center_y

    # Get current pan and tilt angles
    current_pan_angle = elmo.get_current_pan_angle()
    current_tilt_angle = elmo.get_current_tilt_angle()

    # Convert pixel offsets to angle corrections using camera FOV
    horizontal_adjustment = (horizontal_offset / frame_width) * 62.2  # Use 62.2° FOV for pan
    vertical_adjustment = (vertical_offset / frame_height) * 48.8  # Use 48.8° FOV for tilt

    # Apply angle corrections and update default values
    new_pan_angle = round(current_pan_angle - horizontal_adjustment)
    new_tilt_angle = round(current_tilt_angle - vertical_adjustment)

    # Check if values are within valid range
    new_pan_angle = elmo.check_pan_angle(new_pan_angle)
    new_tilt_angle = elmo.check_tilt_angle(new_tilt_angle)

    # Update default values
    if side == "left":
        elmo.set_default_pan_left(new_pan_angle)
        elmo.set_default_tilt_left(new_tilt_angle)
    else:
        elmo.set_default_pan_right(new_pan_angle)
        elmo.set_default_tilt_right(new_tilt_angle)

    elmo.move_pan(new_pan_angle)
    time.sleep(2)
    elmo.move_tilt(new_tilt_angle)



def handle_events():
    """
    Handle events from the GUI window.

    This function reads events from the GUI window and performs corresponding
    actions based on the event type.
    It updates the image displayed in the window, toggles Elmo's behavior and
    motors, sets the pan and tilt values, adjusts the volume, moves Elmo left or
    right, toggles feedback mode, starts or restarts the game, and handles
    window close event.
    """
    event, values = window.read(timeout=1)

    if not debug_mode and not connect_mode:
        img = elmo.grab_image()
        img_bytes = cv2.imencode(".png", img)[1].tobytes()
        window["image"].update(data=img_bytes)

    if event == "Ok":
        logger.set_filename(values["-FILENAME-"])

    if event == "Toggle Behaviour":
        elmo.toggle_behaviour()
        # Change the color of the button
        if elmo.get_control_behaviour():
            window["Toggle Behaviour"].update(button_color=("white", "green"))
        else:
            window["Toggle Behaviour"].update(button_color=("white", "red"))

    if event == "Toggle Motors":
        elmo.toggle_motors()
        # Change the color of the button
        if elmo.get_control_motors():
            window["Toggle Motors"].update(button_color=("white", "green"))
        else:
            window["Toggle Motors"].update(button_color=("white", "red"))

    if event == "SetPan":
        value = values["pan_value"]
        if value: set_pan(value)

    if event == "SetTilt":
        value = values["tilt_value"]
        if value: set_tilt(value)

    if event == "Toggle Blush":
        elmo.toggle_blush()
        # Change the color of the button
        if elmo.get_control_blush():
            window["Toggle Blush"].update(button_color=("white", "green"))
        else:
            window["Toggle Blush"].update(button_color=("white", "red"))

    if event == "Check Speakers":
        elmo.play_sound("picture.wav")

    if event == "⬆":
        elmo.increase_volume()

    if event == "⬇":
        elmo.decrease_volume()

    if event == "Default Screen":
        elmo.set_image("normal.png")

    if event == "Default Icon":
        elmo.set_icon("elmo_idm.png")

    if event == "Move Left":
        elmo.move_left()
        center_player("left")
        
        call_gemini()
        
    if event == "Move Right":
        elmo.move_right()
        center_player("right")
        
    if event == "Idle":
        elmo.set_image("idle.png") # TODO: change to idle image
        
    if (
        event == sg.WIN_CLOSED or event == "Close All"
    ):  # If user closes window or clicks cancel
        print("Closing all...")
        elmo.close_all()
        logger.close()
        window.close()


def main():
    """
    The main function of the Emo-Show game interface.

    This function parses command line arguments, initializes the logger, starts the server,
    creates the game window, and enters the event loop to handle user interactions.
    """
    global elmo, elmo_ip, window, emoshow, debug_mode, connect_mode, logger

    # Parse arguments
    if len(sys.argv) == 1:
        elmo_ip = ""
        elmo_port = 0
        client_ip = ""
        debug_mode = True  # Running in debug mode (just gui)

    elif len(sys.argv) == 4:
        elmo_ip, elmo_port, client_ip = sys.argv[1:4]
        debug_mode = False

    elif len(sys.argv) == 5:
        elmo_ip, elmo_port, client_ip = sys.argv[1:4]
        if sys.argv[4] == "--connect":
            connect_mode = True

    else:
        print("Usage: python3 emoshow_app.py <elmo_ip> <elmo_port> <my_ip>")
        return

    # Start logger
    log_path = "logs/elmo-app.log"

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Create the file only if it does not exist
    if not os.path.exists(log_path):
        with open(log_path, "w") as f:
            f.write("")  # optional: f.write("Log started\n")

    logger = EmoShowLogger(log_file=log_path)
    logger.set_window(window)

    # Start server
    elmo = ElmoServer(
        elmo_ip, int(elmo_port), client_ip, logger, debug_mode, connect_mode
    )

    layout = create_layout()

    # Create window
    title = "Elmo APP"
    if len(elmo_ip) > 0:
        title += "  " + "idmind@" + elmo_ip
    window = sg.Window(title, layout, finalize=True)

    if not debug_mode and not connect_mode:
        # Initial image update
        img = elmo.grab_image()
        img_bytes = cv2.imencode(".png", img)[1].tobytes()
        window["image"].update(data=img_bytes)

    # Event loop
    while True:
        handle_events()


if __name__ == "__main__":
    main()
