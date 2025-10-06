import os
import cv2
import sys
import time
import streamlit as st

from elmo_server import ElmoServer
from emoshow_logger import EmoShowLogger

# -------------------------------------------------------------
# INITIALIZATION
# -------------------------------------------------------------
st.set_page_config(page_title="Elmo Web App", layout="wide")

DEBUG_MODE = False
CONNECT_MODE = False

# Parse arguments
if len(sys.argv) == 1:
    ELMO_IP = ""
    ELMO_PORT = 0
    CLIENT_IP = ""
    DEBUG_MODE = True  # Running in debug mode (just interface)

elif len(sys.argv) == 4:
    ELMO_IP, ELMO_PORT, CLIENT_IP = sys.argv[1:4]
    DEBUG_MODE = False

elif len(sys.argv) == 5:
    ELMO_IP, ELMO_PORT, CLIENT_IP = sys.argv[1:4]
    if sys.argv[4] == "--connect":
        CONNECT_MODE = True

else:
    print("Usage: python3 emoshow_app.py <elmo_ip> <elmo_port> <my_ip>")
    sys.exit(1)


# Start logger
log_path = "logs/elmo-app.log"

os.makedirs(os.path.dirname(log_path), exist_ok=True)

logger = EmoShowLogger("logs/elmo-app.log")
elmo = ElmoServer(ELMO_IP, int(ELMO_PORT), CLIENT_IP, logger, DEBUG_MODE, CONNECT_MODE)

face_classifier = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# -------------------------------------------------------------
# FUNCTIONS
# -------------------------------------------------------------
def center_player(side):
    """Centers the player's face in the frame using Haar cascade."""
    frame = elmo.grab_image()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
    if len(faces) == 0:
        st.warning("No faces detected.")
        return frame

    (x, y, w, h) = faces[0]
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    frame_w, frame_h = frame.shape[1], frame.shape[0]
    dx = (x + w / 2) - (frame_w / 2)
    dy = (frame_h / 2) - (y + h / 2)

    pan_adj = (dx / frame_w) * 62.2
    tilt_adj = (dy / frame_h) * 48.8

    pan = round(elmo.get_current_pan_angle() - pan_adj)
    tilt = round(elmo.get_current_tilt_angle() - tilt_adj)
    pan = elmo.check_pan_angle(pan)
    tilt = elmo.check_tilt_angle(tilt)

    if side == "left":
        elmo.set_default_pan_left(pan)
        elmo.set_default_tilt_left(tilt)
    else:
        elmo.set_default_pan_right(pan)
        elmo.set_default_tilt_right(tilt)

    elmo.move_pan(pan)
    time.sleep(1)
    elmo.move_tilt(tilt)
    return frame

def led_html(is_on: bool):
    """Return HTML for a glowing LED circle."""
    color = "#00ff22" if is_on else "#ff3333"
    shadow = "0 0 10px #00ff22" if is_on else "0 0 10px #ff3333"
    return f"""
    <div style="
        display:inline-block;
        width:18px; height:18px;
        border-radius:50%;
        background-color:{color};
        box-shadow:{shadow};
        margin-right:10px;
        margin-top:10px;
        vertical-align:middle;">
    </div>
    """

def toggle_with_led(label, key, state, on_click):
    """LED appears before the button."""
    col1, col2 = st.columns([0.15, 2])
    with col1:
        st.markdown(led_html(state), unsafe_allow_html=True)
    with col2:
        if st.button(label, key=key):
            on_click()
            st.rerun()

# -------------------------------------------------------------
# INITIALIZE TOGGLE STATES
# -------------------------------------------------------------
if "behaviour_on" not in st.session_state:
    try:
        st.session_state.behaviour_on = elmo.get_control_behaviour()
    except Exception:
        st.session_state.behaviour_on = False

if "motors_on" not in st.session_state:
    try:
        st.session_state.motors_on = elmo.get_control_motors()
    except Exception:
        st.session_state.motors_on = True  # motors usually start ON

