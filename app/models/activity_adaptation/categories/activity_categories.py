"""Activity categories model."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from app.models.core.base import BaseModel
from app.models.activity_adaptation.categories.associations import ActivityCategoryAssociation

class ActivityCategory(BaseModel):
    """Model for activity categories."""
    __tablename__ = "activity_categories"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    parent_id = Column(Integer, ForeignKey('activity_categories.id', ondelete='SET NULL'), nullable=True)
    category_type = Column(String, nullable=False)  # One of ActivityCategoryType values
    category_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Self-referential relationship for hierarchical categories
    parent = relationship("ActivityCategory", remote_side=[id], backref="subcategories")
    
    # Relationships
    category_associations = relationship(
        "ActivityCategoryAssociation",
        back_populates="category",
        foreign_keys="ActivityCategoryAssociation.category_id"
    )
    activities = relationship(
        "Activity",
        secondary="activity_category_associations",
        back_populates="categories",
        viewonly=True
    )

    def __repr__(self):
        return f"<ActivityCategory {self.name}>" 