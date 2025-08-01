"""
Notification Services

This module provides notification implementations for:
- Email notifications using SMTP
- Slack notifications using webhooks
- Generic webhook notifications
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
import json
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram
import asyncio
from collections import defaultdict
import jinja2
import os
from pathlib import Path

from app.core.config import get_settings

# Prometheus metrics
NOTIFICATION_SENT = Counter('notification_sent_total', 'Number of notifications sent', ['channel', 'status'])
NOTIFICATION_LATENCY = Histogram('notification_latency_seconds', 'Notification sending latency', ['channel'])
NOTIFICATION_RATE_LIMITED = Counter('notification_rate_limited_total', 'Number of rate limited notifications', ['channel'])

logger = logging.getLogger(__name__)
settings = get_settings()

class NotificationTemplate:
    """Template manager for notifications."""
    
    def __init__(self):
        self.template_dir = Path(settings.TEMPLATE_DIR) / 'notifications'
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
        
    def render(
        self,
        template_name: str,
        data: Dict[str, Any],
        format_type: str = 'plain'
    ) -> str:
        """
        Render a notification template.
        
        Args:
            template_name: Name of the template file
            data: Template variables
            format_type: Type of template (plain/html/slack)
            
        Returns:
            str: Rendered template
        """
        try:
            template = self.env.get_template(f"{template_name}.{format_type}.j2")
            return template.render(**data)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            # Fallback to basic formatting
            if format_type == 'html':
                return f"<pre>{json.dumps(data, indent=2)}</pre>"
            return json.dumps(data, indent=2)

# Initialize template manager
template_manager = NotificationTemplate()

class NotificationPriority:
    """Priority levels for notifications."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    
    # Retry settings per priority
    RETRY_CONFIG = {
        LOW: {"max_retries": 1, "delay": 300},  # 5 minutes
        NORMAL: {"max_retries": 2, "delay": 60},  # 1 minute
        HIGH: {"max_retries": 3, "delay": 30},  # 30 seconds
        URGENT: {"max_retries": 5, "delay": 10}  # 10 seconds
    }
    
    @classmethod
    def get_retry_config(cls, priority: str) -> Dict[str, int]:
        """Get retry configuration for priority level."""
        return cls.RETRY_CONFIG.get(priority, cls.RETRY_CONFIG[cls.NORMAL])

class RateLimiter:
    """Rate limiter for notification services."""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
        
    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed based on rate limits."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.time_window)
        
        # Clean up old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        # Check if we're under the limit
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True
        return False
    
    def is_rate_limited(self, key: str) -> bool:
        """Check if a key is currently rate limited."""
        return not self.is_allowed(key)
    
    def get_remaining_requests(self, key: str) -> int:
        """Get the number of remaining requests for a key."""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.time_window)
        
        # Clean up old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(self.requests[key]))

class NotificationBatch:
    """Batch notifications for efficient sending."""
    
    def __init__(self, max_size: int = 10, max_wait_seconds: float = 5.0):
        self.max_size = max_size
        self.max_wait = max_wait_seconds
        self.batch = []
        self.last_send = datetime.utcnow()
        
    def should_send(self) -> bool:
        """Check if batch should be sent based on size or time."""
        if len(self.batch) >= self.max_size:
            return True
        
        time_since_last = (datetime.utcnow() - self.last_send).total_seconds()
        return time_since_last >= self.max_wait
        
    def add(self, item: dict):
        """Add item to batch."""
        self.batch.append(item)
        
    def clear(self):
        """Clear the batch and update last send time."""
        self.batch = []
        self.last_send = datetime.utcnow()
        
    def get_batch(self) -> list:
        """Get current batch items."""
        return self.batch.copy()

