import configparser
import os, sys
from flasknode import subnet
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

config = configparser.ConfigParser()
configfile = os.path.normpath (os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'setup.conf'))
config.read(configfile)

my_ip = subnet.get_ip()
print ("Starting on IP: %s" % (my_ip))

app = Flask(__name__,
            static_folder = "static")
CORS(app)

socketio = SocketIO(app, cors_allowed_origins=['http://localhost:8080','http://127.0.0.1:8080'])
# Note on cors_allowed_origins: https://stackoverflow.com/questions/29187933/flask-socketio-cors


from flasknode import api
from flasknode import static_files
from flasknode import channels
