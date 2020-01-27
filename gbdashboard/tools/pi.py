import cv2

import gbrpi
import gbvision as gbv
import subprocess
import platform

from gbdashboard.constants.net import STREAM_PORT
from gbdashboard.constants.ports import LED_RING_PORT

leds = gbrpi.LedRing(LED_RING_PORT)

is_on_rpi = platform.uname()[4].startswith('arm')

CAMERA_AMOUNT = int(subprocess.check_output(['vcgencmd', 'get_camera']).decode('ascii').split()[0].split('=')[
                        1]) if is_on_rpi else 1

cameras = None

def set_cameras():
    global cameras
    cameras = gbv.CameraList([gbv.AsyncUSBCamera(i) for i in range(CAMERA_AMOUNT)])

set_cameras()

conn = gbrpi.TableConn('10.45.90.8', 'vision')

all_thresholds = list(map(lambda x: x.split('=')[0].strip(), filter(lambda x: ord('A') <= ord(x[0]) <= ord('Z'),
                                                                    open(
                                                                        '/home/pi/vision/constants/thresholds.py').read().split()))) if is_on_rpi else [
    'VISION_TARGET',
    'POWER_CELL']

vision_master_process = None


def set_led_state(state):
    if state:
        leds.on()
    else:
        leds.off()


def set_vision_master_debug_mode(state):
    base_algorithm_file = '/home/pi/vision/algorithms/base_algorithm.py'
    lines = open(base_algorithm_file).read().splitlines()
    for i, line in enumerate(lines.copy()):
        if 'DEBUG = ' in line:
            lines[i] = lines[i].replace('DEBUG = True', f'DEBUG = {state}').replace('DEBUG = False', f'DEBUG = {state}')
            break
    open(base_algorithm_file, 'w').write('\n'.join(lines))


def update_cam():
    """Video streaming generator function."""
    global cameras
    while True:
        if cameras.is_opened():
            _, frame = cameras.read()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frame)[1].tobytes() + b'\r\n')


def set_exposure_state(raw: int):
    global cameras
    cameras.set_exposure(raw)


def set_auto_exposure_state(raw: int):
    global cameras
    cameras.set_auto_exposure(raw)


def set_selected_camera(camera: int):
    global cameras
    cameras.select_camera(camera)


def do_vision_master():
    global cameras
    global vision_master_process
    cameras.release(foreach=True)
    vision_master_process = subprocess.Popen(['/home/pi/vision/do_vision.sh'], stdout=subprocess.PIPE)


def close_vision_master_proc():
    global vision_master_process
    if vision_master_process is not None:
        vision_master_process.kill()
        vision_master_process = None
    set_cameras()


def change_vision_algorithm(algo):
    global conn
    conn.set('algorithm', algo)


def send_tcp_stream():
    global cameras
    try:
        stream = gbv.TCPStreamBroadcaster(STREAM_PORT)
        while True:
            ok, frame = cameras.read()
            stream.send_frame(frame)
    except gbv.TCPStreamClosed:
        return


def set_value_in_file(name, code):
    lines = open('/home/pi/vision/constants/thresholds.py').read().splitlines()
    for i, line in enumerate(lines.copy()):
        if line.startswith(name + ' ') or line.startswith(name + '='):
            lines[i] = f'{name} = {code}'

    open('/home/pi/vision/constants/thresholds.py', 'w').write('\n'.join(lines))
