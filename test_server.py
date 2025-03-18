from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any
import uvicorn
import platform
import psutil
import json
import os
import sys
import logging
from datetime import datetime, timedelta
import asyncio
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import re
from collections import deque
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'server.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# App version and build info
VERSION = "0.1.0"
BUILD_DATE = datetime.now().strftime("%Y-%m-%d")
PLATFORM = platform.platform()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Add alert thresholds
ALERT_THRESHOLDS = {
    'cpu_percent': 75.0,  # Alert at 75% CPU usage
    'memory_percent': 75.0,  # Alert at 75% memory usage
    'disk_percent': 80.0,  # Alert at 80% disk usage
    'requests_per_minute': 500,  # Alert at 500 requests per minute
    'error_rate_percent': 5.0,  # Alert at 5% error rate
    'bandwidth_gb': 80.0,  # Alert at 80GB (of 100GB limit)
}

# Add monitoring state
class MonitoringState:
    def __init__(self):
        self.request_times = deque(maxlen=60)  # Last minute of requests
        self.error_times = deque(maxlen=60)  # Last minute of errors
        self.bandwidth_usage = 0  # Total bandwidth usage in bytes
        self.alerts_history = deque(maxlen=100)  # Last 100 alerts
        self.last_alert_times = {}  # Prevent alert spam
        self.lock = threading.Lock()

monitoring = MonitoringState()

# Response Models
class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error details")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: str = Field(..., description="Error timestamp")

class SystemInfo(BaseModel):
    platform: str = Field(..., description="Operating system platform")
    python_version: str = Field(..., description="Python version")
    cpu_count: int = Field(..., description="Number of CPU cores")
    memory_total: str = Field(..., description="Total system memory")
    memory_available: str = Field(..., description="Available system memory")
    memory_percent: float = Field(..., description="Memory usage percentage")
    disk_usage: Dict[str, Any] = Field(..., description="Disk usage information")

class AIComponents(BaseModel):
    pytorch_version: str = Field(..., description="PyTorch version")
    transformers_version: str = Field(..., description="Transformers library version")
    gpu_available: bool = Field(..., description="Whether GPU is available")
    device: str = Field(..., description="Current compute device (GPU model or CPU)")

class VersionResponse(BaseModel):
    version: str = Field(..., description="Server version")
    build_date: str = Field(..., description="Build date")
    platform: str = Field(..., description="Operating system platform")
    uptime: str = Field(..., description="Server uptime")

class APIResponse(BaseModel):
    status: str = Field(..., description="Server status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Server version")
    timestamp: str = Field(..., description="Response timestamp")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    system: SystemInfo = Field(..., description="System information")
    timestamp: str = Field(..., description="Response timestamp")

class AITestResponse(BaseModel):
    status: str = Field(..., description="Test status")
    ai_components: AIComponents = Field(..., description="AI component information")
    timestamp: str = Field(..., description="Response timestamp")

class MetricsResponse(BaseModel):
    requests_total: int = Field(..., description="Total number of requests")
    errors_total: int = Field(..., description="Total number of errors")
    uptime_seconds: float = Field(..., description="Server uptime in seconds")
    memory_usage: Dict[str, Any] = Field(..., description="Memory usage metrics")
    cpu_usage: Dict[str, Any] = Field(..., description="CPU usage metrics")

class Alert(BaseModel):
    type: str = Field(..., description="Type of alert")
    message: str = Field(..., description="Alert message")
    value: float = Field(..., description="Current value that triggered alert")
    threshold: float = Field(..., description="Threshold value")
    timestamp: str = Field(..., description="Alert timestamp")

class AlertsResponse(BaseModel):
    current_alerts: List[Alert] = Field(..., description="Current active alerts")
    alerts_history: List[Alert] = Field(..., description="Recent alerts history")
    resource_usage: Dict[str, float] = Field(..., description="Current resource usage")

# Global metrics
start_time = datetime.now()
request_count = 0
error_count = 0

