"""
Notification Shard Manager Service

This module provides Redis sharding functionality for notification data with
circuit breaker pattern and automatic rebalancing.
"""

from typing import Dict, Any, List, Optional, Set
import asyncio
from redis.asyncio import Redis
import hashlib
import json
from datetime import datetime, timedelta
from collections import defaultdict
import time
from app.core.config import get_settings


class CircuitBreaker:
    """Circuit breaker pattern implementation for Redis shards."""
    
    def __init__(self):
        self.error_count = 0
        self.last_error_time = None
        self.state = "closed"  # closed, open, half-open
        self.threshold = 5  # errors before opening
        self.timeout = 30  # seconds to wait before half-open
        self.success_count = 0
        self.required_successes = 3  # successes before closing

    def allow_request(self) -> bool:
        """Check if request should be allowed."""
        now = time.time()
        
        if self.state == "closed":
            return True
            
        if self.state == "open":
            if now - self.last_error_time > self.timeout:
                self.state = "half-open"
                return True
            return False
            
        if self.state == "half-open":
            return True

    def record_error(self):
        """Record an error and update state."""
        self.error_count += 1
        self.last_error_time = time.time()
        self.success_count = 0
        
        if self.error_count >= self.threshold:
            self.state = "open"

    def record_success(self):
        """Record a success and update state."""
        if self.state == "half-open":
            self.success_count += 1
            if self.success_count >= self.required_successes:
                self.state = "closed"
                self.error_count = 0
                self.success_count = 0


