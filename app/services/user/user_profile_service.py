"""
User Profile Service

This module provides comprehensive user profile management functionality
including CRUD operations, profile picture management, and privacy settings.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, UploadFile, Depends
import os
import uuid
from pathlib import Path

from app.models.core.user import User
from app.models.user_management.user.user_management import UserProfile
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate, UserProfileResponse
from app.db.session import get_db


class UserProfileService:
    """Service for managing user profiles."""
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path("uploads/profiles")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by user ID."""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    async def create_user_profile(self, user_id: int, profile_data: UserProfileCreate) -> UserProfile:
        """Create a new user profile."""
        # Check if profile already exists
        existing_profile = await self.get_user_profile(user_id)
        if existing_profile:
            raise HTTPException(status_code=400, detail="User profile already exists")
        
        # Create new profile
        profile = UserProfile(
            user_id=user_id,
            bio=profile_data.bio,
            timezone=profile_data.timezone or "UTC",
            language=profile_data.language or "en",
            notification_preferences=profile_data.notification_preferences or {},
            custom_settings=profile_data.custom_settings or {}
        )
        
        try:
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to create user profile")
    
    async def update_user_profile(self, user_id: int, profile_data: UserProfileUpdate) -> UserProfile:
        """Update user profile."""
        profile = await self.get_user_profile(user_id)
        if not profile:
            # Create profile if it doesn't exist
            return await self.create_user_profile(user_id, UserProfileCreate(**profile_data.dict()))
        
        # Update profile fields
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        profile.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update user profile")
    
    async def delete_user_profile(self, user_id: int) -> bool:
        """Delete user profile."""
        profile = await self.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        try:
            self.db.delete(profile)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to delete user profile")
    
    async def upload_profile_picture(self, user_id: int, file: UploadFile) -> str:
        """Upload and store profile picture."""
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed")
        
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if file.size and file.size > max_size:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB")
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix if file.filename else ".jpg"
        filename = f"profile_{user_id}_{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / filename
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
        # Update profile with new avatar URL
        profile = await self.get_user_profile(user_id)
        if not profile:
            # Create basic profile if it doesn't exist
            profile = await self.create_user_profile(
                user_id, 
                UserProfileCreate(
                    bio="",
                    timezone="UTC",
                    language="en"
                )
            )
        
        # Store the file path in custom_settings
        if not profile.custom_settings:
            profile.custom_settings = {}
        profile.custom_settings["avatar_url"] = str(file_path)
        profile.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return str(file_path)
        except IntegrityError:
            self.db.rollback()
            # Clean up uploaded file
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=400, detail="Failed to update profile with avatar")
    
    async def remove_profile_picture(self, user_id: int) -> bool:
        """Remove profile picture."""
        profile = await self.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Remove avatar file if it exists
        if profile.custom_settings and "avatar_url" in profile.custom_settings:
            avatar_path = Path(profile.custom_settings["avatar_url"])
            if avatar_path.exists():
                try:
                    avatar_path.unlink()
                except Exception:
                    pass  # Continue even if file deletion fails
        
        # Remove avatar reference from profile
        if profile.custom_settings:
            profile.custom_settings.pop("avatar_url", None)
        profile.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to remove profile picture")
    
    async def update_privacy_settings(self, user_id: int, privacy_settings: Dict[str, Any]) -> UserProfile:
        """Update user privacy settings."""
        profile = await self.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Update privacy settings
        if not profile.custom_settings:
            profile.custom_settings = {}
        profile.custom_settings["privacy"] = privacy_settings
        profile.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update privacy settings")
    
    async def get_privacy_settings(self, user_id: int) -> Dict[str, Any]:
        """Get user privacy settings."""
        profile = await self.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return profile.custom_settings.get("privacy", {}) if profile.custom_settings else {}
    
    async def verify_profile(self, user_id: int, verification_data: Dict[str, Any]) -> UserProfile:
        """Verify user profile with additional information."""
        profile = await self.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Update verification status
        if not profile.custom_settings:
            profile.custom_settings = {}
        profile.custom_settings["verification"] = {
            "verified": True,
            "verified_at": datetime.utcnow().isoformat(),
            "verification_data": verification_data
        }
        profile.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(profile)
            return profile
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to verify profile")
    
    async def get_profile_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user profile by email."""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        return await self.get_user_profile(user.id)
    
    async def search_profiles(self, query: str, limit: int = 10) -> List[UserProfile]:
        """Search user profiles by name or bio."""
        return (
            self.db.query(UserProfile)
            .join(User, UserProfile.user_id == User.id)
            .filter(
                (User.first_name.ilike(f"%{query}%")) |
                (User.last_name.ilike(f"%{query}%")) |
                (UserProfile.bio.ilike(f"%{query}%"))
            )
            .limit(limit)
            .all()
        )


def get_user_profile_service(db: Session = Depends(get_db)) -> UserProfileService:
    """Dependency to get user profile service."""
    return UserProfileService(db) 