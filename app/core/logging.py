"""
Logging Module

This module provides comprehensive logging functionality for the Faraday AI Dashboard.
"""

import logging
import logging.handlers
import json
import sys
import os
import traceback
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from pythonjsonlogger import jsonlogger
from prometheus_client import Counter, Histogram, Gauge
import psutil
import socket
import threading
from functools import wraps

# Import models
from app.models.activity_adaptation.activity.activity_log import ActivityLog
from app.models.audit_log import AuditLog
from app.models.performance_log import PerformanceLog
from app.models.security_log import SecurityLog

# Log metrics
LOG_COUNTER = Counter(
    'faraday_log_total',
    'Total number of log entries',
    ['level', 'module']
)
LOG_LATENCY = Histogram(
    'faraday_log_latency_seconds',
    'Log entry processing latency',
    ['level', 'module']
)
LOG_SIZE = Gauge(
    'faraday_log_size_bytes',
    'Size of log files in bytes',
    ['log_file']
)
LOG_ROTATIONS = Counter(
    'faraday_log_rotations_total',
    'Total number of log rotations',
    ['log_file']
)

def get_settings():
    """Lazy load settings to avoid circular imports."""
    from app.core.config import settings
    return settings

class ContextFilter(logging.Filter):
    """Add context information to log records."""
    
    def filter(self, record):
        settings = get_settings()
        record.request_id = getattr(record, 'request_id', '-')
        record.user_id = getattr(record, 'user_id', '-')
        record.org_id = getattr(record, 'org_id', '-')
        record.environment = getattr(settings, 'ENVIRONMENT', 'development')
        record.hostname = socket.gethostname()
        record.process_id = os.getpid()
        record.thread_id = threading.get_ident()
        return True

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record, record, message_dict):
        settings = get_settings()
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        log_record['environment'] = getattr(settings, 'ENVIRONMENT', 'development')
        log_record['hostname'] = socket.gethostname()
        log_record['process_id'] = os.getpid()
        log_record['thread_id'] = threading.get_ident()
        
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'org_id'):
            log_record['org_id'] = record.org_id
        if hasattr(record, 'performance_metrics'):
            log_record['performance_metrics'] = record.performance_metrics
        if hasattr(record, 'security_context'):
            log_record['security_context'] = record.security_context