app = FastAPI(
    title="Faraday AI Test Server",
    description="""
    Test server for Faraday AI educational platform.
    
    This server provides various endpoints to monitor system health, 
    test AI components, and serve the landing page for the Faraday AI platform.
    
    Key features:
    - System health monitoring
    - AI components testing
    - Static file serving
    - Automatic status logging
    - Rate limiting
    - Security middleware
    - Metrics collection
    """,
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict to needed methods
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=[
        "faraday-ai.onrender.com",  # Add your actual domain
        "localhost",
        "127.0.0.1"
    ]
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create necessary directories
LOGS_DIR = "logs"
STATIC_DIR = "static/images"
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Error handling
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Too many requests",
            "status_code": 429,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    global error_count
    error_count += 1
    logger.error(f"Global error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )

# Request counting middleware
@app.middleware("http")
async def count_requests(request: Request, call_next):
    global request_count
    request_count += 1
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Request error: {str(e)}", exc_info=True)
        raise

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline';"
    return response

# Add scan protection middleware
@app.middleware("http")
async def protect_from_scans(request: Request, call_next):
    path = request.url.path.lower()
    
    # Block known malicious scan patterns
    blocked_patterns = [
        r"wp-admin",
        r"wordpress",
        r"wp-login",
        r"wp-content",
        r"xmlrpc.php",
        r"setup-config.php",
        r"phpMyAdmin",
        r"admin.php",
        r".env",
        r".git",
    ]
    
    if any(re.search(pattern, path) for pattern in blocked_patterns):
        return PlainTextResponse(
            "Not Found", 
            status_code=404,
            headers={"X-Robots-Tag": "noindex"}
        )
    
    # Rate limit based on IP for suspicious behavior
    client_ip = request.client.host
    if request.method == "HEAD" or path.startswith(("/backup", "/old", "/new", "/main", "/home", "/bc", "/bk")):
        limiter.limit("5/minute")(request)
    
    return await call_next(request)

async def auto_save():
    while True:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(LOGS_DIR, f"server_status_{timestamp}.json")
            
            status_data = {
                "timestamp": timestamp,
                "status": "healthy",
                "system": {
                    "platform": platform.platform(),
                    "python_version": platform.python_version(),
                    "cpu_count": psutil.cpu_count(),
                    "memory_total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                    "memory_available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
                    "disk_usage": {
                        "total": f"{psutil.disk_usage('/').total / (1024**3):.2f} GB",
                        "used": f"{psutil.disk_usage('/').used / (1024**3):.2f} GB",
                        "free": f"{psutil.disk_usage('/').free / (1024**3):.2f} GB"
                    }
                },
                "metrics": {
                    "requests_total": request_count,
                    "errors_total": error_count,
                    "uptime_seconds": (datetime.now() - start_time).total_seconds()
                }
            }
            
            with open(log_file, 'w') as f:
                json.dump(status_data, f, indent=4)
            
            logger.info(f"Auto-saved status to {log_file}")
        except Exception as e:
            logger.error(f"Error during auto-save: {str(e)}", exc_info=True)
        
        await asyncio.sleep(300)  # 5 minutes

@app.on_event("startup")
async def startup_event():
    logger.info("Server starting up...")
    asyncio.create_task(auto_save())
    asyncio.create_task(monitor_resources())

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Server shutting down...")

@app.get("/",
    summary="Landing Page",
    description="Serves the main landing page of the Faraday AI platform.",
    response_class=FileResponse)
@limiter.limit("30/minute")  # More restrictive rate limit
async def root(request: Request):
    """
    Returns the landing page HTML file.
    """
    logger.info(f"Serving landing page to {request.client.host}")
    return FileResponse("static/index.html")

@app.get("/api",
    summary="API Status",
    description="Returns the current status of the API service.",
    response_model=APIResponse,
    responses={
        200: {
            "description": "Successful response with API status",
            "content": {
                "application/json": {
                    "example": {
                        "status": "online",
                        "service": "Faraday AI Test Server",
                        "version": "0.1.0",
                        "timestamp": "2025-03-18T04:40:31.123456"
                    }
                }
            }
        }
    })
@limiter.limit("120/minute")
async def api_root(request: Request):
    """
    Returns basic information about the API service.
    """
    return {
        "status": "online",
        "service": "Faraday AI Test Server",
        "version": VERSION,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/version",
    summary="Version Information",
    description="Returns detailed version information about the server.",
    response_model=VersionResponse,
    responses={
        200: {
            "description": "Successful response with version information",
            "content": {
                "application/json": {
                    "example": {
                        "version": "0.1.0",
                        "build_date": "2025-03-18",
                        "platform": "macOS-14.3.1-arm64-arm-64bit",
                        "uptime": "1 day, 2:34:56"
                    }
                }
            }
        }
    })
@limiter.limit("60/minute")
async def version(request: Request):
    """
    Returns version information including build date and platform details.
    """
    uptime = datetime.now() - start_time
    return {
        "version": VERSION,
        "build_date": BUILD_DATE,
        "platform": PLATFORM,
        "uptime": str(uptime).split('.')[0]  # Remove microseconds
    }

@app.get("/health",
    summary="Health Check",
    description="Returns detailed system health information.",
    response_model=HealthResponse,
    responses={
        200: {
            "description": "Successful response with system health information",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "system": {
                            "platform": "macOS-14.3.1-arm64-arm-64bit",
                            "python_version": "3.9.7",
                            "cpu_count": 8,
                            "memory_total": "16.00 GB",
                            "memory_available": "8.50 GB",
                            "memory_percent": 46.9,
                            "disk_usage": {
                                "total": "500.00 GB",
                                "used": "250.00 GB",
                                "free": "250.00 GB"
                            }
                        },
                        "timestamp": "2025-03-18T04:40:31.123456"
                    }
                }
            }
        }
    })
