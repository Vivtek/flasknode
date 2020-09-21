-- 
-- Created by SQL::Translator::Producer::SQLite
-- Created on Sat Feb  8 17:52:34 2020
-- 

BEGIN TRANSACTION;

--
-- Table: client
-- This just holds information about the node, primarily its node ID.
--
CREATE TABLE client (
  client_id INTEGER PRIMARY KEY NOT NULL,
  node_id text,
  version text
);

--
-- Table: message
-- The message table contains all our content.
--
CREATE TABLE message (
  message_id INTEGER PRIMARY KEY NOT NULL,
  parent text,
  node_id text default '',   -- If this message is a subscription, this is its canonical location
  node_msg_id int default 0,
  node_src text default '',  -- If this message is a subscription, this is our source for it
  user_id int default 0,
  type_id text,
  subject text,
  message text,
  create_date timestamp
);

--
-- Table: nodes
-- Lists the other nodes we know about.
--
CREATE TABLE nodes (
  node_id text,
  nickname text,
  latest int
);

--
-- Table: swarm
-- Keeps track of where we have seen the nodes we know about.
--
CREATE TABLE swarm (
  ip text,
  port int,
  node_id text,
  last_contact timestamp
);

--
-- Table: session
-- Currently active sessions between us and other nodes.
--
CREATE TABLE session (
  session_id INTEGER PRIMARY KEY NOT NULL,
  node_id text,
  their_session int,
  started timestamp,
  our_cur int,
  their_cur int
);

--
-- Table: subscriber
-- Other nodes who have subscribed to our messages. (Our own subscriptions are simply in the message table.)
--
CREATE TABLE subscriber (
  node_id text,
  message_id int,
  subscribed_at int,
  last_update int
);


--
-- Table: user
-- Users we know personally (either those who log into our node or those we know from other nodes)
--
CREATE TABLE user (
  user_id INTEGER PRIMARY KEY NOT NULL,
  node_id text,
  ext_user_id int,
  user_handle text,
  password text,
  create_date timestamp
);
insert into user (user_id, user_handle) values (1, '');  -- Our user #1 is our null user and has no handle until one is assigned through the UI or API

COMMIT;

