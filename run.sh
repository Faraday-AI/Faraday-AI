#!/bin/bash

# Database Configuration
export DATABASE_URL="postgresql://faraday_admin:CodaMoeLuna31@faraday-ai.postgres.database.azure.com:5432/postgres?sslmode=require&connect_timeout=50&keepalives=1&keepalives_idle=50&keepalives_interval=30&keepalives_count=5&application_name=faraday_ai&target_session_attrs=read-write"

# Redis Configuration
export REDIS_URL="redis://redis:6379/0"

# OpenAI Configuration
export OPENAI_API_KEY="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"

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