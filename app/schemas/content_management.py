"""Content Management Schemas for managing educational content."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ContentCreate(BaseModel):
    """Schema for creating content."""
    title: str = Field(..., description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    content_type: str = Field(..., description="Type of content")
    content_data: Dict[str, Any] = Field(..., description="Content data")
    tags: Optional[List[str]] = Field(default=[], description="Content tags")
    category: Optional[str] = Field(None, description="Content category")
    difficulty_level: Optional[str] = Field(None, description="Difficulty level")
    target_audience: Optional[List[str]] = Field(default=[], description="Target audience")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

class ContentUpdate(BaseModel):
    """Schema for updating content."""
    title: Optional[str] = Field(None, description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    content_type: Optional[str] = Field(None, description="Type of content")
    content_data: Optional[Dict[str, Any]] = Field(None, description="Content data")
    tags: Optional[List[str]] = Field(None, description="Content tags")
    category: Optional[str] = Field(None, description="Content category")
    difficulty_level: Optional[str] = Field(None, description="Difficulty level")
    target_audience: Optional[List[str]] = Field(None, description="Target audience")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    is_active: Optional[bool] = Field(None, description="Content active status")

class ContentSearch(BaseModel):
    """Schema for content search parameters."""
    query: Optional[str] = Field(None, description="Search query")
    content_type: Optional[str] = Field(None, description="Filter by content type")
    category: Optional[str] = Field(None, description="Filter by category")
    difficulty_level: Optional[str] = Field(None, description="Filter by difficulty level")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    target_audience: Optional[List[str]] = Field(None, description="Filter by target audience")
    created_by: Optional[str] = Field(None, description="Filter by creator")
    date_from: Optional[datetime] = Field(None, description="Filter by creation date from")
    date_to: Optional[datetime] = Field(None, description="Filter by creation date to")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    limit: Optional[int] = Field(100, description="Maximum number of results")
    offset: Optional[int] = Field(0, description="Number of results to skip")

class ContentFilter(BaseModel):
    """Schema for content filtering."""
    content_types: Optional[List[str]] = Field(None, description="Allowed content types")
    categories: Optional[List[str]] = Field(None, description="Allowed categories")
    difficulty_levels: Optional[List[str]] = Field(None, description="Allowed difficulty levels")
    tags: Optional[List[str]] = Field(None, description="Required tags")
    target_audiences: Optional[List[str]] = Field(None, description="Allowed target audiences")
    creators: Optional[List[str]] = Field(None, description="Allowed creators")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    active_only: Optional[bool] = Field(True, description="Include only active content")

class ContentResponse(BaseModel):
    """Schema for content response."""
    id: str = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    content_type: str = Field(..., description="Type of content")
    content_data: Dict[str, Any] = Field(..., description="Content data")
    tags: List[str] = Field(default=[], description="Content tags")
    category: Optional[str] = Field(None, description="Content category")
    difficulty_level: Optional[str] = Field(None, description="Difficulty level")
    target_audience: List[str] = Field(default=[], description="Target audience")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    created_by: str = Field(..., description="Content creator")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    is_active: bool = Field(..., description="Content active status")
    view_count: int = Field(default=0, description="Number of views")
    rating: Optional[float] = Field(None, description="Average rating")
    review_count: int = Field(default=0, description="Number of reviews")

    class Config:
        from_attributes = True 