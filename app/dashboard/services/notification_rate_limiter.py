"""
Notification Rate Limiter Service

This module provides rate limiting functionality specifically designed for
notification handling, including token bucket implementation and event storage.
"""

from typing import Dict, Any, Optional, List, Tuple
import asyncio
import time
from datetime import datetime, timedelta
import json
from collections import defaultdict
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket."""
        async with self.lock:
            now = time.time()
            # Add new tokens based on time passed
            time_passed = now - self.last_update
            self.tokens = min(
                self.capacity,
                self.tokens + time_passed * self.rate
            )
            self.last_update = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

class NotificationRateLimiter:
    def __init__(self):
        self.settings = get_settings()
        self.buckets: Dict[str, TokenBucket] = {}
        self.default_rates = {
            'user': (10, 50),      # 10/s, burst of 50
            'ip': (100, 500),      # 100/s, burst of 500
            'global': (1000, 5000)  # 1000/s, burst of 5000
        }
        self.stats = defaultdict(lambda: {
            'allowed': 0,
            'blocked': 0,
            'last_blocked': None
        })

    def get_bucket(self, key: str, bucket_type: str = 'user') -> TokenBucket:
        """Get or create a token bucket for the key."""
        if key not in self.buckets:
            rate, capacity = self.default_rates.get(bucket_type, (5, 25))
            self.buckets[key] = TokenBucket(rate, capacity)
        return self.buckets[key]

    async def check_rate_limit(
        self,
        key: str,
        bucket_type: str = 'user',
        tokens: int = 1
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if an operation is allowed under rate limits."""
        bucket = self.get_bucket(key, bucket_type)
        allowed = await bucket.consume(tokens)
        
        # Update stats
        self.stats[key]['allowed' if allowed else 'blocked'] += 1
        if not allowed:
            self.stats[key]['last_blocked'] = datetime.utcnow()

        return allowed, {
            'allowed': allowed,
            'bucket_type': bucket_type,
            'tokens_requested': tokens,
            'tokens_remaining': bucket.tokens,
            'reset_time': (bucket.capacity - bucket.tokens) / bucket.rate
        }

class EventStore:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.event_buffer = asyncio.Queue()
        self.processing = False
        self.batch_size = 100
        self.flush_interval = 1  # seconds
        self.stats = defaultdict(int)

    async def start(self):
        """Start event processing."""
        self.processing = True
        asyncio.create_task(self._process_events())
        asyncio.create_task(self._cleanup_old_events())

    async def stop(self):
        """Stop event processing."""
        self.processing = False
        await self._flush_events()

    async def record_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a new event."""
        event = {
            'type': event_type,
            'data': data,
            'metadata': metadata or {},
            'timestamp': datetime.utcnow().isoformat(),
            'version': 1  # For schema versioning
        }
        await self.event_buffer.put(event)
        self.stats['events_queued'] += 1

    async def _process_events(self):
        """Process events in batches."""
        while self.processing:
            try:
                batch = []
                try:
                    # Get first event
                    event = await asyncio.wait_for(
                        self.event_buffer.get(),
                        timeout=self.flush_interval
                    )
                    batch.append(event)
                    
                    # Try to get more events
                    while len(batch) < self.batch_size:
                        try:
                            event = self.event_buffer.get_nowait()
                            batch.append(event)
                        except asyncio.QueueEmpty:
                            break
                    
                except asyncio.TimeoutError:
                    continue

                # Store batch
                await self._store_events(batch)
                
                # Update stats
                self.stats['batches_processed'] += 1
                self.stats['events_processed'] += len(batch)

            except Exception as e:
                logger.error(f"Error processing events: {str(e)}")
                await asyncio.sleep(1)

    async def _store_events(self, events: List[Dict[str, Any]]):
        """Store events in the database."""
        async with self.db.begin() as transaction:
            try:
                for event in events:
                    await self.db.execute(
                        text("""
                            INSERT INTO notification_events
                            (type, data, metadata, timestamp, version)
                            VALUES (:type, :data, :metadata, :timestamp, :version)
                        """),
                        {
                            'type': event['type'],
                            'data': json.dumps(event['data']),
                            'metadata': json.dumps(event['metadata']),
                            'timestamp': event['timestamp'],
                            'version': event['version']
                        }
                    )
                
                await transaction.commit()
                self.stats['successful_writes'] += len(events)
                
            except Exception as e:
                await transaction.rollback()
                logger.error(f"Database write error: {str(e)}")
                self.stats['failed_writes'] += len(events)
                # Requeue failed events
                for event in events:
                    await self.event_buffer.put(event)

    async def get_events(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Retrieve events with filtering."""
        try:
            query = "SELECT * FROM notification_events WHERE 1=1"
            params = {}

            if event_type:
                query += " AND type = :event_type"
                params['event_type'] = event_type

            if start_time:
                query += " AND timestamp >= :start_time"
                params['start_time'] = start_time.isoformat()

            if end_time:
                query += " AND timestamp <= :end_time"
                params['end_time'] = end_time.isoformat()

            query += " ORDER BY timestamp DESC LIMIT :limit"
            params['limit'] = limit

            result = await self.db.execute(text(query), params)
            events = []
            for row in result:
                event = dict(row)
                event['data'] = json.loads(event['data'])
                event['metadata'] = json.loads(event['metadata'])
                events.append(event)

            return events

        except Exception as e:
            logger.error(f"Error retrieving events: {str(e)}")
            return []

    async def _cleanup_old_events(self):
        """Clean up old events based on retention policy."""
        while self.processing:
            try:
                retention_days = self.settings.EVENT_RETENTION_DAYS
                cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
                
                # Delete old events
                await self.db.execute(
                    text("DELETE FROM notification_events WHERE timestamp < :cutoff"),
                    {'cutoff': cutoff_date.isoformat()}
                )
                
                await asyncio.sleep(86400)  # Run daily
                
            except Exception as e:
                logger.error(f"Error cleaning up events: {str(e)}")
                await asyncio.sleep(3600)  # Retry in an hour

    async def _flush_events(self):
        """Flush all pending events."""
        while not self.event_buffer.empty():
            batch = []
            try:
                while len(batch) < self.batch_size:
                    try:
                        event = self.event_buffer.get_nowait()
                        batch.append(event)
                    except asyncio.QueueEmpty:
                        break
                
                if batch:
                    await self._store_events(batch)
                    
            except Exception as e:
                logger.error(f"Error flushing events: {str(e)}")
                # Requeue failed events
                for event in batch:
                    await self.event_buffer.put(event)

    async def get_stats(self) -> Dict[str, Any]:
        """Get event store statistics."""
        return dict(self.stats) 