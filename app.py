# API server for controlling settings
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from utils import utils
import json

utilities = utils.Utils()
app = Flask(__name__)
socketio = SocketIO(app)

# GET route for main HTML page so user can edit his settings
@app.route("/")
def index():
    with open("config.json", "r") as f:
      config = json.load(f)
    return render_template('index.html', config=config)

# POST route for updating data

# Emits sockets to front end for updating logs
def emit_socket(message):
    try:
        socketio.emit("log", message)
    except Exception as e:
        print("Failed to emit log")

# Start scripts
def start_server():
    app.run(host='0.0.0.0')
    socketio.run(app)
