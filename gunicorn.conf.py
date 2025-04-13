import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', '8'))  # Use environment variable or default to 8
threads = 2  # 2 threads per worker
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120  # Increased timeout for long-running operations
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info')

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

# Worker timeout
graceful_timeout = 120  # Give workers time to finish their requests

# SSL configuration (if needed)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem" 