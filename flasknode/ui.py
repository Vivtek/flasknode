# Clunky old-school UI for old-school dinosaur developers
from flasknode import app, db, model, api
from flask import request, redirect

# ---------------------------------------------------------------------------------------------------
# Status and settings
# ---------------------------------------------------------------------------------------------------

# UI /status = API /client
@app.route('/status')
def status():
   client = api.get_client()
   #print ([client[x] for x in ['node', 'cur', 'nickname', 'version']])
   return """
      <table>
      <tr><td>Node:</td><td>%s</td></td>
      <tr><td>Current:</td><td>%s</td></tr>
      <tr><td>Nickname:</td><td>%s [ <a href='/ui/settings/edit'>edit</a> ]</td></tr>
      <tr><td>Version:</td><td>%s</td></tr>
      </table>
      
      <a href="/ui/messages">Messages</a> (%s)<br>
      <a href="/ui/sessions">Sessions</a>
   """ % tuple([client[x] for x in ['node', 'cur', 'nickname', 'version', 'messages']])

# UI settings/edit -> missing in API (because it's just the setup for the posting screen)
@app.route('/ui/settings/edit')
def ui_settings_editor():
   client = api.get_client()
   return """
      <form action="/ui/settings/update" method="post">
      <label for="nickname">Nickname:</label> <input type="text" id="nickname" name="nickname" value="%s"><br/>
      <input type="submit" value="Update">
      </form>
   """ % client['nickname']

# UI settings/update -> missing in API (and needs to be added)
@app.route('/ui/settings/update', methods=['POST'])
def ui_settings_update():
   id = model.set_nickname(request.form['nickname'])
   return redirect('/status')

# ---------------------------------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------------------------------

# UI messages = API /message/list
@app.route('/ui/messages')
def ui_messages():
   s = request.args.get('s', None)
   m = api.message_list(server=s)
   heading = ''
   tracer = ''
   post_s = ''
   if s != None:
      server = model.get_session (s)
      heading = "Messages on '%s' (session %s):<br>" % (server['nickname'], s)
      tracer = '&s=%s' % s
      post_s = '<input type="hidden" id="s" name="s" value="%s">' % s

   def enlist (message):
      if message['comments'] > 0:
         count = " (%d)" % message['comments']
      else:
         count = ""
      return '<li>%s (%s) - <a href="/ui/messages/m?id=%s%s">%s</a>%s</li>' % (message['user'], message['date'], message['id'], tracer, message['subject'], count)
   form = """
      <form action="/ui/messages/post" method="post">
      %s
      <label for="subject">Subject:</label> <input type="text" id="subject" name="subject"><br/>
      <textarea id="message" name="message" rows="3" cols="80"></textarea><br/>
      <input type="submit" value="Post message">
      </form>
   """ % post_s
   if len(m):
      return """
         %s
         <ul>
         %s
         </ul>
         %s
      """ % (heading, "<br/>".join(map(enlist, m)), form)
   else:
      return "%s No messages on node<br/>%s" % (heading, form)

# UI messages/post = API /message/post
@app.route('/ui/messages/post', methods=['POST'])
def ui_message_post():
   s = request.form.get('s', None)
   tracer = ''
   if s != None:
      tracer = '&s=%s' % s

   id = api.message_post (request.form['subject'], request.form['message'], server=s)
   return redirect('/ui/messages/m?id=%s%s' % (id, tracer))


# UI messages/m = API /message
@app.route('/ui/messages/m', methods=['GET'])
def ui_message_show():
   s = request.args.get('s', None)
   m = api.get_message(request.args.get('id', ''), server=s)
   heading = ''
   tracer1 = ''
   tracer2 = ''
   post_s = ''
   if s != None:
      server = model.get_session (s)
      subscribe = '[ <a href="/ui/messages/subscribe?id=%s&s=%s">subscribe</a> ]' % (m['id'], s)
      heading = "<tr><td>Message on:</td><td>'%s' (session %s) %s</td></tr>" % (server['nickname'], s, subscribe)
      tracer1 = '&s=%s' % s
      tracer2 = '?s=%s' % s
      post_s = '<input type="hidden" id="s" name="s" value="%s">' % s
   
   
   def enlist (comment):
      return '<li>%s (%s)<br/>%s</li>' % (comment['user'], comment ['date'], comment['message'])
   form = """
      <form action="/ui/messages/comment" method="post">
      %s
      <input type="hidden" id="parent" name="parent" value="%s">
      <input type="hidden" id="subject" name="subject" value="">
      <textarea id="message" name="message" rows="3" cols="80"></textarea><br/>
      <input type="submit" value="Comment">
      </form>
   """ % (post_s, m['id'])
   
   return """
     [ <a href="/ui/messages%s">back</a> ]
     <table>
     %s
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
   """ % (tracer2, heading, m['id'], m['date'], m['user'], m['subject'], m['message'], "<br/>".join(map(enlist, m['comments'])), form)
   
# UI messages/subscribe --> No API yet
@app.route('/ui/messages/subscribe', methods=['GET'])
def ui_message_subscribe():
   s = request.form.get('s', None)
   m = request.form.get('id', None)
   tracer = ''
   if s == None:
      return redirect('/ui/messages/m/id=%s' % id)
      
   id = api.check_or_make_subscription (s, m, make=True)
   return redirect('/ui/messages/m?id=%s' % id)



# ---------------------------------------------------------------------------------------------------
# Comments (reading happens with the messages; this is just posting)
# ---------------------------------------------------------------------------------------------------

# UI messages/comment = API /comment/post
@app.route('/ui/messages/comment', methods=['POST'])
def ui_comment_post():
   s = request.form.get('s', None)
   tracer = ''
   if s != None:
      tracer = '&s=%s' % s
      
   id = api.comment_post (request.form['parent'], request.form['subject'], request.form['message'], server=s)
   return redirect('/ui/messages/m?id=%s%s' % (request.form['parent'], tracer))

# ---------------------------------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------------------------------

# UI sessions = API /session/list
@app.route('/ui/sessions')
def ui_sessions():
   def enlist (session):
      if session['nickname'] == None:
         return '<li>[<a href="/ui/sessions/s?id=%s">?</a>] %s</li>' % (session['session'], session['node'])
      else:
         return '<li>[<a href="/ui/sessions/s?id=%s">?</a>] %s (%s)</li>' % (session['session'], session['nickname'], session['node'])
   s = api.get_sessions()
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

# UI sessions/s = API session
@app.route('/ui/sessions/s', methods=['GET'])
def ui_session_show():
   s = api.get_session(request.args.get('id', ''))

   return """
     [ <a href="/ui/sessions">back</a> ]
     <table>
     <tr><td>Session ID:</td><td>%s</td></tr>
     <tr><td>Node:</td><td>%s</td></tr>
     <tr><td>Nickname:</td><td>%s</td></tr>
     <tr><td>IP:</td><td>%s:%s</td></tr>
     </table>
     <br/>
     <a href="/ui/messages?s=%s">See feed</a>
   """ % tuple([s[x] for x in ['session', 'node', 'nickname', 'ip', 'port', 'session']])

# UI sessions/connect = API /session/connect
@app.route('/ui/sessions/connect', methods=['POST'])
def ui_session_connect():
   session = api.session_connect (request.form['ip'], request.form['port'])
   
   return redirect('/ui/sessions/s?id=%s' % (session,))


