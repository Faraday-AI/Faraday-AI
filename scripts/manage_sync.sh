#!/bin/bash

# Path to sync script
SYNC_SCRIPT="/Users/joemartucci/Projects/Faraday-AI/scripts/sync.sh"
PID_FILE="/Users/joemartucci/Library/Logs/faraday-ai-sync.pid"

# Function to check if sync is running
check_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null; then
            echo "Sync is running (PID: $PID)"
            return 0
        else
            echo "Sync is not running (stale PID file)"
            return 1
        fi
    else
        echo "Sync is not running"
        return 1
    fi
}

# Function to start sync
start_sync() {
    if check_status; then
        echo "Sync is already running"
        return 1
    fi
    
    echo "Starting sync..."
    nohup "$SYNC_SCRIPT" > /Users/joemartucci/Library/Logs/faraday-ai-sync.log 2>&1 &
    echo $! > "$PID_FILE"
    echo "Sync started (PID: $!)"
}

# Function to stop sync
stop_sync() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null; then
            echo "Stopping sync (PID: $PID)..."
            kill "$PID"
            rm "$PID_FILE"
            echo "Sync stopped"
        else
            echo "Sync is not running"
            rm "$PID_FILE"
        fi
    else
        echo "Sync is not running"
    fi
}

# Main script
case "$1" in
    start)
        start_sync
        ;;
    stop)
        stop_sync
        ;;
    status)
        check_status
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac

exit 0 