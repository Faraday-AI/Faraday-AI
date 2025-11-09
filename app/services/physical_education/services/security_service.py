from typing import Dict, Any, Optional, Union
from datetime import datetime
import logging
import html
import re
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Request

from app.core.database import get_db
from app.core.config import settings
from app.models.core.user import User
from app.models.user_management.user.user_management import Role
from app.models.security.access_control.access_control_management import AccessControlRole, UserRole
from app.models.security.event.security_event import SecurityEvent

# Try to import bleach, fallback to basic sanitization if not available
try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False

class SecurityService:
    """Service for handling security-related operations in physical education."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.access_levels = ["student", "teacher", "admin", "health_staff"]
    
    async def validate_access(
        self,
        user_id: Union[str, int],
        required_level: str,
        db: Session = Depends(get_db)
    ) -> bool:
        """Validate if a user has the required access level."""
        try:
            if required_level not in self.access_levels:
                self.logger.warning(f"Invalid access level '{required_level}'. Must be one of: {self.access_levels}")
                return False
            
            # Convert user_id to int if string
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
            
            # Query user from database
            user = db.query(User).filter(User.id == user_id_int).first()
            if not user:
                self.logger.warning(f"User {user_id_int} not found")
                return False
            
            # Check if user is active
            if not user.is_active:
                self.logger.warning(f"User {user_id_int} is not active")
                return False
            
            # Check 1: User.role column (direct role assignment)
            if user.role:
                user_role_lower = user.role.lower()
                required_level_lower = required_level.lower()
                
                # Map role column values to access levels
                role_mapping = {
                    "student": "student",
                    "teacher": "teacher",
                    "admin": "admin",
                    "super_admin": "admin",
                    "health_staff": "health_staff",
                    "staff": "teacher"  # Staff typically has teacher-level access
                }
                
                mapped_role = role_mapping.get(user_role_lower, user_role_lower)
                if mapped_role == required_level_lower:
                    return True
                
                # Admin has access to everything
                if mapped_role == "admin":
                    return True
            
            # Check 2: AccessControlRole relationships (UserRole table)
            user_roles = db.query(UserRole).filter(
                UserRole.user_id == user_id_int,
                UserRole.is_active == True
            ).all()
            
            for user_role in user_roles:
                role = db.query(AccessControlRole).filter(
                    AccessControlRole.id == user_role.role_id,
                    AccessControlRole.is_active == True
                ).first()
                
                if role:
                    role_name_lower = role.name.lower() if role.name else ""
                    required_level_lower = required_level.lower()
                    
                    # Check if role name matches required level
                    if role_name_lower == required_level_lower:
                        return True
                    
                    # Admin roles have access to everything
                    if "admin" in role_name_lower:
                        return True
            
            # Check 3: Roles relationship (many-to-many through user_roles table)
            if user.roles:
                for role in user.roles:
                    if role.name:
                        role_name_lower = role.name.lower()
                        required_level_lower = required_level.lower()
                        
                        # Map role names to access levels
                        role_mapping = {
                            "student": "student",
                            "teacher": "teacher",
                            "admin": "admin",
                            "super_admin": "admin",
                            "health_staff": "health_staff",
                            "staff": "teacher"
                        }
                        
                        mapped_role = role_mapping.get(role_name_lower, role_name_lower)
                        if mapped_role == required_level_lower:
                            return True
                        
                        # Admin has access to everything
                        if "admin" in role_name_lower:
                            return True
            
            # Check 4: Superuser always has access
            if user.is_superuser:
                return True
            
            # No matching role found
            self.logger.debug(f"User {user_id_int} does not have required level '{required_level}'")
            return False
            
        except ValueError as ve:
            self.logger.error(f"Invalid user_id format: {str(ve)}")
            return False
        except Exception as e:
            self.logger.error(f"Error validating access: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False
    
    async def log_security_event(
        self,
        event_type: str,
        user_id: Optional[Union[str, int]] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: Optional[str] = None,
        severity: str = "info",
        description: Optional[str] = None,
        success: str = "unknown",
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Log a security-related event to the database."""
        try:
            # Convert user_id to int if string
            user_id_int = None
            if user_id:
                try:
                    user_id_int = int(user_id) if isinstance(user_id, str) else user_id
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid user_id format: {user_id}")
            
            # Convert details dict to JSON-serializable format (handle UUIDs, dates, etc.)
            serializable_details = {}
            if details:
                import json
                from uuid import UUID
                from datetime import datetime, date
                
                def make_serializable(obj):
                    """Convert non-serializable objects to strings."""
                    if isinstance(obj, UUID):
                        return str(obj)
                    elif isinstance(obj, (datetime, date)):
                        return obj.isoformat()
                    elif isinstance(obj, dict):
                        return {k: make_serializable(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [make_serializable(item) for item in obj]
                    else:
                        return obj
                
                serializable_details = make_serializable(details)
            
            # Create security event record
            security_event = SecurityEvent(
                event_type=event_type,
                user_id=user_id_int,
                ip_address=ip_address,
                details=serializable_details if serializable_details else None,
                description=description,
                severity=severity.lower(),
                resource_type=resource_type,
                resource_id=resource_id,
                action=action,
                success=success.lower()
            )
            
            db.add(security_event)
            db.commit()
            db.refresh(security_event)
            
            # Also log to application logger
            self.logger.info(
                f"Security event logged: {event_type} by user {user_id_int} "
                f"(IP: {ip_address}, Severity: {severity})"
            )
            
            return {
                "success": True,
                "message": "Security event logged",
                "event_id": security_event.id,
                "timestamp": security_event.created_at.isoformat() if security_event.created_at else datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error logging security event: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "message": f"Error logging security event: {str(e)}"
            }
    
    async def check_rate_limit(
        self,
        user_id: str,
        action_type: str,
        db: Session = Depends(get_db)
    ) -> bool:
        """Check if a user has exceeded their rate limit for an action."""
        try:
            # TODO: Implement actual rate limiting
            # For now, return True for development
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {str(e)}")
            return False
    
    async def validate_request(
        self,
        request_data: Dict[str, Any],
        expected_fields: list,
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Validate incoming request data."""
        try:
            missing_fields = [field for field in expected_fields if field not in request_data]
            if missing_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required fields: {missing_fields}"
                )
            
            return {
                "success": True,
                "message": "Request validation successful",
                "data": request_data
            }
            
        except HTTPException as he:
            raise he
        except Exception as e:
            self.logger.error(f"Error validating request: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error validating request: {str(e)}"
            )
    
    async def sanitize_input(
        self,
        input_data: Any,
        input_type: str = "string",
        db: Session = Depends(get_db)
    ) -> Any:
        """Sanitize input data based on type to prevent XSS, SQL injection, and other attacks."""
        try:
            if input_data is None:
                return None
            
            # SQL injection patterns to detect
            sql_injection_patterns = [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|SCRIPT)\b)",
                r"(--|/\*|\*/|;|\|)",
                r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
                r"(\b(OR|AND)\s+['\"]\w+['\"]\s*=\s*['\"]\w+['\"])",
                r"(\b(OR|AND)\s+\d+\s*=\s*\d+\s*--)",
            ]
            
            # Handle different input types - check input_type parameter first
            # Note: Check boolean before integer because True/False are ints in Python
            if input_type.lower() == "boolean" or isinstance(input_data, bool):
                # Validate boolean input
                if isinstance(input_data, bool):
                    return input_data
                if isinstance(input_data, str):
                    lower_val = input_data.lower()
                    # Return True for truthy strings, False for falsy strings
                    if lower_val in ("true", "1", "yes", "on"):
                        return True
                    elif lower_val in ("false", "0", "no", "off"):
                        return False
                    # For other strings, convert to bool
                    return bool(input_data)
                return bool(input_data)
            
            elif input_type.lower() == "integer" or isinstance(input_data, int):
                # Validate integer input
                try:
                    # Convert to int if it's a string
                    if isinstance(input_data, str):
                        value = int(input_data)
                    else:
                        value = int(input_data)
                    # Check for reasonable bounds (prevent integer overflow attacks)
                    if abs(value) > 2**31 - 1:  # PostgreSQL INTEGER max
                        self.logger.warning(f"Integer value too large: {value}")
                        return None
                    return value
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid integer input: {input_data}")
                    return None
            
            elif input_type.lower() == "string" or isinstance(input_data, str):
                # Convert to string if not already
                sanitized = str(input_data)
                
                # Check for SQL injection patterns
                for pattern in sql_injection_patterns:
                    if re.search(pattern, sanitized, re.IGNORECASE):
                        self.logger.warning(f"Potential SQL injection detected: {sanitized[:100]}")
                        # Remove dangerous patterns
                        sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
                
                # HTML/XSS sanitization - strip HTML tags but preserve text content
                if BLEACH_AVAILABLE:
                    # Use bleach to strip HTML tags but keep text content
                    # Note: 'styles' parameter not supported in all bleach versions
                    sanitized = bleach.clean(
                        sanitized,
                        tags=[],  # No HTML tags allowed
                        attributes={},
                        strip=True,  # Strip tags but keep text
                        strip_comments=True
                    )
                else:
                    # Fallback: Remove HTML tags manually but keep text
                    # Remove HTML tags using regex - this preserves text content
                    sanitized = re.sub(r'<[^>]+>', '', sanitized)
                    # Don't escape - we've already removed HTML tags, just keep text as-is
                    # Escaping would convert & to &amp; which is unnecessary after tag removal
                
                # Remove null bytes and other dangerous characters
                sanitized = sanitized.replace('\x00', '')
                sanitized = sanitized.replace('\r', '')
                # Trim whitespace
                sanitized = sanitized.strip()
                
                return sanitized
            
            elif input_type.lower() == "float" or isinstance(input_data, float):
                # Validate float input
                try:
                    value = float(input_data)
                    # Check for reasonable bounds
                    if abs(value) > 1e308:  # Very large float
                        self.logger.warning(f"Float value too large: {value}")
                        return None
                    return value
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid float input: {input_data}")
                    return None
            
            
            elif isinstance(input_data, dict):
                # Recursively sanitize dictionary values
                sanitized_dict = {}
                for key, value in input_data.items():
                    # Sanitize key
                    sanitized_key = await self.sanitize_input(key, "string", db)
                    # Sanitize value (try to infer type)
                    if isinstance(value, str):
                        sanitized_value = await self.sanitize_input(value, "string", db)
                    elif isinstance(value, (int, float)):
                        sanitized_value = await self.sanitize_input(value, input_type, db)
                    elif isinstance(value, dict):
                        sanitized_value = await self.sanitize_input(value, "dict", db)
                    elif isinstance(value, list):
                        sanitized_value = await self.sanitize_input(value, "list", db)
                    else:
                        sanitized_value = value
                    sanitized_dict[sanitized_key] = sanitized_value
                return sanitized_dict
            
            elif isinstance(input_data, list):
                # Recursively sanitize list items
                sanitized_list = []
                for item in input_data:
                    if isinstance(item, str):
                        sanitized_item = await self.sanitize_input(item, "string", db)
                    elif isinstance(item, dict):
                        sanitized_item = await self.sanitize_input(item, "dict", db)
                    elif isinstance(item, list):
                        sanitized_item = await self.sanitize_input(item, "list", db)
                    else:
                        sanitized_item = item
                    sanitized_list.append(sanitized_item)
                return sanitized_list
            
            else:
                # For other types, return as-is (but log if suspicious)
                if isinstance(input_data, str):
                    # If it's a string but wasn't caught above, sanitize it
                    return await self.sanitize_input(input_data, "string", db)
                return input_data
                
        except Exception as e:
            self.logger.error(f"Error sanitizing input: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            # Return empty string on error for strings, None for others (fail safely)
            if input_type.lower() == "string" or isinstance(input_data, str):
                return ""
            return None