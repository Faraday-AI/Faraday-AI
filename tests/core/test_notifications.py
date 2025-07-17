"""
Tests for notification services.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import json
import asyncio
import time

from app.core.notifications import (
    EmailNotifier,
    SlackNotifier,
    WebhookNotifier,
    NotificationService,
    BatchingEmailNotifier,
    NotificationHistory
)
from app.core.templates import template_manager
from app.core.priority import NotificationPriority

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
def mock_settings():
    """Create mock settings."""
    with patch('app.core.notifications.settings') as mock:
        mock.SMTP_HOST = 'smtp.example.com'
        mock.SMTP_PORT = 587
        mock.SMTP_USERNAME = 'user'
        mock.SMTP_PASSWORD = 'pass'
        mock.SMTP_USE_TLS = True
        mock.SMTP_FROM_EMAIL = 'alerts@example.com'
        mock.SLACK_DEFAULT_WEBHOOK = 'https://hooks.slack.com/services/xxx'
        mock.EMAIL_BATCH_SIZE = 100
        mock.EMAIL_BATCH_WAIT = 60
        yield mock

@pytest.fixture
def email_notifier(mock_settings):
    """Create email notifier instance."""
    return EmailNotifier()

@pytest.fixture
def slack_notifier(mock_settings):
    """Create slack notifier instance."""
    return SlackNotifier()

@pytest.fixture
def webhook_notifier():
    """Create webhook notifier instance."""
    return WebhookNotifier()

@pytest.fixture
def notification_service(mock_settings):
    """Create notification service instance."""
    return NotificationService()

@pytest.fixture
def notification_history():
    """Create notification history instance."""
    return NotificationHistory(max_size=5)

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

@pytest.mark.asyncio
class TestEmailNotifier:
    """Test cases for EmailNotifier."""
    
    async def test_send_email_success(self, email_notifier):
        """Test successful email sending."""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            success = await email_notifier.send(
                to_email='test@example.com',
                subject='Test Alert',
                body='Test message',
                html_body='<p>Test message</p>'
            )
            
            assert success
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with('user', 'pass')
            mock_server.send_message.assert_called_once()
            
    async def test_send_email_failure(self, email_notifier):
        """Test email sending failure."""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.return_value.__enter__.side_effect = Exception('SMTP error')
            
            success = await email_notifier.send(
                to_email='test@example.com',
                subject='Test Alert',
                body='Test message'
            )
            
            assert not success

@pytest.mark.asyncio
class TestSlackNotifier:
    """Test cases for SlackNotifier."""
    
    async def test_send_slack_success(self, slack_notifier):
        """Test successful Slack message sending."""
        mock_response = Mock()
        mock_response.status = 200
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            success = await slack_notifier.send(
                message='Test alert',
                channel='#alerts',
                username='TestBot',
                icon_emoji=':warning:'
            )
            
            assert success
            mock_post.assert_called_once()
            
            # Verify payload
            call_kwargs = mock_post.call_args.kwargs
            payload = json.loads(call_kwargs['json'])
            assert payload['text'] == 'Test alert'
            assert payload['channel'] == '#alerts'
            assert payload['username'] == 'TestBot'
            assert payload['icon_emoji'] == ':warning:'
            
    async def test_send_slack_failure(self, slack_notifier):
        """Test Slack message sending failure."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = Exception('Network error')
            
            success = await slack_notifier.send(message='Test alert')
            assert not success
            
    async def test_send_slack_no_webhook(self, slack_notifier):
        """Test Slack sending with no webhook URL."""
        with patch('app.core.notifications.settings') as mock_settings:
            mock_settings.SLACK_DEFAULT_WEBHOOK = None
            
            success = await slack_notifier.send(message='Test alert')
            assert not success

@pytest.mark.asyncio
class TestWebhookNotifier:
    """Test cases for WebhookNotifier."""
    
    async def test_send_webhook_success(self, webhook_notifier):
        """Test successful webhook sending."""
        mock_response = Mock()
        mock_response.status = 200
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            
            success = await webhook_notifier.send(
                url='https://example.com/webhook',
                payload={'message': 'Test alert'},
                headers={'X-Custom': 'value'}
            )
            
            assert success
            mock_request.assert_called_once()
            
            # Verify request
            call_args = mock_request.call_args
            assert call_args.args[0] == 'POST'  # method
            assert call_args.args[1] == 'https://example.com/webhook'  # url
            assert 'X-Custom' in call_args.kwargs['headers']
            
    async def test_send_webhook_failure(self, webhook_notifier):
        """Test webhook sending failure."""
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_request.side_effect = Exception('Network error')
            
            success = await webhook_notifier.send(
                url='https://example.com/webhook',
                payload={'message': 'Test alert'}
            )
            assert not success
            
    async def test_send_webhook_no_url(self, webhook_notifier):
        """Test webhook sending with no URL."""
        success = await webhook_notifier.send(
            url='',
            payload={'message': 'Test alert'}
        )
        assert not success

