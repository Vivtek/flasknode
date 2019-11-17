from flasknode import app, db

def new_message(message):
   print (message)
   row = db.insert ('insert into message (user_id, message, create_date) values (0, ?, CURRENT_TIMESTAMP)', (message,))

