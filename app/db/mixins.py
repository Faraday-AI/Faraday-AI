"""SQLAlchemy model mixins.
DEPRECATED: Use app.models.mixins instead.
"""

import warnings
from typing import Any, Dict, Optional, Type, TypeVar, List
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, String, Boolean, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.ext.declarative import declared_attr
from uuid import uuid4

from app.models.mixins.timestamped import TimestampedMixin as NewTimestampedMixin

warnings.warn(
    "app.db.mixins is deprecated. Use app.models.mixins instead.",
    DeprecationWarning,
    stacklevel=2
)

T = TypeVar('T', bound='Base')

# Re-export the new mixin for backward compatibility
TimestampMixin = NewTimestampedMixin

class SoftDeleteMixin:
    """Mixin to add soft delete functionality to models."""
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self) -> None:
        """Soft delete the model instance."""
        self.is_active = False
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted model instance."""
        self.is_active = True
        self.deleted_at = None

class UUIDMixin:
    """Mixin to add UUID field to models."""
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid4()))

class MetadataMixin:
    """Mixin to add metadata field to models."""
    _metadata = Column('metadata', JSON, nullable=True)  # Use _metadata internally to avoid conflict

    @property
    def metadata(self):
        """Property to access metadata for backward compatibility."""
        return self._metadata
    
    @metadata.setter
    def metadata(self, value):
        """Property setter for metadata."""
        self._metadata = value

    def update_metadata(self, key: str, value: Any) -> None:
        """Update metadata with a key-value pair."""
        if self._metadata is None:
            self._metadata = {}
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value for a key."""
        if self._metadata is None:
            return default
        return self._metadata.get(key, default)

    def remove_metadata(self, key: str) -> None:
        """Remove metadata key."""
        if self._metadata is not None and key in self._metadata:
            del self._metadata[key]

class VersionMixin:
    """Mixin to add versioning to models."""
    version = Column(Integer, default=1, nullable=False)

    def increment_version(self) -> None:
        """Increment the version number."""
        self.version += 1

class AuditMixin:
    """Mixin to add audit fields to models."""
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    deleted_by = Column(String(36), nullable=True)

    def set_created_by(self, user_id: str) -> None:
        """Set the user who created the record."""
        self.created_by = user_id

    def set_updated_by(self, user_id: str) -> None:
        """Set the user who last updated the record."""
        self.updated_by = user_id

    def set_deleted_by(self, user_id: str) -> None:
        """Set the user who deleted the record."""
        self.deleted_by = user_id

class NameMixin:
    """Mixin to add name fields to models."""
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    def __str__(self) -> str:
        """String representation of the model."""
        return self.name

class StatusMixin:
    """Mixin to add status field to models."""
    status = Column(String(50), nullable=False, default='active')

    def set_status(self, status: str) -> None:
        """Set the status of the model."""
        self.status = status

class PriorityMixin:
    """Mixin to add priority field to models."""
    priority = Column(Integer, default=0, nullable=False)

    def set_priority(self, priority: int) -> None:
        """Set the priority of the model."""
        self.priority = priority

class OrderMixin:
    """Mixin to add ordering to models."""
    order = Column(Integer, default=0, nullable=False)

    def set_order(self, order: int) -> None:
        """Set the order of the model."""
        self.order = order

class SlugMixin:
    """Mixin to add slug field to models."""
    slug = Column(String(255), unique=True, index=True, nullable=False)

    def set_slug(self, slug: str) -> None:
        """Set the slug of the model."""
        self.slug = slug

class CodeMixin:
    """Mixin to add code field to models."""
    code = Column(String(50), unique=True, index=True, nullable=False)

    def set_code(self, code: str) -> None:
        """Set the code of the model."""
        self.code = code

class ExternalIDMixin:
    """Mixin to add external ID field to models."""
    external_id = Column(String(255), unique=True, index=True, nullable=True)

    def set_external_id(self, external_id: str) -> None:
        """Set the external ID of the model."""
        self.external_id = external_id

class TagMixin:
    """Mixin to add tags to models."""
    tags = Column(JSON, default=list, nullable=False)

    def add_tag(self, tag: str) -> None:
        """Add a tag to the model."""
        if self.tags is None:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the model."""
        if self.tags is not None and tag in self.tags:
            self.tags.remove(tag)

    def has_tag(self, tag: str) -> bool:
        """Check if the model has a tag."""
        return self.tags is not None and tag in self.tags

class CategoryMixin:
    """Mixin to add categories to models."""
    categories = Column(JSON, default=list, nullable=False)

    def add_category(self, category: str) -> None:
        """Add a category to the model."""
        if self.categories is None:
            self.categories = []
        if category not in self.categories:
            self.categories.append(category)

    def remove_category(self, category: str) -> None:
        """Remove a category from the model."""
        if self.categories is not None and category in self.categories:
            self.categories.remove(category)

    def has_category(self, category: str) -> bool:
        """Check if the model has a category."""
        return self.categories is not None and category in self.categories

class SearchableMixin:
    """Mixin to add search functionality to models."""
    search_vector = Column(JSON, nullable=True)

    def update_search_vector(self, text: str) -> None:
        """Update the search vector with text."""
        if self.search_vector is None:
            self.search_vector = {}
        self.search_vector['text'] = text

    def get_search_text(self) -> Optional[str]:
        """Get the search text."""
        if self.search_vector is not None:
            return self.search_vector.get('text')
        return None 