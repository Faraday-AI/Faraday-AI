"""
Tests for the load balancer background jobs.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.orm import Session

from app.core.load_balancer_jobs import LoadBalancerJobs
from app.core.regional_failover import Region
from app.models.load_balancer import (
    LoadBalancerConfig,
    RegionConfig,
    MetricsHistory,
    AlertConfig,
    AlertHistory,
    AlertType,
    AlertSeverity,
    RoutingStrategy
)

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    mock = Mock(spec=Session)
    mock.query.return_value.filter.return_value.all.return_value = []
    mock.commit.return_value = None
    mock.close.return_value = None
    return mock

@pytest.fixture
def mock_cache():
    """Create a mock cache."""
    with patch('app.core.load_balancer_jobs.load_balancer_cache') as mock:
        mock.get_recent_metrics.return_value = None
        mock.set_health_status.return_value = None
        yield mock

@pytest.fixture
def jobs(mock_db, mock_cache):
    """Create a load balancer jobs instance with mocked dependencies."""
    with patch('app.core.load_balancer_jobs.get_db') as mock_get_db:
        mock_get_db.return_value = iter([mock_db])
        return LoadBalancerJobs()

@pytest.fixture
def sample_metrics():
    """Create sample metrics data."""
    return [
        {
            'metrics_type': 'requests',
            'value': 100.0,
            'timestamp': datetime.utcnow().isoformat()
        },
        {
            'metrics_type': 'latency',
            'value': 45.7,
            'timestamp': datetime.utcnow().isoformat()
        }
    ]

@pytest.fixture
def sample_alert_config():
    """Create a sample alert configuration."""
    return AlertConfig(
        id=1,
        load_balancer_config_id=1,
        alert_type=AlertType.LOAD,
        severity=AlertSeverity.WARNING,
        threshold_settings={
            'value': 1000,
            'operator': 'gt'
        },
        notification_settings=[
            {'type': 'email', 'to': 'admin@example.com'},
            {'type': 'slack', 'channel': '#alerts'}
        ],
        is_active=True,
        cooldown_seconds=300
    )

@pytest.mark.asyncio
class TestLoadBalancerJobs:
    """Test cases for LoadBalancerJobs."""
    
    async def test_start_stop(self, jobs):
        """Test starting and stopping background jobs."""
        assert not jobs.running
        assert not jobs.tasks
        
        await jobs.start()
        assert jobs.running
        assert len(jobs.tasks) == 4  # 4 background tasks
        
        await jobs.stop()
        assert not jobs.running
        assert not jobs.tasks
        
    async def test_collect_metrics(self, jobs, mock_db, mock_cache, sample_metrics):
        """Test metrics collection job."""
        # Setup active region
        region_config = RegionConfig(
            id=1,
            region=Region.NORTH_AMERICA,
            is_active=True
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [region_config]
        mock_cache.get_recent_metrics.return_value = sample_metrics
        
        # Start collection
        jobs.running = True
        task = asyncio.create_task(jobs._collect_metrics())
        
        # Let it run one iteration
        await asyncio.sleep(0.1)
        jobs.running = False
        await task
        
        # Verify metrics were processed
        mock_cache.get_recent_metrics.assert_called_with(Region.NORTH_AMERICA)
        assert mock_db.add.call_count == 2  # Two metrics types
        mock_db.commit.assert_called_once()
        
    async def test_process_alerts(self, jobs, mock_db, sample_alert_config):
        """Test alert processing job."""
        # Setup active alert
        mock_db.query.return_value.filter.return_value.all.return_value = [sample_alert_config]
        
        # Mock current value check
        with patch.object(jobs, '_get_current_value') as mock_get_value:
            mock_get_value.return_value = 1500  # Above threshold
            
            # Start processing
            jobs.running = True
            task = asyncio.create_task(jobs._process_alerts())
            
            # Let it run one iteration
            await asyncio.sleep(0.1)
            jobs.running = False
            await task
            
            # Verify alert was processed
            mock_get_value.assert_called_with(mock_db, sample_alert_config)
            assert mock_db.add.call_count == 1  # One alert history entry
            mock_db.commit.assert_called_once()
            
    async def test_monitor_health(self, jobs, mock_db, mock_cache):
        """Test health monitoring job."""
        # Setup active region
        region_config = RegionConfig(
            id=1,
            region=Region.NORTH_AMERICA,
            is_active=True
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [region_config]
        
        # Mock health check
        health_status = {
            "status": "healthy",
            "last_check": datetime.utcnow().isoformat(),
            "metrics": {"latency": 45.7}
        }
        with patch.object(jobs, '_check_region_health', new_callable=AsyncMock) as mock_check:
            mock_check.return_value = health_status
            
            # Start monitoring
            jobs.running = True
            task = asyncio.create_task(jobs._monitor_health())
            
            # Let it run one iteration
            await asyncio.sleep(0.1)
            jobs.running = False
            await task
            
            # Verify health was checked
            mock_check.assert_called_with(region_config)
            mock_cache.set_health_status.assert_called_with(
                Region.NORTH_AMERICA,
                health_status
            )
            
    def test_check_alert_conditions(self, jobs, mock_db, sample_alert_config):
        """Test alert condition checking."""
        # Test greater than condition
        with patch.object(jobs, '_get_current_value') as mock_get_value:
            mock_get_value.return_value = 1500  # Above threshold
            assert jobs._check_alert_conditions(mock_db, sample_alert_config)
            
            mock_get_value.return_value = 500  # Below threshold
            assert not jobs._check_alert_conditions(mock_db, sample_alert_config)
            
        # Test less than condition
        sample_alert_config.threshold_settings['operator'] = 'lt'
        with patch.object(jobs, '_get_current_value') as mock_get_value:
            mock_get_value.return_value = 500  # Below threshold
            assert jobs._check_alert_conditions(mock_db, sample_alert_config)
            
            mock_get_value.return_value = 1500  # Above threshold
            assert not jobs._check_alert_conditions(mock_db, sample_alert_config)
            
    def test_get_current_value(self, jobs, mock_db, sample_alert_config):
        """Test getting current metric values."""
        # Test load metric
        with patch.object(jobs, '_get_load_metric') as mock_load:
            mock_load.return_value = 1500
            assert jobs._get_current_value(mock_db, sample_alert_config) == 1500
            
        # Test latency metric
        sample_alert_config.alert_type = AlertType.LATENCY
        with patch.object(jobs, '_get_latency_metric') as mock_latency:
            mock_latency.return_value = 45.7
            assert jobs._get_current_value(mock_db, sample_alert_config) == 45.7
            
        # Test error rate metric
        sample_alert_config.alert_type = AlertType.ERROR_RATE
        with patch.object(jobs, '_get_error_rate_metric') as mock_error:
            mock_error.return_value = 0.05
            assert jobs._get_current_value(mock_db, sample_alert_config) == 0.05
            
        # Test resource usage metric
        sample_alert_config.alert_type = AlertType.RESOURCE_USAGE
        with patch.object(jobs, '_get_resource_metric') as mock_resource:
            mock_resource.return_value = 75.5
            assert jobs._get_current_value(mock_db, sample_alert_config) == 75.5
            
    async def test_send_alert_notifications(self, jobs):
        """Test sending alert notifications."""
        alert = AlertConfig(
            id=1,
            alert_type=AlertType.LOAD,
            severity=AlertSeverity.WARNING,
            notification_settings=[
                {'type': 'email', 'to': 'admin@example.com'},
                {'type': 'slack', 'channel': '#alerts'},
                {'type': 'webhook', 'url': 'http://example.com/webhook'}
            ]
        )
        history = AlertHistory(
            id=1,
            alert_config_id=1,
            trigger_value=1500
        )
        
        # Mock notification methods
        with patch.object(jobs, '_send_email_alert', new_callable=AsyncMock) as mock_email, \
             patch.object(jobs, '_send_slack_alert', new_callable=AsyncMock) as mock_slack, \
             patch.object(jobs, '_send_webhook_alert', new_callable=AsyncMock) as mock_webhook:
            
            mock_email.return_value = True
            mock_slack.return_value = True
            mock_webhook.return_value = True
            
            await jobs._send_alert_notifications(alert, history)
            
            # Verify all channels were called
            mock_email.assert_called_once()
            mock_slack.assert_called_once()
            mock_webhook.assert_called_once()
            
            # Verify notification status
            assert history.notification_status == {
                'email': 'sent',
                'slack': 'sent',
                'webhook': 'sent'
            }
            
    async def test_cleanup_cache(self, jobs, mock_cache):
        """Test cache cleanup job."""
        # Setup test data
        current_time = datetime.utcnow()
        old_metrics = {
            'metrics_type': 'requests',
            'value': 100.0,
            'timestamp': (current_time - timedelta(hours=2)).isoformat()
        }
        new_metrics = {
            'metrics_type': 'requests',
            'value': 200.0,
            'timestamp': current_time.isoformat()
        }
        mock_cache.get_recent_metrics.return_value = [old_metrics, new_metrics]
        
        # Start cleanup
        jobs.running = True
        task = asyncio.create_task(jobs._cleanup_cache())
        
        # Let it run one iteration
        await asyncio.sleep(0.1)
        jobs.running = False
        await task
        
        # Verify cleanup
        mock_cache.get_recent_metrics.assert_called()
        mock_cache.cache.set.assert_called()  # Should set updated metrics
        assert len(mock_cache.cache.set.call_args[0][1]) == 1  # Only new metrics remain 