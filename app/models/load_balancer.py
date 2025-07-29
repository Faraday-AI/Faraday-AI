"""Load balancer models for managing regional routing and failover."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.db.base_class import Base

class LoadBalancerRegion(Base):
    """Model for load balancer regions."""
    
    __tablename__ = "load_balancer_regions"
    
    id = Column(Integer, primary_key=True, index=True)
    region_code = Column(String(10), unique=True, index=True, nullable=False)
    region_name = Column(String(100), nullable=False)
    endpoint_url = Column(String(255), nullable=False)
    health_check_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    max_capacity = Column(Integer, default=1000)
    current_load = Column(Float, default=0.0)
    latency_ms = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    last_health_check = Column(DateTime, default=func.now())
    region_metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class LoadBalancerRoute(Base):
    """Model for load balancer routing rules."""
    
    __tablename__ = "load_balancer_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    route_pattern = Column(String(255), nullable=False, index=True)
    target_region_id = Column(Integer, ForeignKey("load_balancer_regions.id"))
    weight = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    conditions = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    target_region = relationship("LoadBalancerRegion")

class LoadBalancerHealthCheck(Base):
    """Model for load balancer health check results."""
    
    __tablename__ = "load_balancer_health_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("load_balancer_regions.id"))
    check_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # healthy, unhealthy, unknown
    response_time_ms = Column(Float)
    error_message = Column(Text)
    check_data = Column(JSON, default={})
    performed_at = Column(DateTime, default=func.now())
    
    region = relationship("LoadBalancerRegion")

class LoadBalancerMetrics(Base):
    """Model for load balancer performance metrics."""
    
    __tablename__ = "load_balancer_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("load_balancer_regions.id"))
    metric_type = Column(String(50), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))
    timestamp = Column(DateTime, default=func.now())
    metric_metadata = Column(JSON, default={})
    
    region = relationship("LoadBalancerRegion")

class LoadBalancerCircuitBreaker(Base):
    """Model for circuit breaker state."""
    
    __tablename__ = "load_balancer_circuit_breakers"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("load_balancer_regions.id"))
    circuit_state = Column(String(20), nullable=False)  # closed, open, half-open
    failure_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    last_failure_time = Column(DateTime)
    last_success_time = Column(DateTime)
    threshold = Column(Integer, default=5)
    timeout_seconds = Column(Integer, default=30)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    region = relationship("LoadBalancerRegion")

class LoadBalancerRequestLog(Base):
    """Model for load balancer request logging."""
    
    __tablename__ = "load_balancer_request_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(100), index=True)
    source_ip = Column(String(45))
    target_region_id = Column(Integer, ForeignKey("load_balancer_regions.id"))
    request_path = Column(String(255))
    request_method = Column(String(10))
    response_status = Column(Integer)
    response_time_ms = Column(Float)
    request_size_bytes = Column(Integer)
    response_size_bytes = Column(Integer)
    user_agent = Column(String(500))
    headers = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    
    target_region = relationship("LoadBalancerRegion")

class LoadBalancerConfig(Base):
    """Model for load balancer configuration."""
    
    __tablename__ = "load_balancer_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, index=True, nullable=False)
    config_value = Column(JSON, nullable=False)
    config_type = Column(String(50), nullable=False)  # string, number, boolean, json
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class RegionConfig(Base):
    """Model for region configuration."""
    
    __tablename__ = "region_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("load_balancer_regions.id"))
    config_key = Column(String(100), nullable=False)
    config_value = Column(JSON, nullable=False)
    config_type = Column(String(50), nullable=False)  # string, number, boolean, json
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    region = relationship("LoadBalancerRegion")

class MetricsHistory(Base):
    """Model for metrics history."""
    
    __tablename__ = "metrics_history"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("load_balancer_regions.id"))
    metric_type = Column(String(50), nullable=False)
    metric_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    metric_metadata = Column(JSON, default={})
    
    region = relationship("LoadBalancerRegion")

class AlertConfig(Base):
    """Model for alert configuration."""
    __tablename__ = "alert_configs"
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)
    threshold = Column(Float, nullable=False)
    enabled = Column(Boolean, default=True)
    notification_channels = Column(JSON, default=[])
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class RoutingStrategy(Base):
    """Model for routing strategy configuration."""
    __tablename__ = "routing_strategies"
    id = Column(Integer, primary_key=True, index=True)
    strategy_name = Column(String(100), nullable=False)
    strategy_type = Column(String(50), nullable=False)  # round_robin, weighted, least_connections, etc.
    configuration = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AlertHistory(Base):
    """Model for alert history."""
    __tablename__ = "alert_history"
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    message = Column(Text, nullable=False)
    region_id = Column(Integer, ForeignKey("load_balancer_regions.id"))
    triggered_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)
    is_resolved = Column(Boolean, default=False)
    alert_metadata = Column(JSON, default={})
    
    region = relationship("LoadBalancerRegion")


class AlertType:
    """Enum for alert types."""
    HIGH_LOAD = "high_load"
    HIGH_LATENCY = "high_latency"
    HIGH_ERROR_RATE = "high_error_rate"
    REGION_DOWN = "region_down"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CIRCUIT_BREAKER_TRIPPED = "circuit_breaker_tripped"


class AlertSeverity:
    """Enum for alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"