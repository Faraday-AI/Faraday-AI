"""Activity category associations model."""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from app.models.core.base import BaseModel
from app.models.core.activity import CoreActivity

class ActivityCategoryAssociation(BaseModel):
    """Association table for activities and categories."""
    __tablename__ = "activity_category_associations"
    __table_args__ = {
        'extend_existing': True
    }

    # Define columns to match database schema exactly
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    category_id = Column(Integer, ForeignKey("activity_categories.id"))
    primary_category = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define relationships
    activity = relationship(
        "app.models.physical_education.activity.models.Activity",
        back_populates="category_associations",
        foreign_keys=[activity_id]
    )
    category = relationship(
        "ActivityCategory",
        back_populates="category_associations",
        foreign_keys=[category_id]
    )

    def __repr__(self):
        return f"<ActivityCategoryAssociation {self.activity_id} - {self.category_id}>" 