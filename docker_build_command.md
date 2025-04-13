# Docker Build Commands

## Environment Variables Setup
```bash
export DATABASE_URL="postgresql://faraday_admin:CodeMeLuna31@faraday-ai.postgres.database.azure.com:5432/postgres?sslmode=require&connect_timeout=50&keepalives=1&keepalives_idle=50&keepalives_interval=30&keepalives_count=5&application_name=faraday_ai&target_session_attrs=read-write" && \
export REDIS_URL="redis://redis:6379/0" && \
export OPENAI_API_KEY="sk-svcacct-bVHSKIfV87b_mejrPq7aatofeLJXrAw4wZ1lirmyYhqhHh-qR-FFusP0SLhDw4v0eBoZjNsNqYI3BlbkFJTqXCY1mSfANsqZahF788S3DZSq2IOwgL_h4HjQvzvJSLGFsU1pFqR6ISFn_jA6GsIgyoZ2XXkA" && \
export GRAFANA_ADMIN_PASSWORD="admin" && \
export MINIO_ACCESS_KEY="minioadmin" && \
export MINIO_SECRET_KEY="minioadmin" && \
export MINIO_BUCKET="faraday-media" && \
export LOG_LEVEL="INFO" && \
export API_PORT="8000" && \
export METRICS_PORT="9090" && \
export SERVICE_TYPE="pe"
```

## Docker Commands
```bash
docker-compose down && \
docker-compose build --no-cache && \
docker-compose up app pe-movement-analyzer
```

## Notes
- These commands will:
  1. Stop any running containers
  2. Build all services without using cache
  3. Start only the app and pe-movement-analyzer services
- The environment variables include:
  - Database connection settings
  - Redis configuration
  - OpenAI API credentials
  - MinIO storage settings
  - Service ports and logging configuration 