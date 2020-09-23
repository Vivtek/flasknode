from flasknode import app, db, model
from flask import jsonify
from flask import request

# ---------------------------------------------------------------------------------------------------
# Status and handshake
# ---------------------------------------------------------------------------------------------------
# UI /status = API /client
@app.route('/client')
def api_get_client():
   return jsonify(get_client())
def get_client():
   client = model.get_client()
   curver = model.get_curver()
   return {
      'node':     client['node_id'],
      'cur':      curver,
      'nickname': client['nickname'],
      'version':  client['version'],
      'messages': client['messages']
   }

# API /hello -> missing in UI (by design)
@app.route('/hello', methods=['GET', 'POST'])
def api_hello():
   return jsonify(hello())
def hello ():
   hello = request.get_json()
   client = model.get_client()
   curver = model.get_curver()
   model.verify_node (hello['node'], hello['nickname'], hello['curver']);
   model.update_swarm (hello['node'], hello['ip'], hello['port'])
   session = model.verify_session (hello['node'], hello['ip'], hello['port'])
   model.update_session (session, hello['session'])
   
   return {
      'node':     client['node_id'],
      'nickname': client['nickname'],
      'cur':      curver,
      'version':  client['version'],
      'session':  session
   }

@app.route('/updates', methods=['GET', 'POST'])
def updates():
   rq = request.get_json()
   return jsonify (model.get_updates(rq['from']))
   


# ---------------------------------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------------------------------

# UI /messages = API /message/list
@app.route('/message/list')
def api_message_list():
   return jsonify (message_list())
def message_list(last=20):
   return model.get_messages(last)
   
# UI messages/m = API /message
@app.route('/message')
def message_get():
   return jsonify (get_message(request.args['id']))
def get_message (message_id):
   return model.get_message (message_id)

# UI messages/post = API /message/post
@app.route('/message/post', methods=['POST'])
def api_message_post():
   content = request.get_json()
   message_post(content['subject'], content['message']);
   return 'ok'
def message_post(subject, message):
   return model.new_message(subject, message)

# API /message/zero -> not exposed in UI   
# This is only for testing; should be actively deleted from production versions.
@app.route('/message/zero', methods=['GET', 'POST'])
def message_zero():
   print ("Zeroing database\n")
   model.zero_messages()
   return 'ok'
   
   
# ---------------------------------------------------------------------------------------------------
# Comments (reading happens with the messages; this is just posting)
# ---------------------------------------------------------------------------------------------------

# UI messages/comment = API /comment/post
@app.route('/comment/post', methods=['POST'])
def api_comment_post():
   # Note: error handling with request.is_json?
   content = request.get_json()
   comment_post (content['parent'], content['subject'], content['message'])
   return 'ok'
def comment_post (parent, subject, message):
   return model.new_comment(parent, subject, message)


# ---------------------------------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------------------------------

# UI sessions = API /session/list
@app.route('/session/list', methods=['GET'])
def api_sessions_list():
    return jsonify (get_sessions())
def get_sessions():
    return model.get_sessions()
 
# UI sessions/s = API session
@app.route('/session', methods=['GET'])
def api_get_session():
   return jsonify (get_session(request.args['id']))
def get_session (session_id):
   return model.get_session (session_id)

# UI sessions/connect = API session/connect
@app.route('/session/connect', methods=['POST'])
def api_session_connect():
   content = request.get_json()
   session_connect (content['ip'], content['port'])
   return 'ok'
def session_connect (ip, port):
   client = model.get_client()
   curver = model.get_curver()
   
   r = requests.get("http://%s:%s/client" % (ip,port))
   # So we've confirmed this is the right IP/port; let's add a session
   # - add/check the nodes table 
   node = r.json()
   model.verify_node (node['node'], node['nickname'], node['cur']);
   model.update_swarm (node['node'], ip, port)
   session = model.verify_session (node['node'], ip, port)
   
   post = {'node':client['node_id'], 'nickname':client['nickname'], 'curver':curver, 'version':client['version'], 'session':session, 'ip':app.my_ip, 'port':5000}
   r = requests.post("http://%s:%s/hello" % (ip,port), json=post)
   response = r.json()
   model.update_session (session, response['session'])
   return session

