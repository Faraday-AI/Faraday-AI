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