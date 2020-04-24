from flasknode import app, db
from flasknode import socketio

def get_client():
   return db.query('select * from client limit 1', one=True)
   
def get_curver():
   max = db.query('select max(message_id) as m from message where node_id is null and parent is null', one=True)
   if max['m'] == None:
      return 0
   cmax = db.query('select max(c.message_id) as m from message c inner join message p on c.parent=p.message_id where p.node_id is null', one=True)
   if cmax['m'] == None:
      return max['m']
   if cmax['m'] > max['m']:
      return cmax['m']
   return max['m']

def new_message(subject, message):
   row = db.insert ('insert into message (user_id, subject, message, create_date) values (0, ?, ?, CURRENT_TIMESTAMP)', (subject, message))
   socketio.emit('feed', get_message(row), room='feed', json=True)

def get_message(msgid):
   def extract(row):
      node = row['node_id']
      if node == None:
         node = ''
      return {'node':node, 'date':message['create_date'], 'message':row['message']}
      
   message = db.query ('select * from message where message_id=?', (msgid,), one=True)
   comments = list(map (extract, db.query ('select * from message where parent=?', (msgid,))))
   return {'id':message['message_id'], 'subject':message['subject'], 'date':message['create_date'], 'message':message['message'], 'comments':comments}
   
def new_comment(parent, subject, message):
   row = db.insert ('insert into message (user_id, parent, subject, message, create_date) values (0, ?, ?, ?, CURRENT_TIMESTAMP)', (parent, subject, message))
   #socketio.emit('feed', get_message(row), room='feed', json=True)

def get_updates(from_id):
   def extract (row):
      node = row['node_id']
      if node == None:
         node = app.this_node
      return {'id':row['message_id'], 'node':node, 'ver':row['ver']}
      
   query = """
      select p.message_id, p.node_id, max (p.message_id, coalesce(max(c.message_id), 0)) as ver
      from message p left join message c on c.parent=p.message_id
      where p.parent is null and (c.message_id > ? or p.message_id > ?)
      group by p.message_id
   """
   return list(map (extract, db.query (query, (from_id,from_id))))

