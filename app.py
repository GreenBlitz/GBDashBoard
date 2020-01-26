#!/usr/bin/env python
import cv2
from importlib import import_module
import os
from flask import Flask, render_template, Response
import gbvision as gbv

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera
cam = gbv.USBCamera(0)

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera: gbv.Camera):
    """Video streaming generator function."""
    while True:
        _, frame = camera.read()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frame)[1].tobytes() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(cam),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
