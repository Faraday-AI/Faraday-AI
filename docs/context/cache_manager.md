# Cache Manager Documentation

## Overview

The Cache Manager provides a unified caching interface that supports both Redis and in-memory caching, with automatic fallback to in-memory when Redis is unavailable. It includes performance monitoring, connection pooling, and advanced caching strategies.

## Features

- **Dual Storage**: Supports both Redis and in-memory caching
- **Automatic Fallback**: Gracefully falls back to in-memory when Redis is unavailable
- **Advanced Eviction**: Multiple eviction strategies (LRU, LFU, FIFO, Random)
- **Performance Monitoring**: Comprehensive metrics and statistics
- **Batch Operations**: Efficient bulk operations
- **Cache Warming**: Proactive cache population
- **Data Compression**: Automatic compression for large values
- **Thread Safety**: Safe for concurrent access

## Usage

### Basic Operations

```python
from app.dashboard.services.cache_manager import CacheManager, CacheStrategy

# Initialize cache manager
cache = CacheManager(
    redis_url='redis://localhost:6379/0',
    default_ttl=300,  # 5 minutes
    max_memory_size=10000,
    eviction_strategy=CacheStrategy.LRU
)

# Set value
cache.set('key', 'value')

# Get value
value = cache.get('key')

# Delete value
cache.delete('key')
```

### Batch Operations

```python
# Batch set multiple values
items = {'key1': 'value1', 'key2': 'value2'}
cache.batch_set(items)

# Batch get multiple values
results = cache.get_multi(['key1', 'key2'])

# Batch delete multiple keys
cache.batch_delete(['key1', 'key2'])
```

### Cache Warming

```python
# Queue items for warmup
cache.warmup_cache('key', 'value')

# Wait for warmup to complete
time.sleep(0.1)
```

### Monitoring

```python
# Get cache statistics
stats = cache.get_stats()

# Access specific metrics
hits = stats['stats']['hits']
misses = stats['stats']['misses']
memory_usage = stats['memory_usage']
```

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `redis_url` | Redis connection URL | None |
| `default_ttl` | Default time-to-live in seconds | 300 |
| `max_memory_size` | Maximum number of items in memory cache | 10000 |
| `compression_threshold` | Size threshold for compression in bytes | 1024 |
| `connection_pool_size` | Size of Redis connection pool | 10 |
| `eviction_strategy` | Cache eviction strategy | LRU |
| `warmup_enabled` | Whether to enable cache warming | True |
| `batch_size` | Size of batch operations | 100 |
| `monitoring_enabled` | Whether to enable detailed monitoring | True |

## Eviction Strategies

1. **LRU (Least Recently Used)**
   - Removes the least recently accessed items
   - Best for temporal locality

2. **LFU (Least Frequently Used)**
   - Removes the least frequently accessed items
   - Best for stable access patterns

3. **FIFO (First In First Out)**
   - Removes the oldest items
   - Simple and predictable

4. **Random**
   - Randomly removes items
   - Good for uniform access patterns

## Performance Considerations

1. **Memory Usage**
   - Monitor memory usage through `get_stats()`
   - Adjust `max_memory_size` based on available memory
   - Use compression for large values

2. **Redis Connection**
   - Use connection pooling for better performance
   - Handle Redis failures gracefully
   - Monitor Redis availability

3. **Batch Operations**
   - Use batch operations for bulk data
   - Adjust `batch_size` based on workload
   - Monitor batch queue size

## Best Practices

1. **Key Design**
   - Use consistent key prefixes
   - Include version information
   - Keep keys short but descriptive

2. **TTL Management**
   - Set appropriate TTLs
   - Use shorter TTLs for volatile data
   - Consider cache warming for critical data

3. **Error Handling**
   - Handle cache misses gracefully
   - Implement fallback mechanisms
   - Monitor error rates

4. **Monitoring**
   - Track hit/miss ratios
   - Monitor memory usage
   - Set up alerts for critical metrics

## Troubleshooting

1. **High Memory Usage**
   - Check for memory leaks
   - Adjust eviction strategy
   - Increase compression threshold

2. **Redis Connection Issues**
   - Verify Redis configuration
   - Check network connectivity
   - Monitor connection pool

3. **Performance Issues**
   - Check batch sizes
   - Monitor queue lengths
   - Verify compression settings

## API Reference

### CacheManager

```python
class CacheManager:
    def __init__(
        self,
        redis_url: Optional[str] = None,
        default_ttl: int = 300,
        max_memory_size: int = 10000,
        compression_threshold: int = 1024,
        connection_pool_size: int = 10,
        eviction_strategy: CacheStrategy = CacheStrategy.LRU,
        warmup_enabled: bool = True,
        batch_size: int = 100,
        monitoring_enabled: bool = True
    )

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None

    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]

    def delete(self, key: str) -> None

    def batch_set(self, items: Dict[str, Any], ttl: Optional[int] = None) -> None

    def batch_delete(self, keys: List[str]) -> None

    def get_multi(self, keys: List[str]) -> Dict[str, Any]

    def warmup_cache(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None

    def get_stats(self) -> Dict[str, Any]

    def clear(self) -> None
```

## Deployment

### Requirements

- Python 3.7+
- Redis server (optional)
- Prometheus (for monitoring)

### Installation

1. Install dependencies:
```bash
pip install redis prometheus-client
```

2. Configure Redis (optional):
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo service redis-server start
```

3. Configure monitoring:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'cache_manager'
    static_configs:
      - targets: ['localhost:8000']
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | None |
| `CACHE_TTL` | Default cache TTL | 300 |
| `MAX_MEMORY_SIZE` | Maximum memory cache size | 10000 |
| `COMPRESSION_THRESHOLD` | Compression threshold | 1024 |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 