#!/bin/bash

# Database Configuration
export DATABASE_URL=

# Redis Configuration
export REDIS_URL=

# OpenAI Configuration
export OPENAI_API_KEY=

# MinIO Configuration
export MINIO_ACCESS_KEY="minioadmin"
export MINIO_SECRET_KEY="minioadmin"
export MINIO_BUCKET="faraday-media"

# Grafana Configuration
export GRAFANA_ADMIN_PASSWORD="admin"

# Service Configuration
export LOG_LEVEL="INFO"
export API_PORT="8000"
export METRICS_PORT="9090"
export SERVICE_TYPE="pe"

# Stop running containers
echo "Stopping running containers..."
docker-compose down

# Rebuild containers without cache
echo "Rebuilding containers..."
docker-compose build --no-cache

# Start specific services
echo "Starting services..."
docker-compose up app pe-video-processor pe-movement-analyzer prometheus grafana 
