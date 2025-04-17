import logging
from typing import Dict, Any, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.physical_education.activity_manager import ActivityManager
import redis.asyncio as redis
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ActivityRateLimitManager:
    """Service for managing rate limits for activities."""
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.activity_manager = ActivityManager(db)
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        
        # Rate limit settings
        self.settings = {
            'default_limits': {
                'create_activity': {'max_requests': 10, 'time_window': 60},
                'update_activity': {'max_requests': 20, 'time_window': 60},
                'get_activities': {'max_requests': 30, 'time_window': 60},
                'delete_activity': {'max_requests': 5, 'time_window': 60}
            },
            'block_duration': 3600  # 1 hour
        }
        
    async def check_rate_limit(self, user_id: str, action: str) -> bool:
        """Check if user has exceeded rate limit for an action."""
        try:
            limit_key = f"rate_limit:{user_id}:{action}"
            current_time = datetime.now()
            
            # Get current count and window start
            count_data = await self.redis_client.get(limit_key)
            if count_data:
                count, window_start = map(int, count_data.split(':'))
                window_start = datetime.fromtimestamp(window_start)
                
                # Check if window has expired
                if (current_time - window_start).seconds > self.settings['default_limits'][action]['time_window']:
                    count = 0
                    window_start = current_time
            else:
                count = 0
                window_start = current_time
                
            # Check if limit exceeded
            if count >= self.settings['default_limits'][action]['max_requests']:
                return False
                
            # Increment count
            count += 1
            await self.redis_client.setex(
                limit_key,
                self.settings['default_limits'][action]['time_window'],
                f"{count}:{int(window_start.timestamp())}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {str(e)}")
            return True  # Allow request if rate limit check fails
            
    async def block_user(self, user_id: str, reason: str) -> bool:
        """Block a user from making requests."""
        try:
            block_key = f"blocked:{user_id}"
            await self.redis_client.setex(
                block_key,
                self.settings['block_duration'],
                reason
            )
            return True
        except Exception as e:
            self.logger.error(f"Error blocking user: {str(e)}")
            return False
            
    async def is_user_blocked(self, user_id: str) -> Optional[str]:
        """Check if user is blocked and get reason."""
        try:
            block_key = f"blocked:{user_id}"
            reason = await self.redis_client.get(block_key)
            return reason
        except Exception as e:
            self.logger.error(f"Error checking user block status: {str(e)}")
            return None
            
    async def unblock_user(self, user_id: str) -> bool:
        """Unblock a user."""
        try:
            block_key = f"blocked:{user_id}"
            await self.redis_client.delete(block_key)
            return True
        except Exception as e:
            self.logger.error(f"Error unblocking user: {str(e)}")
            return False
            
    async def get_rate_limit_stats(self, user_id: str) -> Dict[str, Any]:
        """Get rate limit statistics for a user."""
        try:
            stats = {}
            for action in self.settings['default_limits']:
                limit_key = f"rate_limit:{user_id}:{action}"
                count_data = await self.redis_client.get(limit_key)
                if count_data:
                    count, window_start = map(int, count_data.split(':'))
                    stats[action] = {
                        'current_count': count,
                        'max_allowed': self.settings['default_limits'][action]['max_requests'],
                        'window_start': datetime.fromtimestamp(window_start).isoformat()
                    }
                else:
                    stats[action] = {
                        'current_count': 0,
                        'max_allowed': self.settings['default_limits'][action]['max_requests'],
                        'window_start': datetime.now().isoformat()
                    }
            return stats
        except Exception as e:
            self.logger.error(f"Error getting rate limit stats: {str(e)}")
            return {} 