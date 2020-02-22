import json
import signal

import gbrpi
import gbvision as gbv
import subprocess
import platform
import os

from flask import Flask, request, send_from_directory

from gbdashboard.constants.net import STREAM_PORT, ROBORIO_IP
from gbdashboard.constants.ports import LED_RING_PORT
from gbdashboard.constants.vision_algorithms import vision_algorithms

leds = gbrpi.LedRing(LED_RING_PORT)

is_on_rpi = platform.uname()[4].startswith('arm')

conn = gbrpi.TableConn(ROBORIO_IP, 'vision')

all_thresholds = list(map(lambda x: x.split('=')[0].strip(), filter(lambda x: ord('A') <= ord(x[0]) <= ord('Z'),
                                                                    open(
                                                                        '/home/pi/vision/constants/thresholds.py').read().split()))) if is_on_rpi else [
    'VISION_TARGET',
    'POWER_CELL']

vision_master_process = None

python_stream_running = False


def route_pi(app: Flask):
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
                lines[i] = lines[i].replace('DEBUG = True', f'DEBUG = {state}').replace('DEBUG = False',
                                                                                        f'DEBUG = {state}')
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
            os.kill(vision_master_process.pid, signal.SIGINT)
            vision_master_process = None

    def change_vision_algorithm(algo):
        global conn
        conn.set('algorithm', algo)

    def send_tcp_stream(port: int):
        global python_stream_running
        if not python_stream_running:
            python_stream_running = True
            camera = gbv.USBCamera(port)
            try:
                stream = gbv.TCPStreamBroadcaster(STREAM_PORT)
                while True:
                    ok, frame = camera.read()
                    stream.send_frame(frame)
            except gbv.TCPStreamClosed:
                camera.release()
                python_stream_running = False

    def set_value_in_file(name, code):
        lines = open('/home/pi/vision/constants/thresholds.py').read().splitlines()
        for i, line in enumerate(lines.copy()):
            if line.startswith(name + ' ') or line.startswith(name + '='):
                lines[i] = f'{name} = {code}'

        open('/home/pi/vision/constants/thresholds.py', 'w').write('\n'.join(lines))

    def led_ring_state_getter():
        global leds
        return leds.get_power() != 0

    def vision_master_state_getter():
        global vision_master_process
        return vision_master_process is not None

    def exposure_state_getter(camera):
        return int(
            subprocess.check_output(['v4l2-ctl', '-d', f'/dev/video{camera}', '-C', f'exposure_absolute']).decode(
                'ascii').split(': ')[1]) == 11

    def auto_exposure_state_getter(camera):
        return int(
            subprocess.check_output(['v4l2-ctl', '-d', f'/dev/video{camera}', '-C', f'exposure_auto']).decode(
                'ascii').split(': ')[1]) == 3

    def vision_master_debug_mode_state_getter():
        base_algorithm_file = '/home/pi/vision/algorithms/base_algorithm.py'
        lines = open(base_algorithm_file).read().splitlines()
        for i, line in enumerate(lines.copy()):
            if 'DEBUG = ' in line:
                return 'True' in line

    def algorithm_state_getter():
        global conn
        return conn.get('algorithm', '')

    def python_stream_state_getter():
        global python_stream_running
        return python_stream_running

    @app.route('/pi')
    def pi():
        return send_from_directory('html', 'pi.html')

    @app.route('/pi/set_leds')
    def set_leds():
        state = json.loads(request.args.get("state"))
        set_led_state(state)
        return ''

    @app.route('/pi/set_debug_mode')
    def set_debug_mode():
        state = json.loads(request.args.get("state"))
        set_vision_master_debug_mode(state)
        return ''

    @app.route('/pi/set_exposure')
    def set_exposure():
        raw = json.loads(request.args.get("raw"))
        camera = json.loads(request.args.get("camera"))
        set_exposure_state(raw, camera)
        return ''

    @app.route('/pi/set_auto_exposure')
    def set_auto_exposure():
        raw = json.loads(request.args.get("raw"))
        camera = json.loads(request.args.get("camera"))
        set_auto_exposure_state(raw, camera)
        return ''

    @app.route('/pi/start_vision_master')
    def start_vision_master():
        do_vision_master()
        return ''

    @app.route('/pi/stop_vision_master')
    def stop_vision_master():
        close_vision_master_proc()
        return ''

    @app.route('/pi/get_algorithms_list')
    def get_algorithms_list():
        return json.dumps(vision_algorithms)

    @app.route('/pi/set_vision_algorithm')
    def set_vision_algorithm():
        algo = request.args.get("algo")
        change_vision_algorithm(algo)
        return ''

    @app.route('/pi/get_all_thresholds')
    def get_all_thresholds():
        return json.dumps(all_thresholds)

    @app.route('/pi/start_gbvision_stream')
    def start_gbvision_stream():
        camera = json.loads(request.args.get("camera"))
        send_tcp_stream(camera)
        return ''

    @app.route('/pi/set_threshold_value')
    def set_threshold_value():
        name = request.args.get("name")
        code = request.args.get("code")
        set_value_in_file(name, code)
        return ''

    @app.route('/pi/get_led_ring_state')
    def get_led_ring_state():
        return json.dumps(led_ring_state_getter())

    @app.route('/pi/get_exposure_state')
    def get_exposure_state():
        camera = json.loads(request.args.get("camera"))
        return json.dumps(exposure_state_getter(camera))

    @app.route('/pi/get_auto_exposure_state')
    def get_auto_exposure_state():
        camera = json.loads(request.args.get("camera"))
        return json.dumps(auto_exposure_state_getter(camera))

    @app.route('/pi/get_vision_master_debug_mode_state')
    def get_vision_master_debug_mode_state():
        return json.dumps(vision_master_debug_mode_state_getter())

    @app.route('/pi/get_vision_master_process_state')
    def get_vision_master_process_state():
        return json.dumps(vision_master_state_getter())

    @app.route('/pi/get_current_algorithm')
    def get_current_algorithm():
        return algorithm_state_getter()

    @app.route('/pi/get_python_stream_state')
    def get_python_stream_state():
        return json.dumps(python_stream_state_getter())
