"""
User preferences model.
"""

from app.models.shared_base import SharedBase
from sqlalchemy import Column, String, JSON, DateTime, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime

class UserPreferences(SharedBase):
    """Enhanced user preferences model."""
    __tablename__ = "user_preferences"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Theme preferences
    theme = Column(String, default="light")  # light, dark, system
    accent_color = Column(String)
    font_size = Column(String, default="medium")  # small, medium, large
    font_family = Column(String, default="system")
    
    # Layout preferences
    dashboard_layout = Column(JSON)  # Custom dashboard layout
    sidebar_position = Column(String, default="left")  # left, right
    sidebar_collapsed = Column(Boolean, default=False)
    grid_view = Column(Boolean, default=True)  # grid or list view
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    in_app_notifications = Column(Boolean, default=True)
    notification_sound = Column(Boolean, default=True)
    notification_types = Column(JSON)  # Types of notifications to receive
    quiet_hours = Column(JSON)  # Time ranges for quiet hours
    
    # Language and regional preferences
    language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    date_format = Column(String, default="YYYY-MM-DD")
    time_format = Column(String, default="24h")  # 12h or 24h
    
    # Privacy preferences
    data_sharing = Column(Boolean, default=False)
    analytics_opt_in = Column(Boolean, default=True)
    personalized_ads = Column(Boolean, default=False)
    
    # Accessibility preferences
    high_contrast = Column(Boolean, default=False)
    reduced_motion = Column(Boolean, default=False)
    screen_reader = Column(Boolean, default=False)
    keyboard_shortcuts = Column(JSON)  # Custom keyboard shortcuts
    
    # Performance preferences
    cache_enabled = Column(Boolean, default=True)
    cache_duration = Column(Integer, default=300)  # Cache duration in seconds
    auto_refresh = Column(Boolean, default=True)
    refresh_interval = Column(Integer, default=60)  # Refresh interval in seconds
    
    # Integration preferences
    connected_services = Column(JSON)  # List of connected third-party services
    webhook_urls = Column(JSON)  # Custom webhook URLs
    api_keys = Column(JSON)  # API keys for integrations
    
    # Backup preferences
    auto_backup = Column(Boolean, default=True)
    backup_frequency = Column(String, default="daily")  # daily, weekly, monthly
    backup_location = Column(String)  # Local or cloud storage location
    
    # Custom preferences
    custom_settings = Column(JSON)  # User-defined custom settings
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="dashboard_preferences") 