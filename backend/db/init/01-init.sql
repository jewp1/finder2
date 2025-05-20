-- Create database if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database
      WHERE  datname = 'project_finder') THEN
      CREATE DATABASE project_finder;
   END IF;
END
$do$;

-- Create extensions in the project_finder database
\c project_finder;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto"; 