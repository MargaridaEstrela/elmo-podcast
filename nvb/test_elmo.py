from elmo_server import ElmoServer
from emoshow_logger import EmoShowLogger
import os
import time
import math

elmo_ip = "192.168.0.109"
elmo_port = 4000
client_ip = "192.168.0.101"


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

#elmo.toggle_motors()

elmo.set_image("blink.gif")
time.sleep(2)






    
elmo.move_tilt(-1)

time.sleep(5)
print(elmo.get_current_tilt_angle())

#elmo.toggle_behaviour()

"""while True:
    print(elmo.get_current_pan_angle())
    print(elmo.get_current_tilt_angle())
    time.sleep(5)"""