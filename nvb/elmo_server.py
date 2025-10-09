import socket
import cv2
import numpy as np
import requests


class ElmoServer:
    """
    Represents the server for controlling Elmo.

    Args:
        elmo_ip (str): The IP address of the Elmo device.
        elmo_port (int): The port number for communication with the Elmo device.
        client_ip (str): The IP address of the client.
        logger (Logger): An instance of the logger for logging messages.
        debug (bool, optional): Specifies whether debug mode is enabled.
                                Defaults to False.
        connect_mode (bool, optional): Specifies whether the server is in
                                    connect mode. Defaults to False.

    Methods:
        set_pan(int): Sets the pan angle
        set_tilt(int): Sets the tilt angle
        set_default_pan_left(default_pan): Set the default left pan angle
        set_default_pan_right(default_pan): Set the default right pan angle
        set_default_tilt_left(default_tilt): Set the default left tilt angle
        set_default_tilt_right(default_tilt): Set the default right tilt angle
        get_default_pan_left(): Get the default left pan angle
        get_default_pan_right(): Get the default right pan angle
        get_default_tilt_left(): Get the default left tilt angle
        get_default_tilt_right(): Get the default right tilt angle
        get_current_tilt_angle(): Get the current tilt angle
        get_current_pan_angle(): Get the current pan angle
        get_control_motors(): Get the status of the motor control
        get_control_behaviour(): Get the status of the behaviour control
        get_control_blush(): Get the status of the behaviour blush
        connect_elmo(): Connect to the Elmo robot
        send_message(message): Send a message to the Elmo robot
        send_request_command(command, **kwargs): Send a request command to the
                                                Elmo robot
        toggle_motors(): Toggle the motor control
        toggle_behaviour(): Toggle the behaviour control
        toggle_blush(): Toggle the blush control
        check_pan_angle(self, angle): Check if the pan angle is valid
        check_tilt_angle(self, angle): Check if the tilt angle is valid
        move_pan(angle): Pan move with a specific angle
        move_tilt(angle): Tilt move with a specific angle
        move_left(): Move to the left
        move_right(): Move to the right
        set_volume(volume): Set the volume
        increase_volume(): Send message to increase the volume
        decrease_volume(): Send message to decrease the volume
        grab_image(): Capture an image
        set_image(image_name): Set the image
        set_icon(icon_name): Set the icon
        play_sound(sound): Play a sound
        close_all(): Close all connections

    """

    def __init__(
        self, elmo_ip, elmo_port, client_ip, logger, debug=False, connect_mode=False
    ):
        self.elmo_ip = elmo_ip
        self.elmo_port = elmo_port
        self.client_ip = client_ip
        self.elmo_socket = None

        self.connect_mode = connect_mode
        self.logger = logger

        self.default_pan_left = 0
        self.default_pan_right = 0
        self.default_tilt_left = 0
        self.default_tilt_right = 0
        
        self.current_pan = 0
        self.current_tilt = 0

        self.send_request_command("enable_behaviour", name="look_around", control=False)
        self.send_request_command("enable_behaviour", name="blush", control=False)
        self.send_request_command("set_tilt_torque", control=True)
        self.send_request_command("set_pan_torque", control=True)

        self.control_motors = True
        self.control_behaviour = False
        self.control_blush = False

        if not debug:
            self.connect_elmo()
            self.debug = False
        else:
            # print("Debug mode has been activated")
            self.debug = True

        self.set_image("normal.png")
        self.set_icon("black.png")
        self.move_pan(0)
        self.move_tilt(0)

    def set_default_pan_left(self, pan_angle):
        """
        Sets the default pan angle for left player.

        Args:
            default_pan (int): The default pan angle.
        """
        self.default_pan_left = pan_angle

    def set_default_pan_right(self, pan_angle):
        """
        Sets the default pan angle for right player.

        Args:
            default_pan (int): The default pan angle.
        """
        self.default_pan_right = pan_angle

    def set_default_tilt_left(self, tilt_angle):
        """
        Sets the default tilt angle for left player.

        Args:
            default_tilt (int): The default tilt angle.
        """
        self.default_tilt_left = tilt_angle

    def set_default_tilt_right(self, tilt_angle):
        """
        Sets the default tilt angle for right player.

        Args:
            default_tilt (int): The default tilt angle.
        """
        self.default_tilt_right = tilt_angle

    def get_default_pan_left(self):
        """
        Returns the default pan angle of the left player.

        Returns:
            int: The default pan angle of the left player.
        """
        return self.default_pan_left

    def get_default_pan_right(self):
        """
        Returns the default pan angle of the right player.

        Returns:
            int: The default pan angle of the right player.
        """
        return self.default_pan_right

    def get_default_tilt_left(self):
        """
        Returns the default tilt angle of the left player.

        Returns:
            int: The default tilt angle of the left player.
        """
        return self.default_tilt_left

    def get_default_tilt_right(self):
        """
        Returns the default tilt angle of the right player.

        Returns:
            int: The default tilt angle of the right player.
        """
        return self.default_tilt_right

    def get_control_motors(self):
        """
        Returns the control motors object.

        Returns:
            bool: The control motors object.
        """
        return self.control_motors

    def get_control_behaviour(self):
        """
        Returns the control behaviour object.

        Returns:
            bool: The control behaviour object.
        """
        return self.control_behaviour

    def get_control_blush(self):
        """
        Returns the control blush object.

        Returns:
            bool: The control blush object.
        """
        return self.control_blush
    
    def get_current_tilt_angle(self):
        """
        Returns the current tilt angle.

        Returns:
            int: The current tilt angle.
        """
        return self.current_tilt
    
    def get_current_pan_angle(self):
        """
        Returns the current pan angle.

        Returns:
            int: The current pan angle.
        """
        return self.current_pan

    def connect_elmo(self):
        """
        Connects to the Elmo robot.
        """
        self.elmo_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # print("Socket created!")

    def send_message(self, message):
        """
        Sends a message to the Elmo robot.

        Args:
            message (str): The message to be sent.
        """
        self.logger.log_message(message)

        if self.debug == True:
            return "debug"

        self.elmo_socket.sendto(message.encode("utf-8"), (self.elmo_ip, self.elmo_port))

    def send_request_command(self, command, **kwargs):
        """
        Sends a request command to the Elmo robot.

        Args:
            command (str): The command to be sent.
            **kwargs: Additional keyword arguments for the command.
        """
        if not self.connect_mode:
            try:
                url = "http://" + self.elmo_ip + ":8001/command"
                kwargs["op"] = command
                # print(kwargs)
                res = requests.post(url, json=kwargs, timeout=1).json()
                if not res["success"]:
                    return
            except Exception as e:
                return

    def toggle_motors(self):
        """
        Toggles the control of the motors and send a message and request command.
        """
        self.control_motors = not self.control_motors
        self.send_message(f"motors::{self.control_motors}")
        self.send_request_command("set_tilt_torque", control=self.control_motors)
        self.send_request_command("set_pan_torque", control=self.control_motors)

    def toggle_behaviour(self):
        """
        Toggles the control behaviour and send a message and request command.
        """
        self.control_behaviour = not self.control_behaviour
        self.send_message(f"behaviour::{self.control_behaviour}")
        self.send_request_command(
            "enable_behaviour", name="look_around", control=self.control_behaviour
        )

    def toggle_blush(self):
        """
        Toggles the control blush and send a message and request command.
        """
        self.control_blush = not self.control_blush
        self.send_message(f"blush::{self.control_blush}")
        self.send_request_command(
            "enable_behaviour", name="blush", control=self.control_blush
        )

    def check_pan_angle(self, angle):
        """
        Checks if the pan angle is valid. If it is not valid then returns a
        valid angle.

        Returns:
            int: The angle
        """
        if angle > 40:
            angle = 40
        elif angle < -40:
            angle = -40
        return angle

    def check_tilt_angle(self, angle):
        """
        Checks if the tilt angle is valid. If it is not valid then returns a
        valid angle.

        Returns:
            int: The angle
        """
        if angle > 15:
            angle = 15
        elif angle < -15:
            angle = -15
        return angle

    def move_pan(self, angle):
        """
        Moves the pan with a specific angle.

        Args:
            angle (int): The angle to move the pan.
        """
        self.current_pan = angle
        self.send_message(f"pan::{angle}")

    def move_tilt(self, angle):
        """
        Moves the tilt with a specific angle.

        Args:
            angle (int): The angle to move the tilt.
        """
        self.current_tilt = angle
        self.send_message(f"tilt::{angle}")

    def move_left(self):
        """
        Moves the device to the left with a symmetrical default pan angle.

        This method adjusts the pan value to move the device to the left.
        The tilt value remains unchanged.
        """
        self.current_pan = self.default_pan_left
        self.current_tilt = self.default_tilt_left
        
        self.send_message(f"pan::{self.default_pan_left}")
        self.send_message(f"tilt::{self.default_tilt_left}")

    def move_right(self):
        """
        Moves the device to the right with a default pan angle.

        This method adjusts the pan value to move the device to the right.
        The tilt value remains unchanged.
        """
        self.current_pan = self.default_pan_right
        self.current_tilt = self.default_tilt_right
        
        self.send_message(f"pan::{self.default_pan_right}")
        self.send_message(f"tilt::{self.default_tilt_right}")

    def increase_volume(self):
        """
        Sends a message to increase the volume.
        """
        self.send_message("speakers::increaseVolume")

    def decrease_volume(self):
        """
        Sends a message to decrease the volume.
        """
        self.send_message("speakers::decreaseVolume")
    
    def set_volume(self, volume):
        """
        Sends a message to set the volume.
        """
        self.send_message(f"speakers::{volume}")

    def grab_image(self):
        """
        Captures an image.

        Returns:
            np.ndarray: The captured image.
        """
        if self.debug:
            return

        if self.connect_mode:
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                self.logger.log_error("Failed to open camera")

            ret, frame = cap.read()  # Capture a frame

            if not ret:
                self.logger.log_error("Failed to capture frame")
                cap.release()
                return np.full((480, 640, 3), 26, dtype=np.uint8)

            cap.release()

        else:
            url = f"http://{self.elmo_ip}:8080/stream.mjpg"
            response = requests.get(url, stream=True)

            if response.status_code == 200:  # Is a valid response
                stream = response.iter_content(chunk_size=1024)
                bytes_ = b""
                for chunk in stream:
                    bytes_ += chunk
                    a = bytes_.find(b"\xff\xd8")
                    b = bytes_.find(b"\xff\xd9")
                    if a != -1 and b != -1:
                        jpg = bytes_[a : b + 2]
                        bytes_ = bytes_[b + 2 :]
                        frame = cv2.imdecode(
                            np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR
                        )
                        break

        # Resize the image to 480x640
        frame = cv2.resize(frame, (640, 480))
        return frame

    def set_image(self, image_name):
        """
        Sets the image.

        Args:
            image_name (str): The source name of the image.
        """
        self.send_message(f"image::{image_name}")

    def set_icon(self, icon_name):
        """
        Sets the icon.

        Args:
            icon_name (str): The source name of the icon.
        """
        self.send_message(f"icon::{icon_name}")

    def set_forever_icon(self, icon_name):
        """
        Sets the icon.

        Args:
            icon_name (str): The source name of the icon.
        """
        self.send_message(f"forever_icon::{icon_name}")

    def play_sound(self, sound):
        """
        Plays the specified sound.

        Args:
            sound (str): The source name of the sound to be played.
        """
        self.send_message(f"sound::{sound}")

    def close_all(self):
        """
        Closes all connections and shuts down the server.

        Sends a "game::off" message to the robot.
        If the debug flag is set to False, it also shuts down the Elmo socket.

        """
        if self.debug == False:
            self.elmo_socket.shutdown(socket.SHUT_RDWR)
            self.elmo_socket.close()
            return
        return
