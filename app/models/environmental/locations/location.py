from sqlalchemy import Column, Integer, String, JSON
from app.models.core.base import BaseModel, StatusMixin, MetadataMixin


class Location(BaseModel, StatusMixin, MetadataMixin):
    """
    Represents a physical location in the system.
    Used for tracking where activities, classes, or resources are located.
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=True)
    type = Column(String, nullable=True)  # e.g., "gym", "field", "classroom", etc.
    meta_data = Column(JSON, nullable=True)  # Additional metadata as JSON 

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "type": self.type,
            "status": self.status,
            "meta_data": self.meta_data
        } 