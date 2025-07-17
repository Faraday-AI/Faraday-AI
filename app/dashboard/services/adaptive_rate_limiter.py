"""
Adaptive Rate Limiter Service

This module provides an adaptive rate limiting service that automatically adjusts
rate limits based on system load and performance metrics.
"""

from typing import Dict, Any, Optional, List, Tuple
import asyncio
import time
import psutil
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class AdaptiveTokenBucket:
    def __init__(
        self,
        initial_rate: float,
        initial_capacity: int,
        min_rate: float,
        max_rate: float
    ):
        self.rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.capacity = initial_capacity
        self.tokens = initial_capacity
        self.last_update = time.time()
        self.lock = asyncio.Lock()
        self.latency_samples = []
        self.error_samples = []
        self.adjustment_factor = 1.0
        self.last_adjustment = time.time()
        self.adjustment_window = 60  # seconds

    async def consume(self, tokens: int = 1, latency: Optional[float] = None) -> bool:
        """Try to consume tokens and record metrics."""
        async with self.lock:
            now = time.time()
            # Add new tokens based on time passed
            time_passed = now - self.last_update
            self.tokens = min(
                self.capacity,
                self.tokens + time_passed * self.rate * self.adjustment_factor
            )
            self.last_update = now

            if latency is not None:
                self.latency_samples.append(latency)
                if len(self.latency_samples) > 1000:
                    self.latency_samples = self.latency_samples[-1000:]

            if self.tokens >= tokens:
                self.tokens -= tokens
                self.error_samples.append(0)  # Success
                return True
            
            self.error_samples.append(1)  # Error
            return False

    async def adjust_rate(self, system_load: float):
        """Adjust rate based on metrics and system load."""
        now = time.time()
        if now - self.last_adjustment < self.adjustment_window:
            return

        try:
            # Calculate metrics
            error_rate = np.mean(self.error_samples[-100:]) if self.error_samples else 0
            avg_latency = np.mean(self.latency_samples) if self.latency_samples else 0
            p95_latency = np.percentile(self.latency_samples, 95) if self.latency_samples else 0

            # Calculate adjustment factor
            latency_factor = 1.0
            if p95_latency > 100:  # If P95 latency > 100ms
                latency_factor = 0.8
            elif avg_latency < 10:  # If avg latency < 10ms
                latency_factor = 1.2

            error_factor = 1.0 - (error_rate * 0.5)  # Reduce by up to 50% based on errors
            load_factor = 1.0 - (max(0, system_load - 0.7) * 2)  # Reduce when load > 70%

            # Combined adjustment
            new_factor = min(
                2.0,  # Max 2x increase
                max(
                    0.1,  # Min 0.1x decrease
                    self.adjustment_factor * latency_factor * error_factor * load_factor
                )
            )

            # Smooth adjustment
            self.adjustment_factor = (self.adjustment_factor * 0.7) + (new_factor * 0.3)
            self.last_adjustment = now

            # Adjust actual rate within bounds
            self.rate = min(
                self.max_rate,
                max(
                    self.min_rate,
                    self.rate * self.adjustment_factor
                )
            )

            # Clear old samples
            if len(self.error_samples) > 1000:
                self.error_samples = self.error_samples[-1000:]

        except Exception as e:
            logger.error(f"Error adjusting rate: {str(e)}")

class AdaptiveRateLimiter:
    def __init__(self):
        self.settings = get_settings()
        self.buckets: Dict[str, AdaptiveTokenBucket] = {}
        self.default_rates = {
            'user': {
                'initial': 10,
                'min': 1,
                'max': 100,
                'capacity': 50
            },
            'ip': {
                'initial': 100,
                'min': 10,
                'max': 1000,
                'capacity': 500
            },
            'global': {
                'initial': 1000,
                'min': 100,
                'max': 10000,
                'capacity': 5000
            }
        }
        self.stats = defaultdict(lambda: {
            'allowed': 0,
            'blocked': 0,
            'last_blocked': None,
            'latencies': []
        })
        self.monitoring = False
        asyncio.create_task(self._monitor_system_load())

    def get_bucket(self, key: str, bucket_type: str = 'user') -> AdaptiveTokenBucket:
        """Get or create an adaptive token bucket for the key."""
        if key not in self.buckets:
            rate_config = self.default_rates.get(bucket_type, self.default_rates['user'])
            self.buckets[key] = AdaptiveTokenBucket(
                initial_rate=rate_config['initial'],
                initial_capacity=rate_config['capacity'],
                min_rate=rate_config['min'],
                max_rate=rate_config['max']
            )
        return self.buckets[key]

    async def check_rate_limit(
        self,
        key: str,
        bucket_type: str = 'user',
        tokens: int = 1,
        latency: Optional[float] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if an operation is allowed under adaptive rate limits."""
        bucket = self.get_bucket(key, bucket_type)
        start_time = time.time()
        allowed = await bucket.consume(tokens, latency)
        
        # Update stats
        self.stats[key]['allowed' if allowed else 'blocked'] += 1
        if not allowed:
            self.stats[key]['last_blocked'] = datetime.utcnow()
        
        # Record latency
        request_latency = (time.time() - start_time) * 1000  # ms
        self.stats[key]['latencies'].append(request_latency)
        if len(self.stats[key]['latencies']) > 1000:
            self.stats[key]['latencies'] = self.stats[key]['latencies'][-1000:]

        return allowed, {
            'allowed': allowed,
            'bucket_type': bucket_type,
            'tokens_requested': tokens,
            'tokens_remaining': bucket.tokens,
            'current_rate': bucket.rate * bucket.adjustment_factor,
            'adjustment_factor': bucket.adjustment_factor,
            'latency_ms': request_latency
        }

    async def _monitor_system_load(self):
        """Monitor system load and adjust rate limits."""
        self.monitoring = True
        while self.monitoring:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent() / 100
                memory = psutil.virtual_memory()
                memory_percent = memory.percent / 100
                
                # Combined load score (70% CPU, 30% memory)
                system_load = (cpu_percent * 0.7) + (memory_percent * 0.3)

                # Adjust all buckets
                for bucket in self.buckets.values():
                    await bucket.adjust_rate(system_load)

                # Log system status
                if system_load > 0.8:  # 80% load
                    logger.warning(
                        f"High system load: {system_load:.2%} "
                        f"(CPU: {cpu_percent:.2%}, Memory: {memory_percent:.2%})"
                    )

                await asyncio.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Error monitoring system load: {str(e)}")
                await asyncio.sleep(30)

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        stats = {}
        for key, bucket in self.buckets.items():
            key_stats = self.stats[key]
            total_requests = key_stats['allowed'] + key_stats['blocked']
            
            if total_requests > 0:
                stats[key] = {
                    'success_rate': key_stats['allowed'] / total_requests,
                    'current_rate': bucket.rate * bucket.adjustment_factor,
                    'adjustment_factor': bucket.adjustment_factor,
                    'avg_latency': np.mean(key_stats['latencies']) if key_stats['latencies'] else 0,
                    'p95_latency': np.percentile(key_stats['latencies'], 95) if key_stats['latencies'] else 0,
                    'p99_latency': np.percentile(key_stats['latencies'], 99) if key_stats['latencies'] else 0,
                    'total_requests': total_requests,
                    'blocked_requests': key_stats['blocked']
                }
        
        return stats 