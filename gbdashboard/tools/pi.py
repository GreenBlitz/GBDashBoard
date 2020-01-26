import cv2

import gbrpi
import gbvision as gbv
import subprocess

from gbdashboard.constants.ports import LED_RING_PORT

leds = gbrpi.LedRing(LED_RING_PORT)
cams = gbv.CameraList([gbv.USBCamera(0)])

def set_led_state(state):
    if state:
        leds.on()
    else:
        leds.off()


def update_cam(port: int):
    """Video streaming generator function."""
    camera = gbv.USBCamera(port)
    while True:
        _, frame = camera.read()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frame)[1].tobytes() + b'\r\n')


def set_exposure_state(raw: int, camera: int):
    subprocess.call(['v4l2-ctl', '-d', f'/dev/video{camera}', '-c', f'exposure_absolute={raw}'])


def set_auto_exposure_state(raw: int, camera: int):
    subprocess.call(['v4l2-ctl', '-d', f'/dev/video{camera}', '-c', f'exposure_auto={raw}'])
