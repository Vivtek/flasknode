# Clunky old-school UI for old-school dinosaur developers
from flasknode import app, db, model
from flask import request, redirect
import requests

@app.route('/status')
def status():
   client = model.get_client()
   curver = model.get_curver()
   return """
      <table>
      <tr><td>Node:</td><td>%s</td></td>
      <tr><td>Current:</td><td>%s</td></tr>
      <tr><td>Nickname:</td><td>%s [ <a href='/ui/settings/edit'>edit</a> ]</td></tr>
      <tr><td>Version:</td><td>%s</td></tr>
      </table>
      
      <a href="/ui/messages">Messages</a>
   """ % (client['node_id'], curver, client['nickname'], client['version'])
   
@app.route('/ui/settings/edit')
def ui_settings_editor():
   client = model.get_client()
   return """
      <form action="/ui/settings/update" method="post">
      <label for="nickname">Nickname:</label> <input type="text" id="nickname" name="nickname" value="%s"><br/>
      <input type="submit" value="Update">
      </form>
   """ % client['nickname']

@app.route('/ui/settings/update', methods=['POST'])
def ui_settings_update():
   id = model.set_nickname(request.form['nickname'])
   return redirect('/status')

   
@app.route('/ui/messages')
def ui_messages():
   def enlist (message):
      if message['comments'] > 0:
         count = " (%d)" % message['comments']
      else:
         count = ""
      return '<li>%s (%s) - <a href="/ui/messages/m?id=%s">%s</a>%s</li>' % (message['user'], message['date'], message['id'], message['subject'], count)
   m = model.get_messages()
   form = """
      <form action="/ui/messages/post" method="post">
      <label for="subject">Subject:</label> <input type="text" id="subject" name="subject"><br/>
      <textarea id="message" name="message" rows="3" cols="80"></textarea><br/>
      <input type="submit" value="Post message">
      </form>
   """
   if len(m):
      return """
         <ul>
         %s
         </ul>
         %s
      """ % ("<br/>".join(map(enlist, m)),form)
   else:
      return "No messages on node<br/>%s" % (form,)

@app.route('/ui/messages/post', methods=['POST'])
def ui_message_post():
   id = model.new_message(request.form['subject'], request.form['message'])
   return redirect('/ui/messages/m?id=%s' % id)



@app.route('/ui/messages/m', methods=['GET'])
def ui_message_show():
   m = model.get_message(request.args.get('id', ''))
   def enlist (comment):
      return '<li>%s (%s)<br/>%s</li>' % (comment['user'], comment ['date'], comment['message'])
   form = """
      <form action="/ui/messages/comment" method="post">
      <input type="hidden" id="parent" name="parent" value="%s">
      <input type="hidden" id="subject" name="subject" value=""><br/>
      <textarea id="message" name="message" rows="3" cols="80"></textarea><br/>
      <input type="submit" value="Comment">
      </form>
   """ % (m['id'],)

   return """
     [ <a href="/ui/messages">back</a> ]
     <table>
     <tr><td>Message ID:</td><td>%s</td></tr>
     <tr><td>Posted:</td><td>%s</td></tr>
     <tr><td>By:</td><td>%s</td></tr>
     <tr><td>Subject:</td><td>%s</td></tr>
     <tr><td colspan="2">%s</td></tr>
     </table>
     <br/>
     <ul>
     %s
     </ul>
     <br/>
     %s
   """ % (m['id'], m['date'], m['user'], m['subject'], m['message'], "<br/>".join(map(enlist, m['comments'])), form)

@app.route('/ui/messages/comment', methods=['POST'])
def ui_comment_post():
   id = model.new_comment(request.form['parent'], request.form['subject'], request.form['message'])
   return redirect('/ui/messages/m?id=%s' % request.form['parent'])


@app.route('/ui/sessions')
def ui_sessions():
   def enlist (session):
      if session['nickname'] == None:
         return '<li>%s</li>' % (session['node'],)
      else:
         return '<li>%s (%s)</li>' % (session['nickname'], session['node'])
   s = model.get_sessions()
   form = """
      <form action="/ui/sessions/connect" method="post">
      <label for="ip">IP address:</label> <input type="text" id="ip" name="ip"><br/>
      <label for="port">Port:</label> <input type="text" id="port" name="port" value="5000"><br/>
      <input type="submit" value="Connect">
      </form>
   """
   if len(s):
      return """
         <ul>
         %s
         </ul>
         %s
      """ % ("<br/>".join(map(enlist, s)),form)
   else:
      return "No remote sessions on node<br/>%s" % (form,)

@app.route('/ui/sessions/connect', methods=['POST'])
def ui_session_connect():
   ip   = request.form['ip']
   port = request.form['port']

   client = model.get_client()
   curver = model.get_curver()
   
   r = requests.get("http://%s:%s/client" % (ip,port))
   # So we've confirmed this is the right IP/port; let's add a session
   # - add/check the nodes table 
   node = r.json()
   print (node)
   model.verify_node (node['node'], node['nickname'], node['cur']);
   model.update_swarm (node['node'], ip, port)
   session = model.verify_session (node['node'], ip, port)
   
   post = {'node':client['node_id'], 'nickname':client['nickname'], 'curver':curver, 'version':client['version'], 'session':['session']}
   r = requests.post("http://%s:%s/hello" % (ip,port), json=post)
   print (r.text)
   
   return redirect('/ui/sessions/s?id=%s' % (session,))

@app.route('/ui/sessions/s', methods=['GET'])
def ui_session_show():
   s = model.get_session(request.args.get('id', ''))

   return """
     [ <a href="/ui/sessions">back</a> ]
     <table>
     <tr><td>Session ID:</td><td>%s</td></tr>
     </table>
     <br/>
   """ % (s['session_id'],)

