"""
Notification Cache Warmer Service

This module provides intelligent cache warming for notifications based on access patterns
and predictive analytics.
"""

from typing import Dict, Any, List, Set, Optional
import asyncio
import time
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class NotificationCacheWarmer:
    def __init__(self, cache_service, shard_manager):
        self.settings = get_settings()
        self.cache_service = cache_service
        self.shard_manager = shard_manager
        self.access_patterns = defaultdict(lambda: {
            'hourly_counts': [0] * 24,
            'daily_counts': [0] * 7,
            'user_patterns': defaultdict(list),
            'type_patterns': defaultdict(list)
        })
        self.metrics = MetricsCollector()
        self.warming = False
        self.prediction_model = None
        self.warm_cache_threshold = 0.7  # Probability threshold for warming

    async def start(self):
        """Start cache warming and metrics collection."""
        self.warming = True
        asyncio.create_task(self._warm_cache_loop())
        asyncio.create_task(self._collect_metrics_loop())
        asyncio.create_task(self._update_patterns_loop())

    async def stop(self):
        """Stop cache warming processes."""
        self.warming = False

    async def record_access(self, notification_data: Dict[str, Any]):
        """Record notification access for pattern analysis."""
        now = datetime.utcnow()
        key = self._get_pattern_key(notification_data)
        patterns = self.access_patterns[key]

        # Update hourly counts
        patterns['hourly_counts'][now.hour] += 1

        # Update daily counts
        patterns['daily_counts'][now.weekday()] += 1

        # Update user patterns
        if user_id := notification_data.get('user_id'):
            patterns['user_patterns'][user_id].append(now.timestamp())
            # Keep last 100 accesses
            patterns['user_patterns'][user_id] = patterns['user_patterns'][user_id][-100:]

        # Update type patterns
        if notification_type := notification_data.get('type'):
            patterns['type_patterns'][notification_type].append(now.timestamp())
            # Keep last 100 accesses
            patterns['type_patterns'][notification_type] = patterns['type_patterns'][notification_type][-100:]

        # Record metrics
        self.metrics.record_access(notification_data)

    def _get_pattern_key(self, notification_data: Dict[str, Any]) -> str:
        """Generate pattern key from notification data."""
        components = [
            notification_data.get('type', 'unknown'),
            notification_data.get('priority', 'normal'),
            notification_data.get('user_id', 'anonymous')
        ]
        return ':'.join(components)

    async def _warm_cache_loop(self):
        """Main cache warming loop."""
        while self.warming:
            try:
                # Get predictions for next hour
                predictions = self._predict_next_hour_accesses()
                
                # Warm cache for predicted accesses
                for notification_id, probability in predictions.items():
                    if probability >= self.warm_cache_threshold:
                        await self._warm_notification(notification_id)
                
                # Sleep until next warming cycle
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"Error in cache warming loop: {str(e)}")
                await asyncio.sleep(60)

    def _predict_next_hour_accesses(self) -> Dict[str, float]:
        """Predict notification accesses for the next hour."""
        predictions = {}
        now = datetime.utcnow()
        next_hour = (now + timedelta(hours=1)).hour
        
        for key, patterns in self.access_patterns.items():
            # Calculate base probability from hourly pattern
            base_prob = patterns['hourly_counts'][next_hour] / max(sum(patterns['hourly_counts']), 1)
            
            # Adjust for day of week
            day_factor = patterns['daily_counts'][now.weekday()] / max(sum(patterns['daily_counts']), 1)
            
            # Adjust for recent access patterns
            recency_factor = self._calculate_recency_factor(patterns)
            
            # Combined probability
            probability = (base_prob * 0.4) + (day_factor * 0.3) + (recency_factor * 0.3)
            
            predictions[key] = probability
        
        return predictions

    def _calculate_recency_factor(self, patterns: Dict[str, Any]) -> float:
        """Calculate recency factor based on recent access patterns."""
        now = time.time()
        recent_accesses = []
        
        # Collect recent accesses across all patterns
        for access_list in patterns['user_patterns'].values():
            recent_accesses.extend(access_list)
        for access_list in patterns['type_patterns'].values():
            recent_accesses.extend(access_list)
        
        if not recent_accesses:
            return 0.0
        
        # Calculate recency score
        recent_accesses.sort(reverse=True)
        latest_access = recent_accesses[0]
        time_since_last = now - latest_access
        
        # Exponential decay factor
        return np.exp(-time_since_last / 3600)  # 1-hour decay

    async def _warm_notification(self, notification_id: str):
        """Warm cache for a specific notification."""
        try:
            # Check if already in cache
            if await self.cache_service.get_notification(notification_id):
                return

            # Fetch from database
            notification_data = await self._fetch_notification(notification_id)
            if notification_data:
                # Store in cache with shorter TTL for warm data
                await self.cache_service.cache_notification(
                    notification_id,
                    notification_data,
                    ttl=1800  # 30 minutes
                )
                
                self.metrics.record_cache_warm(notification_id)
        except Exception as e:
            logger.error(f"Error warming cache for {notification_id}: {str(e)}")

    async def _fetch_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Fetch notification data from database."""
        # Implement actual database fetch logic
        return None

    async def _collect_metrics_loop(self):
        """Collect and aggregate metrics."""
        while self.warming:
            try:
                metrics = self.metrics.get_current_metrics()
                
                # Log metrics
                logger.info("Cache Warming Metrics: %s", metrics)
                
                # Store metrics for trending
                await self._store_metrics(metrics)
                
                await asyncio.sleep(60)  # Collect every minute
            except Exception as e:
                logger.error(f"Error collecting metrics: {str(e)}")
                await asyncio.sleep(300)

    async def _store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics for historical analysis."""
        try:
            # Store in time-series format
            timestamp = datetime.utcnow().isoformat()
            metrics_key = f"metrics:cache_warming:{timestamp}"
            
            await self.shard_manager.set(
                metrics_key,
                metrics,
                ttl=86400 * 7  # Keep for 7 days
            )
        except Exception as e:
            logger.error(f"Error storing metrics: {str(e)}")

    async def _update_patterns_loop(self):
        """Update access patterns and clean up old data."""
        while self.warming:
            try:
                now = time.time()
                
                # Clean up old patterns
                for key, patterns in self.access_patterns.items():
                    # Clean up user patterns
                    for user_id, accesses in patterns['user_patterns'].items():
                        patterns['user_patterns'][user_id] = [
                            ts for ts in accesses
                            if now - ts < 86400 * 7  # Keep 7 days
                        ]
                    
                    # Clean up type patterns
                    for type_id, accesses in patterns['type_patterns'].items():
                        patterns['type_patterns'][type_id] = [
                            ts for ts in accesses
                            if now - ts < 86400 * 7  # Keep 7 days
                        ]
                
                await asyncio.sleep(3600)  # Update every hour
            except Exception as e:
                logger.error(f"Error updating patterns: {str(e)}")
                await asyncio.sleep(300)

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'warm_hits': 0,  # Hits on warmed data
            'warm_misses': 0,  # Misses despite warming
            'warming_operations': 0,
            'warming_errors': 0,
            'pattern_updates': 0,
            'latency_samples': []
        }
        self.warmed_keys = set()

    def record_access(self, notification_data: Dict[str, Any]):
        """Record cache access metrics."""
        notification_id = notification_data.get('id')
        is_hit = notification_data.get('cached', False)
        latency = notification_data.get('latency', 0)

        if is_hit:
            self.metrics['cache_hits'] += 1
            if notification_id in self.warmed_keys:
                self.metrics['warm_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
            if notification_id in self.warmed_keys:
                self.metrics['warm_misses'] += 1

        self.metrics['latency_samples'].append(latency)
        if len(self.metrics['latency_samples']) > 1000:
            self.metrics['latency_samples'] = self.metrics['latency_samples'][-1000:]

    def record_cache_warm(self, notification_id: str):
        """Record cache warming operation."""
        self.metrics['warming_operations'] += 1
        self.warmed_keys.add(notification_id)

    def record_warming_error(self, notification_id: str):
        """Record cache warming error."""
        self.metrics['warming_errors'] += 1
        self.warmed_keys.discard(notification_id)

    def record_pattern_update(self):
        """Record pattern update operation."""
        self.metrics['pattern_updates'] += 1

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics with calculated statistics."""
        total_accesses = self.metrics['cache_hits'] + self.metrics['cache_misses']
        total_warm_accesses = self.metrics['warm_hits'] + self.metrics['warm_misses']
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'hit_rate': self.metrics['cache_hits'] / max(total_accesses, 1),
            'warm_hit_rate': self.metrics['warm_hits'] / max(total_warm_accesses, 1),
            'warming_error_rate': self.metrics['warming_errors'] / max(self.metrics['warming_operations'], 1),
            'avg_latency': np.mean(self.metrics['latency_samples']) if self.metrics['latency_samples'] else 0,
            'p95_latency': np.percentile(self.metrics['latency_samples'], 95) if self.metrics['latency_samples'] else 0,
            'p99_latency': np.percentile(self.metrics['latency_samples'], 99) if self.metrics['latency_samples'] else 0,
            'warmed_keys_count': len(self.warmed_keys),
            'raw_metrics': dict(self.metrics)
        } 