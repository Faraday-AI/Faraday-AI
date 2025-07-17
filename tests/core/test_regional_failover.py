import pytest
import asyncio
from datetime import datetime
from app.core.regional_failover import Region, RegionalFailoverManager
from app.core.database import get_region_db_url, initialize_engines, engines, async_engines
from app.core.cache import RedisCluster, redis_cluster
from app.core.health import check_region_health, HealthCheckResponse, RegionalHealthCheckResponse
import logging
from sqlalchemy import text

# Configure logging
logger = logging.getLogger(__name__)

@pytest.fixture
def failover_manager():
    return RegionalFailoverManager()

@pytest.fixture
def sample_health_data():
    return {
        "system": {"status": "healthy", "cpu": 30, "memory": 50},
        "redis": {"status": "healthy", "connection": "ok"},
        "database": {"status": "healthy", "connection": "ok"},
        "minio": {"status": "healthy", "connection": "ok"}
    }

@pytest.mark.asyncio
async def test_region_enumeration():
    """Test region enumeration values"""
    assert Region.NORTH_AMERICA.value == "north_america"
    assert Region.EUROPE.value == "europe"
    assert Region.ASIA_PACIFIC.value == "asia_pacific"
    assert Region.SOUTH_AMERICA.value == "south_america"
    assert Region.AFRICA.value == "africa"
    assert Region.MIDDLE_EAST.value == "middle_east"

@pytest.mark.asyncio
async def test_database_url_generation():
    """Test database URL generation for different regions"""
    for region in Region:
        db_url = get_region_db_url(region)
        assert region.value in db_url.lower()
        assert "postgres" in db_url.lower()

@pytest.mark.asyncio
async def test_database_engine_initialization():
    """Test database engine initialization for all regions"""
    await initialize_engines()
    for region in Region:
        assert region.value in engines
        assert region.value in async_engines
        assert engines[region.value] is not None
        assert async_engines[region.value] is not None

@pytest.mark.asyncio
async def test_redis_cluster_initialization():
    """Test Redis cluster initialization"""
    assert redis_cluster is not None
    assert redis_cluster.clients is not None
    for region in Region:
        assert region.value in redis_cluster.clients
        assert redis_cluster.clients[region.value] is not None

@pytest.mark.asyncio
async def test_redis_replication():
    """Test Redis cross-region replication"""
    test_key = "test_replication_key"
    test_value = {"test": "data"}
    
    # Set data in primary region
    await redis_cluster.replicate(test_key, test_value)
    
    # Verify data in all regions
    for region in Region:
        client = redis_cluster.get_client(region)
        value = client.get(test_key)
        assert value is not None
        assert value == test_value

@pytest.mark.asyncio
async def test_health_check_single_region():
    """Test health check for a single region"""
    health_data = await check_region_health(Region.NORTH_AMERICA)
    
    assert "status" in health_data
    assert "timestamp" in health_data
    assert "region" in health_data
    assert "details" in health_data
    
    details = health_data["details"]
    assert "system" in details
    assert "redis" in details
    assert "database" in details
    assert "minio" in details

@pytest.mark.asyncio
async def test_health_check_all_regions():
    """Test health check for all regions"""
    health_data = await RegionalHealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        regions={}
    )
    
    for region in Region:
        region_health = await check_region_health(region)
        health_data.regions[region.value] = region_health
    
    assert len(health_data.regions) == len(Region)
    for region in Region:
        assert region.value in health_data.regions
        assert "status" in health_data.regions[region.value]
        assert "details" in health_data.regions[region.value]

@pytest.mark.asyncio
async def test_failover_trigger(failover_manager):
    """Test failover trigger mechanism"""
    # Simulate unhealthy state
    await failover_manager.update_health_status(Region.NORTH_AMERICA, False)
    
    # Check if failover is triggered
    current_region = await failover_manager.get_current_region()
    assert current_region != Region.NORTH_AMERICA
    
    # Verify failover state
    failover_state = await failover_manager.get_failover_state()
    assert failover_state.current_region == current_region
    assert failover_state.last_failover is not None

