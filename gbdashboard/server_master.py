import json
import time
from threading import Thread

from gbdashboard.tools.generic import reroute
from flask import Flask, send_from_directory

from gbdashboard.constants.net import LOCAL_SERVER_IP, SERVER_PORT, RUN_DATABASE
from gbdashboard.dashboard.dashboard_webpage_builder import build_dashboards
from gbdashboard.dashboard.dashboard_builder import generate_dashboard
from gbdashboard.dashboard.database import Database
import gbdashboard.dashboard.dashboard_builder as db
from gbdashboard.tools.pi import route_pi

app = Flask(__name__)


@app.route('/')
def hello_world():
    return send_from_directory('html', 'index.html')


@app.route('/scripts/<path:path>')
def send_js(path):
    return send_from_directory('scripts', path)

@app.after_request
def prevent_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/db/<path:path>')
def send_db(path: str):
    if path.endswith('.db'):
        return send_from_directory('db', path)
    return reroute(f"/db/{path}.db")


@app.route('/db/current')
def send_current_db():
    return reroute(f"/db/{Database.load_config().get('latest_id')}.db")


def threaded_update_database():
    jsondata = {"latest_id": (Database.load_config().get("latest_id") + 1),
                "default_delay": Database.load_config().get("default_delay")}

    with open(Database.get_database_dir() + "config.json", "w") as f:
        json.dump(jsondata, f)

    database = Database(int(Database.load_config().get("latest_id")), db.get_all_network_tables())
    for i in db.get_all_network_tables():
        database.update_database(db.generate_dashboard(i))

    sleep_time = Database.load_config().get("default_delay") / 1000.0

    while True:
        database.flush()
        for dash in db.get_all_network_tables():
            database.update_database(generate_dashboard(dash))
        time.sleep(sleep_time)


if __name__ == '__main__':
    route_pi(app)
    build_dashboards(app)
    if not RUN_DATABASE:
        Thread(target=threaded_update_database, args=[]).start()
    app.run(host=LOCAL_SERVER_IP, port=SERVER_PORT)