class NotificationShardManager:
    """Manager for Redis sharding with circuit breaker pattern."""
    
    def __init__(self):
        self.settings = get_settings()
        self.shards: Dict[str, Redis] = {}
        self.shard_count = 4  # Number of Redis shards
        self.replication_factor = 2  # Number of replicas per shard
        self.circuit_breakers = {}
        self.shard_stats = defaultdict(lambda: {
            'operations': 0,
            'errors': 0,
            'latency': [],
            'last_error': None
        })
        self.rebalancing = False

    async def initialize(self):
        """Initialize Redis shards."""
        # Create Redis connections for each shard
        for i in range(self.shard_count):
            shard_id = f"shard_{i}"
            # Primary shard
            self.shards[shard_id] = await self._create_redis_connection(
                f"{self.settings.REDIS_URL}/{i}"
            )
            # Replicas
            for r in range(self.replication_factor):
                replica_id = f"{shard_id}_replica_{r}"
                self.shards[replica_id] = await self._create_redis_connection(
                    f"{self.settings.REDIS_URL}/{i}_{r}"
                )
            # Initialize circuit breaker
            self.circuit_breakers[shard_id] = CircuitBreaker()

        # Start monitoring
        asyncio.create_task(self._monitor_shards())
        asyncio.create_task(self._auto_rebalance())

    async def _create_redis_connection(self, url: str) -> Redis:
        """Create a Redis connection with retry logic."""
        retries = 3
        while retries > 0:
            try:
                return Redis.from_url(
                    url,
                    encoding='utf-8',
                    decode_responses=True,
                    max_connections=20
                )
            except Exception as e:
                retries -= 1
                if retries == 0:
                    raise
                await asyncio.sleep(1)

    def _get_shard(self, key: str) -> str:
        """Get shard ID for a key using consistent hashing."""
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return f"shard_{hash_value % self.shard_count}"

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in sharded Redis with circuit breaker."""
        shard_id = self._get_shard(key)
        
        # Check circuit breaker
        if not self.circuit_breakers[shard_id].allow_request():
            # Use replica if primary is down
            shard_id = self._get_healthy_replica(shard_id)
            if not shard_id:
                raise Exception("No healthy shards available")

        start_time = time.time()
        try:
            # Store value
            success = await self.shards[shard_id].set(
                key,
                json.dumps(value),
                ex=ttl
            )
            
            # Update stats
            self._update_shard_stats(shard_id, time.time() - start_time)
            
            # Replicate to backup shards
            await self._replicate_data(key, value, ttl, shard_id)
            
            return success
        except Exception as e:
            self._handle_shard_error(shard_id, e)
            raise

    async def get(self, key: str) -> Optional[Any]:
        """Get value from sharded Redis with failover."""
        shard_id = self._get_shard(key)
        
        # Try primary shard
        if self.circuit_breakers[shard_id].allow_request():
            try:
                start_time = time.time()
                value = await self.shards[shard_id].get(key)
                self._update_shard_stats(shard_id, time.time() - start_time)
                if value:
                    return json.loads(value)
            except Exception as e:
                self._handle_shard_error(shard_id, e)

        # Try replicas if primary fails
        for r in range(self.replication_factor):
            replica_id = f"{shard_id}_replica_{r}"
            try:
                start_time = time.time()
                value = await self.shards[replica_id].get(key)
                self._update_shard_stats(replica_id, time.time() - start_time)
                if value:
                    return json.loads(value)
            except Exception as e:
                self._handle_shard_error(replica_id, e)

        return None

    async def delete(self, key: str) -> bool:
        """Delete value from all shards."""
        shard_id = self._get_shard(key)
        success = False
        
        # Delete from primary
        if self.circuit_breakers[shard_id].allow_request():
            try:
                success = await self.shards[shard_id].delete(key)
            except Exception as e:
                self._handle_shard_error(shard_id, e)

        # Delete from replicas
        for r in range(self.replication_factor):
            replica_id = f"{shard_id}_replica_{r}"
            try:
                await self.shards[replica_id].delete(key)
            except Exception as e:
                self._handle_shard_error(replica_id, e)

        return success

    async def _replicate_data(
        self,
        key: str,
        value: Any,
        ttl: Optional[int],
        primary_shard: str
    ):
        """Replicate data to backup shards."""
        tasks = []
        for r in range(self.replication_factor):
            replica_id = f"{primary_shard}_replica_{r}"
            tasks.append(
                self.shards[replica_id].set(
                    key,
                    json.dumps(value),
                    ex=ttl
                )
            )
        await asyncio.gather(*tasks, return_exceptions=True)

    def _get_healthy_replica(self, primary_shard: str) -> Optional[str]:
        """Get healthy replica for a primary shard."""
        for r in range(self.replication_factor):
            replica_id = f"{primary_shard}_replica_{r}"
            if self.circuit_breakers[primary_shard].allow_request():
                return replica_id
        return None

    def _update_shard_stats(self, shard_id: str, latency: float):
        """Update shard statistics."""
        stats = self.shard_stats[shard_id]
        stats['operations'] += 1
        stats['latency'].append(latency)
        if len(stats['latency']) > 1000:
            stats['latency'] = stats['latency'][-1000:]

    def _handle_shard_error(self, shard_id: str, error: Exception):
        """Handle shard error and update circuit breaker."""
        stats = self.shard_stats[shard_id]
        stats['errors'] += 1
        stats['last_error'] = {
            'time': datetime.utcnow().isoformat(),
            'error': str(error)
        }
        self.circuit_breakers[shard_id].record_error()

    async def _monitor_shards(self):
        """Monitor shard health and performance."""
        while True:
            try:
                for shard_id, shard in self.shards.items():
                    # Check connectivity
                    try:
                        await shard.ping()
                        self.circuit_breakers[shard_id].record_success()
                    except Exception as e:
                        self._handle_shard_error(shard_id, e)

                    # Calculate metrics
                    stats = self.shard_stats[shard_id]
                    if stats['latency']:
                        avg_latency = sum(stats['latency']) / len(stats['latency'])
                        error_rate = stats['errors'] / stats['operations'] if stats['operations'] > 0 else 0
                        
                        # Log if performance is degraded
                        if avg_latency > 100 or error_rate > 0.05:  # 100ms latency or 5% error rate
                            print(f"Shard {shard_id} performance degraded: latency={avg_latency}ms, error_rate={error_rate}")

                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Error in shard monitoring: {str(e)}")
                await asyncio.sleep(30)  # Back off on error

    async def _auto_rebalance(self):
        """Automatically rebalance shards based on load."""
        while True:
            try:
                if not self.rebalancing:
                    # Calculate load for each shard
                    shard_loads = {}
                    for shard_id, stats in self.shard_stats.items():
                        if stats['operations'] > 0:
                            avg_latency = sum(stats['latency']) / len(stats['latency'])
                            error_rate = stats['errors'] / stats['operations']
                            load_score = (avg_latency * 0.7) + (error_rate * 0.3)
                            shard_loads[shard_id] = load_score

                    # Check if rebalancing is needed
                    if shard_loads:
                        min_load = min(shard_loads.values())
                        max_load = max(shard_loads.values())
                        if max_load > min_load * 1.5:  # 50% difference triggers rebalancing
                            await self._rebalance_shards(shard_loads)

                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Error in auto-rebalancing: {str(e)}")
                await asyncio.sleep(600)  # Back off on error

    async def _rebalance_shards(self, shard_loads: Dict[str, float]):
        """Rebalance data across shards."""
        try:
            self.rebalancing = True
            
            # Sort shards by load
            sorted_shards = sorted(
                shard_loads.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Move data from most loaded to least loaded shards
            for i, (source_shard, _) in enumerate(sorted_shards[:len(sorted_shards)//2]):
                target_shard = sorted_shards[-(i+1)][0]
                
                # Move ~20% of data
                keys = await self.shards[source_shard].keys('*')
                keys_to_move = keys[:len(keys)//5]
                
                for key in keys_to_move:
                    value = await self.get(key)
                    if value is not None:
                        ttl = await self.shards[source_shard].ttl(key)
                        await self.set(key, value, ttl)
                        await self.shards[source_shard].delete(key)
            
        finally:
            self.rebalancing = False 