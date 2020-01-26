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



if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
