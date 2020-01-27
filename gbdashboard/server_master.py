import json
from flask import Flask, request, send_from_directory, Response

from gbdashboard.constants.net import LOCAL_SERVER_IP, SERVER_PORT
from gbdashboard.constants.vision_algorithms import vision_algorithms
from gbdashboard.tools.pi import set_led_state, set_exposure_state, set_auto_exposure_state, do_vision_master, \
    change_vision_algorithm, all_thresholds, send_tcp_stream, set_value_in_file, \
    set_vision_master_debug_mode, close_vision_master_proc, led_ring_state_getter, exposure_state_getter, \
    auto_exposure_state_getter, vision_master_debug_mode_state_getter, vision_master_state_getter, \
    algorithm_state_getter, python_stream_state_getter

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/scripts/<path:path>')
def send_js(path):
    return send_from_directory('scripts', path)


@app.route('/pi')
def pi():
    return send_from_directory('html', 'pi.html')


@app.route('/set_leds')
def set_leds():
    state = json.loads(request.args.get("state"))
    set_led_state(state)
    return ''


@app.route('/set_debug_mode')
def set_debug_mode():
    state = json.loads(request.args.get("state"))
    set_vision_master_debug_mode(state)
    return ''


@app.route('/set_exposure')
def set_exposure():
    raw = json.loads(request.args.get("raw"))
    camera = json.loads(request.args.get("camera"))
    set_exposure_state(raw, camera)
    return ''


@app.route('/set_auto_exposure')
def set_auto_exposure():
    raw = json.loads(request.args.get("raw"))
    camera = json.loads(request.args.get("camera"))
    set_auto_exposure_state(raw, camera)
    return ''


@app.route('/start_vision_master')
def start_vision_master():
    do_vision_master()
    return ''


@app.route('/stop_vision_master')
def stop_vision_master():
    close_vision_master_proc()
    return ''


@app.route('/get_algorithms_list')
def get_algorithms_list():
    return json.dumps(vision_algorithms)


@app.route('/set_vision_algorithm')
def set_vision_algorithm():
    algo = request.args.get("algo")
    change_vision_algorithm(algo)
    return ''


@app.route('/get_all_thresholds')
def get_all_thresholds():
    return json.dumps(all_thresholds)


@app.route('/start_gbvision_stream')
def start_gbvision_stream():
    camera = json.loads(request.args.get("camera"))
    send_tcp_stream(camera)
    return ''


@app.route('/set_threshold_value')
def set_threshold_value():
    name = request.args.get("name")
    code = request.args.get("code")
    set_value_in_file(name, code)
    return ''


@app.route('/get_led_ring_state')
def get_led_ring_state():
    return json.dumps(led_ring_state_getter())


@app.route('/get_exposure_state')
def get_exposure_state():
    camera = json.loads(request.args.get("camera"))
    return json.dumps(exposure_state_getter(camera))


@app.route('/get_auto_exposure_state')
def get_auto_exposure_state():
    camera = json.loads(request.args.get("camera"))
    return json.dumps(auto_exposure_state_getter(camera))


@app.route('/get_vision_master_debug_mode_state')
def get_vision_master_debug_mode_state():
    return json.dumps(vision_master_debug_mode_state_getter())


@app.route('/get_vision_master_process_state')
def get_vision_master_process_state():
    return json.dumps(vision_master_state_getter())


@app.route('/get_current_algorithm')
def get_current_algorithm():
    return algorithm_state_getter()


@app.route('/get_python_stream_state')
def get_python_stream_state():
    return json.dumps(python_stream_state_getter())


if __name__ == '__main__':
    app.run(host=LOCAL_SERVER_IP, port=SERVER_PORT)
