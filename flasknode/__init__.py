import configparser
import os, sys
from flasknode import subnet
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import requests

config = configparser.ConfigParser()
configfile = os.path.normpath (os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'setup.conf'))
config.read(configfile)

my_ip = subnet.get_ip()
print ("Starting on IP: %s" % (my_ip))
external_ip = requests.get('https://api.ipify.org').text
print ("IP to the outside: %s" % external_ip)

app = Flask(__name__,
            static_folder = "static")
CORS(app)

app.my_ip = my_ip
app.fnconfig = config
app.this_node = '_unknown_node_'
if my_ip == external_ip:
  app.connectable = True
else:
  app.connectable = False
  print ("Warning: node is not connectable")

subnet.start_subnet_maintenance(app)

socketio = SocketIO(app, cors_allowed_origins=['http://localhost:8080','http://127.0.0.1:8080'])
# Note on cors_allowed_origins: https://stackoverflow.com/questions/29187933/flask-socketio-cors


from flasknode import api
from flasknode import static_files
from flasknode import channels
from flasknode import ui
