import eventlet
eventlet.monkey_patch()

from flasknode import app
from flask_socketio import SocketIO
from flasknode import socketio

socketio.run(app, log_output=True)
