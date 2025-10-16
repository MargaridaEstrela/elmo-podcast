from elmo_server import ElmoServer
from emoshow_logger import EmoShowLogger
import os


elmo_ip = "192.168.0.109"
elmo_port = 4000
client_ip = "192.168.0.105"
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
elmo.set_image("wink.gif")