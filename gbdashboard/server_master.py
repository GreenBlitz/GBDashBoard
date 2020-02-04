import json
import time
from threading import Thread

from flask import Flask, request, send_from_directory

from gbdashboard.constants.net import LOCAL_SERVER_IP, SERVER_PORT, DASHBOARDS
from gbdashboard.dashboard.dashboard_webpage_builder import build_dashboards
from gbdashboard.dashboard.dashboard_builder import generate_dashboard
from gbdashboard.tools.generic import reroute
from gbdashboard.tools.pi import set_led_state, set_exposure_state, set_auto_exposure_state
from gbdashboard.dashboard.database import Database
import gbdashboard.dashboard.dashboard_builder as db

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


@app.route('/db/<path:path>')
def send_db(path: str):
    if path.endswith('.db'):
        return send_from_directory('db', path)
    return reroute(f"/db/{path}.db")


@app.route('/db/current')
def send_current_db():
    return reroute(f"/db/{Database.load_config().get('latest_id')}.db")


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


def threaded_update_database():
    jsondata = {"latest_id": (Database.load_config().get("latest_id") + 1),
                "default_delay": Database.load_config().get("default_delay")}

    with open(Database.get_database_dir() + "config.json", "w") as f:
        json.dump(jsondata, f)

    database = Database(int(Database.load_config().get("latest_id")), DASHBOARDS)
    for i in DASHBOARDS:
        database.update_database(db.generate_dashboard(i))

    sleep_time = Database.load_config().get("default_delay") / 1000.0



    while True:
        database.flush()
        for dash in DASHBOARDS:
            database.update_database(generate_dashboard(dash))
        time.sleep(sleep_time)


if __name__ == '__main__':
    build_dashboards(app)
    Thread(target=threaded_update_database, args=[]).start()
    app.run(host=LOCAL_SERVER_IP, port=SERVER_PORT)