@pytest.mark.asyncio
async def test_failover_recovery(failover_manager):
    """Test failover recovery mechanism"""
    # Simulate recovery
    await failover_manager.update_health_status(Region.NORTH_AMERICA, True)
    
    # Check if system returns to primary region
    current_region = await failover_manager.get_current_region()
    assert current_region == Region.NORTH_AMERICA
    
    # Verify recovery state
    failover_state = await failover_manager.get_failover_state()
    assert failover_state.current_region == Region.NORTH_AMERICA
    assert failover_state.last_recovery is not None

@pytest.mark.asyncio
async def test_concurrent_failover(failover_manager):
    """Test concurrent failover handling"""
    # Simulate multiple region failures
    tasks = []
    for region in Region:
        if region != Region.NORTH_AMERICA:
            tasks.append(failover_manager.update_health_status(region, False))
    
    await asyncio.gather(*tasks)
    
    # Verify system remains stable
    current_region = await failover_manager.get_current_region()
    assert current_region is not None
    assert isinstance(current_region, Region)

@pytest.mark.asyncio
async def test_error_handling(failover_manager):
    """Test error handling in failover scenarios"""
    # Test invalid region
    with pytest.raises(ValueError):
        await failover_manager.update_health_status("invalid_region", False)
    
    # Test invalid health status
    with pytest.raises(TypeError):
        await failover_manager.update_health_status(Region.NORTH_AMERICA, "invalid_status")
    
    # Test database connection failure
    with pytest.raises(Exception):
        await failover_manager._test_database_connection("invalid_url")

@pytest.mark.asyncio
async def test_performance_metrics(failover_manager):
    """Test performance metrics collection"""
    # Trigger failover
    await failover_manager.update_health_status(Region.NORTH_AMERICA, False)
    
    # Get metrics
    metrics = await failover_manager.get_performance_metrics()
    
    assert "failover_count" in metrics
    assert "average_failover_time" in metrics
    assert "last_failover_duration" in metrics
    assert "current_region_uptime" in metrics
    
    # Verify metrics are valid
    assert metrics["failover_count"] >= 0
    assert metrics["average_failover_time"] >= 0
    assert metrics["last_failover_duration"] >= 0
    assert metrics["current_region_uptime"] >= 0

@pytest.mark.asyncio
async def test_database_connection_pooling():
    """Test database connection pooling across regions"""
    await initialize_engines()
    
    for region in Region:
        engine = engines[region.value]
        pool = engine.pool
        
        # Verify pool configuration
        assert pool.size() <= DB_CONFIG["pool_size"] + DB_CONFIG["max_overflow"]
        assert pool.checkedin() >= 0
        assert pool.checkedout() >= 0
        
        # Test connection acquisition
        with engine.connect() as conn:
            assert conn is not None
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

@pytest.mark.asyncio
async def test_redis_connection_timeout():
    """Test Redis connection timeout handling"""
    test_key = "timeout_test_key"
    test_value = {"test": "timeout_data"}
    
    # Simulate slow connection
    original_timeout = redis_cluster.replication_timeout
    redis_cluster.replication_timeout = 0.1  # Set very short timeout
    
    try:
        # This should raise a timeout exception
        with pytest.raises(asyncio.TimeoutError):
            await redis_cluster.replicate(test_key, test_value)
    finally:
        # Restore original timeout
        redis_cluster.replication_timeout = original_timeout

@pytest.mark.asyncio
async def test_concurrent_data_access():
    """Test concurrent data access across regions"""
    test_key = "concurrent_test_key"
    test_value = {"test": "concurrent_data"}
    
    # Create multiple concurrent access tasks
    tasks = []
    for _ in range(10):
        tasks.append(redis_cluster.replicate(test_key, test_value))
    
    # Execute all tasks concurrently
    await asyncio.gather(*tasks)
    
    # Verify data consistency
    for region in Region:
        client = redis_cluster.get_client(region)
        value = client.get(test_key)
        assert value == test_value

