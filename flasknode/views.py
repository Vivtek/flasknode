from flasknode import app, db
from flask import jsonify
from flask import request

@app.route('/client')
def json_client():
   client = db.query('select * from client limit 1', one=True)
   return jsonify(
      version=client['version']
   )

@app.route('/message/post', methods=['POST'])
def message_new():
   # Note: error handling with request.is_json
   content = request.get_json()
   print (content);
   
   return "ok"
   
@app.route('/message/list')
def message_list():
   messages = db.query ('select * from message')
   return jsonify ([{'id':message['message_id'], 'subject':message['subject'], 'message':message['message']} for message in messages])

