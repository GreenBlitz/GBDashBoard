import json
import time
import sys
from threading import Thread

from gbdashboard.tools.generic import reroute
from flask import Flask, send_from_directory
import logging

from gbdashboard.constants.net import LOCAL_SERVER_IP, SERVER_PORT, RUN_DATABASE, DEFAULT_TABLES
from gbdashboard.dashboard.dashboard_webpage_builder import build_dashboards
from gbdashboard.dashboard.dashboard_builder import generate_dashboard
from gbdashboard.dashboard.database import Database
import gbdashboard.dashboard.dashboard_builder as db
from gbdashboard.tools.pi import route_pi, is_on_rpi

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

    database = Database(int(Database.load_config().get("latest_id")),
                        set(db.get_all_network_tables() + DEFAULT_TABLES))
    for i in database.table_list:
        database.update_database(db.generate_dashboard(i))

    sleep_time = Database.load_config().get("default_delay") / 1000.0

    while True:
        database.flush()
        for dash in db.get_all_network_tables():
            database.update_database(generate_dashboard(dash))
        time.sleep(sleep_time)


def main():

    args = sys.argv

    if len(args) != 2 or args[1] not in ["Y", "N", "y", "n"]:
        print("Usage: server_master.py [RUN_DATABASE Y/N]")
        return

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    if is_on_rpi:
        print("Setting pi routes...")
        route_pi(app)
    print("Setting dashboard routes...")
    build_dashboards(app)

    if RUN_DATABASE and args[1] in ["Y", "y"]:
        print("Starting database...")
        Thread(target=threaded_update_database, args=[], daemon=True).start()
    print("Starting server...")
    app.run(host=LOCAL_SERVER_IP, port=SERVER_PORT)


if __name__ == '__main__':
    main()
