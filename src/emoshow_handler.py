#! /usr/bin/env python
import os
import socket
import sys

import middleware as mw

s = None  # Socket
pan = mw.Pan()
tilt = mw.Tilt()
onboard = mw.Onboard()
speakers = mw.Speakers()
leds = mw.Leds()
server = mw.Server()

image_path = "images/emoshow/"
sound_path = "emoshow/"
icon_path = "emoshow/"


def enable_torque():
    """
    Enables the torque for the pan and tilt motors.
    """
    pan.enable = True
    tilt.enable = True


def parse_message(message):
    """
    Parses the given message and performs the corresponding actions based on the
    command and value.

    Args:
        message (str): The message to be parsed in the format "command::value".
    """
    splitMessage = message.split("::")

    if len(splitMessage) != 2:
        print("Invalid message")
        return

    command = splitMessage[0]
    value = splitMessage[1]

    if command == "pan":
        pan.angle = int(value)

    elif command == "tilt":
        tilt.angle = int(value)

    elif command == "image":
        if "emoshow" in value:
            image_src = value
        else:
            image_src = os.path.join(image_path, f"{value}")
        onboard.image = image_src

    elif command == "speakers":
        if value == "increaseVolume":
            speakers.volume += 10
        elif value == "decreaseVolume":
            speakers.volume -= 10

    elif command == "sound":
        sound_src = os.path.join(sound_path, f"{value}")
        sound_url = server.url_for_sound(sound_src)
        speakers.url = sound_url

    elif command == "icon":
        icon_src = os.path.join(icon_path, f"{value}")
        icon_url = server.url_for_icon(icon_src)
        leds.load_from_url(icon_url)

    elif command == "game":
        if value == "off":
            s.close()
            exit()


def main():
    """
    Entry point of the Emo-Show handler program.
    Parses command line arguments, establishes a connection, and handles
    incoming messages.
    """

    global s

    # Parse arguments
    if len(sys.argv) == 3 or len(sys.argv) == 4:
        elmo_ip, elmo_port = sys.argv[1:3]
        debug = False
    else:
        print("Usage: python emoshow_handler.py <elmoIp> <port> (--debug)")
        return

    # Check debug flag
    if len(sys.argv) == 4:
        if sys.argv[3] == "--debug":
            debug = True
        else:
            print("Usage: python emoshow_handler.py <elmoIp> <port> (--debug)")
            return

    print("Starting connection...")

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((elmo_ip, int(elmo_port)))

    print("Server Started")

    if not debug:
        enable_torque()

    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode("utf-8")

        if not debug:
            parse_message(data)


if __name__ == "__main__":
    main()
