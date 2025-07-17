"""
Base models for physical education.

This module provides base classes with common functionality for all models.
DEPRECATED: Use app.models.base and app.models.mixins instead.
"""

import warnings
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Float, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import validates
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, TypeVar, Type, List, Set
import json
import hashlib

from app.models.base import Base, BaseModel
from app.models.mixins import NamedMixin, StatusMixin, MetadataMixin, TimestampedMixin

warnings.warn(
    "app.models.physical_education.base.model_base is deprecated. Use app.models.base and app.models.mixins instead.",
    DeprecationWarning,
    stacklevel=2
)

T = TypeVar('T', bound='BaseModel')

class BaseModel(Base):
    """Base model with common functionality for all models."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Hash for change tracking
    _hash = Column('hash', String(64), nullable=True)
    
    # Automatically generate tablename from class name
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "hash": self._hash
        }
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create model instance from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return json.dumps(self.dict())
    
    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """Create model instance from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def calculate_hash(self) -> str:
        """Calculate hash of model data for change tracking."""
        data = self.dict()
        data.pop('hash', None)
        data.pop('updated_at', None)
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def has_changed(self) -> bool:
        """Check if model data has changed."""
        return self._hash != self.calculate_hash()
    
    @validates('*')
    def validate_not_empty(self, key: str, value: Any) -> Any:
        """Validate that string fields are not empty."""
        if isinstance(value, str) and not value.strip():
            raise ValueError(f"{key} cannot be empty")
        return value

class NamedMixin:
    """Mixin for models with name and description."""
    
    __abstract__ = True
    
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    slug = Column(String, nullable=True, index=True)
    
    @validates('name')
    def validate_name(self, key: str, value: str) -> str:
        """Validate name field."""
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        if len(value) > 255:
            raise ValueError("Name is too long")
        return value.strip()
    
    def generate_slug(self) -> str:
        """Generate URL-friendly slug from name."""
        return self.name.lower().replace(' ', '-')
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "name": self.name,
            "description": self.description,
            "slug": self.slug
        }

class StatusMixin:
    """Mixin for models with status tracking."""
    
    __abstract__ = True
    
    status = Column(String, nullable=False, default="active")
    status_changed_at = Column(DateTime, nullable=True)
    status_reason = Column(String, nullable=True)
    previous_status = Column(String, nullable=True)
    status_history = Column(JSON, nullable=True, default=list)
    
    def update_status(self, new_status: str, reason: Optional[str] = None) -> None:
        """Update status with history tracking."""
        if new_status != self.status:
            self.previous_status = self.status
            self.status = new_status
            self.status_changed_at = datetime.utcnow()
            self.status_reason = reason
            
            if not self.status_history:
                self.status_history = []
            
            self.status_history.append({
                "from_status": self.previous_status,
                "to_status": new_status,
                "changed_at": self.status_changed_at.isoformat(),
                "reason": reason
            })
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "status": self.status,
            "status_changed_at": self.status_changed_at.isoformat() if self.status_changed_at else None,
            "status_reason": self.status_reason,
            "previous_status": self.previous_status,
            "status_history": self.status_history
        }

class MetadataMixin:
    """Mixin for models with metadata support."""
    
    __abstract__ = True
    
    meta_data = Column(JSON, nullable=True, default=dict)
    tags = Column(JSON, nullable=True, default=list)
    version = Column(Integer, nullable=False, default=1)
    version_history = Column(JSON, nullable=True, default=list)
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update metadata with versioning."""
        if not self.meta_data:
            self.meta_data = {}
        
        old_value = self.meta_data.get(key)
        if old_value != value:
            self.meta_data[key] = value
            self.version += 1
            
            if not self.version_history:
                self.version_history = []
            
            self.version_history.append({
                "version": self.version,
                "changed_at": datetime.utcnow().isoformat(),
                "key": key,
                "old_value": old_value,
                "new_value": value
            })
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the model."""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the model."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "meta_data": self.meta_data,
            "tags": self.tags,
            "version": self.version,
            "version_history": self.version_history
        }

