"""
Context schemas for the Faraday AI Dashboard.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ContextHistory(BaseModel):
    """Schema for context history."""
    id: str
    gpt_id: str
    user_id: str
    content: Dict[str, Any]
    context_type: str = Field(pattern="^(conversation|task|session|workflow)$")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ContextMetrics(BaseModel):
    """Schema for context metrics."""
    total_contexts: int = 0
    avg_context_length: float = 0.0
    context_types: Dict[str, int] = Field(default_factory=dict)
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True

class ContextPatterns(BaseModel):
    """Schema for context patterns."""
    time_patterns: Dict[int, int] = Field(default_factory=dict)  # Hour -> Count
    content_patterns: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class ContextPreferences(BaseModel):
    """Schema for context preferences."""
    preferred_context_types: List[str] = Field(default_factory=list)
    context_retention_days: int = Field(default=30, ge=1, le=365)
    auto_context_sharing: bool = Field(default=False)
    context_sharing_scope: str = Field(default="private", pattern="^(private|team|public)$")
    gpt_context_preferences: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class ContextSharing(BaseModel):
    """Schema for context sharing."""
    shared_context: ContextHistory
    history: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True 