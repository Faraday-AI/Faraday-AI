#!/bin/bash

# Set Python path to match production
export PYTHONPATH=/app

# Create necessary directories
mkdir -p /app/models
mkdir -p /app/static
mkdir -p /app/logs
mkdir -p /app/exports

# Create symlink for static files
ln -sf /app/static static

# Set permissions
chmod -R 755 /app/static
chmod -R 777 /app/logs /app/exports

echo "Local environment configured to match production"
echo "PYTHONPATH set to: $PYTHONPATH"
echo "Directory structure created and permissions set" 