# Complete Docker Guide

## Table of Contents
1. [Introduction to Docker](#introduction-to-docker)
2. [Getting Started](#getting-started)
3. [Basic Docker Commands](#basic-docker-commands)
4. [Working with Images](#working-with-images)
5. [Working with Containers](#working-with-containers)
6. [Docker Compose](#docker-compose)
7. [Networking](#networking)
8. [Volumes and Storage](#volumes-and-storage)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)
11. [Faraday AI Specific Setup](#faraday-ai-specific-setup)

## Introduction to Docker

Docker is a platform that allows you to package, distribute, and run applications in containers. Containers are lightweight, standalone, and executable packages that include everything needed to run a piece of software, including the code, runtime, system tools, system libraries, and settings.

### Key Concepts
- **Image**: A read-only template with instructions for creating a container
- **Container**: A runnable instance of an image
- **Dockerfile**: A text file containing instructions for building an image
- **Docker Hub**: A cloud-based registry service for sharing Docker images
- **Docker Compose**: A tool for defining and running multi-container applications

## Getting Started

### Installation
1. **Mac**:
   - Download Docker Desktop from [Docker's website](https://www.docker.com/products/docker-desktop)
   - Install the .dmg file
   - Start Docker Desktop from Applications

2. **Windows**:
   - Download Docker Desktop from [Docker's website](https://www.docker.com/products/docker-desktop)
   - Run the installer
   - Start Docker Desktop from the Start menu

3. **Linux**:
   ```bash
   # Update package index
   sudo apt-get update

   # Install prerequisites
   sudo apt-get install -y \
       apt-transport-https \
       ca-certificates \
       curl \
       gnupg \
       ls-release

   # Add Docker's official GPG key
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

   # Set up the stable repository
   echo \
     "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
     $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

   # Install Docker Engine
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io

   # Add your user to the docker group
   sudo usermod -aG docker $USER
   ```

### Verifying Installation
```bash
# Check Docker version
docker --version

# Verify Docker is running
docker run hello-world
```

## Basic Docker Commands

### System Commands
```bash
# Check Docker system information
docker info

# Check Docker version
docker version

# Check Docker disk usage
docker system df

# Clean up unused data
docker system prune
```

### Image Commands
```bash
# List all images
docker images

# Pull an image
docker pull image_name:tag

# Remove an image
docker rmi image_name

# Build an image from Dockerfile
docker build -t image_name:tag .

# Search for images on Docker Hub
docker search image_name
```

### Container Commands
```bash
# Run a container
docker run [options] image_name

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop a container
docker stop container_name

# Start a stopped container
docker start container_name

# Remove a container
docker rm container_name

# View container logs
docker logs container_name

# Execute command in running container
docker exec -it container_name /bin/bash
```

### Common Run Options
- `-d`: Run container in detached mode (background)
- `-p host_port:container_port`: Map ports
- `-v host_path:container_path`: Mount volumes
- `--name`: Give container a specific name
- `-e`: Set environment variables
- `--network`: Specify network
- `--restart`: Set restart policy
- `-it`: Interactive terminal

## Working with Images

### Creating a Dockerfile
```dockerfile
# Use an official base image
FROM node:14

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start command
CMD ["npm", "start"]
```

### Building Images
```bash
# Basic build
docker build -t myapp:1.0 .

# Build with no cache
docker build --no-cache -t myapp:1.0 .

# Build with build arguments
docker build --build-arg VERSION=1.0 -t myapp:1.0 .
```

## Working with Containers

### Container Lifecycle
1. **Create**: `docker create`
2. **Start**: `docker start`
3. **Run**: `docker run` (create + start)
4. **Stop**: `docker stop`
5. **Remove**: `docker rm`

### Container Management
```bash
# Rename container
docker rename old_name new_name

# Pause container
docker pause container_name

# Unpause container
docker unpause container_name

# View container details
docker inspect container_name

# View container resources usage
docker stats container_name
```

## Docker Compose

### Basic docker-compose.yml
```yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
    environment:
      - NODE_ENV=development
  db:
    image: postgres:13
    environment:
      - POSTGRES_PASSWORD=secret
```

### Docker Compose Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs

# Rebuild services
docker-compose up -d --build

# Scale services
docker-compose up -d --scale service_name=3
```

## Faraday AI Specific Setup

### Project Structure
```
Faraday-AI/
├── Dockerfile              # Multi-stage build for all services
├── docker-compose.yml     # Multi-container orchestration
├── .dockerignore         # Files to exclude from builds
├── app/                  # Application code
│   ├── main.py          # FastAPI application
│   └── services/        # Service modules
├── models/              # ML model storage
├── static/             # Static files
├── logs/               # Application logs
└── exports/            # Export data
```

### Multi-Container Architecture
Our application consists of the following services:
- **Main Application (app)**: FastAPI backend with core services
- **PE Video Processor**: Handles video analysis and processing
- **PE Movement Analyzer**: Manages movement tracking and analysis
- **Redis**: In-memory data store and message broker
- **MinIO**: Object storage for media files
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **Exports**: Handles data export operations

### Environment Configuration
```bash
# Core Configuration
PORT=8000                  # Main application port
API_PORT=8000             # API port
APP_METRICS_PORT=9091     # Application metrics port
WEBSOCKET_PORT=9100       # WebSocket port
LOG_LEVEL=INFO           # Logging level

# Database Configuration
DATABASE_URL=postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require

# Redis Configuration
REDIS_PORT=6379         # Redis port
REDIS_URL=              # Redis connection string

# MinIO Configuration
MINIO_ACCESS_KEY=       # MinIO access key
MINIO_SECRET_KEY=       # MinIO secret key
MINIO_BUCKET=          # MinIO bucket name

# Monitoring
PROMETHEUS_PORT=9090    # Prometheus port
GRAFANA_PORT=3000      # Grafana port

# API Keys
OPENAI_API_KEY=        # OpenAI API key
```

### Volume Management
```yaml
volumes:
  # Application Volumes
  - ./app:/app/app           # Application code
  - ./models:/app/models     # ML models
  - ./static:/app/static     # Static files
  - ./logs:/app/logs        # Application logs
  - ./exports:/app/exports  # Export data
  
  # Persistent Data Volumes
  - redis_data:/data        # Redis data
  - minio_data:/data       # MinIO data
  - grafana_data:/var/lib/grafana  # Grafana data
```

### Security Features
1. Multi-stage Docker builds for smaller images
2. Non-root user (appuser) for container execution
3. Environment variable configuration
4. Health checks for critical services
5. Custom bridge network isolation
6. Secure volume permissions

### Health Checks
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Development Workflow
1. Set up environment variables
2. Start required services:
   ```bash
   docker-compose up -d
   ```
3. Monitor logs:
   ```bash
   docker-compose logs -f [service_name]
   ```
4. Make code changes
5. Rebuild affected services:
   ```bash
   docker-compose up -d --build [service_name]
   ```

### Common Issues and Solutions

#### Service Dependencies
- Ensure Redis is running before dependent services
- Check MinIO bucket exists and is accessible
- Verify database connection settings

#### Resource Management
```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2'
```

#### Model Loading
- Models are generated during build
- Check model paths in environment variables
- Verify model file permissions

### Production Deployment
1. Set production environment variables
2. Use production-ready database settings
3. Configure proper logging
4. Set up monitoring alerts
5. Enable health check monitoring

### Monitoring Setup
1. Prometheus metrics collection
2. Grafana dashboards for visualization
3. Application-level metrics
4. Container resource monitoring
5. Custom alert rules

### Backup Strategy
1. Database backups
2. MinIO data backups
3. Model version control
4. Log rotation
5. Export data management

### Development Workflow
1. Make code changes
2. Rebuild affected containers
3. Test locally
4. Push changes to repository
5. Deploy to production

### Production Deployment
- Use `render.yaml` for Render.com deployment
- Configure environment variables in production
- Set up proper monitoring and logging
- Implement health checks

### Monitoring and Logging
```bash
# View container logs
docker-compose logs -f

# Check container health
docker-compose ps

# Monitor resource usage
docker stats
```

### Security Best Practices
1. Use `.dockerignore` to exclude sensitive files
2. Never store secrets in Dockerfiles
3. Use environment variables for configuration
4. Regularly update base images
5. Implement proper access controls 

### Current Database Validation Process (Updated April 2024)

### Validation Script Output
The validation script (`app/scripts/validate_data.py`) provides detailed output in the following format:

1. Table Counts:
   ```
   users: 3 records
   user_memories: 6 records
   memory_interactions: 12 records
   activities: 44 records
   lessons: 3 records
   subject_categories: 5 records
   students: 8 records
   classes: 4 records
   safety_checks: 20 records
   ```

2. Relationship Validation:
   - User-Memory Relationships (2 memories per user)
   - Activity Category Relationships (multiple categories per activity)
   - Parent-Child Category Hierarchies (5 main categories with subcategories)

3. Activity Details:
   - Activity Assignments with Type and Difficulty
   - Category Associations
   - Full Path Information

4. Category Hierarchy Analysis:
   - Validates category structure
   - Checks parent-child relationships
   - Verifies activity distribution

### Current Validation Commands
```bash
# Validate database state
docker-compose exec app python -m app.scripts.validate_data

# Seed final balance activities
docker-compose exec app python -m app.scripts.seed_data.seed_final_balance
```

### Validation Success Indicators
1. All tables exist with correct record counts
2. Relationships are properly established
3. Category hierarchy is maintained
4. Activity distribution matches expected counts
5. No foreign key constraint violations

### Common Validation Issues

1. Missing Tables:
   - Verify migrations have run successfully
   - Check database connection settings
   - Ensure proper environment variables

2. Incomplete Data:
   - Run seed scripts in correct order
   - Verify foreign key constraints
   - Check for failed transactions

3. Category Issues:
   - Validate parent-child relationships
   - Check activity distribution
   - Verify category assignments

### Troubleshooting

1. If validation fails:
   - Check database logs
   - Verify container status
   - Review migration history

2. If seeding fails:
   - Check data integrity
   - Verify foreign keys
   - Review error messages

3. If categories are incorrect:
   - Verify category hierarchy
   - Check activity assignments
   - Review category relationships 