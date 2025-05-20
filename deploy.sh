#!/bin/bash

# Exit on error
set -e

echo "Starting deployment process..."

# Load environment variables
if [ -f .env.production ]; then
    echo "Loading production environment variables..."
    export $(cat .env.production | grep -v '^#' | xargs)
else
    echo "Warning: .env.production file not found. Using default values."
fi

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Pull latest changes
echo "Pulling latest changes..."
git pull origin main

# Build and start containers
echo "Building and starting containers..."
docker-compose up -d --build

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 30

# Check if services are running
echo "Checking service health..."
if curl -f http://localhost:8000/health; then
    echo "Backend is healthy!"
else
    echo "Backend health check failed!"
    exit 1
fi

if curl -f http://localhost:3000; then
    echo "Frontend is healthy!"
else
    echo "Frontend health check failed!"
    exit 1
fi

echo "Deployment completed successfully!" 