#!/bin/sh

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL is ready!"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting the application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug &

# Wait for the application to be ready
echo "Waiting for the application to be ready..."
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
  if curl -s http://localhost:8000/health-check > /dev/null; then
    echo "Application is ready!"
    break
  fi
  echo "Attempt $attempt of $max_attempts: Application not ready yet..."
  sleep 1
  attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
  echo "Application failed to start within the expected time"
  exit 1
fi

# Keep the container running
wait 