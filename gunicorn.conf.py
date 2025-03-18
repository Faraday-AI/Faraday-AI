import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 4  # 2 workers per CPU core
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Process naming
proc_name = 'faraday-ai'

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# SSL
# keyfile = ''
# certfile = ''

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None

# Server hooks
def on_starting(server):
    server.log.info("Server is starting")

def on_reload(server):
    server.log.info("Server is reloading")

def on_exit(server):
    server.log.info("Server is shutting down")

# Development settings
reload = False  # Set to True for development

# Resource management
max_requests_jitter = 50
worker_tmp_dir = "/dev/shm"  # Using shared memory for temp files
worker_exit_on_app_exit = True
graceful_timeout = 30
threads = 4  # Number of threads per worker
