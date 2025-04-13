import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from app.services.notification_service import NotificationService

@pytest.fixture
def mock_streak_info():
    """Fixture for streak information."""
    return {
        "current_streak": 7,
        "tier": 2,
        "tier_name": "Silver",
        "recovery_multiplier": 1.0,
        "daily_bonus": 150,
        "email": "user@example.com",
        "phone_number": "+1234567890"
    }

@pytest.fixture
def notification_service():
    """Fixture for notification service with mocked dependencies."""
    with patch("app.services.notification_service.get_twilio_service") as mock_twilio, \
         patch("app.services.notification_service.get_email_service") as mock_email:
        
        # Configure mock services
        mock_twilio.return_value = Mock()
        mock_twilio.return_value.send_sms.return_value = {"status": "success"}
        
        mock_email.return_value = Mock()
        mock_email.return_value.send_email.return_value = {"status": "success"}
        
        service = NotificationService()
        yield service

class TestNotificationService:
    async def test_streak_notification(self, notification_service, mock_streak_info):
        """Test sending streak milestone notifications."""
        result = await notification_service.send_streak_notification(
            user_id="test_user",
            streak_info=mock_streak_info
        )
        
        assert result["status"] == "success"
        assert len(result["notifications"]) == 2  # Both SMS and email
        assert all(n["status"] == "success" for n in result["notifications"])
        
    async def test_tier_promotion_notification(self, notification_service, mock_streak_info):
        """Test sending tier promotion notifications."""
        result = await notification_service.send_tier_promotion_notification(
            user_id="test_user",
            streak_info=mock_streak_info
        )
        
        assert result["status"] == "success"
        assert any(n["type"] == "email" for n in result["notifications"])
        assert any(n["type"] == "sms" for n in result["notifications"])
        
    async def test_recovery_notification(self, notification_service, mock_streak_info):
        """Test sending recovery completion notifications."""
        mock_streak_info["recovery_bonus"] = 200
        
        result = await notification_service.send_recovery_notification(
            user_id="test_user",
            streak_info=mock_streak_info
        )
        
        assert result["status"] == "success"
        assert len(result["notifications"]) == 2
        
    def test_streak_message_generation(self, notification_service, mock_streak_info):
        """Test streak message content generation."""
        message = notification_service._generate_streak_message(mock_streak_info)
        
        assert str(mock_streak_info["current_streak"]) in message
        assert mock_streak_info["tier_name"] in message
        assert str(mock_streak_info["daily_bonus"]) in message
        
    def test_tier_message_generation(self, notification_service, mock_streak_info):
        """Test tier promotion message content generation."""
        message = notification_service._generate_tier_message(mock_streak_info)
        
        assert mock_streak_info["tier_name"] in message
        assert str(mock_streak_info["current_streak"]) in message
        assert str(mock_streak_info["recovery_multiplier"]) in message
        
    @pytest.mark.parametrize("notification_type", ["email", "sms", "both"])
    async def test_notification_types(
        self,
        notification_service,
        mock_streak_info,
        notification_type
    ):
        """Test different notification type combinations."""
        result = await notification_service.send_streak_notification(
            user_id="test_user",
            streak_info=mock_streak_info,
            notification_type=notification_type
        )
        
        assert result["status"] == "success"
        if notification_type == "both":
            assert len(result["notifications"]) == 2
        else:
            assert len(result["notifications"]) == 1
            assert result["notifications"][0]["type"] == notification_type
            
    async def test_error_handling(self, notification_service, mock_streak_info):
        """Test error handling in notification sending."""
        # Simulate service failure
        notification_service.twilio_service.send_sms.side_effect = Exception("SMS service error")
        
        result = await notification_service.send_streak_notification(
            user_id="test_user",
            streak_info=mock_streak_info
        )
        
        assert result["status"] == "error"
        assert "error" in result 
