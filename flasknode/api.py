from flasknode import app, db, model
from flask import jsonify
from flask import request

@app.route('/client')
def json_client():
   client = model.get_client()
   curver = model.get_curver()
   return jsonify(
      node=client['node_id'],
      cur=curver,
      nickname=client['nickname'],
      version=client['version']
   )
   
@app.route('/hello', methods=['GET', 'POST'])
def hello():
   hello = request.get_json()
   client = model.get_client()
   curver = model.get_curver()
   return jsonify(
      node=client['node_id'],
      cur=curver,
      version=client['version']
   )

@app.route('/message')
def message_get():
   # Note: error handling with request.is_json?
   #content = request.get_json()
   return jsonify (model.get_message(request.args['id']))

@app.route('/message/post', methods=['POST'])
def message_new():
   # Note: error handling with request.is_json?
   content = request.get_json()
   model.new_message(content['subject'], content['message'])
   return 'ok'
   
@app.route('/message/list')
def message_list():
   #messages = db.query ('select * from message order by create_date desc limit 20')
   #return jsonify ([{'id':message['message_id'], 'subject':message['subject'], 'date':message['create_date'], 'message':message['message']} for message in messages])
   return jsonify (model.get_messages(20))
   
# This is only for testing; should be actively deleted from production versions.
@app.route('/message/zero', methods=['GET', 'POST'])
def message_zero():
   print ("Zeroing database\n")
   model.zero_messages()
   return 'ok'
   
@app.route('/comment/post', methods=['POST'])
def comment_new():
   # Note: error handling with request.is_json?
   content = request.get_json()
   model.new_comment(content['parent'], content['subject'], content['message'])
   return 'ok'

   
@app.route('/updates', methods=['GET', 'POST'])
def updates():
   rq = request.get_json()
   return jsonify (model.get_updates(rq['from']))
   

