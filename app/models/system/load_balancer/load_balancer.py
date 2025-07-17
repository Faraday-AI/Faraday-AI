"""
Load Balancer Database Models

This module defines the database models for the load balancer system, including:
- Load balancer configurations
- Region settings
- Metrics history
- Alert configurations
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, JSON, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import BaseModel, NamedMixin, TimestampedMixin, StatusMixin, MetadataMixin

class RoutingStrategy(enum.Enum):
    GEOGRAPHIC = "geographic"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    ADAPTIVE = "adaptive"

class Region(enum.Enum):
    NORTH_AMERICA = "NORTH_AMERICA"
    EUROPE = "EUROPE"
    ASIA = "ASIA"
    SOUTH_AMERICA = "SOUTH_AMERICA"

class AlertSeverity(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(enum.Enum):
    LOAD = "load"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    RESOURCE_USAGE = "resource_usage"
    HEALTH_CHECK = "health_check"
    CIRCUIT_BREAKER = "circuit_breaker"

class LoadBalancerConfig(BaseModel, NamedMixin, StatusMixin):
    """Global load balancer configuration."""
    
    __tablename__ = "load_balancer_configs"
    
    routing_strategy = Column(SQLEnum(RoutingStrategy, name='routing_strategy_enum'), nullable=False)
    settings = Column(JSON, nullable=False)  # Additional configuration settings
    
    # Relationships
    regions = relationship("RegionConfig", back_populates="load_balancer_config")
    alerts = relationship("AlertConfig", back_populates="load_balancer_config")

class RegionConfig(BaseModel, StatusMixin):
    """Configuration for a specific region."""
    
    __tablename__ = "region_configs"
    
    load_balancer_config_id = Column(Integer, ForeignKey("load_balancer_configs.id"), nullable=False)
    region = Column(SQLEnum(Region, name='region_enum'), nullable=False)
    weight = Column(Float, nullable=False, default=1.0)
    health_check_settings = Column(JSON, nullable=False)
    circuit_breaker_settings = Column(JSON, nullable=False)
    
    # Relationships
    load_balancer_config = relationship("LoadBalancerConfig", back_populates="regions")
    metrics = relationship("MetricsHistory", back_populates="region_config")

class MetricsHistory(BaseModel, TimestampedMixin):
    """Historical metrics for regions."""
    
    __tablename__ = "metrics_history"
    
    region_config_id = Column(Integer, ForeignKey("region_configs.id"), nullable=False)
    metrics_type = Column(String, nullable=False)  # e.g., 'requests', 'latency', 'resource_usage'
    value = Column(Float, nullable=False)
    metric_metadata = Column(JSON)
    
    # Relationships
    region_config = relationship("RegionConfig", back_populates="metrics")

class AlertConfig(BaseModel, StatusMixin):
    """Alert configuration for the load balancer."""
    
    __tablename__ = "alert_configs"
    
    load_balancer_config_id = Column(Integer, ForeignKey("load_balancer_configs.id"), nullable=False)
    alert_type = Column(SQLEnum(AlertType, name='alert_type_enum'), nullable=False)
    severity = Column(SQLEnum(AlertSeverity, name='alert_severity_enum'), nullable=False)
    threshold_settings = Column(JSON, nullable=False)
    notification_settings = Column(JSON, nullable=False)
    cooldown_seconds = Column(Integer, default=300, nullable=False)
    
    # Relationships
    load_balancer_config = relationship("LoadBalancerConfig", back_populates="alerts")
    alert_history = relationship("AlertHistory", back_populates="alert_config")

class AlertHistory(BaseModel, TimestampedMixin):
    """Historical record of triggered alerts."""
    
    __tablename__ = "alert_history"
    
    alert_config_id = Column(Integer, ForeignKey("alert_configs.id"), nullable=False)
    resolved_at = Column(DateTime)
    trigger_value = Column(Float, nullable=False)
    alert_metadata = Column(JSON)
    notification_status = Column(JSON)  # Status of notifications sent
    
    # Relationships
    alert_config = relationship("AlertConfig", back_populates="alert_history")

class LoadBalancerMetric(BaseModel, TimestampedMixin):
    """Model for load balancer metrics."""
    
    __tablename__ = "load_balancer_metrics"
    
    balancer_id = Column(Integer, ForeignKey("load_balancers.id"), nullable=False)
    metric_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    metric_metadata = Column(JSON)
    
    # Relationships
    balancer = relationship("LoadBalancer", back_populates="metrics")

    def __repr__(self):
        return f"<LoadBalancerMetric {self.metric_type} - {self.value}>"

class LoadBalancerAlert(BaseModel, TimestampedMixin, StatusMixin):
    """Model for load balancer alerts."""
    
    __tablename__ = "load_balancer_alerts"
    
    balancer_id = Column(Integer, ForeignKey("load_balancers.id"), nullable=False)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    resolved_at = Column(DateTime)
    alert_metadata = Column(JSON)
    
    # Relationships
    balancer = relationship("LoadBalancer", back_populates="alerts")

    def __repr__(self):
        return f"<LoadBalancerAlert {self.alert_type} - {self.severity}>"

# Index creation for better query performance
Index('idx_metrics_timestamp', MetricsHistory.created_at)
Index('idx_metrics_region_type', MetricsHistory.region_config_id, MetricsHistory.metrics_type)
Index('idx_alert_history_triggered', AlertHistory.created_at)
Index('idx_alert_history_config', AlertHistory.alert_config_id)
Index('idx_region_config_active', RegionConfig.status) 