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

## Networking

### Network Commands
```bash
# List networks
docker network ls

# Create network
docker network create my_network

# Remove network
docker network rm my_network

# Connect container to network
docker network connect my_network container_name

# Disconnect container from network
docker network disconnect my_network container_name
```

### Network Types
- **Bridge**: Default network
- **Host**: Uses host's network
- **None**: No network access
- **Overlay**: For swarm mode
- **Macvlan**: Direct access to physical network

## Volumes and Storage

### Volume Commands
```bash
# List volumes
docker volume ls

# Create volume
docker volume create my_volume

# Remove volume
docker volume rm my_volume

# Inspect volume
docker volume inspect my_volume
```

### Volume Types
- **Named Volumes**: Managed by Docker
- **Bind Mounts**: Link to host directory
- **tmpfs Mounts**: Temporary storage

## Troubleshooting

### Common Issues
1. **Docker not running**
   ```bash
   # Check Docker service status
   sudo systemctl status docker
   
   # Restart Docker service
   sudo systemctl restart docker
   ```

2. **Port conflicts**
   ```bash
   # Check port usage
   sudo lsof -i :port_number
   
   # Kill process using port
   sudo kill -9 process_id
   ```

3. **Container won't start**
   ```bash
   # Check container logs
   docker logs container_name
   
   # Check container details
   docker inspect container_name
   ```

### Debugging Commands
```bash
# View container logs with timestamps
docker logs -t container_name

# Follow container logs
docker logs -f container_name

# View container events
docker events

# Check container health
docker inspect --format='{{.State.Health.Status}}' container_name
```

## Best Practices

### Security
1. Use official images
2. Scan images for vulnerabilities
3. Run containers as non-root
4. Use secrets for sensitive data
5. Keep images updated

### Performance
1. Use multi-stage builds
2. Optimize layer caching
3. Remove unnecessary files
4. Use .dockerignore
5. Keep images small

### Development
1. Use Docker Compose for development
2. Implement health checks
3. Use environment variables
4. Document Dockerfile steps
5. Version control Dockerfile

### Maintenance
1. Regular cleanup
2. Monitor resource usage
3. Update base images
4. Review security patches
5. Backup important data

## Additional Resources
- [Docker Official Documentation](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/) 