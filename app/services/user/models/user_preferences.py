from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.shared_base import SharedBase
from app.dashboard.models.user_preferences import UserPreferences

# Re-export the UserPreferences class
__all__ = ['UserPreferences'] 