@limiter.limit("30/minute")
async def health_check(request: Request):
    """
    Returns comprehensive system health information including memory and CPU details.
    """
    return {
        "status": "healthy",
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "memory_available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": {
                "total": f"{psutil.disk_usage('/').total / (1024**3):.2f} GB",
                "used": f"{psutil.disk_usage('/').used / (1024**3):.2f} GB",
                "free": f"{psutil.disk_usage('/').free / (1024**3):.2f} GB"
            }
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test-ai",
    summary="AI Components Test",
    description="Tests and returns status of AI-related components.",
    response_model=AITestResponse,
    responses={
        200: {
            "description": "Successful response with AI components status",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "ai_components": {
                            "pytorch_version": "2.2.1",
                            "transformers_version": "4.37.2",
                            "gpu_available": False,
                            "device": "CPU"
                        },
                        "timestamp": "2025-03-18T04:40:31.123456"
                    }
                }
            }
        },
        500: {
            "description": "Error testing AI components",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error importing required AI libraries",
                        "status_code": 500,
                        "timestamp": "2025-03-18T04:40:31.123456"
                    }
                }
            }
        }
    })
@limiter.limit("10/minute")
async def test_ai(request: Request):
    """
    Tests AI components and returns their status and version information.
    Checks PyTorch and Transformers availability and GPU status.
    """
    try:
        import torch
        import transformers
        return {
            "status": "success",
            "ai_components": {
                "pytorch_version": torch.__version__,
                "transformers_version": transformers.__version__,
                "gpu_available": torch.cuda.is_available(),
                "device": str(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"AI test error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/metrics",
    summary="Server Metrics",
    description="Returns detailed server metrics and statistics.",
    response_model=MetricsResponse,
    responses={
        200: {
            "description": "Successful response with server metrics",
            "content": {
                "application/json": {
                    "example": {
                        "requests_total": 1234,
                        "errors_total": 5,
                        "uptime_seconds": 86400,
                        "memory_usage": {
                            "total": "16.00 GB",
                            "available": "8.50 GB",
                            "percent": 46.9
                        },
                        "cpu_usage": {
                            "percent": 25.5,
                            "cores": 8
                        }
                    }
                }
            }
        }
    })
@limiter.limit("30/minute")
async def metrics(request: Request):
    """
    Returns comprehensive server metrics including request counts, errors, and resource usage.
    """
    return {
        "requests_total": request_count,
        "errors_total": error_count,
        "uptime_seconds": (datetime.now() - start_time).total_seconds(),
        "memory_usage": {
            "total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            "available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
            "percent": psutil.virtual_memory().percent
        },
        "cpu_usage": {
            "percent": psutil.cpu_percent(interval=1),
            "cores": psutil.cpu_count()
        }
    }

@app.get("/favicon.ico",
    summary="Favicon",
    description="Serves the website favicon.",
    response_class=FileResponse)
async def favicon():
    """
    Returns the favicon.ico file.
    """
    return FileResponse("static/favicon.ico")

# Add to your request counting middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    global request_count
    start_time = datetime.now()
    
    try:
        with monitoring.lock:
            monitoring.request_times.append(start_time)
        
        response = await call_next(request)
        
        # Estimate bandwidth (very rough approximation)
        response_size = len(str(response.body)) if hasattr(response, 'body') else 0
        with monitoring.lock:
            monitoring.bandwidth_usage += response_size
        
        return response
    except Exception as e:
        with monitoring.lock:
            monitoring.error_times.append(start_time)
        raise
    finally:
        request_count += 1

def check_alerts():
    """Check resource usage and generate alerts if needed"""
    current_time = datetime.now()
    alerts = []

    # Calculate metrics
    with monitoring.lock:
        # Request rate
        recent_requests = sum(1 for t in monitoring.request_times 
                            if (current_time - t).total_seconds() <= 60)
        if recent_requests > 0:
            recent_errors = sum(1 for t in monitoring.error_times 
                              if (current_time - t).total_seconds() <= 60)
            error_rate = (recent_errors / recent_requests) * 100
        else:
            error_rate = 0

    # System metrics
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Check thresholds
    if cpu_percent > ALERT_THRESHOLDS['cpu_percent']:
        alerts.append(Alert(
            type="cpu_usage",
            message=f"High CPU usage: {cpu_percent}%",
            value=cpu_percent,
            threshold=ALERT_THRESHOLDS['cpu_percent'],
            timestamp=current_time.isoformat()
        ))
    
    if memory.percent > ALERT_THRESHOLDS['memory_percent']:
        alerts.append(Alert(
            type="memory_usage",
            message=f"High memory usage: {memory.percent}%",
            value=memory.percent,
            threshold=ALERT_THRESHOLDS['memory_percent'],
            timestamp=current_time.isoformat()
        ))
    
    if disk.percent > ALERT_THRESHOLDS['disk_percent']:
        alerts.append(Alert(
            type="disk_usage",
            message=f"High disk usage: {disk.percent}%",
            value=disk.percent,
            threshold=ALERT_THRESHOLDS['disk_percent'],
            timestamp=current_time.isoformat()
        ))
    
    if recent_requests > ALERT_THRESHOLDS['requests_per_minute']:
        alerts.append(Alert(
            type="request_rate",
            message=f"High request rate: {recent_requests}/minute",
            value=float(recent_requests),
            threshold=ALERT_THRESHOLDS['requests_per_minute'],
            timestamp=current_time.isoformat()
        ))
    
    if error_rate > ALERT_THRESHOLDS['error_rate_percent']:
        alerts.append(Alert(
            type="error_rate",
            message=f"High error rate: {error_rate:.1f}%",
            value=error_rate,
            threshold=ALERT_THRESHOLDS['error_rate_percent'],
            timestamp=current_time.isoformat()
        ))
    
    bandwidth_gb = monitoring.bandwidth_usage / (1024**3)  # Convert to GB
    if bandwidth_gb > ALERT_THRESHOLDS['bandwidth_gb']:
        alerts.append(Alert(
            type="bandwidth_usage",
            message=f"High bandwidth usage: {bandwidth_gb:.1f}GB",
            value=bandwidth_gb,
            threshold=ALERT_THRESHOLDS['bandwidth_gb'],
            timestamp=current_time.isoformat()
        ))

    # Store alerts
    with monitoring.lock:
        for alert in alerts:
            # Prevent alert spam by checking last alert time
            if alert.type not in monitoring.last_alert_times or \
               (current_time - datetime.fromisoformat(monitoring.last_alert_times[alert.type])).total_seconds() > 3600:
                monitoring.alerts_history.append(alert)
                monitoring.last_alert_times[alert.type] = current_time.isoformat()
                logger.warning(f"ALERT: {alert.message}")

async def monitor_resources():
    """Background task to monitor resources"""
    while True:
        try:
            check_alerts()
        except Exception as e:
            logger.error(f"Error in resource monitoring: {str(e)}", exc_info=True)
        await asyncio.sleep(60)  # Check every minute

# Add new alerts endpoint
@app.get("/alerts",
    summary="Resource Alerts",
    description="Returns current alerts and resource usage information.",
    response_model=AlertsResponse,
    responses={
        200: {
            "description": "Current alerts and resource usage",
            "content": {
                "application/json": {
                    "example": {
                        "current_alerts": [
                            {
                                "type": "cpu_usage",
                                "message": "High CPU usage: 85%",
                                "value": 85.0,
                                "threshold": 75.0,
                                "timestamp": "2024-03-18T04:40:31.123456"
                            }
                        ],
                        "alerts_history": [],
                        "resource_usage": {
                            "cpu_percent": 85.0,
                            "memory_percent": 60.0,
                            "disk_percent": 70.0,
                            "requests_per_minute": 300,
                            "error_rate": 1.5,
                            "bandwidth_gb": 50.0
                        }
                    }
                }
            }
        }
    })
@limiter.limit("30/minute")
async def get_alerts(request: Request):
    """
    Returns current alerts and resource usage information.
    """
    current_time = datetime.now()
    
    # Calculate current metrics
    with monitoring.lock:
        recent_requests = sum(1 for t in monitoring.request_times 
                            if (current_time - t).total_seconds() <= 60)
        if recent_requests > 0:
            recent_errors = sum(1 for t in monitoring.error_times 
                              if (current_time - t).total_seconds() <= 60)
            error_rate = (recent_errors / recent_requests) * 100
        else:
            error_rate = 0
    
    # Get current resource usage
    resource_usage = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "requests_per_minute": float(recent_requests),
        "error_rate": error_rate,
        "bandwidth_gb": monitoring.bandwidth_usage / (1024**3)
    }
    
    # Get current alerts
    check_alerts()
    
    with monitoring.lock:
        current_alerts = [alert for alert in monitoring.alerts_history 
                         if (current_time - datetime.fromisoformat(alert.timestamp)).total_seconds() <= 3600]
    
    return {
        "current_alerts": current_alerts,
        "alerts_history": list(monitoring.alerts_history),
        "resource_usage": resource_usage
    }

if __name__ == "__main__":
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 