class EmailNotifier:
    """Email notification service using SMTP."""
    
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.use_tls = settings.SMTP_USE_TLS
        self.from_email = settings.SMTP_FROM_EMAIL
        self.rate_limiter = RateLimiter(
            max_requests=settings.SMTP_RATE_LIMIT,
            time_window=settings.SMTP_RATE_WINDOW
        )
        
    async def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        priority: str = NotificationPriority.NORMAL
    ) -> bool:
        """
        Send an email notification.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body (or template name)
            html_body: Optional HTML email body
            template_name: Optional template to use
            template_data: Optional template data
            priority: Notification priority level
            
        Returns:
            bool: Whether the email was sent successfully
        """
        # Check rate limit
        if not self.rate_limiter.is_allowed(to_email):
            NOTIFICATION_RATE_LIMITED.labels(channel='email').inc()
            logger.warning(f"Rate limit exceeded for email: {to_email}")
            return False
            
        try:
            # Use template if provided
            if template_name and template_data:
                body = template_manager.render(template_name, template_data, 'plain')
                if html_body is None:  # Only override if not explicitly provided
                    html_body = template_manager.render(template_name, template_data, 'html')
                    
            with NOTIFICATION_LATENCY.labels(channel='email').time():
                # Create message
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.from_email
                msg['To'] = to_email
                msg['X-Priority'] = str(self._get_priority_header(priority))
                
                # Add plain text body
                msg.attach(MIMEText(body, 'plain'))
                
                # Add HTML body if provided
                if html_body:
                    msg.attach(MIMEText(html_body, 'html'))
                
                # Get retry config
                retry_config = NotificationPriority.get_retry_config(priority)
                success = False
                
                # Try sending with retries
                for attempt in range(retry_config['max_retries']):
                    try:
                        with smtplib.SMTP(self.host, self.port) as server:
                            if self.use_tls:
                                server.starttls()
                            if self.username and self.password:
                                server.login(self.username, self.password)
                            server.send_message(msg)
                            success = True
                            break
                    except Exception as e:
                        logger.warning(f"Email attempt {attempt + 1} failed: {e}")
                        if attempt < retry_config['max_retries'] - 1:
                            await asyncio.sleep(retry_config['delay'])
                            
                if success:
                    NOTIFICATION_SENT.labels(channel='email', status='success').inc()
                else:
                    NOTIFICATION_SENT.labels(channel='email', status='error').inc()
                return success
                
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            NOTIFICATION_SENT.labels(channel='email', status='error').inc()
            return False
            
    def _get_priority_header(self, priority: str) -> int:
        """Convert priority to email header value."""
        priority_map = {
            NotificationPriority.LOW: 5,
            NotificationPriority.NORMAL: 3,
            NotificationPriority.HIGH: 2,
            NotificationPriority.URGENT: 1
        }
        return priority_map.get(priority, 3)

class BatchingEmailNotifier(EmailNotifier):
    """Email notifier with batching support."""
    
    def __init__(self):
        super().__init__()
        self.batch = NotificationBatch(
            max_size=settings.EMAIL_BATCH_SIZE,
            max_wait_seconds=settings.EMAIL_BATCH_WAIT
        )
        self._batch_task = None
        
    async def start(self):
        """Start the background batch processing task."""
        if not self._batch_task:
            self._batch_task = asyncio.create_task(self._process_batch())
            
    async def stop(self):
        """Stop the background batch processing task."""
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
            self._batch_task = None
            
    async def _process_batch(self):
        """Process batched emails periodically."""
        while True:
            try:
                if self.batch.should_send() and self.batch.batch:
                    # Create multi-part message
                    msg = MIMEMultipart('mixed')
                    msg['From'] = self.from_email
                    msg['To'] = self.from_email  # BCC will be used for recipients
                    msg['Subject'] = 'Batch Notification'
                    
                    # Process each email in batch
                    for email in self.batch.get_batch():
                        # Add recipient to BCC
                        if 'Bcc' not in msg or msg['Bcc'] is None:
                            msg['Bcc'] = email['to']
                        else:
                            msg['Bcc'] += f", {email['to']}"
                            
                        # Create message part
                        part = MIMEMultipart('alternative')
                        part.attach(MIMEText(email['body'], 'plain'))
                        if email.get('html_body'):
                            part.attach(MIMEText(email['html_body'], 'html'))
                        msg.attach(part)
                    
                    # Send batch
                    try:
                        with smtplib.SMTP(self.host, self.port) as server:
                            if self.use_tls:
                                server.starttls()
                            if self.username and self.password:
                                server.login(self.username, self.password)
                            server.send_message(msg)
                            NOTIFICATION_SENT.labels(channel='email_batch', status='success').inc()
                    except Exception as e:
                        logger.error(f"Failed to send batch email: {e}")
                        NOTIFICATION_SENT.labels(channel='email_batch', status='error').inc()
                    
                    self.batch.clear()
                    
            except Exception as e:
                logger.error(f"Error in batch processing: {e}")
                
            await asyncio.sleep(1)  # Check every second
            
    async def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        immediate: bool = False
    ) -> bool:
        """
        Send an email notification, optionally batching it.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            immediate: Whether to send immediately or batch
            
        Returns:
            bool: Whether the email was sent or queued successfully
        """
        # Check rate limit
        if not self.rate_limiter.is_allowed(to_email):
            NOTIFICATION_RATE_LIMITED.labels(channel='email').inc()
            logger.warning(f"Rate limit exceeded for email: {to_email}")
            return False
            
        if immediate:
            return await super().send(to_email, subject, body, html_body)
            
        try:
            self.batch.add({
                'to': to_email,
                'subject': subject,
                'body': body,
                'html_body': html_body
            })
            return True
        except Exception as e:
            logger.error(f"Failed to queue email notification: {e}")
            return False

