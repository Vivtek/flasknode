from flasknode import app, db, model
from flask import jsonify
from flask import request

@app.route('/client')
def json_client():
   client = db.query('select * from client limit 1', one=True)
   return jsonify(
      node=client['node_id'],
      version=client['version']
   )

@app.route('/message/post', methods=['POST'])
def message_new():
   # Note: error handling with request.is_json?
   content = request.get_json()
   model.new_message(content['message'])
   return 'ok'
   
@app.route('/message/list')
def message_list():
   messages = db.query ('select * from message order by create_date desc limit 20')
   return jsonify ([{'id':message['message_id'], 'subject':message['subject'], 'date':message['create_date'], 'message':message['message']} for message in messages])

