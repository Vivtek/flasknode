-- 
-- Created by SQL::Translator::Producer::SQLite
-- Created on Sat Feb  8 17:52:34 2020
-- 

BEGIN TRANSACTION;

--
-- Table: client
--
CREATE TABLE client (
  client_id INTEGER PRIMARY KEY NOT NULL,
  node_id text,
  version text
);

--
-- Table: message
--
CREATE TABLE message (
  message_id INTEGER PRIMARY KEY NOT NULL,
  parent text,
  node_id text,
  user_id text,
  type_id text,
  subject text,
  message text,
  create_date timestamp
);

--
-- Table: swarm
--
CREATE TABLE swarm (
  ip text,
  port int,
  node_id text,
  last_contact timestamp,
  current int
);

--
-- Table: nodes
--
CREATE TABLE nodes (
  node_id text,
  nickname text,
  latest text
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

COMMIT;