class SlackNotifier:
    """Slack notification service using webhooks."""
    
    def __init__(self):
        self.default_webhook = settings.SLACK_DEFAULT_WEBHOOK
        self.timeout = aiohttp.ClientTimeout(total=5)  # 5 seconds timeout
        self.rate_limiter = RateLimiter(
            max_requests=settings.SLACK_RATE_LIMIT,
            time_window=settings.SLACK_RATE_WINDOW
        )
        
    async def send(
        self,
        message: str,
        webhook_url: Optional[str] = None,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        attachments: Optional[list] = None,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None,
        priority: str = NotificationPriority.NORMAL
    ) -> bool:
        """
        Send a Slack notification.
        
        Args:
            message: Message text or template name
            webhook_url: Optional custom webhook URL
            channel: Optional channel override
            username: Optional bot username
            icon_emoji: Optional bot icon emoji
            attachments: Optional message attachments
            template_name: Optional template to use
            template_data: Optional template data
            priority: Notification priority level
            
        Returns:
            bool: Whether the message was sent successfully
        """
        try:
            webhook = webhook_url or self.default_webhook
            if not webhook:
                raise ValueError("No webhook URL provided")
                
            # Check rate limit
            if not self.rate_limiter.is_allowed(webhook):
                NOTIFICATION_RATE_LIMITED.labels(channel='slack').inc()
                logger.warning(f"Rate limit exceeded for Slack webhook: {webhook}")
                return False
                
            # Use template if provided
            if template_name and template_data:
                message = template_manager.render(template_name, template_data, 'slack')
                
            # Add priority indicator
            priority_indicators = {
                NotificationPriority.LOW: "ℹ️",
                NotificationPriority.NORMAL: "📝",
                NotificationPriority.HIGH: "⚠️",
                NotificationPriority.URGENT: "🚨"
            }
            message = f"{priority_indicators.get(priority, '📝')} {message}"
                
            # Prepare payload
            payload = {
                "text": message
            }
            if channel:
                payload["channel"] = channel
            if username:
                payload["username"] = username
            if icon_emoji:
                payload["icon_emoji"] = icon_emoji
            if attachments:
                payload["attachments"] = attachments
                
            # Get retry config
            retry_config = NotificationPriority.get_retry_config(priority)
            success = False
            
            # Try sending with retries
            for attempt in range(retry_config['max_retries']):
                try:
                    async with aiohttp.ClientSession(timeout=self.timeout) as session:
                        with NOTIFICATION_LATENCY.labels(channel='slack').time():
                            async with session.post(webhook, json=payload) as response:
                                success = response.status == 200
                                if success:
                                    break
                except Exception as e:
                    logger.warning(f"Slack attempt {attempt + 1} failed: {e}")
                    if attempt < retry_config['max_retries'] - 1:
                        await asyncio.sleep(retry_config['delay'])
                        
            status = 'success' if success else 'error'
            NOTIFICATION_SENT.labels(channel='slack', status=status).inc()
            return success
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            NOTIFICATION_SENT.labels(channel='slack', status='error').inc()
            return False

