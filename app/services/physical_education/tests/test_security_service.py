import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from unittest.mock import Mock
from app.services.physical_education.security_service import SecurityService, ThreatLevel

@pytest.fixture
async def redis_client():
    """Create a Redis client for testing."""
    redis = await aioredis.from_url("redis://redis:6379/1")
    yield redis
    await redis.flushdb()
    await redis.close()

@pytest.fixture
async def security_service(redis_client):
    """Create a SecurityService instance."""
    service = SecurityService(redis_client)
    await service.initialize()
    yield service
    await service.cleanup()

@pytest.fixture
def mock_request():
    """Create a mock request."""
    request = Mock(spec=Request)
    request.client.host = "127.0.0.1"
    request.url.path = "/test"
    return request

@pytest.mark.asyncio
async def test_initialization(security_service):
    """Test service initialization."""
    assert security_service.blocked_ips == set()
    assert len(security_service.suspicious_patterns['critical']) > 0
    assert len(security_service.suspicious_patterns['high']) > 0
    assert len(security_service.suspicious_patterns['medium']) > 0
    assert len(security_service.suspicious_patterns['low']) > 0
    assert 'default' in security_service.rate_limits
    assert 'critical' in security_service.rate_limits
    assert ThreatLevel.CRITICAL in security_service.threat_thresholds

@pytest.mark.asyncio
async def test_threat_level_detection(security_service):
    """Test threat level detection for different patterns."""
    # Test critical patterns
    assert security_service._check_threat_level("/.env") == ThreatLevel.CRITICAL
    assert security_service._check_threat_level("/.git/config") == ThreatLevel.CRITICAL
    assert security_service._check_threat_level("/backup.sql") == ThreatLevel.CRITICAL
    
    # Test high risk patterns
    assert security_service._check_threat_level("/wp-admin") == ThreatLevel.HIGH
    assert security_service._check_threat_level("/.htaccess") == ThreatLevel.HIGH
    assert security_service._check_threat_level("/error.log") == ThreatLevel.HIGH
    
    # Test medium risk patterns
    assert security_service._check_threat_level("/test.php") == ThreatLevel.MEDIUM
    assert security_service._check_threat_level("/config.yaml") == ThreatLevel.MEDIUM
    assert security_service._check_threat_level("/backup") == ThreatLevel.MEDIUM
    
    # Test low risk patterns
    assert security_service._check_threat_level("/test") == ThreatLevel.LOW
    assert security_service._check_threat_level("/demo") == ThreatLevel.LOW
    
    # Test safe patterns
    assert security_service._check_threat_level("/api/v1/users") == ThreatLevel.LOW
    assert security_service._check_threat_level("/static/css/style.css") == ThreatLevel.LOW

@pytest.mark.asyncio
async def test_threat_tracking(security_service):
    """Test threat tracking functionality."""
    ip = "192.168.1.1"
    
    # Track critical threat
    await security_service.track_suspicious_request(ip, "/.env", ThreatLevel.CRITICAL)
    assert await security_service.is_ip_blocked(ip)  # Should be blocked after critical threat
    
    # Test different IP with high threat
    ip2 = "192.168.1.2"
    for _ in range(4):  # One less than threshold
        await security_service.track_suspicious_request(ip2, "/wp-admin", ThreatLevel.HIGH)
    assert not await security_service.is_ip_blocked(ip2)
    
    # One more request should trigger block
    await security_service.track_suspicious_request(ip2, "/wp-admin", ThreatLevel.HIGH)
    assert await security_service.is_ip_blocked(ip2)

@pytest.mark.asyncio
async def test_rate_limiting_by_threat_level(security_service, mock_request):
    """Test rate limiting based on threat levels."""
    # Test critical rate limit
    mock_request.url.path = "/.env"
    for _ in range(2):  # Critical limit is 2
        assert await security_service.check_rate_limit(mock_request.client.host, mock_request.url.path, 'critical')
    assert not await security_service.check_rate_limit(mock_request.client.host, mock_request.url.path, 'critical')
    
    # Test suspicious rate limit
    mock_request.url.path = "/test.php"
    for _ in range(10):  # Suspicious limit is 10
        assert await security_service.check_rate_limit(mock_request.client.host, mock_request.url.path, 'suspicious')
    assert not await security_service.check_rate_limit(mock_request.client.host, mock_request.url.path, 'suspicious')

@pytest.mark.asyncio
async def test_threat_assessment(security_service):
    """Test threat assessment functionality."""
    ip = "192.168.1.1"
    
    # Test initial assessment
    assert await security_service._assess_threat_level(ip) == ThreatLevel.LOW
    
    # Test critical threat assessment
    await security_service.track_suspicious_request(ip, "/.env", ThreatLevel.CRITICAL)
    assert await security_service._assess_threat_level(ip) == ThreatLevel.CRITICAL
    
    # Test high threat assessment
    ip2 = "192.168.1.2"
    for _ in range(5):
        await security_service.track_suspicious_request(ip2, "/wp-admin", ThreatLevel.HIGH)
    assert await security_service._assess_threat_level(ip2) == ThreatLevel.HIGH

