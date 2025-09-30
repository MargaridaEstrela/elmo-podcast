#! /usr/bin/env python


"""

Driver node.

Leverages libcamera to capture frames from the camera.

Server the frames as a MJPEG stream.

"""


from flask import Flask, Response
#from deepface import DeepFace
import middleware as mw

import libcamera
import time


app = Flask(__name__)

class DriverCamera:

    # Create a Camera instance using libcamera
    def __init__(self):
        self.camera = libcamera.Camera() 
        self.node = mw.Node("camera")
        self.camera.configure()
        self.camera.start()

    # Define a generator function to capture frames
    def generate_frames(self):
        while True:
            # Capture a frame from the camera
            frame = self.camera.capture()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Define a function to capture a frame from the camera
    def capture_frame(self):
        frame = camera.capture()
        return (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Analyse a specific frame with the given path
    def frame_analysis(self, frame):
        #face_analysis = DeepFace.analyze(img_path = None, img = frame)
        print(face_analysis["emotion"])
        return {}

@app.route('/video')
def video():
    return Response(DriverCamera.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    camera = DriverCamera()
