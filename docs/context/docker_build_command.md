# Docker Build Commands

## Environment Variables Setup
```bash
# Core Configuration
export PORT=8000
export API_PORT=8000
export APP_METRICS_PORT=9091
export WEBSOCKET_PORT=9100
export LOG_LEVEL="INFO"

# Database Configuration
export DATABASE_URL="postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require"

# Redis Configuration
export REDIS_PORT=6379
export REDIS_URL="redis://redis:6379/0"

# MinIO Configuration
export MINIO_ACCESS_KEY="minioadmin"
export MINIO_SECRET_KEY="minioadmin"
export MINIO_BUCKET="faraday-media"

# Monitoring Configuration
export PROMETHEUS_PORT=9090
export GRAFANA_PORT=3000
export GRAFANA_ADMIN_PASSWORD="admin"

# OpenAI Configuration
export OPENAI_API_KEY="your-api-key-here"

# Service Configuration
export SERVICE_TYPE="pe"
```

## Docker Commands

### Basic Build and Run
```bash
# Build and start all services
docker-compose up -d

# Build and start specific services
docker-compose up -d app pe-video-processor pe-movement-analyzer prometheus grafana

# Build without cache
docker-compose build --no-cache

# Stop all services
docker-compose down
```

### Development Commands
```bash
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f app

# Rebuild specific service
docker-compose up -d --build app

# Check service health
docker-compose ps
```

### Cleanup Commands
```bash
# Remove all containers and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Clean system
docker system prune -a
```

## Service Ports
- Main Application: 8000
- Metrics: 9091
- WebSocket: 9100
- Redis: 6379
- MinIO: 9002 (API), 9003 (Console)
- Prometheus: 9090
- Grafana: 3000

## Volume Mounts
- Application Code: ./app:/app/app
- Models: ./models:/app/models
- Static Files: ./static:/app/static
- Logs: ./logs:/app/logs
- Exports: ./exports:/app/exports
- Redis Data: redis_data:/data
- MinIO Data: minio_data:/data
- Grafana Data: grafana_data:/var/lib/grafana

## Notes
- The application uses a multi-stage Docker build for optimization
- All services run in a custom bridge network (faraday-network)
- Health checks are implemented for critical services
- Environment variables can be overridden using a .env file
- The application runs as a non-root user (appuser) for security 