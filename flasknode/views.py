from flasknode import app, db
from flask import jsonify

@app.route('/client')
def json_client():
   client = db.query('select * from client limit 1', one=True)
   return jsonify(
      version=client['version']
   )

@app.route('/feed')
def feed_list():
   return jsonify(
      username='me',
      email='me@email.com',
      id=42
   )
   
@app.route('/message/new', methods=['POST'])
def message_new():
   # Note: error handling with request.is_json
   content = request.get_json()
   
   return "ok"
   
@app.route('/message/list')
def message_list():
   messages = db.query ('select * from message')
   return jsonify ([{'id':message['message_id'], 'subject':message['subject'], 'message':message['message']} for message in messages])

