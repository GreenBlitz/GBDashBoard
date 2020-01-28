from flask import Flask, send_from_directory

from gbdashboard.constants.net import LOCAL_SERVER_IP, SERVER_PORT
from gbdashboard.tools.pi import route_pi

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/scripts/<path:path>')
def send_js(path):
    return send_from_directory('scripts', path)


route_pi(app)

if __name__ == '__main__':
    app.run(host=LOCAL_SERVER_IP, port=SERVER_PORT)
