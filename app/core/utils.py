"""
Utility functions for the Faraday AI application.
"""

import os
import re
import json
import time
import uuid
import hashlib
import logging
import datetime
import mimetypes
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from pathlib import Path
from functools import wraps
from cryptography.fernet import Fernet
from pydantic import BaseModel, ValidationError
import redis
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar('T')
ModelType = TypeVar('ModelType', bound=BaseModel)

# Time Utilities
def get_current_timestamp() -> float:
    """Get current timestamp in seconds."""
    return time.time()

def format_timestamp(timestamp: float, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp to string."""
    return datetime.datetime.fromtimestamp(timestamp).strftime(format)

def parse_timestamp(timestamp_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> float:
    """Parse timestamp string to float."""
    return datetime.datetime.strptime(timestamp_str, format).timestamp()

def get_timezone_offset() -> int:
    """Get current timezone offset in seconds."""
    return datetime.datetime.now().astimezone().utcoffset().total_seconds()

def calculate_duration(start_time: float, end_time: float) -> float:
    """Calculate duration between timestamps in seconds."""
    return end_time - start_time

# String Utilities
def sanitize_string(text: str) -> str:
    """Sanitize string by removing special characters."""
    return re.sub(r'[^a-zA-Z0-9\s-]', '', text)

def format_string(template: str, **kwargs) -> str:
    """Format string with named parameters."""
    return template.format(**kwargs)

def validate_string(text: str, min_length: int = 0, max_length: int = None) -> bool:
    """Validate string length."""
    if len(text) < min_length:
        return False
    if max_length and len(text) > max_length:
        return False
    return True

def generate_random_string(length: int = 32) -> str:
    """Generate random string of specified length."""
    return uuid.uuid4().hex[:length]

# JSON Utilities
def serialize_json(data: Any) -> str:
    """Serialize data to JSON string."""
    return json.dumps(data, default=str)

def deserialize_json(json_str: str) -> Any:
    """Deserialize JSON string to data."""
    return json.loads(json_str)

def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate data against JSON schema."""
    try:
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False

def format_json(data: Dict[str, Any], indent: int = 2) -> str:
    """Format JSON data with indentation."""
    return json.dumps(data, indent=indent, default=str)

# File Utilities
def get_file_extension(file_path: str) -> str:
    """Get file extension from path."""
    return os.path.splitext(file_path)[1]

def get_mime_type(file_path: str) -> str:
    """Get MIME type for file."""
    return mimetypes.guess_type(file_path)[0] or 'application/octet-stream'

def ensure_directory(directory: str) -> None:
    """Ensure directory exists."""
    Path(directory).mkdir(parents=True, exist_ok=True)

def list_files(directory: str, pattern: str = "*") -> List[str]:
    """List files in directory matching pattern."""
    return [f for f in Path(directory).glob(pattern) if f.is_file()]

# Security Utilities
def generate_key() -> bytes:
    """Generate encryption key."""
    return Fernet.generate_key()

def encrypt_data(data: str, key: bytes) -> str:
    """Encrypt data using Fernet."""
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """Decrypt data using Fernet."""
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()

def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return hash_password(password) == hashed

def generate_token() -> str:
    """Generate random token."""
    return uuid.uuid4().hex

# Validation Utilities
def validate_data(data: Dict[str, Any], model: Type[ModelType]) -> ModelType:
    """Validate data against Pydantic model."""
    return model(**data)

def validate_type(value: Any, expected_type: type) -> bool:
    """Validate value type."""
    return isinstance(value, expected_type)

def validate_range(value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float]) -> bool:
    """Validate value is within range."""
    return min_value <= value <= max_value

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Logging Utilities
def setup_logging(level: int = logging.INFO) -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """Log error with context."""
    logger.error(
        f"Error: {str(error)}",
        extra={"context": context or {}}
    )

def log_info(message: str, context: Dict[str, Any] = None) -> None:
    """Log info with context."""
    logger.info(
        message,
        extra={"context": context or {}}
    )

def log_warning(message: str, context: Dict[str, Any] = None) -> None:
    """Log warning with context."""
    logger.warning(
        message,
        extra={"context": context or {}}
    )

# Cache Utilities
def get_cache() -> redis.Redis:
    """Get Redis cache instance."""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )

def cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate cache key."""
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)

def cache_get(key: str) -> Optional[str]:
    """Get value from cache."""
    cache = get_cache()
    return cache.get(key)

def cache_set(key: str, value: str, expire: int = None) -> None:
    """Set value in cache."""
    cache = get_cache()
    cache.set(key, value, ex=expire)

def cache_delete(key: str) -> None:
    """Delete value from cache."""
    cache = get_cache()
    cache.delete(key)

def cache_clear(pattern: str = "*") -> None:
    """Clear cache by pattern."""
    cache = get_cache()
    for key in cache.scan_iter(pattern):
        cache.delete(key)

# Decorator Utilities
def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator for functions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay)
            raise last_error
        return wrapper
    return decorator

def cache_result(expire: int = 300):
    """Cache function result decorator."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = cache_key(func.__name__, *args, **kwargs)
            result = cache_get(key)
            if result is not None:
                return deserialize_json(result)
            result = await func(*args, **kwargs)
            cache_set(key, serialize_json(result), expire)
            return result
        return wrapper
    return decorator

def validate_input(model: Type[ModelType]):
    """Validate input data decorator."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                validated_data = validate_data(kwargs, model)
                return await func(*args, **validated_data.dict())
            except ValidationError as e:
                raise ValueError(str(e))
        return wrapper
    return decorator

def log_execution_time():
    """Log function execution time decorator."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = get_current_timestamp()
            try:
                result = await func(*args, **kwargs)
                execution_time = calculate_duration(start_time, get_current_timestamp())
                log_info(
                    f"Function {func.__name__} executed in {execution_time:.2f} seconds",
                    {"execution_time": execution_time}
                )
                return result
            except Exception as e:
                execution_time = calculate_duration(start_time, get_current_timestamp())
                log_error(
                    e,
                    {
                        "function": func.__name__,
                        "execution_time": execution_time
                    }
                )
                raise
        return wrapper
    return decorator 