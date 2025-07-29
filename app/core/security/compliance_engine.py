"""Compliance engine for data classification and security management."""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db

class DataClassification(str, Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    CLASSIFIED = "classified"

class ComplianceEngine:
    """Engine for managing data compliance and security."""
    
    def __init__(self, db: Session = None):
        self.logger = logging.getLogger("compliance_engine")
        self.db = db
        
    async def classify_data(self, data: Dict[str, Any]) -> DataClassification:
        """Classify data based on content and context."""
        try:
            # Simple classification logic
            if self._contains_sensitive_info(data):
                return DataClassification.CONFIDENTIAL
            elif self._contains_internal_info(data):
                return DataClassification.INTERNAL
            else:
                return DataClassification.PUBLIC
        except Exception as e:
            self.logger.error(f"Error classifying data: {str(e)}")
            return DataClassification.INTERNAL  # Default to internal for safety
    
    def _contains_sensitive_info(self, data: Dict[str, Any]) -> bool:
        """Check if data contains sensitive information."""
        sensitive_keywords = [
            "password", "secret", "private", "confidential", 
            "ssn", "credit_card", "bank_account", "medical"
        ]
        
        data_str = str(data).lower()
        return any(keyword in data_str for keyword in sensitive_keywords)
    
    def _contains_internal_info(self, data: Dict[str, Any]) -> bool:
        """Check if data contains internal information."""
        internal_keywords = [
            "internal", "employee", "staff", "company", 
            "business", "proprietary", "trade_secret"
        ]
        
        data_str = str(data).lower()
        return any(keyword in data_str for keyword in internal_keywords)
    
    async def validate_compliance(self, data: Dict[str, Any], classification: DataClassification) -> Dict[str, Any]:
        """Validate data compliance with security policies."""
        try:
            validation_result = {
                "compliant": True,
                "warnings": [],
                "errors": [],
                "recommendations": []
            }
            
            # Check data classification
            if classification == DataClassification.CONFIDENTIAL:
                if not self._has_encryption(data):
                    validation_result["warnings"].append("Confidential data should be encrypted")
                
                if not self._has_access_controls(data):
                    validation_result["warnings"].append("Confidential data should have access controls")
            
            # Check for sensitive data patterns
            if self._contains_sensitive_info(data):
                validation_result["recommendations"].append("Consider reclassifying as confidential")
            
            # Check data retention
            if not self._has_retention_policy(data):
                validation_result["warnings"].append("Data should have a retention policy")
            
            return validation_result
        except Exception as e:
            self.logger.error(f"Error validating compliance: {str(e)}")
            return {
                "compliant": False,
                "warnings": [],
                "errors": [f"Validation error: {str(e)}"],
                "recommendations": []
            }
    
    def _has_encryption(self, data: Dict[str, Any]) -> bool:
        """Check if data has encryption indicators."""
        # Mock implementation
        return data.get("encrypted", False)
    
    def _has_access_controls(self, data: Dict[str, Any]) -> bool:
        """Check if data has access control indicators."""
        # Mock implementation
        return data.get("access_controlled", False)
    
    def _has_retention_policy(self, data: Dict[str, Any]) -> bool:
        """Check if data has retention policy indicators."""
        # Mock implementation
        return data.get("retention_policy", False)
    
    async def audit_data_access(self, user_id: str, data_id: str, action: str) -> Dict[str, Any]:
        """Audit data access for compliance tracking."""
        try:
            audit_record = {
                "user_id": user_id,
                "data_id": data_id,
                "action": action,
                "timestamp": datetime.now().isoformat(),
                "classification": DataClassification.INTERNAL,
                "compliant": True
            }
            
            # Log audit record
            self.logger.info(f"Data access audit: {audit_record}")
            
            return audit_record
        except Exception as e:
            self.logger.error(f"Error auditing data access: {str(e)}")
            raise
    
    async def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report for the specified period."""
        try:
            # Mock report generation
            report = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "summary": {
                    "total_accesses": 150,
                    "compliant_accesses": 145,
                    "non_compliant_accesses": 5,
                    "compliance_rate": 96.7
                },
                "classifications": {
                    "public": 50,
                    "internal": 80,
                    "confidential": 15,
                    "restricted": 5
                },
                "recommendations": [
                    "Implement additional encryption for confidential data",
                    "Review access controls for restricted data",
                    "Update retention policies for internal data"
                ]
            }
            
            return report
        except Exception as e:
            self.logger.error(f"Error generating compliance report: {str(e)}")
            raise 