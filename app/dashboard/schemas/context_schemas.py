"""
Context Schemas

This module defines the Pydantic schemas for GPT context management
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ContextBase(BaseModel):
    """Base schema for context data."""
    name: Optional[str] = None
    description: Optional[str] = None
    context_data: Dict = Field(default_factory=dict)

class ContextCreate(BaseModel):
    """Schema for creating a new context."""
    primary_gpt_id: str
    name: str
    description: Optional[str] = None
    context_data: Dict[str, Any]

class ContextUpdate(BaseModel):
    """Schema for updating a context."""
    context_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class AddGPTToContext(BaseModel):
    """Schema for adding a GPT to a context."""
    gpt_id: str
    role: str

class ShareContextData(BaseModel):
    """Schema for sharing context data between GPTs."""
    source_gpt_id: str
    target_gpt_id: str
    shared_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class ContextSummaryCreate(BaseModel):
    """Schema for creating a context summary."""
    summary: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class ContextHistoryFilter(BaseModel):
    """Schema for filtering context history."""
    gpt_id: Optional[str] = None
    interaction_type: Optional[str] = None

class ContextInteractionResponse(BaseModel):
    """Schema for context interaction response."""
    interaction_id: str
    context_id: str
    gpt_id: str
    interaction_type: str
    interaction_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

class SharedContextResponse(BaseModel):
    """Schema for shared context response."""
    share_id: str
    context_id: str
    source_gpt_id: str
    target_gpt_id: str
    shared_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

class ContextResponse(BaseModel):
    """Schema for context response."""
    context_id: str
    primary_gpt_id: str
    name: str
    description: Optional[str] = None
    context_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class ContextSummaryResponse(BaseModel):
    """Schema for context summary response."""
    summary_id: str
    context_id: str
    summary: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class ContextTemplateCreate(BaseModel):
    """Schema for creating a context template."""
    name: str
    description: Optional[str] = None
    template_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True) 