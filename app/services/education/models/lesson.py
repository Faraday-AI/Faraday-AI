from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.shared_base import SharedBase
from app.models.core.lesson import Lesson

# Re-export the Lesson model
__all__ = ['Lesson']

# Remove duplicate Lesson class definition 