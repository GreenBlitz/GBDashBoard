import cv2

import gbrpi
import gbvision as gbv
import subprocess
import platform
import os

from gbdashboard.constants.net import STREAM_PORT
from gbdashboard.constants.ports import LED_RING_PORT

leds = gbrpi.LedRing(LED_RING_PORT)

is_on_rpi = platform.uname()[4].startswith('arm')

conn = gbrpi.TableConn('10.45.90.2', 'vision')

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


def set_exposure_state(raw: int, camera: int):
    subprocess.call(['v4l2-ctl', '-d', f'/dev/video{camera}', '-c', f'exposure_absolute={raw}'])


def set_auto_exposure_state(raw: int, camera: int):
    subprocess.call(['v4l2-ctl', '-d', f'/dev/video{camera}', '-c', f'exposure_auto={raw}'])


def do_vision_master():
    global vision_master_process
    open('/home/pi/vision/do_vision.sh', 'w').write(
        '#!/bin/bash\nsource /home/pi/bash_config\ncd /home/pi/vision\npy vision_master.py')
    os.chmod('/home/pi/vision/do_vision.sh', 0o0777)
    vision_master_process = subprocess.Popen(['/home/pi/vision/do_vision.sh'], stdout=subprocess.PIPE)


def close_vision_master_proc():
    global vision_master_process
    if vision_master_process is not None:
        vision_master_process.kill()
        vision_master_process = None


def change_vision_algorithm(algo):
    global conn
    conn.set('algorithm', algo)


def send_tcp_stream(port: int):
    camera = gbv.USBCamera(port)
    try:
        stream = gbv.TCPStreamBroadcaster(STREAM_PORT)
        while True:
            ok, frame = camera.read()
            stream.send_frame(frame)
    except gbv.TCPStreamClosed:
        return


def set_value_in_file(name, code):
    lines = open('/home/pi/vision/constants/thresholds.py').read().splitlines()
    for i, line in enumerate(lines.copy()):
        if line.startswith(name + ' ') or line.startswith(name + '='):
            lines[i] = f'{name} = {code}'

    open('/home/pi/vision/constants/thresholds.py', 'w').write('\n'.join(lines))