@pytest.mark.asyncio
async def test_request_checking(security_service, mock_request):
    """Test comprehensive request checking."""
    # Test normal request
    assert await security_service.check_request(mock_request)
    
    # Test critical pattern
    mock_request.url.path = "/.env"
    with pytest.raises(Exception) as exc_info:
        await security_service.check_request(mock_request)
    assert "Critical risk activity detected" in str(exc_info.value)
    
    # Test high risk pattern
    mock_request.url.path = "/wp-admin"
    for _ in range(5):
        with pytest.raises(Exception) as exc_info:
            await security_service.check_request(mock_request)
    assert "High risk activity detected" in str(exc_info.value)

@pytest.mark.asyncio
async def test_monitoring_task(security_service):
    """Test threat monitoring task."""
    # Add some suspicious activity
    ip = "192.168.1.1"
    await security_service.track_suspicious_request(ip, "/.env", ThreatLevel.CRITICAL)
    
    # Wait for monitoring task to run
    await asyncio.sleep(1)
    
    # Check if IP was blocked by monitoring task
    assert await security_service.is_ip_blocked(ip)
    
    # Check metrics
    metrics = await security_service.get_security_metrics()
    assert metrics['blocked_ips_count'] > 0
    assert metrics['suspicious_requests'] > 0

@pytest.mark.asyncio
async def test_cleanup_task(security_service):
    """Test cleanup task functionality."""
    # Block some IPs
    test_ips = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
    for ip in test_ips:
        await security_service.block_ip(ip, "Test block")
    
    # Verify all IPs are blocked
    for ip in test_ips:
        assert await security_service.is_ip_blocked(ip)
    
    # Wait for cleanup task cycle
    await asyncio.sleep(1)
    
    # IPs should still be blocked (not enough time passed)
    for ip in test_ips:
        assert await security_service.is_ip_blocked(ip)

@pytest.mark.asyncio
async def test_concurrent_operations(security_service):
    """Test concurrent security operations."""
    async def simulate_requests(ip: str, path: str):
        for _ in range(10):
            try:
                mock_req = Mock(spec=Request)
                mock_req.client.host = ip
                mock_req.url.path = path
                await security_service.check_request(mock_req)
            except Exception:
                pass
    
    # Run concurrent requests with different patterns
    tasks = [
        simulate_requests(f"192.168.1.{i}", path)
        for i, path in enumerate(["/test", "/.env", "/wp-admin", "/config.php"])
    ]
    await asyncio.gather(*tasks)
    
    # Check metrics
    metrics = await security_service.get_security_metrics()
    assert metrics['blocked_ips_count'] > 0
    assert metrics['suspicious_requests'] > 0
    assert metrics['rate_limit_violations'] > 0

@pytest.mark.asyncio
async def test_request_size_limits(security_service, mock_request):
    """Test request size limit enforcement"""
    # Test headers size limit
    mock_request.headers = {"x-test": "a" * 9000}  # Exceeds 8KB limit
    with pytest.raises(HTTPException) as exc_info:
        await security_service.check_request(mock_request)
    assert exc_info.value.status_code == 413
    assert "headers too large" in str(exc_info.value.detail)
    
    # Test URL size limit
    mock_request.url = Mock()
    mock_request.url.path = "/" + "a" * 3000  # Exceeds 2KB limit
    with pytest.raises(HTTPException) as exc_info:
        await security_service.check_request(mock_request)
    assert exc_info.value.status_code == 414
    assert "URL too long" in str(exc_info.value.detail)
    
    # Test query string limit
    mock_request.query_params = "a" * 2000  # Exceeds 1KB limit
    with pytest.raises(HTTPException) as exc_info:
        await security_service.check_request(mock_request)
    assert exc_info.value.status_code == 414
    assert "Query string too long" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_malicious_user_agent_detection(security_service, mock_request):
    """Test malicious user agent detection"""
    # Test known malicious user agent
    mock_request.headers = {"user-agent": "curl/7.68.0"}
    await security_service.check_request(mock_request)
    metrics = await security_service.get_security_metrics()
    assert metrics['malicious_user_agents'] > 0
    
    # Test normal user agent
    mock_request.headers = {"user-agent": "Mozilla/5.0"}
    await security_service.check_request(mock_request)
    metrics = await security_service.get_security_metrics()
    assert metrics['malicious_user_agents'] == 0

@pytest.mark.asyncio
async def test_malicious_ip_range_detection(security_service, mock_request):
    """Test malicious IP range detection"""
    # Test IP in malicious range
    mock_request.client.host = "1.0.0.1"  # In example malicious range
    await security_service.check_request(mock_request)
    metrics = await security_service.get_security_metrics()
    assert metrics['malicious_ip_ranges'] > 0
    
    # Test IP not in malicious range
    mock_request.client.host = "192.168.1.1"  # Not in malicious range
    await security_service.check_request(mock_request)
    metrics = await security_service.get_security_metrics()
    assert metrics['malicious_ip_ranges'] == 0

@pytest.mark.asyncio
async def test_security_metrics_integration(security_service, mock_request):
    """Test integration of all security metrics"""
    # Trigger various security events
    mock_request.headers = {"user-agent": "curl/7.68.0"}
    mock_request.client.host = "1.0.0.1"
    mock_request.url.path = "/.env"
    
    try:
        await security_service.check_request(mock_request)
    except HTTPException:
        pass
    
    metrics = await security_service.get_security_metrics()
    assert all(key in metrics for key in [
        'blocked_ips_count',
        'suspicious_requests',
        'rate_limit_violations',
        'malicious_user_agents',
        'malicious_ip_ranges',
        'request_size_violations'
    ]) 