@pytest.mark.asyncio
async def test_health_check_thresholds():
    """Test health check threshold handling"""
    # Test CPU threshold
    system_health = {
        "cpu": 95,  # High CPU usage
        "memory": 50,
        "disk": 60
    }
    
    health_status = await check_region_health(Region.NORTH_AMERICA)
    assert health_status["status"] == "unhealthy"
    
    # Test memory threshold
    system_health = {
        "cpu": 30,
        "memory": 95,  # High memory usage
        "disk": 60
    }
    
    health_status = await check_region_health(Region.NORTH_AMERICA)
    assert health_status["status"] == "unhealthy"

@pytest.mark.asyncio
async def test_failover_priority():
    """Test failover priority order"""
    # Simulate primary region failure
    await failover_manager.update_health_status(Region.NORTH_AMERICA, False)
    
    # Get current region after failover
    current_region = await failover_manager.get_current_region()
    
    # Verify failover priority
    priority_regions = [
        Region.EUROPE,
        Region.ASIA_PACIFIC,
        Region.SOUTH_AMERICA,
        Region.AFRICA,
        Region.MIDDLE_EAST
    ]
    
    assert current_region in priority_regions

@pytest.mark.asyncio
async def test_data_consistency_after_failover():
    """Test data consistency after failover"""
    # Create test data
    test_data = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    }
    
    # Store data in primary region
    for key, value in test_data.items():
        await redis_cluster.replicate(key, value)
    
    # Simulate failover
    await failover_manager.update_health_status(Region.NORTH_AMERICA, False)
    current_region = await failover_manager.get_current_region()
    
    # Verify data in new primary region
    for key, value in test_data.items():
        client = redis_cluster.get_client(current_region)
        stored_value = client.get(key)
        assert stored_value == value

@pytest.mark.asyncio
async def test_graceful_degradation():
    """Test system behavior under partial failure"""
    # Simulate partial service failure
    await failover_manager.update_health_status(Region.NORTH_AMERICA, False)
    await failover_manager.update_health_status(Region.EUROPE, False)
    
    # System should still be operational
    current_region = await failover_manager.get_current_region()
    assert current_region is not None
    assert current_region != Region.NORTH_AMERICA
    assert current_region != Region.EUROPE
    
    # Verify basic operations still work
    test_key = "degradation_test_key"
    test_value = {"test": "degradation_data"}
    await redis_cluster.replicate(test_key, test_value)
    
    client = redis_cluster.get_client(current_region)
    value = client.get(test_key)
    assert value == test_value

@pytest.mark.asyncio
async def test_metrics_accuracy():
    """Test accuracy of performance metrics"""
    # Clear existing metrics
    await failover_manager.reset_metrics()
    
    # Perform multiple failovers
    for _ in range(3):
        await failover_manager.update_health_status(Region.NORTH_AMERICA, False)
        await asyncio.sleep(0.1)  # Small delay between failovers
        await failover_manager.update_health_status(Region.NORTH_AMERICA, True)
    
    # Get metrics
    metrics = await failover_manager.get_performance_metrics()
    
    # Verify metrics accuracy
    assert metrics["failover_count"] == 3
    assert metrics["average_failover_time"] > 0
    assert metrics["last_failover_duration"] > 0
    assert metrics["current_region_uptime"] > 0

@pytest.mark.asyncio
async def test_resource_cleanup():
    """Test proper resource cleanup after operations"""
    # Perform operations that allocate resources
    await initialize_engines()
    await redis_cluster.initialize()
    
    # Verify resource allocation
    for region in Region:
        assert engines[region.value].pool.checkedin() > 0
        assert redis_cluster.clients[region.value] is not None
    
    # Cleanup resources
    for region in Region:
        engines[region.value].dispose()
        await redis_cluster.clients[region.value].close()
    
    # Verify resource cleanup
    for region in Region:
        assert engines[region.value].pool.checkedin() == 0
        assert redis_cluster.clients[region.value].closed 