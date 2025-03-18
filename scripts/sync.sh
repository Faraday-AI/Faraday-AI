#!/bin/bash

# Set source and destination directories
SOURCE_DIR="/Users/joemartucci/Projects/Faraday-AI"
BACKUP_DIR="/Users/joemartucci/Faraday-AI_backup_latest"

# Create initial backup if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Creating initial backup..."
    mkdir -p "$BACKUP_DIR"
    rsync -av --exclude 'venv/' \
        --exclude '__pycache__/' \
        --exclude '.pytest_cache/' \
        --exclude '.git/' \
        --exclude '*.pyc' \
        --exclude '.DS_Store' \
        "${SOURCE_DIR}/" "${BACKUP_DIR}/"
fi

# Function to sync changes
sync_changes() {
    echo "Syncing changes..."
    rsync -av --exclude 'venv/' \
        --exclude '__pycache__/' \
        --exclude '.pytest_cache/' \
        --exclude '.git/' \
        --exclude '*.pyc' \
        --exclude '.DS_Store' \
        "${SOURCE_DIR}/" "${BACKUP_DIR}/"
}

# Watch for changes and sync
echo "Starting real-time sync from ${SOURCE_DIR} to ${BACKUP_DIR}"
echo "Press Ctrl+C to stop"

fswatch -o "$SOURCE_DIR" | while read f; do
    sync_changes
done 