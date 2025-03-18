#!/bin/bash

# Set source and destination directories
SOURCE_DIR="/Users/joemartucci/Projects/Faraday-AI"
BACKUP_DIR="/Users/joemartucci"

# Create timestamp for backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create backup directory with timestamp
BACKUP_NAME="Faraday-AI_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Create backup
echo "Creating backup at ${BACKUP_PATH}..."
rsync -av --exclude 'venv/' \
    --exclude '__pycache__/' \
    --exclude '.pytest_cache/' \
    --exclude '.git/' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    "${SOURCE_DIR}/" "${BACKUP_PATH}/"

# Create symlink to latest backup
echo "Creating symlink to latest backup..."
rm -f "${BACKUP_DIR}/Faraday-AI_backup_latest"
ln -s "${BACKUP_PATH}" "${BACKUP_DIR}/Faraday-AI_backup_latest"

echo "Backup completed successfully!"
echo "Latest backup: ${BACKUP_PATH}" 