from flask import Flask

from gbdashboard.constants.net import LOCAL_SERVER_IP, SERVER_PORT

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(host=LOCAL_SERVER_IP, port=SERVER_PORT)
