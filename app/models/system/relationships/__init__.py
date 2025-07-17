"""
Relationship Models

This module exports relationship setup functions.
"""

from app.models.system.relationships.relationships import setup_activity_relationships, setup_student_relationships, setup_safety_relationships, setup_security_relationships, setup_security_rule_relationships, setup_security_audit_relationships, setup_security_incident_relationships

__all__ = ['setup_activity_relationships', 'setup_student_relationships', 'setup_safety_relationships', 'setup_security_relationships', 'setup_security_rule_relationships', 'setup_security_audit_relationships', 'setup_security_incident_relationships'] 