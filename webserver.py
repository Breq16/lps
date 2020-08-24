import threading

from flask import Flask, jsonify

app = Flask(__name__)

state = {}


def update(new_state):
    global state
    state = new_state


@app.route("/state")
def send_state():
    global state
    return jsonify(state)


flask_thread = threading.Thread(target=app.run, args=("0.0.0.0",))
flask_thread.start()
