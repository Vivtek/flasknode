from flasknode import app
import sqlite3
import os
from flask import g
import uuid

def db_path():
   return os.path.join (app.instance_path, 'local_node.sqlt')

def get_db():
   db = getattr(g, '_database', None)
   if db is None:
      database = db_path()
      exists = os.path.exists(database)
      db = g._database = sqlite3.connect(database)
      if not exists:
         create_db(db)
      node_result = query('select node_id from client limit 1', one=True)
      app.this_node = node_result['node_id']
   db.row_factory = sqlite3.Row
   return db
   
def create_db(db):
   cur = db.cursor()
   with app.open_resource('schema.sql', mode='r') as f:
      cur.executescript(f.read())
   node_id = uuid.uuid4()
   cur.execute('insert into client(client_id, version, node_id) values (0, ?, ?)', (0.1, str(node_id)))
   db.commit()


@app.teardown_appcontext
def close_connection(exception):
   db = getattr(g, '_database', None)
   if db is not None:
      db.close();

def query (query, args=(), one=False):
   cur = get_db().execute(query, args)
   rv = cur.fetchall()
   cur.close()
   return (rv[0] if rv else None) if one else rv

def insert (sql, args=()):
   db = get_db()
   cur = db.cursor()
   cur.execute (sql, args)
   db.commit()
   cur.close()
   return cur.lastrowid
   
def do (sql, args=()):
   db = get_db()
   cur = db.cursor()
   cur.execute (sql, args)
   db.commit()
   cur.close()
   
