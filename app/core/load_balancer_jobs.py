"""
Load Balancer Background Jobs

This module provides background jobs for:
- Metrics collection and aggregation
- Alert processing and notification
- Health check monitoring
- Cache maintenance
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
from prometheus_client import Counter, Gauge, Histogram
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.core.load_balancer_cache import load_balancer_cache
from app.core.database import get_db
from app.models.load_balancer import (
    LoadBalancerConfig,
    RegionConfig,
    MetricsHistory,
    AlertConfig,
    AlertHistory,
    AlertType,
    AlertSeverity
)
from app.core.regional_failover import Region

# Prometheus metrics
METRICS_PROCESSED = Counter('load_balancer_metrics_processed_total', 'Number of metrics processed')
ALERTS_TRIGGERED = Counter('load_balancer_alerts_triggered_total', 'Number of alerts triggered', ['severity'])
JOB_DURATION = Histogram('load_balancer_job_duration_seconds', 'Background job duration', ['job_type'])
METRICS_AGE = Gauge('load_balancer_metrics_age_seconds', 'Age of latest metrics')

logger = logging.getLogger(__name__)

class LoadBalancerJobs:
    """Manager for load balancer background jobs."""
    
    def __init__(self):
        self.metrics_interval = 60  # 1 minute
        self.alert_interval = 30    # 30 seconds
        self.health_interval = 15   # 15 seconds
        self.cache_cleanup_interval = 300  # 5 minutes
        self.running = False
        self.tasks = []
        
    async def start(self):
        """Start all background jobs."""
        if self.running:
            return
            
        self.running = True
        self.tasks = [
            asyncio.create_task(self._collect_metrics()),
            asyncio.create_task(self._process_alerts()),
            asyncio.create_task(self._monitor_health()),
            asyncio.create_task(self._cleanup_cache())
        ]
        logger.info("Load balancer background jobs started")
        
    async def stop(self):
        """Stop all background jobs."""
        self.running = False
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks = []
        logger.info("Load balancer background jobs stopped")
        
    async def _collect_metrics(self):
        """Collect and aggregate metrics."""
        while self.running:
            try:
                start_time = datetime.utcnow()
                with JOB_DURATION.labels(job_type="metrics_collection").time():
                    db = next(get_db())
                    try:
                        # Get active regions
                        regions = (
                            db.query(RegionConfig)
                            .filter(RegionConfig.is_active == True)
                            .all()
                        )
                        
                        for region_config in regions:
                            # Get metrics from cache
                            cached_metrics = load_balancer_cache.get_recent_metrics(region_config.region)
                            if not cached_metrics:
                                continue
                                
                            # Aggregate metrics
                            aggregated = self._aggregate_metrics(cached_metrics)
                            
                            # Store in database
                            for metric_type, value in aggregated.items():
                                metric = MetricsHistory(
                                    region_config_id=region_config.id,
                                    metrics_type=metric_type,
                                    value=value,
                                    metadata={
                                        "aggregation": "avg",
                                        "sample_count": len(cached_metrics)
                                    }
                                )
                                db.add(metric)
                                
                            db.commit()
                            METRICS_PROCESSED.inc()
                            
                    finally:
                        db.close()
                        
                # Update metrics age
                METRICS_AGE.set((datetime.utcnow() - start_time).total_seconds())
                
                await asyncio.sleep(self.metrics_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(self.metrics_interval)
                
    def _aggregate_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """Aggregate metrics by type."""
        aggregated = {}
        for metric in metrics:
            metric_type = metric['metrics_type']
            value = metric['value']
            
            if metric_type not in aggregated:
                aggregated[metric_type] = []
            aggregated[metric_type].append(value)
            
        # Calculate averages
        return {
            metric_type: sum(values) / len(values)
            for metric_type, values in aggregated.items()
        }
        
    async def _process_alerts(self):
        """Process alerts and send notifications."""
        while self.running:
            try:
                with JOB_DURATION.labels(job_type="alert_processing").time():
                    db = next(get_db())
                    try:
                        # Get active alert configs
                        alerts = (
                            db.query(AlertConfig)
                            .filter(AlertConfig.is_active == True)
                            .all()
                        )
                        
                        for alert in alerts:
                            # Check if alert is in cooldown
                            last_alert = (
                                db.query(AlertHistory)
                                .filter(AlertHistory.alert_config_id == alert.id)
                                .order_by(AlertHistory.triggered_at.desc())
                                .first()
                            )
                            
                            if last_alert and not last_alert.resolved_at:
                                cooldown_end = last_alert.triggered_at + timedelta(seconds=alert.cooldown_seconds)
                                if datetime.utcnow() < cooldown_end:
                                    continue
                                    
                            # Check alert conditions
                            if self._check_alert_conditions(db, alert):
                                # Create alert history entry
                                history = AlertHistory(
                                    alert_config_id=alert.id,
                                    trigger_value=self._get_current_value(db, alert),
                                    metadata={
                                        "threshold": alert.threshold_settings,
                                        "notification_channels": alert.notification_settings
                                    }
                                )
                                db.add(history)
                                db.commit()
                                
                                # Send notifications
                                await self._send_alert_notifications(alert, history)
                                
                                ALERTS_TRIGGERED.labels(severity=alert.severity.value).inc()
                                
                    finally:
                        db.close()
                        
                await asyncio.sleep(self.alert_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert processing: {e}")
                await asyncio.sleep(self.alert_interval)
                
    def _check_alert_conditions(self, db: Session, alert: AlertConfig) -> bool:
        """Check if alert conditions are met."""
        current_value = self._get_current_value(db, alert)
        if current_value is None:
            return False
            
        threshold = alert.threshold_settings.get('value', 0)
        operator = alert.threshold_settings.get('operator', 'gt')
        
        if operator == 'gt':
            return current_value > threshold
        elif operator == 'lt':
            return current_value < threshold
        elif operator == 'gte':
            return current_value >= threshold
        elif operator == 'lte':
            return current_value <= threshold
        elif operator == 'eq':
            return abs(current_value - threshold) < 0.0001
            
        return False
        
    def _get_current_value(self, db: Session, alert: AlertConfig) -> float:
        """Get current value for alert metric."""
        if alert.alert_type == AlertType.LOAD:
            # Get average request count
            return self._get_load_metric(db)
        elif alert.alert_type == AlertType.LATENCY:
            # Get average latency
            return self._get_latency_metric(db)
        elif alert.alert_type == AlertType.ERROR_RATE:
            # Get error rate
            return self._get_error_rate_metric(db)
        elif alert.alert_type == AlertType.RESOURCE_USAGE:
            # Get resource usage
            return self._get_resource_metric(db)
            
        return None
        
    def _get_load_metric(self, db: Session) -> float:
        """Get current load metric."""
        result = (
            db.query(func.avg(MetricsHistory.value))
            .filter(
                and_(
                    MetricsHistory.metrics_type == 'requests',
                    MetricsHistory.timestamp >= datetime.utcnow() - timedelta(minutes=5)
                )
            )
            .scalar()
        )
        return float(result) if result else 0.0
        
    def _get_latency_metric(self, db: Session) -> float:
        """Get current latency metric."""
        result = (
            db.query(func.avg(MetricsHistory.value))
            .filter(
                and_(
                    MetricsHistory.metrics_type == 'latency',
                    MetricsHistory.timestamp >= datetime.utcnow() - timedelta(minutes=5)
                )
            )
            .scalar()
        )
        return float(result) if result else 0.0
        
    def _get_error_rate_metric(self, db: Session) -> float:
        """Get current error rate metric."""
        result = (
            db.query(func.avg(MetricsHistory.value))
            .filter(
                and_(
                    MetricsHistory.metrics_type == 'errors',
                    MetricsHistory.timestamp >= datetime.utcnow() - timedelta(minutes=5)
                )
            )
            .scalar()
        )
        return float(result) if result else 0.0
        
    def _get_resource_metric(self, db: Session) -> float:
        """Get current resource usage metric."""
        result = (
            db.query(func.avg(MetricsHistory.value))
            .filter(
                and_(
                    MetricsHistory.metrics_type == 'resource_usage',
                    MetricsHistory.timestamp >= datetime.utcnow() - timedelta(minutes=5)
                )
            )
            .scalar()
        )
        return float(result) if result else 0.0
        
    async def _send_alert_notifications(self, alert: AlertConfig, history: AlertHistory):
        """Send alert notifications through configured channels."""
        notification_status = {}
        
        for channel in alert.notification_settings:
            try:
                if channel['type'] == 'email':
                    success = await self._send_email_alert(alert, history, channel)
                elif channel['type'] == 'slack':
                    success = await self._send_slack_alert(alert, history, channel)
                elif channel['type'] == 'webhook':
                    success = await self._send_webhook_alert(alert, history, channel)
                else:
                    success = False
                    
                notification_status[channel['type']] = 'sent' if success else 'failed'
                
            except Exception as e:
                logger.error(f"Error sending {channel['type']} alert: {e}")
                notification_status[channel['type']] = 'failed'
                
        # Update alert history with notification status
        history.notification_status = notification_status
        
    async def _send_email_alert(self, alert: AlertConfig, history: AlertHistory, config: Dict[str, Any]) -> bool:
        """Send alert via email."""
        # Implementation depends on your email service
        logger.info(f"Would send email alert: {alert.alert_type} - {history.trigger_value}")
        return True
        
    async def _send_slack_alert(self, alert: AlertConfig, history: AlertHistory, config: Dict[str, Any]) -> bool:
        """Send alert via Slack."""
        # Implementation depends on your Slack integration
        logger.info(f"Would send Slack alert: {alert.alert_type} - {history.trigger_value}")
        return True
        
    async def _send_webhook_alert(self, alert: AlertConfig, history: AlertHistory, config: Dict[str, Any]) -> bool:
        """Send alert via webhook."""
        # Implementation depends on your webhook configuration
        logger.info(f"Would send webhook alert: {alert.alert_type} - {history.trigger_value}")
        return True
        
    async def _monitor_health(self):
        """Monitor health status of regions."""
        while self.running:
            try:
                with JOB_DURATION.labels(job_type="health_monitoring").time():
                    db = next(get_db())
                    try:
                        # Get active regions
                        regions = (
                            db.query(RegionConfig)
                            .filter(RegionConfig.is_active == True)
                            .all()
                        )
                        
                        for region_config in regions:
                            # Perform health check
                            health_status = await self._check_region_health(region_config)
                            
                            # Update cache
                            load_balancer_cache.set_health_status(
                                region_config.region,
                                health_status
                            )
                            
                    finally:
                        db.close()
                        
                await asyncio.sleep(self.health_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(self.health_interval)
                
    async def _check_region_health(self, region_config: RegionConfig) -> Dict[str, Any]:
        """Check health of a region."""
        # Implementation depends on your health check logic
        return {
            "status": "healthy",
            "last_check": datetime.utcnow().isoformat(),
            "metrics": {
                "latency": 45.7,
                "error_rate": 0.01,
                "resource_usage": 0.65
            }
        }
        
    async def _cleanup_cache(self):
        """Clean up old cache entries."""
        while self.running:
            try:
                with JOB_DURATION.labels(job_type="cache_cleanup").time():
                    # Clean up metrics cache
                    for region in Region:
                        metrics = load_balancer_cache.get_recent_metrics(region)
                        if metrics:
                            # Keep only last hour
                            cutoff = datetime.utcnow() - timedelta(hours=1)
                            metrics = [
                                m for m in metrics
                                if datetime.fromisoformat(m['timestamp']) > cutoff
                            ]
                            if metrics:
                                load_balancer_cache.cache.set(
                                    load_balancer_cache._get_metrics_key(region),
                                    metrics,
                                    load_balancer_cache.metrics_ttl
                                )
                            else:
                                load_balancer_cache.invalidate_metrics(region)
                                
                await asyncio.sleep(self.cache_cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
                await asyncio.sleep(self.cache_cleanup_interval)

# Initialize global jobs manager
load_balancer_jobs = LoadBalancerJobs() 