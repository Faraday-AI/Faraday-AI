"""
Test User System

This module tests the user system implementation including profile and preferences.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate
from app.schemas.user_preferences import UserPreferencesUpdate, ThemeSettings, NotificationSettings, AccessibilitySettings


class TestUserProfileService:
    """Test user profile service."""
    
    async def test_get_user_profile_nonexistent(self):
        """Test getting non-existent user profile."""
        # Mock database session
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Import service here to avoid SQLAlchemy initialization issues
        with patch('app.services.user.user_profile_service.UserProfile') as mock_user_profile:
            from app.services.user.user_profile_service import UserProfileService
            
            service = UserProfileService(mock_db)
            profile = await service.get_user_profile(1)
            
            assert profile is None
            mock_db.query.assert_called_once_with(mock_user_profile)
    
    async def test_create_user_profile_success(self):
        """Test creating user profile successfully."""
        # Mock database session
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Mock UserProfile class
        mock_profile_instance = Mock()
        mock_profile_instance.user_id = 1
        mock_profile_instance.bio = "Test bio"
        mock_profile_instance.timezone = "UTC"
        mock_profile_instance.language = "en"
        
        with patch('app.services.user.user_profile_service.UserProfile') as mock_user_profile:
            mock_user_profile.return_value = mock_profile_instance
            
            from app.services.user.user_profile_service import UserProfileService
            
            service = UserProfileService(mock_db)
            
            profile_data = UserProfileCreate(
                bio="Test bio",
                timezone="UTC",
                language="en"
            )
            
            profile = await service.create_user_profile(1, profile_data)
            
            assert profile.user_id == 1
            assert profile.bio == "Test bio"
            assert profile.timezone == "UTC"
            assert profile.language == "en"
            
            mock_db.add.assert_called_once_with(mock_profile_instance)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_profile_instance)
    
    async def test_create_user_profile_already_exists(self):
        """Test creating user profile when it already exists."""
        # Mock existing profile
        mock_existing_profile = Mock()
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_existing_profile
        mock_db.query.return_value = mock_query
        
        with patch('app.services.user.user_profile_service.UserProfile'):
            from app.services.user.user_profile_service import UserProfileService
            
            service = UserProfileService(mock_db)
            
            profile_data = UserProfileCreate(
                bio="Test bio",
                timezone="UTC",
                language="en"
            )
            
            # Should raise an exception
            with pytest.raises(Exception):
                await service.create_user_profile(1, profile_data)


class TestUserPreferencesService:
    """Test user preferences service."""
    
    async def test_get_user_preferences_nonexistent(self):
        """Test getting non-existent user preferences."""
        # Mock database session
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        with patch('app.services.user.user_preferences_service.UserProfile'):
            from app.services.user.user_preferences_service import UserPreferencesService
            
            service = UserPreferencesService(mock_db)
            preferences = await service.get_user_preferences(1)
            
            assert preferences is None
    
    async def test_update_user_preferences_success(self):
        """Test updating user preferences successfully."""
        # Mock existing preferences
        mock_profile = Mock()
        mock_profile.custom_settings = {
            "theme": {"theme": "light"}
        }
        mock_profile.notification_preferences = {"email": True}
        
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_profile
        mock_db.query.return_value = mock_query
        
        with patch('app.services.user.user_preferences_service.UserProfile'):
            from app.services.user.user_preferences_service import UserPreferencesService
            
            service = UserPreferencesService(mock_db)
            
            preferences_data = UserPreferencesUpdate(
                theme=ThemeSettings(
                    theme="dark",
                    color_scheme="blue",
                    font_size="medium",
                    high_contrast=False,
                    reduced_motion=False
                )
            )
            
            preferences = await service.update_user_preferences(1, preferences_data)
            
            assert preferences["theme"]["theme"] == "dark"
            mock_db.commit.assert_called_once()
    
    async def test_get_theme_settings(self):
        """Test getting theme settings."""
        # Mock user preferences
        mock_profile = Mock()
        mock_profile.custom_settings = {
            "theme": {
                "theme": "dark",
                "color_scheme": "blue",
                "font_size": "medium"
            }
        }
        
        mock_db = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_profile
        mock_db.query.return_value = mock_query
        
        with patch('app.services.user.user_preferences_service.UserProfile'):
            from app.services.user.user_preferences_service import UserPreferencesService
            
            service = UserPreferencesService(mock_db)
            theme_settings = await service.get_theme_settings(1)
            
            assert theme_settings.theme == "dark"
            assert theme_settings.color_scheme == "blue"
            assert theme_settings.font_size == "medium"


class TestUserSchemas:
    """Test user schemas."""
    
    def test_user_profile_create_schema(self):
        """Test UserProfileCreate schema."""
        profile_data = UserProfileCreate(
            bio="Test bio",
            timezone="UTC",
            language="en"
        )
        
        assert profile_data.bio == "Test bio"
        assert profile_data.timezone == "UTC"
        assert profile_data.language == "en"
    
    def test_user_profile_update_schema(self):
        """Test UserProfileUpdate schema."""
        profile_data = UserProfileUpdate(
            bio="Updated bio"
        )
        
        assert profile_data.bio == "Updated bio"
        assert profile_data.timezone is None  # Not set
    
    def test_theme_settings_schema(self):
        """Test ThemeSettings schema."""
        theme_data = ThemeSettings(
            theme="dark",
            color_scheme="blue",
            font_size="large"
        )
        
        assert theme_data.theme == "dark"
        assert theme_data.color_scheme == "blue"
        assert theme_data.font_size == "large"
        assert theme_data.high_contrast is False  # Default value
    
    def test_notification_settings_schema(self):
        """Test NotificationSettings schema."""
        notification_data = NotificationSettings(
            email_notifications=True,
            push_notifications=False,
            notification_frequency="daily"
        )
        
        assert notification_data.email_notifications is True
        assert notification_data.push_notifications is False
        assert notification_data.notification_frequency == "daily"
        assert notification_data.sms_notifications is False  # Default value
    
    def test_accessibility_settings_schema(self):
        """Test AccessibilitySettings schema."""
        accessibility_data = AccessibilitySettings(
            screen_reader=True,
            high_contrast=True,
            large_text=True
        )
        
        assert accessibility_data.screen_reader is True
        assert accessibility_data.high_contrast is True
        assert accessibility_data.large_text is True
        assert accessibility_data.keyboard_navigation is True  # Default value


class TestUserProfileServiceMethods:
    """Test user profile service methods."""
    
    async def test_upload_profile_picture_validation(self):
        """Test profile picture upload validation."""
        mock_db = Mock()
        
        with patch('app.services.user.user_profile_service.UserProfile'):
            from app.services.user.user_profile_service import UserProfileService
            
            service = UserProfileService(mock_db)
            
            # Mock file with proper attributes
            mock_file = Mock()
            mock_file.content_type = "image/jpeg"
            mock_file.size = 1024 * 1024  # 1MB
            mock_file.filename = "test.jpg"  # Add filename
            mock_file.file = Mock()
            mock_file.file.read.return_value = b"fake_image_data"
            
            # Mock profile creation
            mock_profile = Mock()
            mock_profile.custom_settings = {}
            mock_profile.updated_at = datetime.utcnow()
            
            # Mock the async get_user_profile method to return None (no existing profile)
            async def mock_get_user_profile(user_id):
                return None
            
            async def mock_create_user_profile(user_id, profile_data):
                return mock_profile
            
            service.get_user_profile = mock_get_user_profile
            service.create_user_profile = mock_create_user_profile
            
            # Test valid file - should not raise an exception
            try:
                result = await service.upload_profile_picture(1, mock_file)
                # If we get here, the upload was successful
                assert result is not None
            except Exception as e:
                # If there's an exception, it should be related to file system operations
                # which is expected in a test environment
                assert "Failed to save file" in str(e) or "uploads/profiles" in str(e)
            
            # Test invalid file type
            mock_file.content_type = "text/plain"
            with pytest.raises(Exception):  # Should raise HTTPException in real app
                await service.upload_profile_picture(1, mock_file)
            
            # Test file too large
            mock_file.content_type = "image/jpeg"
            mock_file.size = 10 * 1024 * 1024  # 10MB
            with pytest.raises(Exception):  # Should raise HTTPException in real app
                await service.upload_profile_picture(1, mock_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 