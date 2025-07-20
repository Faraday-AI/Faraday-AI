"""
Organization Management Schemas

This module defines Pydantic schemas for organization management.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class OrganizationType(str, Enum):
    """Organization types."""
    ENTERPRISE = "enterprise"
    ACADEMIC = "academic"
    RESEARCH = "research"
    NON_PROFIT = "non_profit"
    GOVERNMENT = "government"
    STARTUP = "startup"
    OTHER = "other"


class SubscriptionTier(str, Enum):
    """Subscription tiers."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class OrganizationBase(BaseModel):
    """Base organization schema."""
    name: str = Field(..., description="Organization name")
    type: OrganizationType = Field(..., description="Organization type")
    subscription_tier: SubscriptionTier = Field(..., description="Subscription tier")
    settings_data: Optional[Dict[str, Any]] = Field(None, description="Organization settings")
    credits_balance: Optional[float] = Field(0.0, description="Credits balance")


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, description="Organization name")
    type: Optional[OrganizationType] = Field(None, description="Organization type")
    subscription_tier: Optional[SubscriptionTier] = Field(None, description="Subscription tier")
    settings_data: Optional[Dict[str, Any]] = Field(None, description="Organization settings")
    credits_balance: Optional[float] = Field(None, description="Credits balance")


class OrganizationResponse(OrganizationBase):
    """Schema for organization responses."""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationMemberBase(BaseModel):
    """Base organization member schema."""
    user_id: int = Field(..., description="User ID")
    role_id: Optional[int] = Field(None, description="Role ID")
    permissions: Optional[Dict[str, Any]] = Field(None, description="Member permissions")


class OrganizationMemberCreate(OrganizationMemberBase):
    """Schema for creating an organization member."""
    pass


class OrganizationMemberUpdate(BaseModel):
    """Schema for updating an organization member."""
    role_id: Optional[int] = Field(None, description="Role ID")
    permissions: Optional[Dict[str, Any]] = Field(None, description="Member permissions")


class OrganizationMemberResponse(OrganizationMemberBase):
    """Schema for organization member responses."""
    id: int
    organization_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DepartmentBase(BaseModel):
    """Base department schema."""
    name: str = Field(..., description="Department name")
    description: Optional[str] = Field(None, description="Department description")
    settings: Optional[Dict[str, Any]] = Field(None, description="Department settings")


class DepartmentCreate(DepartmentBase):
    """Schema for creating a department."""
    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating a department."""
    name: Optional[str] = Field(None, description="Department name")
    description: Optional[str] = Field(None, description="Department description")
    settings: Optional[Dict[str, Any]] = Field(None, description="Department settings")


class DepartmentResponse(DepartmentBase):
    """Schema for department responses."""
    id: int
    organization_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DepartmentMemberBase(BaseModel):
    """Base department member schema."""
    user_id: int = Field(..., description="User ID")
    role: str = Field(..., description="Member role")
    permissions: Optional[Dict[str, Any]] = Field(None, description="Member permissions")


class DepartmentMemberCreate(DepartmentMemberBase):
    """Schema for creating a department member."""
    pass


class DepartmentMemberUpdate(BaseModel):
    """Schema for updating a department member."""
    role: Optional[str] = Field(None, description="Member role")
    permissions: Optional[Dict[str, Any]] = Field(None, description="Member permissions")


class DepartmentMemberResponse(DepartmentMemberBase):
    """Schema for department member responses."""
    id: int
    department_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationSummary(BaseModel):
    """Schema for organization summary."""
    id: int
    name: str
    type: str
    subscription_tier: str
    credits_balance: float
    member_count: int
    department_count: int
    created_at: datetime
    updated_at: datetime


class OrganizationSearch(BaseModel):
    """Schema for organization search."""
    query: Optional[str] = Field(None, description="Search query")
    type: Optional[OrganizationType] = Field(None, description="Filter by type")
    subscription_tier: Optional[SubscriptionTier] = Field(None, description="Filter by subscription tier")
    limit: int = Field(10, description="Maximum number of results")


class OrganizationFilter(BaseModel):
    """Schema for organization filtering."""
    name_contains: Optional[str] = Field(None, description="Organization name contains")
    type: Optional[OrganizationType] = Field(None, description="Filter by type")
    subscription_tier: Optional[SubscriptionTier] = Field(None, description="Filter by subscription tier")
    min_members: Optional[int] = Field(None, description="Minimum member count")
    max_members: Optional[int] = Field(None, description="Maximum member count")
    min_credits: Optional[float] = Field(None, description="Minimum credits balance")
    max_credits: Optional[float] = Field(None, description="Maximum credits balance")


class OrganizationInvitation(BaseModel):
    """Schema for organization invitation."""
    email: str = Field(..., description="Invitee email")
    role_id: Optional[int] = Field(None, description="Role ID")
    permissions: Optional[Dict[str, Any]] = Field(None, description="Invitee permissions")
    message: Optional[str] = Field(None, description="Invitation message")


class OrganizationBulkOperation(BaseModel):
    """Schema for bulk organization operations."""
    operation: str = Field(..., description="Operation type")
    organization_ids: List[int] = Field(..., description="Organization IDs")
    data: Optional[Dict[str, Any]] = Field(None, description="Operation data")


class OrganizationStatistics(BaseModel):
    """Schema for organization statistics."""
    total_organizations: int
    organizations_by_type: Dict[str, int]
    organizations_by_tier: Dict[str, int]
    average_members_per_org: float
    total_members: int
    total_departments: int
    average_credits_per_org: float
    most_active_organizations: List[str] 