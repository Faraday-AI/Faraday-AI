import logging
from typing import Dict, Any, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.physical_education.services.activity_manager import ActivityManager
import redis.asyncio as redis
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class ActivityCircuitBreakerManager:
    """Service for managing circuit breaking for activities."""
    
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
        
        # Circuit breaker settings
        self.settings = {
            'failure_threshold': 5,
            'reset_timeout': 60,  # 1 minute
            'half_open_timeout': 30,  # 30 seconds
            'success_threshold': 3
        }
        
    async def check_circuit(self, service_name: str) -> bool:
        """Check if circuit is closed for a service."""
        try:
            state_key = f"circuit:{service_name}:state"
            state = await self.redis_client.get(state_key)
            
            if not state:
                return True  # Default to closed
                
            if state == CircuitState.OPEN.value:
                # Check if reset timeout has passed
                last_failure_key = f"circuit:{service_name}:last_failure"
                last_failure = await self.redis_client.get(last_failure_key)
                if last_failure:
                    last_failure_time = datetime.fromtimestamp(float(last_failure))
                    if (datetime.now() - last_failure_time).seconds >= self.settings['reset_timeout']:
                        # Move to half-open state
                        await self.redis_client.set(state_key, CircuitState.HALF_OPEN.value)
                        return True
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking circuit: {str(e)}")
            return True  # Default to closed
            
    async def record_failure(self, service_name: str) -> None:
        """Record a service failure."""
        try:
            failure_key = f"circuit:{service_name}:failures"
            last_failure_key = f"circuit:{service_name}:last_failure"
            state_key = f"circuit:{service_name}:state"
            
            # Increment failure count
            failures = int(await self.redis_client.get(failure_key) or 0)
            failures += 1
            
            # Update last failure time
            await self.redis_client.set(last_failure_key, datetime.now().timestamp())
            
            # Check if threshold reached
            if failures >= self.settings['failure_threshold']:
                await self.redis_client.set(state_key, CircuitState.OPEN.value)
                self.logger.warning(f"Circuit breaker opened for {service_name}")
                
            await self.redis_client.set(failure_key, failures)
            
        except Exception as e:
            self.logger.error(f"Error recording failure: {str(e)}")
            
    async def record_success(self, service_name: str) -> None:
        """Record a service success."""
        try:
            success_key = f"circuit:{service_name}:successes"
            state_key = f"circuit:{service_name}:state"
            
            # Increment success count
            successes = int(await self.redis_client.get(success_key) or 0)
            successes += 1
            
            # Check if in half-open state
            current_state = await self.redis_client.get(state_key)
            if current_state == CircuitState.HALF_OPEN.value:
                if successes >= self.settings['success_threshold']:
                    # Reset circuit
                    await self.reset_circuit(service_name)
                    
            await self.redis_client.set(success_key, successes)
            
        except Exception as e:
            self.logger.error(f"Error recording success: {str(e)}")
            
    async def reset_circuit(self, service_name: str) -> None:
        """Reset circuit breaker for a service."""
        try:
            # Reset all counters and state
            await self.redis_client.delete(f"circuit:{service_name}:failures")
            await self.redis_client.delete(f"circuit:{service_name}:successes")
            await self.redis_client.delete(f"circuit:{service_name}:last_failure")
            await self.redis_client.set(f"circuit:{service_name}:state", CircuitState.CLOSED.value)
            
            self.logger.info(f"Circuit breaker reset for {service_name}")
            
        except Exception as e:
            self.logger.error(f"Error resetting circuit: {str(e)}")
            
    async def get_circuit_stats(self, service_name: str) -> Dict[str, Any]:
        """Get circuit breaker statistics for a service."""
        try:
            failures = int(await self.redis_client.get(f"circuit:{service_name}:failures") or 0)
            successes = int(await self.redis_client.get(f"circuit:{service_name}:successes") or 0)
            state = await self.redis_client.get(f"circuit:{service_name}:state") or CircuitState.CLOSED.value
            last_failure = await self.redis_client.get(f"circuit:{service_name}:last_failure")
            
            return {
                'state': state,
                'failures': failures,
                'successes': successes,
                'last_failure': datetime.fromtimestamp(float(last_failure)).isoformat() if last_failure else None,
                'threshold': self.settings['failure_threshold']
            }
        except Exception as e:
            self.logger.error(f"Error getting circuit stats: {str(e)}")
            return {} 