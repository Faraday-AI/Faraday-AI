import asyncio
import time
from typing import Any, Callable, Optional, TypeVar, cast
from functools import wraps
import logging
from datetime import datetime, timedelta

T = TypeVar('T')

class CircuitBreaker:
    """Circuit breaker pattern implementation for Redis operations."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        half_open_timeout: int = 30,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening the circuit
            reset_timeout: Time in seconds to wait before attempting to reset
            half_open_timeout: Time in seconds to wait in half-open state
            logger: Optional logger instance
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        self.logger = logger or logging.getLogger(__name__)
        
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
        self._lock = asyncio.Lock()

    async def __call__(self, func: Callable[..., Any]) -> Any:
        """Decorator for circuit breaker pattern."""
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if self.state == "open":
                if self._should_reset():
                    self.state = "half-open"
                    self.logger.info("Circuit breaker entering half-open state")
                else:
                    self.logger.warning("Circuit breaker is open, operation skipped")
                    raise CircuitBreakerOpenError("Circuit breaker is open")

            try:
                result = await func(*args, **kwargs)
                if self.state == "half-open":
                    await self._reset()
                return result
            except Exception as e:
                await self._record_failure()
                raise

        return wrapper

    def _should_reset(self) -> bool:
        """Check if the circuit breaker should reset."""
        if not self.last_failure_time:
            return False
        return (datetime.utcnow() - self.last_failure_time).total_seconds() > self.reset_timeout

    async def _record_failure(self) -> None:
        """Record a failure and update circuit breaker state."""
        async with self._lock:
            self.failures += 1
            self.last_failure_time = datetime.utcnow()
            
            if self.failures >= self.failure_threshold:
                self.state = "open"
                self.logger.error(f"Circuit breaker opened after {self.failures} failures")
                
                # Schedule reset attempt
                asyncio.create_task(self._attempt_reset())

    async def _attempt_reset(self) -> None:
        """Attempt to reset the circuit breaker."""
        await asyncio.sleep(self.reset_timeout)
        async with self._lock:
            if self.state == "open":
                self.state = "half-open"
                self.logger.info("Circuit breaker entering half-open state")

    async def _reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        async with self._lock:
            self.failures = 0
            self.last_failure_time = None
            self.state = "closed"
            self.logger.info("Circuit breaker reset to closed state")

    def get_state(self) -> dict:
        """Get the current state of the circuit breaker."""
        return {
            "state": self.state,
            "failures": self.failures,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "failure_threshold": self.failure_threshold,
            "reset_timeout": self.reset_timeout
        }

class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass

def circuit_breaker(
    failure_threshold: int = 5,
    reset_timeout: int = 60,
    half_open_timeout: int = 30,
    logger: Optional[logging.Logger] = None
) -> Callable[[Callable[..., Any]], Any]:
    """
    Decorator factory for circuit breaker pattern.
    
    Args:
        failure_threshold: Number of failures before opening the circuit
        reset_timeout: Time in seconds to wait before attempting to reset
        half_open_timeout: Time in seconds to wait in half-open state
        logger: Optional logger instance
    
    Returns:
        Decorator function
    """
    breaker = CircuitBreaker(failure_threshold, reset_timeout, half_open_timeout, logger)
    
    def decorator(func: Callable[..., Any]) -> Any:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await breaker(func)(*args, **kwargs)
        return wrapper
    
    return decorator 