if "blush_on" not in st.session_state:
    try:
        st.session_state.blush_on = elmo.get_control_blush()
    except Exception:
        st.session_state.blush_on = False
        

# -------------------------------------------------------------
# STREAMLIT LAYOUT
# -------------------------------------------------------------
st.title("🤖 Elmo")

# Centered main layout
left_spacer, main_col, right_spacer = st.columns([0.5, 3, 0.5])

with main_col:
    tab1, tab2 = st.tabs(["Settings", "Modes"])

    # =========================================================
    # TAB 1: SETTINGS
    # =========================================================
    with tab1:

        # ---------- TOGGLE BUTTONS ----------
        colA, colB, colC = st.columns([1, 1, 1])

        # --- Define toggle callbacks ---
        def toggle_motors():
            st.session_state.motors_on = not st.session_state.motors_on
            elmo.toggle_motors()

        def toggle_behaviour():
            st.session_state.behaviour_on = not st.session_state.behaviour_on
            elmo.toggle_behaviour()

        def toggle_blush():
            st.session_state.blush_on = not st.session_state.blush_on
            elmo.toggle_blush()

        # --- Column A: Toggles with LEDs ---
        with colA:
            st.markdown("<div style='margin-left: 40px;'>", unsafe_allow_html=True)
            toggle_with_led("Toggle Motors", "motors_button", st.session_state.motors_on, toggle_motors)
            toggle_with_led("Toggle Behaviour", "behaviour_button", st.session_state.behaviour_on, toggle_behaviour)
            toggle_with_led("Toggle Blush", "blush_button", st.session_state.blush_on, toggle_blush)
            st.markdown("</div>", unsafe_allow_html=True)

        # --- Column B: Audio controls ---
        with colB:
            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            st.button("⬆ Volume Up")
            st.button("⬇ Volume Down")
            st.button("🔊 Check Speakers")
            st.markdown("</div>", unsafe_allow_html=True)

        # --- Column C: Display controls ---
        with colC:
            st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
            st.button("Default Screen")
            st.button("Default Icon")
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        # =========================================================
        # PAN / TILT CONTROLS
        # =========================================================
        st.markdown("### Pan / Tilt Controls")

        col1, col2 = st.columns(2)
        pan = col1.number_input("Pan", -40, 40, 0)
        if col1.button("Set Pan"):
            elmo.move_pan(pan)
            elmo.set_default_pan_left(-pan)
            elmo.set_default_pan_right(pan)

        tilt = col2.number_input("Tilt", -15, 15, 0)
        if col2.button("Set Tilt"):
            elmo.move_tilt(tilt)
            elmo.set_default_tilt_left(tilt)
            elmo.set_default_tilt_right(tilt)

        st.divider()

        # =========================================================
        # MOVEMENT + CAMERA
        # =========================================================
        st.markdown("### Movement & Camera")

        col6, col7 = st.columns(2)
        if col6.button("⬅️ Turn Left"):
            elmo.move_left()
            frame = center_player("left")
        elif col7.button("➡️ Turn Right"):
            elmo.move_right()
            frame = center_player("right")

        # --- Live Camera Feed ---
        frame_placeholder = st.empty()
        run = st.checkbox("🔴 Live camera", value=True)

        while run:
            img = elmo.grab_image()
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(img_rgb, channels="RGB", use_container_width=True)
            time.sleep(0.1)
            run = st.session_state.get("🔴 Live camera", True)

        st.success("✅ Stream stopped")

    # =========================================================
    # TAB 2: DISPLAY
    # =========================================================
    with tab2:
        st.markdown("### Display")
        
        colA, colB, colC, colD = st.columns(4)

        with colA:
            if st.button("Normal"):
                elmo.set_image("normal.png")
                
        with colB:
            if st.button("Surprise"):
                elmo.set_image("surprise.png")
                
        st.divider()
        
        st.markdown("### Icons")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("None"):
                elmo.set_icon("black.png")
        
        with col2:
            if st.button("IDMind Icon"):
                elmo.set_icon("elmo_idm.png")