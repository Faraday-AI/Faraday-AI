"""
Enhanced Redis and In-Memory Cache Manager

This module provides a unified caching interface that supports both Redis and in-memory caching,
with automatic fallback to in-memory when Redis is unavailable. Includes performance monitoring,
connection pooling, and advanced caching strategies.
"""

import json
from typing import Any, Optional, Dict, Tuple, List, Callable, TypeVar, Union
from datetime import datetime, timedelta
import hashlib
import redis
from redis.exceptions import RedisError
import logging
from threading import Lock, RLock
import time
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import zlib
import pickle
import asyncio
from typing import AsyncGenerator, Set
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import random
from prometheus_client import Counter, Histogram, Gauge, Summary
import re
from collections import defaultdict
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

# Prometheus metrics
CACHE_OPERATIONS = Counter('cache_operations_total', 'Total cache operations', ['operation', 'type', 'status'])
CACHE_LATENCY = Histogram('cache_latency_seconds', 'Cache operation latency', ['operation', 'type'])
CACHE_SIZE = Gauge('cache_size_bytes', 'Cache size in bytes', ['type'])
CACHE_HIT_RATIO = Gauge('cache_hit_ratio', 'Cache hit ratio', ['type'])
CACHE_SECURITY = Counter('cache_security_total', 'Security-related events', ['type', 'status'])
CACHE_PATTERNS = Summary('cache_patterns_seconds', 'Cache access patterns', ['pattern'])
CACHE_HEALTH = Gauge('cache_health_status', 'Cache health status', ['component'])
CACHE_PREDICTIONS = Gauge('cache_predictions', 'Cache performance predictions', ['metric'])

# Security constants
MAX_KEY_LENGTH = 256
MAX_VALUE_SIZE = 10 * 1024 * 1024  # 10MB
RATE_LIMIT_WINDOW = 60  # 1 minute
MAX_REQUESTS_PER_WINDOW = 1000

class CacheType(Enum):
    REDIS = "redis"
    MEMORY = "memory"

class CacheStrategy(Enum):
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    RANDOM = "random"  # Random replacement

class CacheHealth(Enum):
    HEALTHY = 1
    WARNING = 2
    CRITICAL = 3

@dataclass
class CacheEntry:
    value: Any
    timestamp: datetime
    ttl: int
    hits: int = 0
    last_accessed: datetime = None
    metadata: Dict[str, Any] = None
    size: int = 0  # Size in bytes
    priority: int = 0  # For priority-based eviction
    access_pattern: List[datetime] = None  # Track access times for pattern analysis