@pytest.mark.asyncio
class TestNotificationService:
    """Test cases for NotificationService."""
    
    async def test_send_alert_all_channels(self, notification_service):
        """Test sending alert through all channels."""
        # Mock individual notifiers
        with patch.object(notification_service.email, 'send', new_callable=AsyncMock) as mock_email, \
             patch.object(notification_service.slack, 'send', new_callable=AsyncMock) as mock_slack, \
             patch.object(notification_service.webhook, 'send', new_callable=AsyncMock) as mock_webhook:
            
            mock_email.return_value = True
            mock_slack.return_value = True
            mock_webhook.return_value = True
            
            results = await notification_service.send_alert(
                alert_type='LOAD',
                severity='warning',
                message='High load detected',
                details={'load': 95.5},
                notification_config=[
                    {'type': 'email', 'to': 'admin@example.com'},
                    {'type': 'slack', 'channel': '#alerts'},
                    {'type': 'webhook', 'url': 'https://example.com/webhook'}
                ]
            )
            
            assert results == {
                'email': 'sent',
                'slack': 'sent',
                'webhook': 'sent'
            }
            
            mock_email.assert_called_once()
            mock_slack.assert_called_once()
            mock_webhook.assert_called_once()
            
    async def test_send_alert_partial_failure(self, notification_service):
        """Test sending alert with some channels failing."""
        # Mock individual notifiers
        with patch.object(notification_service.email, 'send', new_callable=AsyncMock) as mock_email, \
             patch.object(notification_service.slack, 'send', new_callable=AsyncMock) as mock_slack:
            
            mock_email.return_value = True
            mock_slack.side_effect = Exception('Network error')
            
            results = await notification_service.send_alert(
                alert_type='ERROR',
                severity='critical',
                message='Service down',
                details={'error': 'Connection refused'},
                notification_config=[
                    {'type': 'email', 'to': 'admin@example.com'},
                    {'type': 'slack', 'channel': '#alerts'}
                ]
            )
            
            assert results == {
                'email': 'sent',
                'slack': 'failed'
            }
            
    async def test_send_alert_formatting(self, notification_service):
        """Test alert message formatting."""
        with patch.object(notification_service.email, 'send', new_callable=AsyncMock) as mock_email:
            mock_email.return_value = True
            
            await notification_service.send_alert(
                alert_type='LATENCY',
                severity='warning',
                message='High latency detected',
                details={'latency': 500},
                notification_config=[
                    {'type': 'email', 'to': 'admin@example.com'}
                ]
            )
            
            # Verify email formatting
            call_args = mock_email.call_args
            assert '[WARNING] LATENCY Alert' in call_args.kwargs['subject']
            assert 'High latency detected' in call_args.kwargs['body']
            assert 'latency' in call_args.kwargs['body']
            assert '<h2>Alert:' in call_args.kwargs['html_body'] 

