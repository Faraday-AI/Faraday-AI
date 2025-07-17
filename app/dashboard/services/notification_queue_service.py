from typing import Dict, List, Optional, Any
import json
import asyncio
from datetime import datetime, timedelta
from redis.asyncio import Redis
from app.core.config import get_settings

class NotificationQueueService:
    def __init__(self):
        self.settings = get_settings()
        self.redis = None
        self.processing = False
        self.batch_size = 100
        self.processing_interval = 1  # seconds

    async def initialize(self):
        """Initialize Redis connection pool."""
        if not self.redis:
            self.redis = Redis.from_url(
                self.settings.REDIS_URL,
                encoding='utf-8',
                decode_responses=True
            )

    async def close(self):
        """Close Redis connections."""
        if self.redis:
            await self.redis.close()

    async def enqueue_notification(self, notification: Dict[str, Any]) -> str:
        """Add notification to queue with priority."""
        await self.initialize()
        
        # Generate unique ID for notification
        notification_id = f"notification:{datetime.utcnow().isoformat()}:{notification['user_id']}"
        
        # Store full notification data
        await self.redis.set(
            notification_id,
            json.dumps(notification),
            ex=86400  # 24 hours TTL
        )
        
        # Add to priority queue
        priority_score = self._calculate_priority_score(notification)
        await self.redis.zadd(
            'notification_queue',
            {notification_id: priority_score}
        )
        
        return notification_id

    def _calculate_priority_score(self, notification: Dict[str, Any]) -> float:
        """Calculate priority score for notification ordering."""
        base_scores = {
            'urgent': 1000,
            'high': 100,
            'normal': 10,
            'low': 1
        }
        
        # Base score from priority
        score = base_scores.get(notification.get('priority', 'normal'), 10)
        
        # Adjust for notification type
        type_multipliers = {
            'security': 2.0,
            'system': 1.5,
            'resource': 1.3,
            'achievement': 0.8
        }
        score *= type_multipliers.get(notification.get('type', ''), 1.0)
        
        # Add timestamp factor (newer = higher priority)
        timestamp = datetime.fromisoformat(notification.get('timestamp', datetime.utcnow().isoformat()))
        time_factor = (datetime.utcnow() - timestamp).total_seconds()
        score += (1000000 - time_factor) / 1000000
        
        return score

    async def start_processing(self):
        """Start processing notification queue."""
        self.processing = True
        while self.processing:
            try:
                await self._process_batch()
                await asyncio.sleep(self.processing_interval)
            except Exception as e:
                print(f"Error processing notification batch: {str(e)}")
                await asyncio.sleep(5)  # Back off on error

    async def stop_processing(self):
        """Stop processing notification queue."""
        self.processing = False

    async def _process_batch(self):
        """Process a batch of notifications from queue."""
        await self.initialize()
        
        # Get batch of highest priority notifications
        notifications = await self.redis.zrange(
            'notification_queue',
            0,
            self.batch_size - 1,
            withscores=True
        )
        
        if not notifications:
            return
        
        # Process notifications
        for notification_id, score in notifications:
            try:
                # Get notification data
                notification_data = await self.redis.get(notification_id)
                if not notification_data:
                    continue
                
                notification = json.loads(notification_data)
                
                # Process notification (implement actual processing logic)
                success = await self._process_notification(notification)
                
                if success:
                    # Remove from queue and data store
                    await asyncio.gather(
                        self.redis.zrem('notification_queue', notification_id),
                        self.redis.delete(notification_id)
                    )
                else:
                    # Decrease priority and push back to queue
                    new_score = score * 0.8  # 20% priority reduction
                    await self.redis.zadd('notification_queue', {notification_id: new_score})
                
            except Exception as e:
                print(f"Error processing notification {notification_id}: {str(e)}")

    async def _process_notification(self, notification: Dict[str, Any]) -> bool:
        """Process a single notification."""
        try:
            # Add actual notification processing logic here
            # This is where you'd call your notification service
            return True
        except Exception as e:
            print(f"Error in notification processing: {str(e)}")
            return False

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get current queue statistics."""
        await self.initialize()
        
        total_count = await self.redis.zcard('notification_queue')
        
        # Get counts by priority
        priorities = ['urgent', 'high', 'normal', 'low']
        counts_by_priority = {}
        
        for priority in priorities:
            min_score = self._calculate_priority_score({'priority': priority, 'timestamp': datetime.utcnow().isoformat()})
            count = await self.redis.zcount(
                'notification_queue',
                min_score,
                float('inf')
            )
            counts_by_priority[priority] = count
        
        return {
            'total_notifications': total_count,
            'by_priority': counts_by_priority,
            'processing_rate': self.batch_size / self.processing_interval
        } 