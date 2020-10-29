from flasknode import app, db, model
from flask import jsonify
from flask import request
import requests

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
def message_list(last=20, server=None):
   if (server == None):
      return model.get_messages(last)
   return remote_api (server, 'g', '/message/list', {})
   
# UI messages/m = API /message
@app.route('/message')
def message_get():
   return jsonify (get_message(request.args['id']))
def get_message (message_id, server=None):
   if (server == None):
      return model.get_message (message_id)
   return remote_api (server, 'g', '/message', {'id':message_id})

# UI messages/post = API /message/post
@app.route('/message/post', methods=['POST'])
def api_message_post():
   content = request.get_json()
   (user, is_new) = get_session_user (content)
   id = message_post (content['subject'], content['message'], user=user)
   retval = {'ok':'ok', 'id':id}
   if is_new:
      retval['user'] = '?'
   return jsonify(retval)

def message_post(subject, message, server=None, user=1):
   if server == None:
      return model.new_message(subject, message, user=user)
   else:
      retval = remote_api (server, 'p', '/message/post', {'subject':subject, 'message':message})
      return retval['id']


# API /message/zero -> not exposed in UI   
# This is only for testing; should be actively deleted from production versions.
#@app.route('/message/zero', methods=['GET', 'POST'])
#def message_zero():
#   print ("Zeroing database\n")
#   model.zero_messages()
#   return 'ok'
   
   
# ---------------------------------------------------------------------------------------------------
# Comments (reading happens with the messages; this is just posting)
# ---------------------------------------------------------------------------------------------------

# UI messages/comment = API /comment/post
@app.route('/comment/post', methods=['POST'])
def api_comment_post():
   # Note: error handling with request.is_json?
   content = request.get_json()
   (user, is_new) = get_session_user (content)
   comment_post (content['parent'], content['subject'], content['message'], user=user)
   retval = {'ok':'ok'}
   if is_new:
      retval['user'] = '?'
   return jsonify(retval)
   
def comment_post (parent, subject, message, server=None, user=1):
   if server == None:
      return model.new_comment(parent, subject, message, user)
   return remote_api (server, 'p', '/comment/post', {'parent':parent, 'subject':subject, 'message':message})

def get_session_user (content):
   user = 1
   new_user = False
   if 'user' in content:
      user = content['user']
   if 'session' in content:
      session = model.get_session(content['session']) # Handle error
      our_user = model.find_remote_user(session['node'], user)
      if our_user == None:
         new_user = True
         if user == 1: # a remote null user - we know their nickname
            our_user = model.add_remote_user(session['node'], user, session['nickname'])
         else:
            our_user = model.add_remote_user(session['node'], user, 'anon')
            model.rename_user (our_user, 'anon-%s' % our_user)
         
      user = our_user
      
   return (user, new_user)
   
def find_or_make_remote_user (session, user):
    our_user = model.find_remote_user(session['node'], user)
    if our_user == None:
       #new_user = True
       if user == 1: # a remote null user - we know their nickname
          our_user = model.add_remote_user(session['node'], user, session['nickname'])
       else:
          our_user = model.add_remote_user(session['node'], user, 'anon')
          model.rename_user (our_user, 'anon-%s' % our_user)
    return our_user

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
   return jsonify({'ok':'ok'})
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
   
# ---------------------------------------------------------------------------------------------------
# Subscriptions
# ---------------------------------------------------------------------------------------------------

def check_or_make_subscription (s, m, make=False):
   session = model.get_session (s) # Handle if session isn't found
   subscribed_message = model.get_message_subscription (s, m)
   if subscribed_message != None:
      return subscribed_message['id']
   if make == False:
      return None
   # So let's subscribe!
   # Ask remote server for the subscribed message
   remote_message = remote_api (s, 'g', '/subscription/start', {'id':message_id})
   our_user = find_or_make_remote_user (s, remote_message['user'])
   our_msg = model.new_message (remote_message['subject'], remote_message['message'], user=our_user, sub_node=session['node'], sub_msg=remote_message['id'])
   # Do the same for comments
   return our_msg

@app.route('/subscription/start')
def api_subscribe():
   message = model.get_message(request.args['id']) # Make sure this message exists
   remote = model.get_session (request.args['session'])
   model.make_subscription (remote['node'], message['id'])
   return jsonify (message)

# ---------------------------------------------------------------------------------------------------
# Calling a remote API
# ---------------------------------------------------------------------------------------------------

def remote_api (server, post_or_get, api, parms):
   session = model.get_session (server)
   url = "http://%s:%s%s" % (session['ip'], session['port'], api)
   parms['session'] = session['their']
   
   if post_or_get == 'p':
      r = requests.post(url, json=parms)
   else:
      r = requests.get(url, params=parms)
      
   return r.json()
