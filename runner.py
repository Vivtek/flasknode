from flasknode import app
from flask_socketio import SocketIO

socketio = SocketIO(app)
socketio.run(app)
