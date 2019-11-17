from flasknode import app
import sqlite3
import os
from flask import g

def db_path():
   return os.path.join (app.instance_path, 'local_node.sqlt')

def get_db():
   db = getattr(g, '_database', None)
   if db is None:
      database = db_path()
      exists = os.path.exists(database);
      db = g._database = sqlite3.connect(database)
      if not exists:
         cur = db.cursor()
         with app.open_resource('schema.sql', mode='r') as f:
            cur.executescript(f.read())
         cur.execute('insert into client(client_id, version) values (0, 0.1)')
         db.commit()
   db.row_factory = sqlite3.Row
   return db

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

def insert (sql, args):
   db = get_db()
   cur = db.cursor()
   cur.execute (sql, args)
   db.commit()
   cur.close()
   return cur.lastrowid
