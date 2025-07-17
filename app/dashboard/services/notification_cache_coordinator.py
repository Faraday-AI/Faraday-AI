"""
Notification Cache Coordinator Service

This module provides cache coordination functionality for notifications across
multiple application instances.
"""

from typing import Dict, Any, Optional, List, Set
import asyncio
from redis.asyncio import Redis
import json
from datetime import datetime, timedelta
import hashlib
from app.core.config import get_settings


class NotificationCacheCoordinator:
    """Coordinator for notification cache across multiple instances."""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis = None
        self.instance_id = self._generate_instance_id()
        self.sync_interval = 5  # seconds
        self.lock_timeout = 10  # seconds
        self.is_master = False
        self.sync_running = False

    def _generate_instance_id(self) -> str:
        """Generate unique instance ID."""
        timestamp = datetime.utcnow().isoformat()
        return hashlib.md5(f"{timestamp}:{id(self)}".encode()).hexdigest()

    async def initialize(self):
        """Initialize Redis connection and start coordination."""
        if not self.redis:
            self.redis = Redis.from_url(
                self.settings.REDIS_URL,
                encoding='utf-8',
                decode_responses=True,
                max_connections=20
            )
        
        # Register instance
        await self.redis.sadd('notification:instances', self.instance_id)
        await self.start_coordination()

    async def close(self):
        """Clean up resources."""
        if self.redis:
            # Deregister instance
            await self.redis.srem('notification:instances', self.instance_id)
            if self.is_master:
                await self.redis.delete('notification:master_instance')
            
            await self.redis.close()

    async def start_coordination(self):
        """Start cache coordination process."""
        self.sync_running = True
        asyncio.create_task(self._coordination_loop())

    async def stop_coordination(self):
        """Stop cache coordination process."""
        self.sync_running = False

    async def _coordination_loop(self):
        """Main coordination loop."""
        while self.sync_running:
            try:
                # Attempt to become master
                await self._elect_master()
                
                if self.is_master:
                    await self._master_sync()
                else:
                    await self._replica_sync()
                
                await asyncio.sleep(self.sync_interval)
            except Exception as e:
                print(f"Error in coordination loop: {str(e)}")
                await asyncio.sleep(self.sync_interval)

    async def _elect_master(self):
        """Participate in master election."""
        async with self._get_lock('notification:master_election'):
            current_master = await self.redis.get('notification:master_instance')
            
            if not current_master:
                # No master exists, become master
                await self.redis.set(
                    'notification:master_instance',
                    self.instance_id,
                    ex=self.lock_timeout
                )
                self.is_master = True
            elif current_master == self.instance_id:
                # Refresh master status
                await self.redis.expire(
                    'notification:master_instance',
                    self.lock_timeout
                )
                self.is_master = True
            else:
                self.is_master = False

    async def _master_sync(self):
        """Master instance synchronization tasks."""
        try:
            # Get all instances
            instances = await self.redis.smembers('notification:instances')
            
            # Collect cache updates from all instances
            updates = await self._collect_cache_updates()
            
            if updates:
                # Broadcast updates to all instances
                await self._broadcast_cache_updates(updates)
                
                # Clean up processed updates
                await self.redis.delete('notification:cache_updates')
        except Exception as e:
            print(f"Error in master sync: {str(e)}")

    async def _replica_sync(self):
        """Replica instance synchronization tasks."""
        try:
            # Check for cache updates
            updates = await self._get_cache_updates()
            
            if updates:
                # Apply updates to local cache
                await self._apply_cache_updates(updates)
        except Exception as e:
            print(f"Error in replica sync: {str(e)}")

    async def _collect_cache_updates(self) -> List[Dict[str, Any]]:
        """Collect cache updates from all instances."""
        updates = []
        
        # Get all pending updates
        update_keys = await self.redis.smembers('notification:pending_updates')
        
        for key in update_keys:
            update_data = await self.redis.get(key)
            if update_data:
                updates.append(json.loads(update_data))
                await self.redis.delete(key)
        
        await self.redis.delete('notification:pending_updates')
        return updates

    async def _broadcast_cache_updates(self, updates: List[Dict[str, Any]]):
        """Broadcast cache updates to all instances."""
        # Store updates for replicas to fetch
        await self.redis.set(
            'notification:cache_updates',
            json.dumps(updates),
            ex=self.sync_interval * 2
        )

    async def _get_cache_updates(self) -> List[Dict[str, Any]]:
        """Get cache updates for replica."""
        updates_data = await self.redis.get('notification:cache_updates')
        return json.loads(updates_data) if updates_data else []

    async def _apply_cache_updates(self, updates: List[Dict[str, Any]]):
        """Apply cache updates to local cache."""
        for update in updates:
            if update['operation'] == 'set':
                await self._local_cache_set(
                    update['key'],
                    update['value'],
                    update['ttl']
                )
            elif update['operation'] == 'delete':
                await self._local_cache_delete(update['key'])

    async def submit_cache_update(
        self,
        operation: str,
        key: str,
        value: Optional[Any] = None,
        ttl: Optional[int] = None
    ):
        """Submit a cache update for synchronization."""
        update = {
            'operation': operation,
            'key': key,
            'value': value,
            'ttl': ttl,
            'timestamp': datetime.utcnow().isoformat(),
            'instance_id': self.instance_id
        }
        
        update_key = f"notification:update:{self.instance_id}:{datetime.utcnow().timestamp()}"
        
        # Store update
        await self.redis.set(
            update_key,
            json.dumps(update),
            ex=self.sync_interval * 2
        )
        await self.redis.sadd('notification:pending_updates', update_key)

    async def _get_lock(self, lock_name: str):
        """Get distributed lock."""
        return DistributedLock(self.redis, lock_name, self.lock_timeout)

    async def _local_cache_set(self, key: str, value: Any, ttl: Optional[int]):
        """Update local cache."""
        # Implement local cache update logic
        pass

    async def _local_cache_delete(self, key: str):
        """Delete from local cache."""
        # Implement local cache deletion logic
        pass


class DistributedLock:
    """Distributed lock implementation using Redis."""
    
    def __init__(self, redis: Redis, lock_name: str, timeout: int):
        self.redis = redis
        self.lock_name = f"lock:{lock_name}"
        self.timeout = timeout
        self.locked = False

    async def __aenter__(self):
        """Acquire lock."""
        while not self.locked:
            locked = await self.redis.set(
                self.lock_name,
                '1',
                ex=self.timeout,
                nx=True
            )
            if locked:
                self.locked = True
                break
            await asyncio.sleep(0.1)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release lock."""
        if self.locked:
            await self.redis.delete(self.lock_name)
            self.locked = False 