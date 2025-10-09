
import os
from elmo_server import ElmoServer
from emoshow_logger import EmoShowLogger
import time

debug_mode = False
connect_mode = False

robot_angles = {0: [None, None], 1: [-40, -10], 2: [0, -10], 3: [40, -10]}

# Start logger
log_path = "logs/elmo-app.log"
os.makedirs(os.path.dirname(log_path), exist_ok=True)

# Create the file only if it does not exist
if not os.path.exists(log_path):
    with open(log_path, "w") as f:
        f.write("")

elmo_logger = EmoShowLogger(log_file=log_path)
elmo_ip = "192.168.0.109"
elmo_port = 4000
client_ip = "192.168.0.105"

# Start server
elmo = ElmoServer(
    elmo_ip, int(elmo_port), client_ip, elmo_logger, debug_mode, connect_mode
)

print("Autonomous control initialized")

elmo.move_tilt(-7)
#elmo.set_forever_icon("fast_loading.gif")

