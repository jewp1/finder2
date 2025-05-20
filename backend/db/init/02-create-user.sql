-- Create the project_finder user
CREATE USER project_finder WITH PASSWORD 'project_finder_password_2024';

-- Grant privileges to project_finder
ALTER USER project_finder WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE project_finder TO project_finder;

-- Connect to project_finder database
\c project_finder;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO project_finder;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO project_finder;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO project_finder;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO project_finder;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO project_finder; 