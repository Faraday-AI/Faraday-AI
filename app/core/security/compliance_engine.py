from typing import Dict, Optional, Any
import jwt
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import hashlib
import logging
from enum import Enum
from .regional_compliance import Region, DataProtectionRegulation, RegionalCompliance

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"

class ComplianceEngine:
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)
        self.logger = logging.getLogger(__name__)
        self.regional_compliance = RegionalCompliance()
        
    async def encrypt_student_data(self, data: Dict[str, Any], classification: DataClassification, region: str = Region.NORTH_AMERICA.value) -> Dict[str, Any]:
        """Encrypts student data according to regional compliance requirements"""
        try:
            # Validate regional compliance before encryption
            compliance_check = self.regional_compliance.validate_compliance(region, data)
            if not compliance_check["valid"]:
                self.logger.error(f"Regional compliance validation failed: {compliance_check}")
                raise ValueError(f"Data does not meet regional compliance requirements: {compliance_check['details']}")

            encrypted_data = {}
            for key, value in data.items():
                if isinstance(value, (str, int, float, bool)):
                    encrypted_value = self.fernet.encrypt(str(value).encode())
                    encrypted_data[key] = {
                        'value': encrypted_value,
                        'classification': classification.value,
                        'encryption_timestamp': datetime.utcnow().isoformat(),
                        'region': region
                    }
            return encrypted_data
        except Exception as e:
            self.logger.error(f"Encryption error: {str(e)}")
            raise

    async def decrypt_student_data(self, encrypted_data: Dict[str, Any], user_role: str, permissions: list, region: str = Region.NORTH_AMERICA.value) -> Dict[str, Any]:
        """Decrypts student data with proper access controls and regional compliance"""
        try:
            decrypted_data = {}
            for key, value_dict in encrypted_data.items():
                if self._check_access_permission(value_dict['classification'], user_role, permissions):
                    decrypted_value = self.fernet.decrypt(value_dict['value']).decode()
                    decrypted_data[key] = decrypted_value
            
            # Validate regional compliance after decryption
            compliance_check = self.regional_compliance.validate_compliance(region, decrypted_data)
            if not compliance_check["valid"]:
                self.logger.error(f"Regional compliance validation failed: {compliance_check}")
                raise ValueError(f"Data does not meet regional compliance requirements: {compliance_check['details']}")
                
            return decrypted_data
        except Exception as e:
            self.logger.error(f"Decryption error: {str(e)}")
            raise

    def _check_access_permission(self, classification: str, user_role: str, permissions: list) -> bool:
        """Validates user permissions for data access"""
        access_matrix = {
            DataClassification.PUBLIC.value: ["student", "teacher", "admin", "parent"],
            DataClassification.INTERNAL.value: ["teacher", "admin"],
            DataClassification.SENSITIVE.value: ["admin"],
            DataClassification.RESTRICTED.value: ["admin"]
        }
        return user_role in access_matrix.get(classification, [])

    async def generate_audit_log(self, user_id: str, action: str, data_accessed: str, region: str = Region.NORTH_AMERICA.value) -> Dict[str, Any]:
        """Creates region-specific compliant audit logs"""
        region_config = self.regional_compliance.get_region_config(region)
        if not region_config:
            raise ValueError(f"Unsupported region: {region}")
            
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'data_accessed': data_accessed,
            'ip_address': None,  # To be filled by the request context
            'success': True,
            'region': region,
            'compliance_requirements': region_config["audit_requirements"]
        }
        return audit_entry

    async def validate_parental_consent(self, student_id: str, feature: str, region: str = Region.NORTH_AMERICA.value) -> bool:
        """Validates if parental consent exists for specific features according to regional requirements"""
        region_config = self.regional_compliance.get_region_config(region)
        if not region_config:
            raise ValueError(f"Unsupported region: {region}")
            
        # Check if parental consent is required for this feature in the region
        if "parental_consent" in region_config["content_restrictions"]["access_controls"]:
            # TODO: Implement region-specific consent validation logic
            return True
        return True

    async def generate_mfa_token(self, user_id: str, region: str = Region.NORTH_AMERICA.value) -> str:
        """Generates Multi-Factor Authentication token with regional compliance"""
        region_config = self.regional_compliance.get_region_config(region)
        if not region_config:
            raise ValueError(f"Unsupported region: {region}")
            
        # TODO: Implement region-specific MFA token generation
        return "temporary_mfa_token"

    async def verify_mfa_token(self, user_id: str, token: str, region: str = Region.NORTH_AMERICA.value) -> bool:
        """Verifies Multi-Factor Authentication token with regional compliance"""
        region_config = self.regional_compliance.get_region_config(region)
        if not region_config:
            raise ValueError(f"Unsupported region: {region}")
            
        # TODO: Implement region-specific MFA token verification
        return True

    async def get_compliance_report(self, region: str = Region.NORTH_AMERICA.value) -> Dict[str, Any]:
        """Gets a comprehensive compliance report for the specified region"""
        return await self.regional_compliance.generate_compliance_report(region) 