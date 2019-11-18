from flasknode import app, db
from flasknode import socketio

def new_message(message):
   row = db.insert ('insert into message (user_id, message, create_date) values (0, ?, CURRENT_TIMESTAMP)', (message,))
   socketio.emit('feed', get_message(row), room='feed', json=True)

def get_message(msgid):
   message = db.query ('select * from message where message_id=?', (msgid,), one=True)
   return {'id':message['message_id'], 'subject':message['subject'], 'date':message['create_date'], 'message':message['message']}