class AuditableModel(BaseModel):
    """Base model with audit trail support."""
    __abstract__ = True
    
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    audit_trail = Column(JSON, nullable=True, default=list)
    last_audit_at = Column(DateTime, nullable=True)
    audit_status = Column(String, nullable=True)
    # PE-specific tracking
    safety_incidents = Column(JSON, nullable=True, default=list)
    equipment_usage = Column(JSON, nullable=True, default=list)
    student_interactions = Column(JSON, nullable=True, default=list)
    performance_records = Column(JSON, nullable=True, default=list)
    
    def add_safety_incident(self, incident_type: str, description: str, severity: str, reporter: str) -> None:
        """Record a safety incident."""
        if not self.safety_incidents:
            self.safety_incidents = []
        
        self.safety_incidents.append({
            "type": incident_type,
            "description": description,
            "severity": severity,
            "reporter": reporter,
            "reported_at": datetime.utcnow().isoformat()
        })
    
    def track_equipment_usage(self, equipment_id: int, activity_type: str, duration: int, user: str) -> None:
        """Track equipment usage."""
        if not self.equipment_usage:
            self.equipment_usage = []
        
        self.equipment_usage.append({
            "equipment_id": equipment_id,
            "activity_type": activity_type,
            "duration": duration,
            "user": user,
            "used_at": datetime.utcnow().isoformat()
        })
    
    def record_student_interaction(self, student_id: int, interaction_type: str, notes: str, teacher: str) -> None:
        """Record a student interaction."""
        if not self.student_interactions:
            self.student_interactions = []
        
        self.student_interactions.append({
            "student_id": student_id,
            "interaction_type": interaction_type,
            "notes": notes,
            "teacher": teacher,
            "recorded_at": datetime.utcnow().isoformat()
        })
    
    def record_performance(self, activity_type: str, metrics: Dict[str, Any], evaluator: str) -> None:
        """Record performance metrics."""
        if not self.performance_records:
            self.performance_records = []
        
        self.performance_records.append({
            "activity_type": activity_type,
            "metrics": metrics,
            "evaluator": evaluator,
            "recorded_at": datetime.utcnow().isoformat()
        })
    
    def get_safety_summary(self) -> Dict[str, Any]:
        """Get summary of safety incidents."""
        if not self.safety_incidents:
            return {"total": 0, "by_severity": {}, "by_type": {}}
        
        summary = {
            "total": len(self.safety_incidents),
            "by_severity": {},
            "by_type": {}
        }
        
        for incident in self.safety_incidents:
            severity = incident["severity"]
            incident_type = incident["type"]
            
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            summary["by_type"][incident_type] = summary["by_type"].get(incident_type, 0) + 1
        
        return summary
    
    def get_equipment_usage_summary(self) -> Dict[str, Any]:
        """Get summary of equipment usage."""
        if not self.equipment_usage:
            return {"total_usage": 0, "by_equipment": {}, "by_activity": {}}
        
        summary = {
            "total_usage": len(self.equipment_usage),
            "by_equipment": {},
            "by_activity": {}
        }
        
        for usage in self.equipment_usage:
            equipment_id = usage["equipment_id"]
            activity_type = usage["activity_type"]
            duration = usage["duration"]
            
            if equipment_id not in summary["by_equipment"]:
                summary["by_equipment"][equipment_id] = {"count": 0, "total_duration": 0}
            summary["by_equipment"][equipment_id]["count"] += 1
            summary["by_equipment"][equipment_id]["total_duration"] += duration
            
            if activity_type not in summary["by_activity"]:
                summary["by_activity"][activity_type] = {"count": 0, "total_duration": 0}
            summary["by_activity"][activity_type]["count"] += 1
            summary["by_activity"][activity_type]["total_duration"] += duration
        
        return summary
    
    def get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends over time."""
        if not self.performance_records:
            return {"total_records": 0, "by_activity": {}, "trends": {}}
        
        trends = {
            "total_records": len(self.performance_records),
            "by_activity": {},
            "trends": {}
        }
        
        for record in self.performance_records:
            activity_type = record["activity_type"]
            metrics = record["metrics"]
            
            if activity_type not in trends["by_activity"]:
                trends["by_activity"][activity_type] = {
                    "count": 0,
                    "metrics": {}
                }
            
            trends["by_activity"][activity_type]["count"] += 1
            
            for metric_name, value in metrics.items():
                if metric_name not in trends["by_activity"][activity_type]["metrics"]:
                    trends["by_activity"][activity_type]["metrics"][metric_name] = []
                trends["by_activity"][activity_type]["metrics"][metric_name].append(value)
        
        # Calculate trends
        for activity_type, data in trends["by_activity"].items():
            trends["trends"][activity_type] = {}
            for metric_name, values in data["metrics"].items():
                if len(values) > 1:
                    trends["trends"][activity_type][metric_name] = {
                        "start": values[0],
                        "end": values[-1],
                        "change": values[-1] - values[0],
                        "change_percent": ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
                    }
        
        return trends
    
    def add_audit_entry(self, action: str, user: str, details: Dict[str, Any]) -> None:
        """Add an audit trail entry."""
        if not self.audit_trail:
            self.audit_trail = []
        
        self.audit_trail.append({
            "action": action,
            "user": user,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        self.last_audit_at = datetime.utcnow()
    
    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            **super().dict(),
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "audit_trail": self.audit_trail,
            "last_audit_at": self.last_audit_at.isoformat() if self.last_audit_at else None,
            "audit_status": self.audit_status,
            "safety_incidents": self.safety_incidents,
            "equipment_usage": self.equipment_usage,
            "student_interactions": self.student_interactions,
            "performance_records": self.performance_records
        }

# Re-export for backward compatibility
__all__ = ['BaseModel', 'AuditableModel', 'NamedMixin', 'StatusMixin', 'MetadataMixin', 'TimestampedMixin'] 