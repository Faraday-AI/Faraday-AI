"""
Content Management Schemas

This module defines Pydantic schemas for content management functionality.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ContentCreate(BaseModel):
    """Schema for creating content."""
    title: str = Field(..., description="Content title")
    content_type: str = Field(..., description="Type of content")
    description: Optional[str] = Field(None, description="Content description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ContentUpdate(BaseModel):
    """Schema for updating content."""
    title: Optional[str] = Field(None, description="Content title")
    description: Optional[str] = Field(None, description="Content description")
    content_type: Optional[str] = Field(None, description="Type of content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ContentResponse(BaseModel):
    """Schema for content response."""
    content_id: str
    title: str
    content_type: str
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

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