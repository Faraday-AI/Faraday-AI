"""
User Profile API Endpoints

This module provides API endpoints for user profile management.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import (
    require_permission, 
    require_any_permission,
    Permission
)
from app.models.core.user import User
from app.services.user.user_profile_service import UserProfileService, get_user_profile_service
from app.schemas.user_profile import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    UserProfilePrivacySettings,
    UserProfileComplete,
    UserProfileSearchResult,
    UserProfileStats
)

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(require_permission(Permission.VIEW_USER_PROFILES)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Get current user's profile."""
    profile = await profile_service.get_user_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Convert model to response schema with all required fields
    # Get timestamps from the model (should have them from SharedBase/TimestampedMixin)
    created_at = getattr(profile, 'created_at', None)
    updated_at = getattr(profile, 'updated_at', None)
    
    # Fallback to current time if timestamps are missing
    if created_at is None:
        created_at = datetime.utcnow()
    if updated_at is None:
        updated_at = datetime.utcnow()
    
    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        bio=getattr(profile, 'bio', None),
        timezone=getattr(profile, 'timezone', 'UTC'),
        language=getattr(profile, 'language', 'en'),
        notification_preferences=getattr(profile, 'notification_preferences', None) or {},
        custom_settings=getattr(profile, 'custom_settings', None) or {},
        avatar_url=profile.custom_settings.get("avatar_url") if hasattr(profile, 'custom_settings') and profile.custom_settings else None,
        created_at=created_at,
        updated_at=updated_at
    )


@router.post("/profile", response_model=UserProfileResponse)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(require_permission(Permission.CREATE_USER_PROFILES)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Create user profile."""
    profile = await profile_service.create_user_profile(current_user.id, profile_data)
    return profile


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(require_permission(Permission.EDIT_USER_PROFILES)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Update user profile."""
    profile = await profile_service.update_user_profile(current_user.id, profile_data)
    return profile


@router.delete("/profile")
async def delete_user_profile(
    current_user: User = Depends(require_permission(Permission.DELETE_USER_PROFILES)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Delete user profile."""
    success = await profile_service.delete_user_profile(current_user.id)
    return {"message": "Profile deleted successfully"}


@router.post("/profile/avatar", response_model=dict)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission(Permission.UPLOAD_PROFILE_PICTURES)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Upload profile picture."""
    avatar_url = await profile_service.upload_profile_picture(current_user.id, file)
    return {"avatar_url": avatar_url, "message": "Profile picture uploaded successfully"}


@router.delete("/profile/avatar")
async def remove_profile_picture(
    current_user: User = Depends(require_permission(Permission.REMOVE_PROFILE_PICTURES)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Remove profile picture."""
    success = await profile_service.remove_profile_picture(current_user.id)
    return {"message": "Profile picture removed successfully"}


@router.get("/profile/privacy", response_model=UserProfilePrivacySettings)
async def get_privacy_settings(
    current_user: User = Depends(require_permission(Permission.VIEW_USER_PRIVACY)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Get user privacy settings."""
    privacy_settings = await profile_service.get_privacy_settings(current_user.id)
    return UserProfilePrivacySettings(**privacy_settings)


@router.put("/profile/privacy", response_model=UserProfileResponse)
async def update_privacy_settings(
    privacy_settings: UserProfilePrivacySettings,
    current_user: User = Depends(require_permission(Permission.EDIT_USER_PRIVACY)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Update user privacy settings."""
    profile = await profile_service.update_privacy_settings(
        current_user.id, 
        privacy_settings.dict()
    )
    return profile


@router.get("/profile/complete", response_model=UserProfileComplete)
async def get_complete_profile(
    current_user: User = Depends(require_any_permission(Permission.VIEW_USER_PROFILES, Permission.VIEW_USER_PREFERENCES)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Get complete user profile with all settings."""
    profile = await profile_service.get_user_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Build complete profile response
    privacy_settings = await profile_service.get_privacy_settings(current_user.id)
    
    return UserProfileComplete(
        id=profile.id,
        user_id=profile.user_id,
        bio=profile.bio,
        timezone=profile.timezone,
        language=profile.language,
        avatar_url=profile.custom_settings.get("avatar_url") if profile.custom_settings else None,
        privacy_settings=UserProfilePrivacySettings(**privacy_settings),
        notification_settings=UserProfilePrivacySettings(**profile.notification_preferences or {}),
        theme_settings=UserProfilePrivacySettings(**profile.custom_settings.get("theme", {}) if profile.custom_settings else {}),
        accessibility_settings=UserProfilePrivacySettings(**profile.custom_settings.get("accessibility", {}) if profile.custom_settings else {}),
        custom_settings=profile.custom_settings or {},
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )


@router.get("/profile/stats", response_model=UserProfileStats)
async def get_profile_stats(
    current_user: User = Depends(require_permission(Permission.VIEW_USER_PROFILES)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Get user profile statistics."""
    profile = await profile_service.get_user_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Calculate profile completeness
    completeness = 0.0
    if profile.bio:
        completeness += 20.0
    if profile.timezone and profile.timezone != "UTC":
        completeness += 10.0
    if profile.language and profile.language != "en":
        completeness += 10.0
    if profile.custom_settings and profile.custom_settings.get("avatar_url"):
        completeness += 20.0
    if profile.notification_preferences:
        completeness += 20.0
    if profile.custom_settings and profile.custom_settings.get("privacy"):
        completeness += 20.0
    
    # Get verification status
    verification_status = "unverified"
    if profile.custom_settings and profile.custom_settings.get("verification", {}).get("verified"):
        verification_status = "verified"
    
    return UserProfileStats(
        profile_views=profile.custom_settings.get("profile_views", 0) if profile.custom_settings else 0,
        last_profile_view=profile.custom_settings.get("last_profile_view") if profile.custom_settings else None,
        profile_completeness=completeness,
        verification_status=verification_status,
        member_since=current_user.created_at,
        last_activity=current_user.last_login
    )


@router.get("/profiles/search", response_model=List[UserProfileSearchResult])
async def search_profiles(
    query: str,
    limit: int = 10,
    current_user: User = Depends(require_permission(Permission.VIEW_USER_PROFILES)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Search user profiles."""
    profiles = await profile_service.search_profiles(query, limit)
    
    # Convert to search result format
    results = []
    for profile in profiles:
        user = profile.user
        results.append(UserProfileSearchResult(
            id=profile.id,
            user_id=profile.user_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            bio=profile.bio,
            avatar_url=profile.custom_settings.get("avatar_url") if profile.custom_settings else None,
            created_at=profile.created_at
        ))
    
    return results


@router.get("/profiles/{user_id}", response_model=UserProfileResponse)
async def get_user_profile_by_id(
    user_id: int,
    current_user: User = Depends(require_permission(Permission.VIEW_USER_PROFILES)),
    profile_service: UserProfileService = Depends(get_user_profile_service)
):
    """Get user profile by ID (public information only)."""
    profile = await profile_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Check privacy settings
    privacy_settings = await profile_service.get_privacy_settings(user_id)
    if privacy_settings.get("profile_visibility") == "private" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Profile is private")
    
    # Return limited information based on privacy settings
    response_data = {
        "id": profile.id,
        "user_id": profile.user_id,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at
    }
    
    if privacy_settings.get("show_bio", True):
        response_data["bio"] = profile.bio
    
    if privacy_settings.get("show_email", False) or current_user.id == user_id:
        response_data["email"] = profile.user.email
    
    return UserProfileResponse(**response_data)
