from flasknode import app
from flask_socketio import SocketIO
from flasknode import socketio

#socketio = SocketIO(app, cors_allowed_origins="*")
socketio.run(app, log_output=True)
