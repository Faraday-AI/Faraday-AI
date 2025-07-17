"""
Notification Monitor Service

This module provides system monitoring functionality for notification processing,
including metrics collection, analysis, and resource adjustment.
"""

from typing import Dict, Any, List
import asyncio
import psutil
import time
from datetime import datetime, timedelta
from collections import deque
import statistics
from app.core.config import get_settings


class NotificationMonitorService:
    """Service for monitoring notification system health and performance."""
    
    def __init__(self):
        self.settings = get_settings()
        self.metrics_window = 300  # 5 minutes
        self.metrics = {
            'processing_times': deque(maxlen=1000),
            'queue_lengths': deque(maxlen=300),
            'error_rates': deque(maxlen=300),
            'cpu_usage': deque(maxlen=300),
            'memory_usage': deque(maxlen=300)
        }
        self.monitoring = False
        self.alert_thresholds = {
            'processing_time_ms': 1000,  # 1 second
            'queue_length': 10000,
            'error_rate': 0.05,  # 5%
            'cpu_usage': 80,  # 80%
            'memory_usage': 80  # 80%
        }

    async def start_monitoring(self):
        """Start monitoring system metrics."""
        self.monitoring = True
        while self.monitoring:
            try:
                await self._collect_metrics()
                await self._analyze_metrics()
                await asyncio.sleep(1)  # Collect metrics every second
            except Exception as e:
                print(f"Error in monitoring: {str(e)}")
                await asyncio.sleep(5)

    async def stop_monitoring(self):
        """Stop monitoring system metrics."""
        self.monitoring = False

    async def _collect_metrics(self):
        """Collect current system metrics."""
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        
        self.metrics['cpu_usage'].append(cpu_percent)
        self.metrics['memory_usage'].append(memory.percent)
        
        # Get queue metrics from NotificationQueueService
        queue_stats = await self.queue_service.get_queue_stats()
        self.metrics['queue_lengths'].append(queue_stats['total_notifications'])

    async def _analyze_metrics(self):
        """Analyze collected metrics and trigger actions if needed."""
        analysis = self._calculate_metrics()
        
        # Check for alert conditions
        alerts = []
        if analysis['avg_processing_time'] > self.alert_thresholds['processing_time_ms']:
            alerts.append({
                'type': 'performance',
                'metric': 'processing_time',
                'value': analysis['avg_processing_time'],
                'threshold': self.alert_thresholds['processing_time_ms']
            })
        
        if analysis['avg_queue_length'] > self.alert_thresholds['queue_length']:
            alerts.append({
                'type': 'capacity',
                'metric': 'queue_length',
                'value': analysis['avg_queue_length'],
                'threshold': self.alert_thresholds['queue_length']
            })
        
        if analysis['error_rate'] > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'reliability',
                'metric': 'error_rate',
                'value': analysis['error_rate'],
                'threshold': self.alert_thresholds['error_rate']
            })
        
        # Trigger auto-scaling if needed
        if alerts:
            await self._handle_alerts(alerts)
            await self._adjust_resources(analysis)

    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate current system metrics."""
        return {
            'avg_processing_time': statistics.mean(self.metrics['processing_times'])
                if self.metrics['processing_times'] else 0,
            'avg_queue_length': statistics.mean(self.metrics['queue_lengths'])
                if self.metrics['queue_lengths'] else 0,
            'error_rate': len([x for x in self.metrics['error_rates'] if x]) /
                len(self.metrics['error_rates']) if self.metrics['error_rates'] else 0,
            'cpu_usage': statistics.mean(self.metrics['cpu_usage'])
                if self.metrics['cpu_usage'] else 0,
            'memory_usage': statistics.mean(self.metrics['memory_usage'])
                if self.metrics['memory_usage'] else 0,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def _handle_alerts(self, alerts: List[Dict[str, Any]]):
        """Handle system alerts."""
        for alert in alerts:
            # Log alert
            print(f"System alert: {alert['type']} - {alert['metric']} = {alert['value']}")
            
            # Send notification to system administrators
            await self.notification_service.send_notification(
                user_id='admin',
                notification_type='system',
                title=f"System Alert: {alert['type']}",
                message=f"{alert['metric']} exceeded threshold: {alert['value']} > {alert['threshold']}",
                priority='high'
            )

    async def _adjust_resources(self, metrics: Dict[str, Any]):
        """Adjust system resources based on metrics."""
        # Adjust batch processing size
        if metrics['avg_processing_time'] > self.alert_thresholds['processing_time_ms']:
            self.queue_service.batch_size = max(10, self.queue_service.batch_size // 2)
        elif metrics['avg_processing_time'] < self.alert_thresholds['processing_time_ms'] / 2:
            self.queue_service.batch_size = min(1000, self.queue_service.batch_size * 2)
        
        # Adjust processing interval
        if metrics['avg_queue_length'] > self.alert_thresholds['queue_length']:
            self.queue_service.processing_interval = max(0.1, self.queue_service.processing_interval / 2)
        elif metrics['avg_queue_length'] < self.alert_thresholds['queue_length'] / 2:
            self.queue_service.processing_interval = min(5, self.queue_service.processing_interval * 2)

    async def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics."""
        metrics = self._calculate_metrics()
        
        return {
            'status': 'healthy' if not any([
                metrics['avg_processing_time'] > self.alert_thresholds['processing_time_ms'],
                metrics['avg_queue_length'] > self.alert_thresholds['queue_length'],
                metrics['error_rate'] > self.alert_thresholds['error_rate'],
                metrics['cpu_usage'] > self.alert_thresholds['cpu_usage'],
                metrics['memory_usage'] > self.alert_thresholds['memory_usage']
            ]) else 'degraded',
            'metrics': metrics,
            'thresholds': self.alert_thresholds,
            'queue_info': {
                'batch_size': self.queue_service.batch_size,
                'processing_interval': self.queue_service.processing_interval
            }
        } 