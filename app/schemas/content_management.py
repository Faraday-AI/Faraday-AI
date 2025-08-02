"""
Content Management Schemas

This module defines Pydantic schemas for content management functionality.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from pydantic import BaseModel, Field

class ContentCreate(BaseModel):
    """Schema for creating content."""
    title: str = Field(..., description="Content title")
    subject_category_id: Optional[int] = Field(None, description="Subject category ID")
    grade_level: Optional[str] = Field(None, description="Grade level")
    content: Optional[str] = Field(None, description="Content text")
    objectives: Optional[List[str]] = Field(None, description="Learning objectives")
    materials: Optional[List[str]] = Field(None, description="Required materials")
    tags: Optional[List[str]] = Field(None, description="Content tags")
    status: Optional[str] = Field("draft", description="Content status")
    content_type: Optional[str] = Field(None, description="Type of content")
    description: Optional[str] = Field(None, description="Content description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ContentUpdate(BaseModel):
    """Schema for updating content."""
    title: Optional[str] = Field(None, description="Content title")
    status: Optional[str] = Field(None, description="Content status")
    subject_category_id: Optional[int] = Field(None, description="Subject category ID")
    description: Optional[str] = Field(None, description="Content description")
    content_type: Optional[str] = Field(None, description="Type of content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ContentSearch(BaseModel):
    """Schema for content search."""
    query: str = Field(..., description="Search query string")
    user_id: Optional[int] = Field(None, description="User ID")
    status: Optional[str] = Field(None, description="Filter by status")
    subject_category_id: Optional[int] = Field(None, description="Subject category ID")
    grade_level: Optional[str] = Field(None, description="Grade level")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    limit: Optional[int] = Field(10, description="Number of results to return")
    content_type: Optional[str] = Field(None, description="Filter by content type")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")

class ContentFilter(BaseModel):
    """Schema for content filtering."""
    user_id: Optional[int] = Field(None, description="User ID")
    status: Optional[str] = Field(None, description="Filter by status")
    subject_category_id: Optional[int] = Field(None, description="Subject category ID")
    grade_level: Optional[str] = Field(None, description="Grade level")
    content_area: Optional[str] = Field(None, description="Content area")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date after")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date before")
    sort_by: Optional[str] = Field(None, description="Sort field")
    limit: Optional[int] = Field(10, description="Number of results to return")
    content_type: Optional[str] = Field(None, description="Filter by content type")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")

class ContentResponse(BaseModel):
    """Schema for content response."""
    id: int = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    user_id: int = Field(..., description="User ID")
    subject_category_id: Optional[int] = Field(None, description="Subject category ID")
    assistant_profile_id: Optional[int] = Field(None, description="Assistant profile ID")
    grade_level: Optional[str] = Field(None, description="Grade level")
    week_of: Optional[date] = Field(None, description="Week of")
    content_area: Optional[str] = Field(None, description="Content area")
    content: Optional[str] = Field(None, description="Content text")
    lesson_data: Optional[Dict[str, Any]] = Field(None, description="Lesson data")
    objectives: Optional[List[str]] = Field(None, description="Learning objectives")
    materials: Optional[List[str]] = Field(None, description="Required materials")
    activities: Optional[List[Dict[str, Any]]] = Field(None, description="Activities")
    assessment_criteria: Optional[Dict[str, Any]] = Field(None, description="Assessment criteria")
    feedback: Optional[Dict[str, Any]] = Field(None, description="Feedback")
    status: Optional[str] = Field(None, description="Content status")
    version: Optional[int] = Field(None, description="Content version")
    tags: Optional[List[str]] = Field(None, description="Content tags")
    related_lessons: Optional[List[int]] = Field(None, description="Related lesson IDs")
    content_type: Optional[str] = Field(None, description="Type of content")
    description: Optional[str] = Field(None, description="Content description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True

class ContentListResponse(BaseModel):
    """Schema for content list response."""
    contents: List[ContentResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool 