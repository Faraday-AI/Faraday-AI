"""
Email Service for Teacher Communications

Handles sending emails for teacher registration, verification, password reset,
and other teacher-related communications for the beta version.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime
import os
from jinja2 import Template

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails to teachers."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@faraday-ai.com")
        self.from_name = os.getenv("FROM_NAME", "Faraday AI")
        
        # Email templates
        self.templates = {
            "verification": self._get_verification_template(),
            "password_reset": self._get_password_reset_template(),
            "welcome": self._get_welcome_template(),
            "beta_announcement": self._get_beta_announcement_template()
        }
    
    async def send_verification_email(self, email: str, name: str, token: str) -> bool:
        """
        Send email verification email to teacher.
        
        Args:
            email: Teacher's email address
            name: Teacher's full name
            token: Verification token
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            subject = "Verify Your Faraday AI Teacher Account"
            
            # Create verification URL
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            
            # Render email template
            template = Template(self.templates["verification"])
            html_content = template.render(
                name=name,
                verification_url=verification_url,
                support_email=settings.SUPPORT_EMAIL
            )
            
            # Send email
            success = await self._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )
            
            if success:
                self.logger.info(f"Verification email sent to {email}")
            else:
                self.logger.error(f"Failed to send verification email to {email}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending verification email to {email}: {str(e)}")
            return False
    
    async def send_password_reset_email(self, email: str, token: str) -> bool:
        """
        Send password reset email to teacher.
        
        Args:
            email: Teacher's email address
            token: Password reset token
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            subject = "Reset Your Faraday AI Password"
            
            # Create password reset URL
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            
            # Render email template
            template = Template(self.templates["password_reset"])
            html_content = template.render(
                reset_url=reset_url,
                support_email=settings.SUPPORT_EMAIL
            )
            
            # Send email
            success = await self._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )
            
            if success:
                self.logger.info(f"Password reset email sent to {email}")
            else:
                self.logger.error(f"Failed to send password reset email to {email}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending password reset email to {email}: {str(e)}")
            return False
    
    async def send_welcome_email(self, email: str, name: str) -> bool:
        """
        Send welcome email to verified teacher.
        
        Args:
            email: Teacher's email address
            name: Teacher's full name
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            subject = "Welcome to Faraday AI - Your PE Assistant is Ready!"
            
            # Render email template
            template = Template(self.templates["welcome"])
            html_content = template.render(
                name=name,
                dashboard_url=f"{settings.FRONTEND_URL}/dashboard",
                support_email=settings.SUPPORT_EMAIL,
                help_url=f"{settings.FRONTEND_URL}/help"
            )
            
            # Send email
            success = await self._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )
            
            if success:
                self.logger.info(f"Welcome email sent to {email}")
            else:
                self.logger.error(f"Failed to send welcome email to {email}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending welcome email to {email}: {str(e)}")
            return False
    
    async def send_beta_announcement(self, email: str, content: str) -> bool:
        """
        Send beta announcement email to teacher.
        
        Args:
            email: Teacher's email address
            content: Announcement content
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            subject = "Faraday AI Beta Update"
            
            # Render email template
            template = Template(self.templates["beta_announcement"])
            html_content = template.render(
                content=content,
                support_email=settings.SUPPORT_EMAIL
            )
            
            # Send email
            success = await self._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )
            
            if success:
                self.logger.info(f"Beta announcement sent to {email}")
            else:
                self.logger.error(f"Failed to send beta announcement to {email}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending beta announcement to {email}: {str(e)}")
            return False
    
    async def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Send email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def _get_verification_template(self) -> str:
        """Get email verification template."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Verify Your Email</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f9f9f9; }
                .button { display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }
                .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Faraday AI!</h1>
                </div>
                <div class="content">
                    <h2>Hi {{ name }},</h2>
                    <p>Thank you for registering for the Faraday AI Physical Education Assistant Beta!</p>
                    <p>To complete your registration and start using your AI-powered PE tools, please verify your email address by clicking the button below:</p>
                    <p style="text-align: center;">
                        <a href="{{ verification_url }}" class="button">Verify Email Address</a>
                    </p>
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666;">{{ verification_url }}</p>
                    <p>This verification link will expire in 24 hours.</p>
                    <p>If you didn't create an account with Faraday AI, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>Need help? Contact us at <a href="mailto:{{ support_email }}">{{ support_email }}</a></p>
                    <p>&copy; 2024 Faraday AI. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_password_reset_template(self) -> str:
        """Get password reset template."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Reset Your Password</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #2196F3; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f9f9f9; }
                .button { display: inline-block; padding: 12px 24px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }
                .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Reset Your Password</h2>
                    <p>We received a request to reset your Faraday AI password.</p>
                    <p>To reset your password, click the button below:</p>
                    <p style="text-align: center;">
                        <a href="{{ reset_url }}" class="button">Reset Password</a>
                    </p>
                    <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666;">{{ reset_url }}</p>
                    <p>This reset link will expire in 1 hour.</p>
                    <p>If you didn't request a password reset, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>Need help? Contact us at <a href="mailto:{{ support_email }}">{{ support_email }}</a></p>
                    <p>&copy; 2024 Faraday AI. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_welcome_template(self) -> str:
        """Get welcome email template."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Faraday AI</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f9f9f9; }
                .button { display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }
                .feature { margin: 15px 0; padding: 15px; background-color: white; border-radius: 4px; }
                .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Faraday AI!</h1>
                    <p>Your AI-Powered Physical Education Assistant</p>
                </div>
                <div class="content">
                    <h2>Hi {{ name }},</h2>
                    <p>Welcome to the Faraday AI Beta! Your account has been verified and you're ready to start using your AI-powered Physical Education tools.</p>
                    
                    <h3>What you can do with Faraday AI:</h3>
                    <div class="feature">
                        <strong>🏃‍♂️ Create PE Activities</strong><br>
                        Design engaging physical education activities with AI assistance
                    </div>
                    <div class="feature">
                        <strong>📝 Build Lesson Plans</strong><br>
                        Generate comprehensive lesson plans tailored to your students' needs
                    </div>
                    <div class="feature">
                        <strong>📊 Assessment Tools</strong><br>
                        Create rubrics and assessments for your PE classes
                    </div>
                    <div class="feature">
                        <strong>🤖 AI Assistant</strong><br>
                        Get personalized recommendations and teaching strategies
                    </div>
                    
                    <p style="text-align: center;">
                        <a href="{{ dashboard_url }}" class="button">Go to Your Dashboard</a>
                    </p>
                    
                    <p>Need help getting started? Check out our <a href="{{ help_url }}">help center</a> or contact our support team.</p>
                </div>
                <div class="footer">
                    <p>Need help? Contact us at <a href="mailto:{{ support_email }}">{{ support_email }}</a></p>
                    <p>&copy; 2024 Faraday AI. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_beta_announcement_template(self) -> str:
        """Get beta announcement template."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Faraday AI Beta Update</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #FF9800; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background-color: #f9f9f9; }
                .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Faraday AI Beta Update</h1>
                </div>
                <div class="content">
                    <h2>Hello Faraday AI Teachers!</h2>
                    {{ content | safe }}
                </div>
                <div class="footer">
                    <p>Need help? Contact us at <a href="mailto:{{ support_email }}">{{ support_email }}</a></p>
                    <p>&copy; 2024 Faraday AI. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
