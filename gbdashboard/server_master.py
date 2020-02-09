from flask import Flask, send_from_directory, Response

from gbdashboard.constants.net import LOCAL_SERVER_IP, SERVER_PORT
from gbdashboard.dashboard.dashboard_webpage_builder import build_dashboards
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


if __name__ == '__main__':
    route_pi(app)
    build_dashboards(app)
    app.run(host=LOCAL_SERVER_IP, port=SERVER_PORT)
