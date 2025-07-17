"""
GPT schemas for the dashboard.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum

class GPTSubscriptionStatus(str, Enum):
    """Enumeration of possible GPT subscription statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class GPTSubscriptionType(str, Enum):
    """Enumeration of possible GPT subscription types."""
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    TRIAL = "trial"
    CUSTOM = "custom"

class GPTSubscriptionResponse(BaseModel):
    """Response schema for GPT subscription."""
    id: str = Field(..., description="Unique identifier for the subscription")
    user_id: str = Field(..., description="ID of the user who owns the subscription")
    gpt_id: str = Field(..., description="ID of the GPT model")
    subscription_date: datetime = Field(..., description="When the subscription was created")
    status: GPTSubscriptionStatus = Field(..., description="Current status of the subscription")
    subscription_type: GPTSubscriptionType = Field(..., description="Type of subscription")
    is_active: bool = Field(..., description="Whether the subscription is currently active")
    preferences: Optional[Dict] = Field(None, description="User preferences for this GPT")
    rate_limit: Optional[int] = Field(None, description="Rate limit for API calls")
    usage_count: Optional[int] = Field(None, description="Number of times the GPT has been used")
    last_used: Optional[datetime] = Field(None, description="When the GPT was last used")
    expires_at: Optional[datetime] = Field(None, description="When the subscription expires")
    features: Optional[List[str]] = Field(None, description="List of enabled features")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="When the subscription was created")
    updated_at: datetime = Field(..., description="When the subscription was last updated")

class GPTSubscriptionCreate(BaseModel):
    """Schema for creating a new GPT subscription."""
    gpt_id: str = Field(..., description="ID of the GPT model")
    subscription_type: GPTSubscriptionType = Field(..., description="Type of subscription")
    preferences: Optional[Dict] = Field(None, description="User preferences for this GPT")
    features: Optional[List[str]] = Field(None, description="List of features to enable")
    metadata: Optional[Dict] = Field(None, description="Additional metadata")

class GPTSubscriptionUpdate(BaseModel):
    """Schema for updating an existing GPT subscription."""
    status: Optional[GPTSubscriptionStatus] = Field(None, description="New status")
    subscription_type: Optional[GPTSubscriptionType] = Field(None, description="New subscription type")
    preferences: Optional[Dict] = Field(None, description="Updated preferences")
    features: Optional[List[str]] = Field(None, description="Updated feature list")
    metadata: Optional[Dict] = Field(None, description="Updated metadata")

class GPTUsageStats(BaseModel):
    """Schema for GPT usage statistics."""
    total_calls: int = Field(..., description="Total number of API calls")
    total_tokens: int = Field(..., description="Total tokens consumed")
    average_response_time: float = Field(..., description="Average response time in seconds")
    error_rate: float = Field(..., description="Error rate percentage")
    last_24h_calls: int = Field(..., description="Calls in the last 24 hours")
    last_24h_tokens: int = Field(..., description="Tokens consumed in the last 24 hours")
    peak_usage_time: Optional[datetime] = Field(None, description="Time of peak usage") 