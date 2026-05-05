-- Grant schema privileges to project_finder user (created in 01-init.sql)
\c project_finder;

GRANT ALL ON SCHEMA public TO project_finder;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO project_finder;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO project_finder;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO project_finder;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO project_finder;
