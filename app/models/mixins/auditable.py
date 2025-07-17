"""
Auditable Mixin

This module provides audit trail functionality for models.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON

class AuditableModel:
    """Mixin for models that need audit trail functionality."""
    
    __abstract__ = True
    
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    deleted_by = Column(String, nullable=True)
    audit_trail = Column(JSON, nullable=True)
    
    def add_audit_entry(self, action: str, user_id: str, details: dict = None) -> None:
        """Add an entry to the audit trail."""
        if not self.audit_trail:
            self.audit_trail = []
            
        entry = {
            "action": action,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        self.audit_trail.append(entry)
    
    def record_creation(self, user_id: str) -> None:
        """Record creation in audit trail."""
        self.created_by = user_id
        self.add_audit_entry("create", user_id)
    
    def record_update(self, user_id: str, details: dict = None) -> None:
        """Record update in audit trail."""
        self.updated_by = user_id
        self.add_audit_entry("update", user_id, details)
    
    def record_deletion(self, user_id: str, details: dict = None) -> None:
        """Record deletion in audit trail."""
        self.deleted_by = user_id
        self.add_audit_entry("delete", user_id, details) 