@pytest.mark.asyncio
class TestRateLimiting:
    """Test cases for rate limiting functionality."""
    
    async def test_email_rate_limiting(self, email_notifier):
        """Test email rate limiting."""
        # Send emails up to the rate limit
        for i in range(settings.SMTP_RATE_LIMIT):
            success = await email_notifier.send(
                to_email='test@example.com',
                subject=f'Test {i}',
                body='Test message'
            )
            assert success
            
        # Next email should be rate limited
        success = await email_notifier.send(
            to_email='test@example.com',
            subject='Rate Limited',
            body='Test message'
        )
        assert not success
        
    async def test_slack_rate_limiting(self, slack_notifier):
        """Test Slack rate limiting."""
        # Send messages up to the rate limit
        for i in range(settings.SLACK_RATE_LIMIT):
            success = await slack_notifier.send(
                message=f'Test {i}',
                channel='#test'
            )
            assert success
            
        # Next message should be rate limited
        success = await slack_notifier.send(
            message='Rate Limited',
            channel='#test'
        )
        assert not success
        
    async def test_webhook_rate_limiting(self, webhook_notifier):
        """Test webhook rate limiting."""
        # Send webhooks up to the rate limit
        for i in range(settings.WEBHOOK_RATE_LIMIT):
            success = await webhook_notifier.send(
                url='https://example.com/webhook',
                payload={'message': f'Test {i}'}
            )
            assert success
            
        # Next webhook should be rate limited
        success = await webhook_notifier.send(
            url='https://example.com/webhook',
            payload={'message': 'Rate Limited'}
        )
        assert not success
        
    async def test_rate_limit_reset(self, email_notifier):
        """Test rate limit window reset."""
        # Send emails up to the rate limit
        for i in range(settings.SMTP_RATE_LIMIT):
            success = await email_notifier.send(
                to_email='test@example.com',
                subject=f'Test {i}',
                body='Test message'
            )
            assert success
            
        # Wait for rate limit window to expire
        await asyncio.sleep(settings.SMTP_RATE_WINDOW)
        
        # Should be able to send again
        success = await email_notifier.send(
            to_email='test@example.com',
            subject='After Reset',
            body='Test message'
        )
        assert success
        
    async def test_different_recipients(self, email_notifier):
        """Test rate limiting with different recipients."""
        # Send to first recipient
        for i in range(settings.SMTP_RATE_LIMIT):
            success = await email_notifier.send(
                to_email='test1@example.com',
                subject=f'Test {i}',
                body='Test message'
            )
            assert success
            
        # Should still be able to send to different recipient
        success = await email_notifier.send(
            to_email='test2@example.com',
            subject='Different Recipient',
            body='Test message'
        )
        assert success 

@pytest.mark.asyncio
class TestEmailBatching:
    """Test cases for email batching functionality."""
    
    async def test_batch_collection(self, mock_settings):
        """Test collecting emails into a batch."""
        notifier = BatchingEmailNotifier()
        
        # Add emails to batch
        for i in range(5):
            success = await notifier.send(
                to_email=f'test{i}@example.com',
                subject=f'Test {i}',
                body='Test message',
                immediate=False
            )
            assert success
            
        # Verify batch contents
        assert len(notifier.batch.batch) == 5
        assert all(email['subject'].startswith('Test') for email in notifier.batch.batch)
        
    async def test_immediate_send(self, mock_settings):
        """Test immediate send bypassing batch."""
        notifier = BatchingEmailNotifier()
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # Send immediate email
            success = await notifier.send(
                to_email='test@example.com',
                subject='Immediate Test',
                body='Test message',
                immediate=True
            )
            
            assert success
            assert len(notifier.batch.batch) == 0  # Should not be in batch
            mock_server.send_message.assert_called_once()
            
    async def test_batch_size_trigger(self, mock_settings):
        """Test sending batch when size limit reached."""
        notifier = BatchingEmailNotifier()
        await notifier.start()
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # Fill batch to limit
            for i in range(settings.EMAIL_BATCH_SIZE):
                await notifier.send(
                    to_email=f'test{i}@example.com',
                    subject=f'Test {i}',
                    body='Test message'
                )
                
            # Wait for batch processing
            await asyncio.sleep(1.1)
            
            # Verify batch was sent
            assert len(notifier.batch.batch) == 0
            mock_server.send_message.assert_called_once()
            
        await notifier.stop()
        
    async def test_batch_time_trigger(self, mock_settings):
        """Test sending batch when time limit reached."""
        notifier = BatchingEmailNotifier()
        await notifier.start()
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # Add a few emails
            for i in range(3):
                await notifier.send(
                    to_email=f'test{i}@example.com',
                    subject=f'Test {i}',
                    body='Test message'
                )
                
            # Wait for time limit
            await asyncio.sleep(settings.EMAIL_BATCH_WAIT + 0.1)
            
            # Verify batch was sent
            assert len(notifier.batch.batch) == 0
            mock_server.send_message.assert_called_once()
            
        await notifier.stop()
        
    async def test_batch_error_handling(self, mock_settings):
        """Test error handling in batch processing."""
        notifier = BatchingEmailNotifier()
        await notifier.start()
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.return_value.__enter__.side_effect = Exception('SMTP error')
            
            # Add emails to batch
            for i in range(3):
                await notifier.send(
                    to_email=f'test{i}@example.com',
                    subject=f'Test {i}',
                    body='Test message'
                )
                
            # Wait for batch processing
            await asyncio.sleep(settings.EMAIL_BATCH_WAIT + 0.1)
            
            # Verify batch was cleared despite error
            assert len(notifier.batch.batch) == 0
            
        await notifier.stop() 

