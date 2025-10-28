"""
Teacher Registration Service for Beta Version

Handles individual teacher registration, email verification, and account management
without requiring school district integration.
"""

import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext
from jose import JWTError, jwt
import uuid

from app.core.database import get_db
from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TeacherRegistrationService:
    """Service for managing teacher registration and authentication."""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def register_teacher(
        self, 
        email: str, 
        password: str, 
        first_name: str, 
        last_name: str,
        school_name: str = None,
        school_district: str = None,
        teaching_experience_years: int = None,
        grade_levels: List[str] = None,
        specializations: List[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new teacher account.
        
        Args:
            email: Teacher's email address
            password: Plain text password
            first_name: Teacher's first name
            last_name: Teacher's last name
            school_name: Optional school name
            school_district: Optional school district
            teaching_experience_years: Years of teaching experience
            grade_levels: List of grade levels taught
            specializations: List of teaching specializations
            
        Returns:
            Dict containing registration result and verification token
            
        Raises:
            ValueError: If email already exists or validation fails
        """
        try:
            # Check if email already exists
            if await self.check_email_availability(email):
                raise ValueError("Email address is already registered")
            
            # Validate input data
            self._validate_registration_data(email, password, first_name, last_name)
            
            # Hash password
            password_hash = pwd_context.hash(password)
            
            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            verification_expires = datetime.utcnow() + timedelta(hours=24)
            
            # Create teacher record
            teacher_id = str(uuid.uuid4())
            
            insert_query = text("""
                INSERT INTO teacher_registrations (
                    id, email, password_hash, first_name, last_name,
                    school_name, school_district, teaching_experience_years,
                    grade_levels, specializations, verification_token, verification_expires
                ) VALUES (
                    :id, :email, :password_hash, :first_name, :last_name,
                    :school_name, :school_district, :teaching_experience_years,
                    :grade_levels, :specializations, :verification_token, :verification_expires
                )
            """)
            
            self.db.execute(insert_query, {
                'id': teacher_id,
                'email': email.lower().strip(),
                'password_hash': password_hash,
                'first_name': first_name.strip(),
                'last_name': last_name.strip(),
                'school_name': school_name.strip() if school_name else None,
                'school_district': school_district.strip() if school_district else None,
                'teaching_experience_years': teaching_experience_years,
                'grade_levels': grade_levels or [],
                'specializations': specializations or [],
                'verification_token': verification_token,
                'verification_expires': verification_expires
            })
            
            # Create default preferences
            await self._create_default_preferences(teacher_id)
            
            self.db.commit()
            
            self.logger.info(f"Teacher registered successfully: {email}")
            
            return {
                "success": True,
                "teacher_id": teacher_id,
                "email": email,
                "verification_token": verification_token,
                "message": "Registration successful. Please check your email to verify your account."
            }
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error registering teacher {email}: {str(e)}")
            raise
    
    async def verify_email(self, token: str) -> bool:
        """
        Verify teacher email using verification token.
        
        Args:
            token: Email verification token
            
        Returns:
            True if verification successful, False otherwise
        """
        try:
            # Check if token exists and is valid
            query = text("""
                SELECT id, verification_expires 
                FROM teacher_registrations 
                WHERE verification_token = :token 
                AND verification_expires > NOW()
                AND email_verified = FALSE
            """)
            
            result = self.db.execute(query, {'token': token}).fetchone()
            
            if not result:
                return False
            
            teacher_id, expires_at = result
            
            # Update verification status
            update_query = text("""
                UPDATE teacher_registrations 
                SET email_verified = TRUE, 
                    verification_token = NULL,
                    verification_expires = NULL,
                    updated_at = NOW()
                WHERE id = :teacher_id
            """)
            
            self.db.execute(update_query, {'teacher_id': teacher_id})
            self.db.commit()
            
            self.logger.info(f"Email verified successfully for teacher: {teacher_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error verifying email with token {token}: {str(e)}")
            return False
    
    async def resend_verification(self, email: str) -> bool:
        """
        Resend email verification token.
        
        Args:
            email: Teacher's email address
            
        Returns:
            True if token resent successfully, False otherwise
        """
        try:
            # Check if teacher exists and needs verification
            query = text("""
                SELECT id FROM teacher_registrations 
                WHERE email = :email AND email_verified = FALSE
            """)
            
            result = self.db.execute(query, {'email': email.lower().strip()}).fetchone()
            
            if not result:
                return False
            
            teacher_id = result[0]
            
            # Generate new verification token
            verification_token = secrets.token_urlsafe(32)
            verification_expires = datetime.utcnow() + timedelta(hours=24)
            
            # Update verification token
            update_query = text("""
                UPDATE teacher_registrations 
                SET verification_token = :token,
                    verification_expires = :expires,
                    updated_at = NOW()
                WHERE id = :teacher_id
            """)
            
            self.db.execute(update_query, {
                'token': verification_token,
                'expires': verification_expires,
                'teacher_id': teacher_id
            })
            self.db.commit()
            
            self.logger.info(f"Verification token resent for teacher: {email}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error resending verification for {email}: {str(e)}")
            return False
    
    async def check_email_availability(self, email: str) -> bool:
        """
        Check if email address is available for registration.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email is available, False if already registered
        """
        try:
            query = text("""
                SELECT id FROM teacher_registrations 
                WHERE email = :email
            """)
            
            result = self.db.execute(query, {'email': email.lower().strip()}).fetchone()
            return result is None
            
        except Exception as e:
            self.logger.error(f"Error checking email availability for {email}: {str(e)}")
            return False
    
    async def authenticate_teacher(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate teacher with email and password.
        
        Args:
            email: Teacher's email address
            password: Plain text password
            
        Returns:
            Teacher data if authentication successful, None otherwise
        """
        try:
            # Get teacher data
            query = text("""
                SELECT id, email, password_hash, first_name, last_name,
                       email_verified, account_status, last_login
                FROM teacher_registrations 
                WHERE email = :email AND account_status = 'active'
            """)
            
            result = self.db.execute(query, {'email': email.lower().strip()}).fetchone()
            
            if not result:
                return None
            
            (teacher_id, email, password_hash, first_name, last_name, 
             email_verified, account_status, last_login) = result
            
            # Verify password
            if not pwd_context.verify(password, password_hash):
                return None
            
            # Check if email is verified
            if not email_verified:
                return {"error": "Email not verified", "teacher_id": teacher_id}
            
            # Update last login
            update_query = text("""
                UPDATE teacher_registrations 
                SET last_login = NOW(), updated_at = NOW()
                WHERE id = :teacher_id
            """)
            
            self.db.execute(update_query, {'teacher_id': teacher_id})
            self.db.commit()
            
            return {
                "teacher_id": teacher_id,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "email_verified": email_verified,
                "account_status": account_status,
                "last_login": last_login
            }
            
        except Exception as e:
            self.logger.error(f"Error authenticating teacher {email}: {str(e)}")
            return None
    
    async def create_password_reset_token(self, email: str) -> Optional[str]:
        """
        Create password reset token for teacher.
        
        Args:
            email: Teacher's email address
            
        Returns:
            Reset token if successful, None otherwise
        """
        try:
            # Check if teacher exists
            query = text("""
                SELECT id FROM teacher_registrations 
                WHERE email = :email AND account_status = 'active'
            """)
            
            result = self.db.execute(query, {'email': email.lower().strip()}).fetchone()
            
            if not result:
                return None
            
            teacher_id = result[0]
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            # Store reset token
            insert_query = text("""
                INSERT INTO password_reset_tokens (teacher_id, token, expires_at)
                VALUES (:teacher_id, :token, :expires_at)
            """)
            
            self.db.execute(insert_query, {
                'teacher_id': teacher_id,
                'token': reset_token,
                'expires_at': expires_at
            })
            self.db.commit()
            
            return reset_token
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating password reset token for {email}: {str(e)}")
            return None
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset teacher password using reset token.
        
        Args:
            token: Password reset token
            new_password: New plain text password
            
        Returns:
            True if reset successful, False otherwise
        """
        try:
            # Validate new password
            self._validate_password(new_password)
            
            # Check if token is valid
            query = text("""
                SELECT teacher_id FROM password_reset_tokens 
                WHERE token = :token 
                AND expires_at > NOW() 
                AND used = FALSE
            """)
            
            result = self.db.execute(query, {'token': token}).fetchone()
            
            if not result:
                return False
            
            teacher_id = result[0]
            
            # Hash new password
            password_hash = pwd_context.hash(new_password)
            
            # Update password
            update_query = text("""
                UPDATE teacher_registrations 
                SET password_hash = :password_hash, updated_at = NOW()
                WHERE id = :teacher_id
            """)
            
            self.db.execute(update_query, {
                'password_hash': password_hash,
                'teacher_id': teacher_id
            })
            
            # Mark token as used
            mark_used_query = text("""
                UPDATE password_reset_tokens 
                SET used = TRUE 
                WHERE token = :token
            """)
            
            self.db.execute(mark_used_query, {'token': token})
            self.db.commit()
            
            self.logger.info(f"Password reset successfully for teacher: {teacher_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error resetting password with token {token}: {str(e)}")
            return False
    
    def _validate_registration_data(self, email: str, password: str, first_name: str, last_name: str):
        """Validate registration input data."""
        if not email or '@' not in email:
            raise ValueError("Valid email address is required")
        
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not first_name or len(first_name.strip()) < 2:
            raise ValueError("First name must be at least 2 characters long")
        
        if not last_name or len(last_name.strip()) < 2:
            raise ValueError("Last name must be at least 2 characters long")
    
    def _validate_password(self, password: str):
        """Validate password strength."""
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if len(password) > 128:
            raise ValueError("Password must be less than 128 characters long")
    
    async def _create_default_preferences(self, teacher_id: str):
        """Create default preferences for new teacher."""
        try:
            insert_query = text("""
                INSERT INTO teacher_preferences (teacher_id)
                VALUES (:teacher_id)
            """)
            
            self.db.execute(insert_query, {'teacher_id': teacher_id})
            
        except Exception as e:
            self.logger.error(f"Error creating default preferences for teacher {teacher_id}: {str(e)}")
            raise
