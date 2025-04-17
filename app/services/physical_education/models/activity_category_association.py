from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from pydantic import BaseModel, Field

class ActivityCategoryAssociation(Base):
    """Model for associating activities with categories."""
    __tablename__ = "activity_category_associations"

    id = Column(Integer, primary_key=True)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activity = relationship("Activity", back_populates="category_associations")

    def __repr__(self):
        return f"<ActivityCategoryAssociation(id={self.id}, activity_id={self.activity_id}, category={self.category})>"

class ActivityCategoryAssociationBase(BaseModel):
    activity_id: str
    category: str

class ActivityCategoryAssociationCreate(ActivityCategoryAssociationBase):
    pass

class ActivityCategoryAssociationUpdate(BaseModel):
    category: str | None = None

class ActivityCategoryAssociationResponse(ActivityCategoryAssociationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 