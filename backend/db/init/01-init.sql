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

-- Create the project_finder user if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'project_finder') THEN
      CREATE USER project_finder WITH PASSWORD 'project_finder_password_2024';
   END IF;
END
$do$;

-- Grant privileges to project_finder
ALTER USER project_finder WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE project_finder TO project_finder;

-- Connect to project_finder database
\c project_finder

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO project_finder; 