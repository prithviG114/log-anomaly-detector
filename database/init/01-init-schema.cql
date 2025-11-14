-- Create keyspace
CREATE KEYSPACE IF NOT EXISTS logs
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};

-- Use the keyspace
USE logs;

-- Create table
CREATE TABLE IF NOT EXISTS logs_table (
  id uuid PRIMARY KEY,
  service_name text,
  message text,
  timestamp bigint,
  is_anomaly boolean,
  score double
);

-- Create indexes for filtering
CREATE INDEX IF NOT EXISTS logs_service_name_idx ON logs.logs_table (service_name);
CREATE INDEX IF NOT EXISTS logs_is_anomaly_idx ON logs.logs_table (is_anomaly);