def setup_logging():
    """Set up logging configuration."""
    settings = get_settings()
    # Create log directory if it doesn't exist
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    console_formatter = logging.Formatter(settings.LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "faraday.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(settings.LOG_LEVEL)
    file_formatter = CustomJsonFormatter()
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Performance log handler
    performance_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "performance.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    performance_handler.setLevel(logging.INFO)
    performance_handler.setFormatter(file_formatter)
    root_logger.addHandler(performance_handler)
    
    # Security log handler
    security_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "security.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(file_formatter)
    root_logger.addHandler(security_handler)
    
    # Audit log handler
    audit_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "audit.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(file_formatter)
    root_logger.addHandler(audit_handler)
    
    # Add context filter
    context_filter = ContextFilter()
    root_logger.addFilter(context_filter)
    
    # Configure specific loggers
    loggers = {
        'app': logging.INFO,
        'sqlalchemy': logging.WARNING,
        'uvicorn': logging.INFO,
        'fastapi': logging.INFO,
        'security': logging.INFO,
        'performance': logging.INFO,
        'audit': logging.INFO
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    return root_logger

# Initialize logging
logger = setup_logging()

class LogContext:
    """Context manager for logging with context."""
    
    def __init__(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        performance_metrics: Optional[Dict[str, Any]] = None,
        security_context: Optional[Dict[str, Any]] = None
    ):
        self.request_id = request_id
        self.user_id = user_id
        self.org_id = org_id
        self.performance_metrics = performance_metrics
        self.security_context = security_context
        self.old_context = {}
    
    def __enter__(self):
        # Store old context
        self.old_context = {
            'request_id': getattr(logging.getLogger(), 'request_id', None),
            'user_id': getattr(logging.getLogger(), 'user_id', None),
            'org_id': getattr(logging.getLogger(), 'org_id', None),
            'performance_metrics': getattr(logging.getLogger(), 'performance_metrics', None),
            'security_context': getattr(logging.getLogger(), 'security_context', None)
        }
        
        # Set new context
        if self.request_id:
            logging.getLogger().request_id = self.request_id
        if self.user_id:
            logging.getLogger().user_id = self.user_id
        if self.org_id:
            logging.getLogger().org_id = self.org_id
        if self.performance_metrics:
            logging.getLogger().performance_metrics = self.performance_metrics
        if self.security_context:
            logging.getLogger().security_context = self.security_context
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore old context
        for key, value in self.old_context.items():
            setattr(logging.getLogger(), key, value)

async def log_activity(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> ActivityLog:
    """
    Log an activity in the system.

    Args:
        db: Database session
        action: The action being performed (e.g., "create", "update", "delete")
        resource_type: Type of resource being acted upon
        resource_id: ID of the resource
        details: Optional additional details about the activity
        user_id: Optional ID of the user performing the action
        org_id: Optional ID of the organization context
        request_id: Optional ID of the request

    Returns:
        ActivityLog: The created activity log entry
    """
    with LogContext(request_id, user_id, org_id):
        with LOG_LATENCY.labels(level='info', module='activity').time():
            try:
                # Create activity log entry
                log_entry = ActivityLog(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details or {},
                    user_id=user_id,
                    org_id=org_id,
                    timestamp=datetime.utcnow()
                )
                
                # Add to database
                db.add(log_entry)
                db.commit()
                db.refresh(log_entry)
                
                # Log to file
                logger.info(
                    f"Activity logged: {action} on {resource_type} {resource_id}",
                    extra={
                        'activity_log_id': log_entry.id,
                        'action': action,
                        'resource_type': resource_type,
                        'resource_id': resource_id,
                        'details': details
                    }
                )
                
                return log_entry
            except Exception as e:
                logger.error(
                    f"Failed to log activity: {str(e)}",
                    exc_info=True,
                    extra={
                        'action': action,
                        'resource_type': resource_type,
                        'resource_id': resource_id
                    }
                )
                raise

async def log_performance(
    db: Session,
    operation: str,
    duration: float,
    metrics: Dict[str, Any],
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> PerformanceLog:
    """
    Log performance metrics.

    Args:
        db: Database session
        operation: The operation being performed
        duration: Duration of the operation in seconds
        metrics: Additional performance metrics
        user_id: Optional ID of the user
        org_id: Optional ID of the organization
        request_id: Optional ID of the request

    Returns:
        PerformanceLog: The created performance log entry
    """
    with LogContext(request_id, user_id, org_id, performance_metrics=metrics):
        with LOG_LATENCY.labels(level='info', module='performance').time():
            try:
                # Create performance log entry
                log_entry = PerformanceLog(
                    operation=operation,
                    duration=duration,
                    metrics=metrics,
                    user_id=user_id,
                    org_id=org_id,
                    timestamp=datetime.utcnow()
                )
                
                # Add to database
                db.add(log_entry)
                db.commit()
                db.refresh(log_entry)
                
                # Log to file
                logger.info(
                    f"Performance logged: {operation} took {duration:.2f}s",
                    extra={
                        'performance_log_id': log_entry.id,
                        'operation': operation,
                        'duration': duration,
                        'metrics': metrics
                    }
                )
                
                return log_entry
            except Exception as e:
                logger.error(
                    f"Failed to log performance: {str(e)}",
                    exc_info=True,
                    extra={
                        'operation': operation,
                        'duration': duration
                    }
                )
                raise

async def log_security(
    db: Session,
    event_type: str,
    severity: str,
    details: Dict[str, Any],
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> SecurityLog:
    """
    Log security events.

    Args:
        db: Database session
        event_type: Type of security event
        severity: Severity level of the event
        details: Additional security event details
        user_id: Optional ID of the user
        org_id: Optional ID of the organization
        request_id: Optional ID of the request

    Returns:
        SecurityLog: The created security log entry
    """
    with LogContext(request_id, user_id, org_id, security_context=details):
        with LOG_LATENCY.labels(level='info', module='security').time():
            try:
                # Create security log entry
                log_entry = SecurityLog(
                    event_type=event_type,
                    severity=severity,
                    details=details,
                    user_id=user_id,
                    org_id=org_id,
                    timestamp=datetime.utcnow()
                )
                
                # Add to database
                db.add(log_entry)
                db.commit()
                db.refresh(log_entry)
                
                # Log to file
                logger.info(
                    f"Security event logged: {event_type} ({severity})",
                    extra={
                        'security_log_id': log_entry.id,
                        'event_type': event_type,
                        'severity': severity,
                        'details': details
                    }
                )
                
                return log_entry
            except Exception as e:
                logger.error(
                    f"Failed to log security event: {str(e)}",
                    exc_info=True,
                    extra={
                        'event_type': event_type,
                        'severity': severity
                    }
                )
                raise

async def log_audit(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: str,
    changes: Dict[str, Any],
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> AuditLog:
    """
    Log audit events.

    Args:
        db: Database session
        action: The action being performed
        resource_type: Type of resource being acted upon
        resource_id: ID of the resource
        changes: Changes made to the resource
        user_id: Optional ID of the user
        org_id: Optional ID of the organization
        request_id: Optional ID of the request

    Returns:
        AuditLog: The created audit log entry
    """
    with LogContext(request_id, user_id, org_id):
        with LOG_LATENCY.labels(level='info', module='audit').time():
            try:
                # Create audit log entry
                log_entry = AuditLog(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    changes=changes,
                    user_id=user_id,
                    org_id=org_id,
                    timestamp=datetime.utcnow()
                )
                
                # Add to database
                db.add(log_entry)
                db.commit()
                db.refresh(log_entry)
                
                # Log to file
                logger.info(
                    f"Audit event logged: {action} on {resource_type} {resource_id}",
                    extra={
                        'audit_log_id': log_entry.id,
                        'action': action,
                        'resource_type': resource_type,
                        'resource_id': resource_id,
                        'changes': changes
                    }
                )
                
                return log_entry
            except Exception as e:
                logger.error(
                    f"Failed to log audit event: {str(e)}",
                    exc_info=True,
                    extra={
                        'action': action,
                        'resource_type': resource_type,
                        'resource_id': resource_id
                    }
                )
                raise

def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> None:
    """
    Log an error with context.

    Args:
        error: The exception to log
        context: Optional additional context
        user_id: Optional ID of the user
        org_id: Optional ID of the organization
        request_id: Optional ID of the request
    """
    with LogContext(request_id, user_id, org_id):
        with LOG_LATENCY.labels(level='error', module='error').time():
            error_context = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc(),
                **(context or {})
            }
            
            logger.error(
                f"Error occurred: {str(error)}",
                exc_info=True,
                extra=error_context
            )

def log_metrics(
    metrics: Dict[str, Any],
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> None:
    """
    Log metrics.

    Args:
        metrics: Metrics to log
        user_id: Optional ID of the user
        org_id: Optional ID of the organization
        request_id: Optional ID of the request
    """
    with LogContext(request_id, user_id, org_id):
        with LOG_LATENCY.labels(level='info', module='metrics').time():
            logger.info(
                "Metrics logged",
                extra={'metrics': metrics}
            )

def log_debug(
    message: str,
    data: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    request_id: Optional[str] = None
) -> None:
    """
    Log debug information.

    Args:
        message: Debug message
        data: Optional additional data
        user_id: Optional ID of the user
        org_id: Optional ID of the organization
        request_id: Optional ID of the request
    """
    with LogContext(request_id, user_id, org_id):
        with LOG_LATENCY.labels(level='debug', module='debug').time():
            logger.debug(
                message,
                extra={'debug_data': data} if data else None
            )

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Name of the logger

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name) 