class WebhookNotifier:
    """Generic webhook notification service."""
    
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=5)  # 5 seconds timeout
        self.rate_limiter = RateLimiter(
            max_requests=settings.WEBHOOK_RATE_LIMIT,
            time_window=settings.WEBHOOK_RATE_WINDOW
        )
        
    async def send(
        self,
        url: str,
        payload: Dict[str, Any],
        method: str = 'POST',
        headers: Optional[Dict[str, str]] = None,
        verify_ssl: bool = True
    ) -> bool:
        """
        Send a webhook notification.
        
        Args:
            url: Webhook URL
            payload: JSON payload to send
            method: HTTP method to use
            headers: Optional HTTP headers
            verify_ssl: Whether to verify SSL certificates
            
        Returns:
            bool: Whether the notification was sent successfully
        """
        try:
            if not url:
                raise ValueError("No webhook URL provided")
                
            # Check rate limit
            if not self.rate_limiter.is_allowed(url):
                NOTIFICATION_RATE_LIMITED.labels(channel='webhook').inc()
                logger.warning(f"Rate limit exceeded for webhook: {url}")
                return False
                
            # Default headers
            headers = headers or {
                'Content-Type': 'application/json',
                'User-Agent': 'Faraday-LoadBalancer/1.0'
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                with NOTIFICATION_LATENCY.labels(channel='webhook').time():
                    async with session.request(
                        method,
                        url,
                        json=payload,
                        headers=headers,
                        ssl=verify_ssl
                    ) as response:
                        success = 200 <= response.status < 300
                        
            status = 'success' if success else 'error'
            NOTIFICATION_SENT.labels(channel='webhook', status=status).inc()
            return success
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            NOTIFICATION_SENT.labels(channel='webhook', status='error').inc()
            return False

class NotificationHistory:
    """Track recent notifications to prevent duplicates and enable digests."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.notifications = []
        self.lock = asyncio.Lock()
        
    async def add(self, notification: Dict[str, Any]):
        """Add a notification to history."""
        async with self.lock:
            # Use provided timestamp or current time
            timestamp = notification.get('timestamp', datetime.utcnow().isoformat())
            self.notifications.append({
                **notification,
                'timestamp': timestamp
            })
            # Trim if over max size
            if len(self.notifications) > self.max_size:
                self.notifications = self.notifications[-self.max_size:]
                
    async def get_recent(
        self,
        minutes: int = 60,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent notifications with optional filtering."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        async with self.lock:
            filtered = [
                n for n in self.notifications
                if datetime.fromisoformat(n['timestamp']) > cutoff
                and (severity is None or n.get('severity') == severity)
                and (alert_type is None or n.get('alert_type') == alert_type)
            ]
            return filtered
            
    async def is_duplicate(
        self,
        message: str,
        alert_type: str,
        window_minutes: int = 60
    ) -> bool:
        """Check if a similar notification was sent recently."""
        recent = await self.get_recent(minutes=window_minutes, alert_type=alert_type)
        return any(n['message'] == message for n in recent)
        
    async def get_digest(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get notification digest for a time period."""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(days=1)
        if not end_time:
            end_time = datetime.utcnow()
            
        async with self.lock:
            # Filter notifications in time range
            notifications = [
                n for n in self.notifications
                if start_time <= datetime.fromisoformat(n['timestamp']) <= end_time
            ]
            
            # Count by type
            type_counts = {}
            for n in notifications:
                alert_type = n.get('alert_type', 'unknown')
                type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
                
            return {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'notifications': notifications,
                'notification_counts': type_counts
            }
            
    async def clear_old(self, days: int = 7):
        """Clear notifications older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        async with self.lock:
            self.notifications = [
                n for n in self.notifications
                if datetime.fromisoformat(n['timestamp']) > cutoff
            ]

# Initialize global notification history
notification_history = NotificationHistory()

class NotificationService:
    """Combined notification service."""
    
    def __init__(self):
        self.email = EmailNotifier()
        self.slack = SlackNotifier()
        self.webhook = WebhookNotifier()
        
    async def send_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        details: Dict[str, Any],
        notification_config: Dict[str, Any],
        check_duplicates: bool = True
    ) -> Dict[str, str]:
        """
        Send alert through configured channels.
        
        Args:
            alert_type: Type of alert
            severity: Alert severity
            message: Alert message
            details: Alert details
            notification_config: Notification configuration
            check_duplicates: Whether to check for duplicate alerts
            
        Returns:
            Dict[str, str]: Status of each notification channel
        """
        # Check for duplicates if enabled
        if check_duplicates:
            is_duplicate = await notification_history.is_duplicate(message, alert_type)
            if is_duplicate:
                logger.info(f"Skipping duplicate notification: {message}")
                return {'status': 'skipped_duplicate'}
                
        results = {}
        timestamp = datetime.utcnow().isoformat()
        
        # Store notification in history
        await notification_history.add({
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'details': details,
            'timestamp': timestamp
        })
        
        # Format email content
        email_subject = f"[{severity.upper()}] {alert_type} Alert"
        email_body = template_manager.render('alert', {
            'message': message,
            'severity': severity,
            'alert_type': alert_type,
            'timestamp': timestamp,
            'details': details
        }, 'plain')
        
        email_html = template_manager.render('alert', {
            'message': message,
            'severity': severity,
            'alert_type': alert_type,
            'timestamp': timestamp,
            'details': details
        }, 'html')
        
        # Format Slack content
        slack_message = template_manager.render('alert', {
            'message': message,
            'severity': severity,
            'alert_type': alert_type,
            'timestamp': timestamp,
            'details': details
        }, 'slack')
        
        # Send notifications through configured channels
        for channel in notification_config:
            try:
                if channel['type'] == 'email':
                    success = await self.email.send(
                        to_email=channel['to'],
                        subject=email_subject,
                        body=email_body,
                        html_body=email_html,
                        priority=severity
                    )
                    results['email'] = 'sent' if success else 'failed'
                    
                elif channel['type'] == 'slack':
                    success = await self.slack.send(
                        message=slack_message,
                        channel=channel.get('channel'),
                        username=channel.get('username', 'Load Balancer'),
                        icon_emoji=channel.get('icon_emoji', ':warning:'),
                        priority=severity
                    )
                    results['slack'] = 'sent' if success else 'failed'
                    
                elif channel['type'] == 'webhook':
                    payload = {
                        'alert': {
                            'type': alert_type,
                            'severity': severity,
                            'message': message,
                            'timestamp': timestamp,
                            'details': details
                        }
                    }
                    success = await self.webhook.send(
                        url=channel['url'],
                        payload=payload,
                        headers=channel.get('headers'),
                        verify_ssl=channel.get('verify_ssl', True)
                    )
                    results['webhook'] = 'sent' if success else 'failed'
                    
            except Exception as e:
                logger.error(f"Failed to send {channel['type']} notification: {e}")
                results[channel['type']] = 'failed'
                
        return results
        
    async def send_digest(
        self,
        notification_config: Dict[str, Any],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, str]:
        """
        Send notification digest through configured channels.
        
        Args:
            notification_config: Notification configuration
            start_time: Optional start time for digest
            end_time: Optional end time for digest
            
        Returns:
            Dict[str, str]: Status of each notification channel
        """
        # Get digest data
        digest_data = await notification_history.get_digest(start_time, end_time)
        
        results = {}
        
        # Format email content
        email_subject = f"Notification Digest ({digest_data['start_time']} to {digest_data['end_time']})"
        email_body = template_manager.render('digest', digest_data, 'plain')
        email_html = template_manager.render('digest', digest_data, 'html')
        
        # Send digest through configured channels
        for channel in notification_config:
            try:
                if channel['type'] == 'email':
                    success = await self.email.send(
                        to_email=channel['to'],
                        subject=email_subject,
                        body=email_body,
                        html_body=email_html,
                        priority=NotificationPriority.NORMAL
                    )
                    results['email'] = 'sent' if success else 'failed'
                    
            except Exception as e:
                logger.error(f"Failed to send digest to {channel['type']}: {e}")
                results[channel['type']] = 'failed'
                
        return results

# Initialize global notification service
notification_service = NotificationService() 