-- create keyspace
CREATE KEYSPACE IF NOT EXISTS logs
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};

-- use the keyspace
USE logs;

-- table for simple logs
CREATE TABLE IF NOT EXISTS logs_table (
  id uuid PRIMARY KEY,
  service_name text,
  message text,
  timestamp bigint,
  is_anomaly boolean,
  score double
);
