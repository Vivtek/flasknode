from flasknode import app, db
from flasknode import socketio

def get_client():
   user = db.query ('select user_handle from user where user_id=1', one=True)
   client = db.query ('select * from client limit 1', one=True)
   messages = db.query ('select count(*) as c from message', one=True)
   return {
      'client_id': client['client_id'],
      'node_id':   client['node_id'],
      'version':   client['version'],
      'nickname':  user['user_handle'],
      'messages':  messages['c']
   }
   
def set_nickname(nickname):
   db.do ('update user set user_handle=? where user_id=1', (nickname,))
   return
   
def get_curver():
   max = db.query('select max(message_id) as m from message where node_id="" and parent is null', one=True)
   if max['m'] == None:
      return 0
   cmax = db.query('select max(c.message_id) as m from message c inner join message p on c.parent=p.message_id where p.node_id=""', one=True)
   if cmax['m'] == None:
      return max['m']
   if cmax['m'] > max['m']:
      return cmax['m']
   return max['m']

def new_message(subject, message):
   row = db.insert ('insert into message (user_id, subject, message, create_date) values (1, ?, ?, CURRENT_TIMESTAMP)', (subject, message))
   socketio.emit('feed', get_message(row), room='feed', json=True)
   return row
   
def zero_messages():
   ret = db.do ('delete from message')

def get_messages(last=20):
   def extract(row):
      node = row['node']
      if node == None:
         node = ''
      return {'node':node, 'id':row['id'], 'user_id':row['user_id'], 'user':row['user'], 'date':row['date'], 'subject':row['subject'], 'comments':row['comments']}
   messages = db.query ("""
    select       p.node_id as node, u.user_id as user_id, u.user_handle as user, p.message_id as id, p.create_date as date, p.subject, count(c.message_id) as comments
           from  message p left join message c on c.parent=p.message_id left join user u on p.user_id=u.user_id
          where  p.parent is null
       group by  p.message_id
       order by  p.create_date desc
       limit %d
   """ % (last,))
   return list(map (extract, messages))

def get_message(msgid):
   def extract(row):
      return {'user_id':row['user_id'], 'user':row['user'], 'date':row['date'], 'message':row['message']}
      
   message = db.query ("""
      select m.message_id as id, m.user_id as user_id, u.user_handle as user, m.subject as subject, m.create_date as date, m.message as message
        from message m left join user u on m.user_id=u.user_id
       where m.message_id=?
   """, (msgid,), one=True)
   comments = list(map (extract, db.query ("""
      select m.message_id as id, m.user_id as user_id, u.user_handle as user, m.create_date as date, m.message as message
        from message m left join user u on m.user_id=u.user_id
       where parent=?
   """, (msgid,))))
   return {'id':message['id'], 'user_id':message['user_id'], 'user':message['user'], 'subject':message['subject'],
            'date':message['date'], 'message':message['message'], 'comments':comments
           }
   
def new_comment(parent, subject, message):
   row = db.insert ('insert into message (user_id, parent, subject, message, create_date) values (1, ?, ?, ?, CURRENT_TIMESTAMP)', (parent, subject, message))
   #socketio.emit('feed', get_message(row), room='feed', json=True)
   return row

def get_updates(from_id):
   def extract (row):
      node = row['node_id']
      if node == '':
         node = app.this_node
      return {'id':row['message_id'], 'node':node, 'ver':row['ver']}
      
   query = """
      select p.message_id, p.node_id, max (p.message_id, coalesce(max(c.message_id), 0)) as ver
      from message p left join message c on c.parent=p.message_id
      where p.parent is null and (c.message_id > ? or p.message_id > ?)
      group by p.message_id
   """
   return list(map (extract, db.query (query, (from_id,from_id))))

def get_sessions():
   sessions = db.query ("""
    select       s.node_id as node, n.nickname as nickname, s.session_id as session, s.their_session as their_session, s.ip, s.port
           from  session s left join nodes n on s.node_id = n.node_id
   """)
   def extract(row):
      return {
         'node':          row['node'],
         'nickname':      row['nickname'],
         'session':       row['session'],
         'their_session': row['their_session'],
         'ip':            row['ip'],
         'port':          row['port']
      }
   return list(map (extract, sessions))

def get_session(sessid):
   session = db.query ("""
    select       s.node_id as node, n.nickname as nickname, s.session_id as session, s.their_session as their_session, s.ip, s.port
           from  session s left join nodes n on s.node_id = n.node_id
          where  session=?
   """, (sessid,), one=True)
   return {
      'session':  session['session'],
      'node':     session['node'],
      'nickname': session['nickname'],
      'ip':       session['ip'],
      'port':     session['port']
   }

def verify_session(node, ip, port):
   srec = db.query('select session_id, ip, port from session where node_id=?', (node,), one=True)
   if srec != None:
      if srec['ip'] != ip or srec['port'] != port:
         db.do('delete from session where session_id=?', (srec['session_id'],))
         srec = None
      else:
         return srec['session_id']
   session = db.insert ('insert into session (node_id, ip, port, started) values (?, ?, ?, CURRENT_TIMESTAMP)', (node, ip, port))
   return session

   
def update_session(sessid, their_session):
   db.do ('update session set their_session=? where session_id=?', (their_session, sessid))


def verify_node(node, nickname, cur):
   nrec = db.query('select node_id, nickname, latest from nodes where node_id=?', (node,), one=True)
   if nrec == None:
      db.insert ('insert into nodes (node_id, nickname, latest) values (?, ?, ?)', (node, nickname, cur))
   else:
      db.do ('update nodes set latest=? where node_id=?', (cur, node))
   return 1
   
def update_swarm(node, ip, port):
   db.do ('delete from swarm where ip=? and port=?', (ip, port))
   db.insert ('insert into swarm (ip, port, node_id, last_contact) values (?, ?, ?, CURRENT_TIMESTAMP)', (ip, port, node))


