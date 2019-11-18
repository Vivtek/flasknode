from flasknode import app, db, model
from flask import jsonify
from flask_socketio import join_room, leave_room, send, emit
from flasknode import socketio

@socketio.on('join')
def on_join(data):
   room = data['topic']
   print('connecting to topic ' + room)
   join_room(room)
   
@socketio.on('hello_world')
def on_hello_world(data):
   print ("hello world")

