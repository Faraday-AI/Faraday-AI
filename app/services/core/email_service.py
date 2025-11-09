import logging
from typing import List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from functools import lru_cache
from pydantic import BaseModel, EmailStr

from app.core.config import get_settings

logger = logging.getLogger(__name__)

class EmailMessage(BaseModel):
    to_email: EmailStr
    subject: str
    body: str
    html_content: Optional[str] = None
    cc: List[EmailStr] = []
    bcc: List[EmailStr] = []

class EmailService:
    def __init__(self):
        self.settings = get_settings()
        self.smtp_server = self.settings.SMTP_HOST
        self.smtp_port = self.settings.SMTP_PORT
        self.smtp_username = self.settings.SMTP_USERNAME
        self.smtp_password = self.settings.SMTP_PASSWORD
        self.from_email = self.settings.SMTP_FROM_EMAIL
        self.is_initialized = False

    def initialize(self) -> None:
        """Initialize the SMTP connection."""
        if not self.is_initialized:
            try:
                self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                self.server.starttls()
                self.server.login(self.smtp_username, self.smtp_password)
                self.is_initialized = True
                logger.info("Email service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize email service: {str(e)}")
                raise

    def send_email(self, message: EmailMessage) -> bool:
        """Send an email using the configured SMTP server."""
        if not self.is_initialized:
            self.initialize()

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.subject
            msg['From'] = self.from_email
            msg['To'] = message.to_email
            
            if message.cc:
                msg['Cc'] = ', '.join(message.cc)
            if message.bcc:
                msg['Bcc'] = ', '.join(message.bcc)

            # Plain text version
            text_part = MIMEText(message.body, 'plain')
            msg.attach(text_part)

            # HTML version (if provided)
            if message.html_content:
                html_part = MIMEText(message.html_content, 'html')
                msg.attach(html_part)

            recipients = [message.to_email] + message.cc + message.bcc
            self.server.sendmail(self.from_email, recipients, msg.as_string())
            
            logger.info(f"Email sent successfully to {message.to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def close(self) -> None:
        """Close the SMTP connection."""
        if self.is_initialized:
            try:
                self.server.quit()
                self.is_initialized = False
                logger.info("Email service connection closed")
            except Exception as e:
                logger.error(f"Error closing email service connection: {str(e)}")

@lru_cache()
def get_email_service() -> EmailService:
    """Get a singleton instance of EmailService."""
    return EmailService() 
