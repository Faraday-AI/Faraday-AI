# Deployment Configuration Guide

## Overview
This document outlines the deployment configuration for the Faraday AI Dashboard's compatibility service and related components.

## Prerequisites
- Python 3.8+
- Redis 6.0+
- Prometheus
- Grafana
- Docker
- Docker Compose

## Environment Setup

### Environment Variables
```env
# Server Configuration
FARADAY_ENV=production
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/faraday

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_CACHE_TTL=300  # 5 minutes

# Prometheus Configuration
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus-multiproc
METRICS_PORT=9090

# Grafana Configuration
GRAFANA_PORT=3000
```

## Service Dependencies

### Redis Setup
```yaml
# docker-compose.yml
redis:
  image: redis:6.0
  ports:
    - "6379:6379"
  volumes:
    - redis-data:/data
  command: redis-server --appendonly yes
```

### Prometheus Setup
```yaml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
```

### Grafana Setup
```yaml
grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  volumes:
    - ./grafana/dashboards:/var/lib/grafana/dashboards
    - ./grafana/provisioning:/etc/grafana/provisioning
```

## Performance Tuning

### Redis Configuration
```conf
maxmemory 2gb
maxmemory-policy allkeys-lru
timeout 300
tcp-keepalive 60
```

### Application Server Configuration
```python
# uvicorn configuration
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 65
timeout = 120
max_requests = 1000
max_requests_jitter = 50
```

## Monitoring Setup

### Prometheus Metrics
The following metrics are collected:
- `gpt_recommendation_requests_total`
- `gpt_recommendation_latency_seconds`
- `gpt_context_switches_total`
- `gpt_active_contexts`
- `gpt_context_sharing_latency_seconds`
- `gpt_performance_score`

### Grafana Dashboards
Pre-configured dashboards are available at:
- `/grafana/dashboards/gpt_dashboard.json`
- `/grafana/dashboards/compatibility_dashboard.json`

## Load Testing

### Running Load Tests
```bash
# Install locust
pip install locust

# Run load tests
cd app/dashboard/tests/load_tests
locust -f locustfile.py --host=http://localhost:8000

# Access load test UI at http://localhost:8089
```

### Load Test Scenarios
1. Normal Load: 50 users, spawn rate 5/second
2. High Load: 200 users, spawn rate 20/second
3. Cache Testing: 100 users, spawn rate 10/second

## Deployment Steps

1. **Environment Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Database Migration**
   ```bash
   alembic upgrade head
   ```

3. **Start Services**
   ```bash
   # Start all services
   docker-compose up -d
   
   # Start application server
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

4. **Verify Deployment**
   ```bash
   # Check service health
   curl http://localhost:8000/health
   
   # Check metrics endpoint
   curl http://localhost:9090/metrics
   ```

## Troubleshooting

### Common Issues

1. **Redis Connection Issues**
   - Check Redis service status
   - Verify Redis connection URL
   - Check Redis memory usage

2. **Performance Issues**
   - Monitor Prometheus metrics
   - Check Redis cache hit rate
   - Review application logs

3. **High Memory Usage**
   - Adjust Redis maxmemory setting
   - Review cache TTL values
   - Check for memory leaks

### Monitoring Checklist

- [ ] Redis cache hit rate > 80%
- [ ] API response time < 200ms
- [ ] Error rate < 1%
- [ ] Memory usage < 80%
- [ ] CPU usage < 70%

## Security Considerations

1. **Redis Security**
   - Enable authentication
   - Use SSL/TLS for remote connections
   - Restrict network access

2. **API Security**
   - Enable rate limiting
   - Use API keys
   - Implement request validation

3. **Monitoring Security**
   - Secure Prometheus endpoints
   - Use Grafana authentication
   - Encrypt metrics traffic

## Backup and Recovery

1. **Redis Backup**
   ```bash
   # Automatic backup configuration
   dir /var/lib/redis
   dbfilename dump.rdb
   save 900 1
   save 300 10
   save 60 10000
   ```

2. **Metrics Backup**
   - Configure Prometheus data retention
   - Set up periodic snapshots
   - Implement backup rotation

## Scaling Guidelines

1. **Horizontal Scaling**
   - Add application servers
   - Configure load balancing
   - Implement session stickiness

2. **Cache Scaling**
   - Redis cluster configuration
   - Cache sharding
   - Implement cache warm-up

3. **Monitoring Scaling**
   - Prometheus federation
   - Grafana clustering
   - Metrics aggregation 