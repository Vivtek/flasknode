-- 
-- Created by SQL::Translator::Producer::SQLite
-- Created on Sun Nov 10 22:19:56 2019
-- 

BEGIN TRANSACTION;

--
-- Table: client
--
CREATE TABLE client (
  client_id INTEGER PRIMARY KEY NOT NULL,
  version text
);

--
-- Table: message
--
CREATE TABLE message (
  message_id INTEGER PRIMARY KEY NOT NULL,
  user_id text,
  type_id text,
  subject text,
  message text,
  create_date timestamp
);

--
-- Table: user
--
CREATE TABLE user (
  user_id INTEGER PRIMARY KEY NOT NULL,
  user_handle text,
  password text,
  create_date timestamp
);

--
-- Table: message_user_map
--
CREATE TABLE message_user_map (
  message_user_id INTEGER PRIMARY KEY NOT NULL,
  message_id text,
  user_id text,
  create_date timestamp
);

--
-- Table: message_message_map
--
CREATE TABLE message_message_map (
  message_map_id INTEGER PRIMARY KEY NOT NULL,
  previous_message_id text,
  new_message_id text,
  create_date timestamp
);

COMMIT;