class CacheManager:
    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl: int = 300,
        max_memory_size: int = 10000,
        compression_threshold: int = 1024,  # 1KB
        connection_pool_size: int = 10,
        eviction_strategy: CacheStrategy = CacheStrategy.LRU,
        warmup_enabled: bool = True,
        batch_size: int = 100,
        monitoring_enabled: bool = True,
        security_enabled: bool = True,
        rate_limit_enabled: bool = True,
        audit_logging_enabled: bool = True
    ):
        """
        Initialize the cache manager with enhanced features.
        
        Args:
            redis_url: Optional Redis connection URL
            default_ttl: Default time-to-live in seconds for cache entries
            max_memory_size: Maximum number of items in memory cache
            compression_threshold: Size threshold for compression in bytes
            connection_pool_size: Size of Redis connection pool
            eviction_strategy: Cache eviction strategy
            warmup_enabled: Whether to enable cache warming
            batch_size: Size of batch operations
            monitoring_enabled: Whether to enable detailed monitoring
            security_enabled: Whether to enable security features
            rate_limit_enabled: Whether to enable rate limiting
            audit_logging_enabled: Whether to enable audit logging
        """
        self.default_ttl = default_ttl
        self.max_memory_size = max_memory_size
        self.compression_threshold = compression_threshold
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._redis_client = None
        self._redis_available = False
        self._lock = Lock()
        self._stats = {
            'hits': {'redis': 0, 'memory': 0},
            'misses': {'redis': 0, 'memory': 0},
            'errors': {'redis': 0, 'memory': 0},
            'compressed': 0,
            'decompressed': 0
        }
        
        if redis_url:
            try:
                self._redis_client = redis.Redis.from_url(
                    redis_url,
                    max_connections=connection_pool_size,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
                # Test Redis connection
                self._redis_client.ping()
                self._redis_available = True
                logger.info("Redis cache initialized successfully")
            except RedisError as e:
                logger.warning(f"Redis connection failed, falling back to in-memory cache: {e}")
                self._redis_available = False

        self.eviction_strategy = eviction_strategy
        self.warmup_enabled = warmup_enabled
        self.batch_size = batch_size
        self.monitoring_enabled = monitoring_enabled
        self.security_enabled = security_enabled
        self.rate_limit_enabled = rate_limit_enabled
        self.audit_logging_enabled = audit_logging_enabled
        self._warmup_queue = queue.Queue()
        self._warmup_thread = threading.Thread(target=self._process_warmup_queue, daemon=True)
        self._warmup_thread.start()
        self._batch_queue = queue.Queue()
        self._batch_thread = threading.Thread(target=self._process_batch_queue, daemon=True)
        self._batch_thread.start()
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        self._monitoring_thread = threading.Thread(target=self._update_monitoring_metrics, daemon=True)
        if monitoring_enabled:
            self._monitoring_thread.start()
        self._rate_limit = defaultdict(list)
        self._rate_limit_lock = RLock()
        self._audit_log = []
        self._audit_log_lock = RLock()
        self._access_patterns = defaultdict(list)
        self._pattern_lock = RLock()
        self._health_status = {
            'redis': CacheHealth.HEALTHY,
            'memory': CacheHealth.HEALTHY,
            'overall': CacheHealth.HEALTHY
        }
        self._health_check_thread = threading.Thread(target=self._check_health, daemon=True)
        self._health_check_thread.start()
        self._prediction_thread = threading.Thread(target=self._update_predictions, daemon=True)
        self._prediction_thread.start()

    def _get_cache_key(self, prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments."""
        key_parts = [prefix] + [str(arg) for arg in args]
        return hashlib.md5('_'.join(key_parts).encode()).hexdigest()

    def _serialize(self, value: Any) -> bytes:
        """Serialize a value for storage with optional compression."""
        try:
            data = pickle.dumps(value)
            if len(data) > self.compression_threshold:
                data = zlib.compress(data)
                self._stats['compressed'] += 1
            return data
        except Exception as e:
            logger.error(f"Serialization failed: {e}")
            raise

    def _deserialize(self, data: bytes) -> Any:
        """Deserialize a value from storage with optional decompression."""
        try:
            try:
                return pickle.loads(data)
            except:
                # Try decompression if normal deserialization fails
                decompressed = zlib.decompress(data)
                self._stats['decompressed'] += 1
                return pickle.loads(decompressed)
        except Exception as e:
            logger.error(f"Deserialization failed: {e}")
            raise

    def _validate_key(self, key: str) -> bool:
        """Validate cache key format and length."""
        if not isinstance(key, str):
            CACHE_SECURITY.labels(type='key_validation', status='invalid_type').inc()
            return False
        if len(key) > MAX_KEY_LENGTH:
            CACHE_SECURITY.labels(type='key_validation', status='too_long').inc()
            return False
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', key):
            CACHE_SECURITY.labels(type='key_validation', status='invalid_format').inc()
            return False
        return True

    def _validate_value(self, value: Any) -> bool:
        """Validate cache value size and type."""
        try:
            serialized = pickle.dumps(value)
            if len(serialized) > MAX_VALUE_SIZE:
                CACHE_SECURITY.labels(type='value_validation', status='too_large').inc()
                return False
            return True
        except Exception:
            CACHE_SECURITY.labels(type='value_validation', status='serialization_error').inc()
            return False

    def _check_rate_limit(self, operation: str) -> bool:
        """Check if operation is within rate limits."""
        if not self.rate_limit_enabled:
            return True
            
        current_time = time.time()
        with self._rate_limit_lock:
            # Clean up old entries
            self._rate_limit[operation] = [
                t for t in self._rate_limit[operation]
                if current_time - t < RATE_LIMIT_WINDOW
            ]
            
            if len(self._rate_limit[operation]) >= MAX_REQUESTS_PER_WINDOW:
                CACHE_SECURITY.labels(type='rate_limit', status='exceeded').inc()
                return False
                
            self._rate_limit[operation].append(current_time)
            return True

    def _log_audit(self, operation: str, key: str, success: bool, details: str = None):
        """Log security-relevant operations."""
        if not self.audit_logging_enabled:
            return
            
        with self._audit_log_lock:
            self._audit_log.append({
                'timestamp': datetime.utcnow(),
                'operation': operation,
                'key': key,
                'success': success,
                'details': details
            })
            # Keep only last 1000 entries
            if len(self._audit_log) > 1000:
                self._audit_log.pop(0)

    def _update_access_pattern(self, key: str):
        """Update access pattern for predictive analysis."""
        with self._pattern_lock:
            self._access_patterns[key].append(datetime.utcnow())
            # Keep only last 100 access times
            if len(self._access_patterns[key]) > 100:
                self._access_patterns[key].pop(0)

    def _check_health(self):
        """Periodically check cache health status."""
        while True:
            try:
                # Check Redis health
                if self._redis_available:
                    try:
                        self._redis_client.ping()
                        self._health_status['redis'] = CacheHealth.HEALTHY
                    except RedisError:
                        self._health_status['redis'] = CacheHealth.CRITICAL

                # Check memory cache health
                memory_usage = sum(entry.size for entry in self._memory_cache.values())
                if memory_usage > self.max_memory_size * 0.9:  # 90% threshold
                    self._health_status['memory'] = CacheHealth.WARNING
                else:
                    self._health_status['memory'] = CacheHealth.HEALTHY

                # Update overall health
                self._health_status['overall'] = max(
                    self._health_status['redis'],
                    self._health_status['memory']
                )

                # Update Prometheus metrics
                for component, status in self._health_status.items():
                    CACHE_HEALTH.labels(component=component).set(status.value)

                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                time.sleep(300)  # Wait longer on error

    def _update_predictions(self):
        """Update performance predictions based on access patterns."""
        while True:
            try:
                with self._pattern_lock:
                    for key, access_times in self._access_patterns.items():
                        if len(access_times) >= 10:  # Need enough data points
                            # Calculate time between accesses
                            intervals = [
                                (access_times[i+1] - access_times[i]).total_seconds()
                                for i in range(len(access_times)-1)
                            ]
                            
                            if intervals:
                                # Predict next access time
                                mean_interval = np.mean(intervals)
                                std_interval = np.std(intervals)
                                next_access = datetime.utcnow() + timedelta(seconds=mean_interval)
                                
                                # Update prediction metrics
                                CACHE_PREDICTIONS.labels(metric='next_access').set(
                                    next_access.timestamp()
                                )
                                CACHE_PREDICTIONS.labels(metric='confidence').set(
                                    1 - min(1, std_interval / mean_interval)
                                )

                time.sleep(300)  # Update every 5 minutes
            except Exception as e:
                logger.error(f"Prediction update failed: {e}")
                time.sleep(600)  # Wait longer on error

    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """Get a value from cache with enhanced security and monitoring."""
        if not self._validate_key(key):
            self._log_audit('get', key, False, 'Invalid key format')
            return None

        if not self._check_rate_limit('get'):
            self._log_audit('get', key, False, 'Rate limit exceeded')
            return None

        start_time = time.time()
        try:
            value = self._get_impl(key, ttl)
            if value is not None:
                self._update_access_pattern(key)
                self._log_audit('get', key, True)
            return value
        finally:
            CACHE_PATTERNS.labels(pattern='get').observe(time.time() - start_time)

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Set a value in cache with enhanced security and monitoring."""
        if not self._validate_key(key):
            self._log_audit('set', key, False, 'Invalid key format')
            return

        if not self._validate_value(value):
            self._log_audit('set', key, False, 'Invalid value')
            return

        if not self._check_rate_limit('set'):
            self._log_audit('set', key, False, 'Rate limit exceeded')
            return

        start_time = time.time()
        try:
            self._set_impl(key, value, ttl, metadata)
            self._log_audit('set', key, True)
        finally:
            CACHE_PATTERNS.labels(pattern='set').observe(time.time() - start_time)

    def _get_impl(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """Implementation of get method."""
        # Try Redis first if available
        if self._redis_available:
            try:
                data = self._redis_client.get(key)
                if data:
                    value = self._deserialize(data)
                    self._stats['hits']['redis'] += 1
                    return value
                self._stats['misses']['redis'] += 1
            except RedisError as e:
                logger.warning(f"Redis get failed: {e}")
                self._stats['errors']['redis'] += 1
                self._redis_available = False

        # Fall back to memory cache
        with self._lock:
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                if entry.timestamp + timedelta(seconds=ttl or entry.ttl) > datetime.utcnow():
                    entry.hits += 1
                    entry.last_accessed = datetime.utcnow()
                    self._stats['hits']['memory'] += 1
                    return entry.value
                del self._memory_cache[key]
            self._stats['misses']['memory'] += 1

        return None

    def _set_impl(self, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Implementation of set method."""
        ttl = ttl or self.default_ttl
        
        # Try Redis first if available
        if self._redis_available:
            try:
                data = self._serialize(value)
                self._redis_client.setex(key, ttl, data)
            except RedisError as e:
                logger.warning(f"Redis set failed: {e}")
                self._stats['errors']['redis'] += 1
                self._redis_available = False

        # Always update memory cache as fallback
        with self._lock:
            self._memory_cache[key] = CacheEntry(
                value=value,
                timestamp=datetime.utcnow(),
                ttl=ttl,
                metadata=metadata
            )
            self._clean_memory_cache()

    def delete(self, key: str) -> None:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key to delete
        """
        # Try Redis first if available
        if self._redis_available:
            try:
                self._redis_client.delete(key)
            except RedisError as e:
                logger.warning(f"Redis delete failed: {e}")
                self._stats['errors']['redis'] += 1
                self._redis_available = False

        # Delete from memory cache
        with self._lock:
            if key in self._memory_cache:
                del self._memory_cache[key]

    def _clean_memory_cache(self) -> None:
        """Clean expired entries and enforce size limits in memory cache."""
        current_time = datetime.utcnow()
        
        # Remove expired entries
        self._memory_cache = {
            k: v for k, v in self._memory_cache.items()
            if v.timestamp + timedelta(seconds=v.ttl) > current_time
        }
        
        # If still over limit, apply eviction strategy
        if len(self._memory_cache) > self.max_memory_size:
            if self.eviction_strategy == CacheStrategy.LRU:
                sorted_entries = sorted(
                    self._memory_cache.items(),
                    key=lambda x: (x[1].last_accessed or x[1].timestamp)
                )
            elif self.eviction_strategy == CacheStrategy.LFU:
                sorted_entries = sorted(
                    self._memory_cache.items(),
                    key=lambda x: x[1].hits
                )
            elif self.eviction_strategy == CacheStrategy.FIFO:
                sorted_entries = sorted(
                    self._memory_cache.items(),
                    key=lambda x: x[1].timestamp
                )
            else:  # RANDOM
                sorted_entries = list(self._memory_cache.items())
                random.shuffle(sorted_entries)
            
            self._memory_cache = dict(sorted_entries[-self.max_memory_size:])

    def get_stats(self) -> Dict[str, Any]:
        """
        Get detailed cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        stats = {
            'redis_available': self._redis_available,
            'memory_cache_size': len(self._memory_cache),
            'default_ttl': self.default_ttl,
            'stats': self._stats.copy(),
            'memory_usage': {
                'total': len(self._memory_cache),
                'total_size': sum(entry.size for entry in self._memory_cache.values()),
                'avg_entry_size': sum(entry.size for entry in self._memory_cache.values()) / len(self._memory_cache) if self._memory_cache else 0
            },
            'eviction_strategy': self.eviction_strategy.value,
            'warmup_queue_size': self._warmup_queue.qsize(),
            'batch_queue_size': self._batch_queue.qsize(),
            'compression_stats': {
                'compressed': self._stats['compressed'],
                'decompressed': self._stats['decompressed']
            }
        }
        
        if self._redis_available:
            try:
                redis_info = self._redis_client.info()
                stats['redis_info'] = {
                    'used_memory': redis_info['used_memory'],
                    'connected_clients': redis_info['connected_clients'],
                    'total_commands_processed': redis_info['total_commands_processed']
                }
            except RedisError:
                pass
        
        return stats

    def clear(self) -> None:
        """Clear all cache entries."""
        if self._redis_available:
            try:
                self._redis_client.flushdb()
            except RedisError as e:
                logger.warning(f"Redis clear failed: {e}")
                self._stats['errors']['redis'] += 1
        
        with self._lock:
            self._memory_cache.clear()

    def get_keys(self, pattern: str = "*") -> List[str]:
        """
        Get all cache keys matching a pattern.
        
        Args:
            pattern: Pattern to match keys against
            
        Returns:
            List of matching keys
        """
        keys = []
        
        if self._redis_available:
            try:
                keys.extend(self._redis_client.keys(pattern))
            except RedisError as e:
                logger.warning(f"Redis keys failed: {e}")
                self._stats['errors']['redis'] += 1
        
        with self._lock:
            keys.extend(k for k in self._memory_cache.keys() if pattern == "*" or pattern in k)
        
        return keys

    def _update_monitoring_metrics(self) -> None:
        """Update Prometheus metrics periodically."""
        while True:
            try:
                # Update cache size metrics
                CACHE_SIZE.labels(type='memory').set(
                    sum(entry.size for entry in self._memory_cache.values())
                )
                if self._redis_available:
                    try:
                        CACHE_SIZE.labels(type='redis').set(
                            self._redis_client.info()['used_memory']
                        )
                    except RedisError:
                        pass

                # Update hit ratio metrics
                total_hits = sum(self._stats['hits'].values())
                total_requests = total_hits + sum(self._stats['misses'].values())
                if total_requests > 0:
                    hit_ratio = total_hits / total_requests
                    CACHE_HIT_RATIO.labels(type='memory').set(hit_ratio)
                    if self._redis_available:
                        CACHE_HIT_RATIO.labels(type='redis').set(hit_ratio)

                time.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Failed to update monitoring metrics: {e}")
                time.sleep(300)  # Wait longer on error

    def _process_warmup_queue(self) -> None:
        """Process cache warmup requests in background."""
        while True:
            try:
                warmup_request = self._warmup_queue.get()
                if warmup_request is None:  # Shutdown signal
                    break
                
                key, value, ttl, metadata = warmup_request
                self.set(key, value, ttl, metadata)
                self._warmup_queue.task_done()
            except Exception as e:
                logger.error(f"Failed to process warmup request: {e}")

    def _process_batch_queue(self) -> None:
        """Process batch operations in background."""
        while True:
            try:
                batch_operations = []
                while len(batch_operations) < self.batch_size:
                    try:
                        operation = self._batch_queue.get_nowait()
                        if operation is None:  # Shutdown signal
                            return
                        batch_operations.append(operation)
                        self._batch_queue.task_done()
                    except queue.Empty:
                        break

                if batch_operations:
                    self._execute_batch_operations(batch_operations)
            except Exception as e:
                logger.error(f"Failed to process batch operations: {e}")

    def _execute_batch_operations(self, operations: List[Tuple[str, Any, Any]]) -> None:
        """Execute a batch of cache operations."""
        try:
            if self._redis_available:
                pipeline = self._redis_client.pipeline()
                for op_type, key, value in operations:
                    if op_type == 'set':
                        data = self._serialize(value)
                        pipeline.setex(key, self.default_ttl, data)
                    elif op_type == 'delete':
                        pipeline.delete(key)
                pipeline.execute()
        except RedisError as e:
            logger.warning(f"Redis batch operation failed: {e}")
            self._redis_available = False

        # Always update memory cache
        with self._lock:
            for op_type, key, value in operations:
                if op_type == 'set':
                    self._memory_cache[key] = CacheEntry(
                        value=value,
                        timestamp=datetime.utcnow(),
                        ttl=self.default_ttl
                    )
                elif op_type == 'delete':
                    self._memory_cache.pop(key, None)
            self._clean_memory_cache()

    def warmup_cache(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Queue a cache entry for warmup.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional time-to-live override
            metadata: Optional metadata for the cache entry
        """
        if self.warmup_enabled:
            self._warmup_queue.put((key, value, ttl or self.default_ttl, metadata))

    def batch_set(self, items: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """
        Queue multiple items for batch setting.
        
        Args:
            items: Dictionary of key-value pairs to cache
            ttl: Optional time-to-live override
        """
        for key, value in items.items():
            self._batch_queue.put(('set', key, value))

    def batch_delete(self, keys: List[str]) -> None:
        """
        Queue multiple keys for batch deletion.
        
        Args:
            keys: List of keys to delete
        """
        for key in keys:
            self._batch_queue.put(('delete', key, None))

    def get_multi(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.
        
        Args:
            keys: List of keys to retrieve
            
        Returns:
            Dictionary of key-value pairs
        """
        results = {}
        if self._redis_available:
            try:
                pipeline = self._redis_client.pipeline()
                for key in keys:
                    pipeline.get(key)
                values = pipeline.execute()
                
                for key, data in zip(keys, values):
                    if data:
                        results[key] = self._deserialize(data)
                        self._stats['hits']['redis'] += 1
                    else:
                        self._stats['misses']['redis'] += 1
            except RedisError as e:
                logger.warning(f"Redis multi-get failed: {e}")
                self._redis_available = False

        # Fall back to memory cache for remaining keys
        with self._lock:
            for key in keys:
                if key not in results and key in self._memory_cache:
                    entry = self._memory_cache[key]
                    if entry.timestamp + timedelta(seconds=entry.ttl) > datetime.utcnow():
                        results[key] = entry.value
                        entry.hits += 1
                        entry.last_accessed = datetime.utcnow()
                        self._stats['hits']['memory'] += 1
                    else:
                        del self._memory_cache[key]
                        self._stats['misses']['memory'] += 1

        return results

T = TypeVar('T')

def cached(
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None,
    cache_type: CacheType = CacheType.REDIS
):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Optional time-to-live in seconds
        key_prefix: Optional prefix for cache key
        cache_type: Preferred cache type to use
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> T:
            if not hasattr(self, 'cache'):
                return await func(self, *args, **kwargs)
                
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            key = self.cache._get_cache_key(prefix, *args, *sorted(kwargs.items()))
            
            # Try to get from cache
            result = self.cache.get(key, ttl)
            if result is not None:
                return result
                
            # Call function and cache result
            result = await func(self, *args, **kwargs)
            self.cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator 