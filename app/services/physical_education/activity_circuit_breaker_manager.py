"""Activity circuit breaker manager for physical education."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.activity import (
    Activity,
    ActivityType,
    DifficultyLevel,
    EquipmentRequirement,
    ActivityCategoryAssociation
)
from app.models.student import Student
from app.models.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerPolicy,
    CircuitBreakerMetrics,
    CircuitBreakerStatus
)
from app.models.physical_education.pe_enums.pe_types import (
    CircuitBreakerType,
    CircuitBreakerLevel,
    CircuitBreakerStatus,
    CircuitBreakerTrigger
)
from app.models.physical_education.activity.models import (
    StudentActivityPerformance,
    StudentActivityPreference
)

class ActivityCircuitBreakerManager:
    """Service for managing physical education activity circuit breakers."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ActivityCircuitBreakerManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.logger = logging.getLogger("activity_circuit_breaker_manager")
        self.db = None
        
        # Circuit breaker settings
        self.settings = {
            "circuit_breaker_enabled": True,
            "auto_break": True,
            "failure_threshold": 5,
            "reset_timeout": 60,  # seconds
            "half_open_timeout": 30,  # seconds
            "thresholds": {
                "error_rate": 0.5,
                "latency": 1000,  # ms
                "timeout": 5000  # ms
            }
        }
        
        # Circuit breaker components
        self.circuit_breakers = {}
        self.breaker_metrics = {}
        self.failure_history = []
        self.state_history = []
    
    async def initialize(self):
        """Initialize the circuit breaker manager."""
        try:
            self.db = next(get_db())
            
            # Initialize circuit breaker components
            self.initialize_circuit_breaker_components()
            
            self.logger.info("Activity Circuit Breaker Manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Activity Circuit Breaker Manager: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup the circuit breaker manager."""
        try:
            # Clear all data
            self.circuit_breakers.clear()
            self.breaker_metrics.clear()
            self.failure_history.clear()
            self.state_history.clear()
            
            # Reset service references
            self.db = None
            
            self.logger.info("Activity Circuit Breaker Manager cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error cleaning up Activity Circuit Breaker Manager: {str(e)}")
            raise

    def initialize_circuit_breaker_components(self):
        """Initialize circuit breaker components."""
        try:
            # Initialize breaker metrics
            self.breaker_metrics = {
                "failures": {
                    "count": 0,
                    "rate": 0.0,
                    "window_start": datetime.now().isoformat()
                },
                "trips": {
                    "count": 0,
                    "rate": 0.0
                },
                "resets": {
                    "count": 0,
                    "rate": 0.0
                }
            }
            
            self.logger.info("Circuit breaker components initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing circuit breaker components: {str(e)}")
            raise

    async def check_circuit_breaker(
        self,
        activity_id: str,
        student_id: str
    ) -> Dict[str, Any]:
        """Check if circuit breaker allows request."""
        try:
            if not self.settings["circuit_breaker_enabled"]:
                return {"allowed": True}
            
            # Get circuit breaker key
            breaker_key = f"{student_id}_{activity_id}"
            
            # Get or create circuit breaker
            breaker = self._get_or_create_breaker(breaker_key)
            
            # Check breaker state
            if breaker["state"] == "open":
                if self._should_transition_to_half_open(breaker):
                    breaker["state"] = "half-open"
                    self._update_state_history(breaker_key, "half-open")
                else:
                    return {
                        "allowed": False,
                        "reason": "Circuit breaker is open"
                    }
            
            # Allow request if breaker is closed or half-open
            return {"allowed": True}
            
        except Exception as e:
            self.logger.error(f"Error checking circuit breaker: {str(e)}")
            raise

    async def record_success(
        self,
        activity_id: str,
        student_id: str
    ) -> None:
        """Record successful request."""
        try:
            breaker_key = f"{student_id}_{activity_id}"
            breaker = self._get_or_create_breaker(breaker_key)
            
            # Reset failure count
            breaker["failure_count"] = 0
            
            # Transition to closed state if in half-open
            if breaker["state"] == "half-open":
                breaker["state"] = "closed"
                self._update_state_history(breaker_key, "closed")
            
        except Exception as e:
            self.logger.error(f"Error recording success: {str(e)}")
            raise

    async def record_failure(
        self,
        activity_id: str,
        student_id: str,
        error: Optional[str] = None
    ) -> None:
        """Record failed request."""
        try:
            breaker_key = f"{student_id}_{activity_id}"
            breaker = self._get_or_create_breaker(breaker_key)
            
            # Increment failure count
            breaker["failure_count"] += 1
            
            # Update failure history
            self._update_failure_history(
                breaker_key,
                error or "Unknown error"
            )
            
            # Update metrics
            self._update_breaker_metrics("failures")
            
            # Check if should trip breaker
            if self._should_trip_breaker(breaker):
                breaker["state"] = "open"
                breaker["last_trip_time"] = datetime.now().isoformat()
                self._update_state_history(breaker_key, "open")
                self._update_breaker_metrics("trips")
            
        except Exception as e:
            self.logger.error(f"Error recording failure: {str(e)}")
            raise

    async def get_breaker_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        try:
            # Calculate rates
            window_start = datetime.fromisoformat(
                self.breaker_metrics["failures"]["window_start"]
            )
            now = datetime.now()
            window_duration = (now - window_start).total_seconds()
            
            if window_duration > 0:
                self.breaker_metrics["failures"]["rate"] = (
                    self.breaker_metrics["failures"]["count"] /
                    window_duration
                )
                
                self.breaker_metrics["trips"]["rate"] = (
                    self.breaker_metrics["trips"]["count"] /
                    window_duration
                )
                
                self.breaker_metrics["resets"]["rate"] = (
                    self.breaker_metrics["resets"]["count"] /
                    window_duration
                )
            
            return self.breaker_metrics
            
        except Exception as e:
            self.logger.error(f"Error getting breaker metrics: {str(e)}")
            raise

    def _get_or_create_breaker(
        self,
        breaker_key: str
    ) -> Dict[str, Any]:
        """Get or create circuit breaker."""
        try:
            if breaker_key not in self.circuit_breakers:
                self.circuit_breakers[breaker_key] = {
                    "state": "closed",
                    "failure_count": 0,
                    "last_failure_time": None,
                    "last_trip_time": None,
                    "last_reset_time": None
                }
            
            return self.circuit_breakers[breaker_key]
            
        except Exception as e:
            self.logger.error(f"Error getting or creating breaker: {str(e)}")
            raise

    def _should_trip_breaker(
        self,
        breaker: Dict[str, Any]
    ) -> bool:
        """Check if breaker should trip."""
        try:
            return (
                breaker["failure_count"] >= self.settings["failure_threshold"]
            )
            
        except Exception as e:
            self.logger.error(f"Error checking if should trip breaker: {str(e)}")
            return False

    def _should_transition_to_half_open(
        self,
        breaker: Dict[str, Any]
    ) -> bool:
        """Check if breaker should transition to half-open state."""
        try:
            if not breaker["last_trip_time"]:
                return False
            
            last_trip = datetime.fromisoformat(breaker["last_trip_time"])
            now = datetime.now()
            
            return (
                (now - last_trip).total_seconds() >=
                self.settings["reset_timeout"]
            )
            
        except Exception as e:
            self.logger.error(f"Error checking if should transition to half-open: {str(e)}")
            return False

    def _update_failure_history(
        self,
        breaker_key: str,
        error: str
    ) -> None:
        """Update failure history."""
        try:
            self.failure_history.append({
                "breaker_key": breaker_key,
                "error": error,
                "timestamp": datetime.now().isoformat()
            })
            
            # Trim history if needed
            if len(self.failure_history) > 1000:  # Keep last 1000 records
                self.failure_history = self.failure_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error updating failure history: {str(e)}")
            raise

    def _update_state_history(
        self,
        breaker_key: str,
        state: str
    ) -> None:
        """Update state history."""
        try:
            self.state_history.append({
                "breaker_key": breaker_key,
                "state": state,
                "timestamp": datetime.now().isoformat()
            })
            
            # Trim history if needed
            if len(self.state_history) > 1000:  # Keep last 1000 records
                self.state_history = self.state_history[-1000:]
            
        except Exception as e:
            self.logger.error(f"Error updating state history: {str(e)}")
            raise

    def _update_breaker_metrics(
        self,
        metric_type: str
    ) -> None:
        """Update circuit breaker metrics."""
        try:
            if metric_type == "failures":
                self.breaker_metrics["failures"]["count"] += 1
            elif metric_type == "trips":
                self.breaker_metrics["trips"]["count"] += 1
            elif metric_type == "resets":
                self.breaker_metrics["resets"]["count"] += 1
            
        except Exception as e:
            self.logger.error(f"Error updating breaker metrics: {str(e)}")
            raise 