@pytest.mark.asyncio
class TestNotificationTemplates:
    """Test cases for notification templates."""
    
    async def test_email_template(self, email_notifier):
        """Test email with template."""
        template_data = {
            'message': 'Test Alert',
            'severity': 'warning',
            'alert_type': 'load',
            'timestamp': datetime.utcnow().isoformat(),
            'details': {'load': 95.5},
            'recommendations': ['Scale up resources', 'Check for bottlenecks']
        }
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            success = await email_notifier.send(
                to_email='test@example.com',
                subject='Template Test',
                body='placeholder',  # Will be replaced by template
                template_name='alert',
                template_data=template_data
            )
            
            assert success
            # Verify template was used
            call_args = mock_server.send_message.call_args
            message = call_args[0][0]
            assert 'Test Alert' in str(message)
            assert 'Scale up resources' in str(message)
            
    async def test_slack_template(self, slack_notifier):
        """Test Slack with template."""
        template_data = {
            'message': 'Test Alert',
            'severity': 'warning',
            'alert_type': 'load',
            'timestamp': datetime.utcnow().isoformat(),
            'details': {'load': 95.5},
            'recommendations': ['Scale up resources']
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = Mock()
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response
            
            success = await slack_notifier.send(
                message='placeholder',  # Will be replaced by template
                template_name='alert',
                template_data=template_data
            )
            
            assert success
            # Verify template was used
            call_args = mock_post.call_args
            payload = json.loads(call_args.kwargs['json'])
            assert 'Test Alert' in payload['text']
            assert 'Scale up resources' in payload['text']
            
    def test_template_error_handling(self):
        """Test template error handling."""
        # Test with non-existent template
        result = template_manager.render(
            'nonexistent',
            {'data': 'test'},
            'plain'
        )
        assert json.loads(result)['data'] == 'test'  # Fallback to JSON
        
        # Test with invalid template data
        result = template_manager.render(
            'alert',
            {'invalid': 'data'},
            'plain'
        )
        assert 'invalid' in result  # Basic formatting used

@pytest.mark.asyncio
class TestNotificationPriority:
    """Test cases for notification priority functionality."""
    
    async def test_email_priority(self, email_notifier):
        """Test email priority levels."""
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # Test urgent priority
            success = await email_notifier.send(
                to_email='test@example.com',
                subject='Urgent Test',
                body='Test message',
                priority=NotificationPriority.URGENT
            )
            
            assert success
            # Verify priority header
            call_args = mock_server.send_message.call_args
            message = call_args[0][0]
            assert message['X-Priority'] == '1'  # Urgent
            
    async def test_slack_priority(self, slack_notifier):
        """Test Slack priority indicators."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = Mock()
            mock_response.status = 200
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Test high priority
            success = await slack_notifier.send(
                message='High priority test',
                priority=NotificationPriority.HIGH
            )
            
            assert success
            # Verify priority indicator
            call_args = mock_post.call_args
            payload = json.loads(call_args.kwargs['json'])
            assert '⚠️' in payload['text']
            
    async def test_retry_behavior(self, email_notifier):
        """Test retry behavior for different priorities."""
        with patch('smtplib.SMTP') as mock_smtp:
            # Fail first attempts
            mock_smtp.return_value.__enter__.side_effect = [
                Exception("First attempt"),
                Exception("Second attempt"),
                Mock()  # Succeed on third try
            ]
            
            # Test with high priority (3 retries)
            start_time = time.time()
            success = await email_notifier.send(
                to_email='test@example.com',
                subject='Retry Test',
                body='Test message',
                priority=NotificationPriority.HIGH
            )
            
            duration = time.time() - start_time
            assert success
            assert duration >= NotificationPriority.RETRY_CONFIG[NotificationPriority.HIGH]['delay'] * 2
            
    async def test_priority_rate_limiting(self, email_notifier):
        """Test rate limiting with different priorities."""
        # Fill up rate limit
        for i in range(settings.SMTP_RATE_LIMIT):
            success = await email_notifier.send(
                to_email='test@example.com',
                subject=f'Test {i}',
                body='Test message',
                priority=NotificationPriority.LOW
            )
            assert success
            
        # Even urgent priority should be rate limited
        success = await email_notifier.send(
            to_email='test@example.com',
            subject='Urgent Test',
            body='Test message',
            priority=NotificationPriority.URGENT
        )
        assert not success 

@pytest.mark.asyncio
class TestNotificationHistory:
    """Test cases for notification history functionality."""
    
    async def test_add_and_get_recent(self):
        """Test adding and retrieving recent notifications."""
        history = NotificationHistory(max_size=5)
        
        # Add notifications
        for i in range(3):
            await history.add({
                'message': f'Test {i}',
                'alert_type': 'test',
                'severity': 'normal'
            })
            
        # Get recent
        recent = await history.get_recent(minutes=5)
        assert len(recent) == 3
        assert all(n['alert_type'] == 'test' for n in recent)
        
    async def test_max_size_limit(self):
        """Test max size limiting."""
        history = NotificationHistory(max_size=2)
        
        # Add more than max
        for i in range(4):
            await history.add({'message': f'Test {i}'})
            
        # Should only keep latest 2
        recent = await history.get_recent()
        assert len(recent) == 2
        assert recent[-1]['message'] == 'Test 3'
        
    async def test_duplicate_detection(self):
        """Test duplicate notification detection."""
        history = NotificationHistory()
        
        # Add notification
        await history.add({
            'message': 'Test Alert',
            'alert_type': 'test'
        })
        
        # Check for duplicate
        is_duplicate = await history.is_duplicate('Test Alert', 'test')
        assert is_duplicate
        
        # Different message shouldn't be duplicate
        is_duplicate = await history.is_duplicate('Different Alert', 'test')
        assert not is_duplicate
        
    async def test_digest_generation(self):
        """Test notification digest generation."""
        history = NotificationHistory()
        start_time = datetime.utcnow() - timedelta(hours=2)
        
        # Add notifications
        notifications = [
            {
                'message': 'Urgent Alert',
                'alert_type': 'error',
                'severity': 'urgent',
                'details': {'error': 'Critical failure'}
            },
            {
                'message': 'Warning Alert',
                'alert_type': 'performance',
                'severity': 'warning',
                'details': {'latency': 500}
            }
        ]
        
        for n in notifications:
            await history.add(n)
            
        # Get digest
        digest = await history.get_digest(start_time=start_time)
        
        assert len(digest['notifications']) == 2
        assert 'error' in digest['notification_counts']
        assert 'performance' in digest['notification_counts']
        
    async def test_clear_old(self):
        """Test clearing old notifications."""
        history = NotificationHistory()
        
        # Add old notification
        old_time = datetime.utcnow() - timedelta(days=10)
        await history.add({
            'message': 'Old Alert',
            'timestamp': old_time.isoformat()
        })
        
        # Add recent notification
        await history.add({
            'message': 'Recent Alert'
        })
        
        # Clear old
        await history.clear_old(days=7)
        
        # Should only have recent
        recent = await history.get_recent()
        assert len(recent) == 1
        assert recent[0]['message'] == 'Recent Alert'

@pytest.mark.asyncio
class TestDigestNotifications:
    """Test cases for notification digests."""
    
    async def test_send_digest(self, notification_service, mock_settings):
        """Test sending notification digest."""
        # Add some notifications to history
        for severity in ['urgent', 'high', 'normal']:
            await notification_history.add({
                'message': f'{severity.title()} Alert',
                'alert_type': 'test',
                'severity': severity,
                'details': {'test': 'data'}
            })
            
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            # Send digest
            results = await notification_service.send_digest([
                {'type': 'email', 'to': 'test@example.com'}
            ])
            
            assert results['email'] == 'sent'
            # Verify digest content
            call_args = mock_server.send_message.call_args
            message = call_args[0][0]
            content = str(message)
            assert 'Notification Digest' in content
            assert 'Urgent Alert' in content
            assert 'High Alert' in content
            assert 'Normal Alert' in content
            
    async def test_digest_filtering(self):
        """Test digest time range filtering."""
        history = NotificationHistory()
        
        # Add old notification
        old_time = datetime.utcnow() - timedelta(days=2)
        await history.add({
            'message': 'Old Alert',
            'timestamp': old_time.isoformat()
        })
        
        # Add recent notification
        await history.add({
            'message': 'Recent Alert'
        })
        
        # Get digest for last day
        start_time = datetime.utcnow() - timedelta(days=1)
        digest = await history.get_digest(start_time=start_time)
        
        assert len(digest['notifications']) == 1
        assert digest['notifications'][0]['message'] == 'Recent Alert'
