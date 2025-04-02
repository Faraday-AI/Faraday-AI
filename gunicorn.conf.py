import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = 8  # 2 workers per CPU for 4 CPUs
threads = 2  # 2 threads per worker
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 60  # Increased timeout for long-running operations
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "faraday-ai"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Memory management
max_requests = 1000  # Restart workers after handling this many requests
max_requests_jitter = 50  # Add jitter to prevent all workers from restarting at once 