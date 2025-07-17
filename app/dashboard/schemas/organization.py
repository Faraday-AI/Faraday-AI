"""
Organization Schemas

This module provides Pydantic models for organization-related data validation
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class OrganizationBase(BaseModel):
    """Base organization schema."""
    name: str = Field(..., description="Organization name")
    type: str = Field(..., description="Organization type (enterprise, academic, research, etc.)")
    subscription_tier: str = Field(..., description="Subscription tier")
    settings: Optional[Dict] = Field(default=None, description="Organization settings")

class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""
    pass

class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, description="Organization name")
    type: Optional[str] = Field(None, description="Organization type")
    subscription_tier: Optional[str] = Field(None, description="Subscription tier")
    settings: Optional[Dict] = Field(None, description="Organization settings")

class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""
    id: int = Field(..., description="Organization ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True

class MemberBase(BaseModel):
    """Base member schema."""
    user_id: str = Field(..., description="User ID")
    role: str = Field(..., description="Member role")
    permissions: Optional[Dict] = Field(default=None, description="Member permissions")

class MemberCreate(MemberBase):
    """Schema for adding a member."""
    pass

class MemberResponse(MemberBase):
    """Schema for member response."""
    id: int = Field(..., description="Member ID")
    organization_id: int = Field(..., description="Organization ID")
    status: str = Field(..., description="Member status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True

class DepartmentBase(BaseModel):
    """Base department schema."""
    name: str = Field(..., description="Department name")
    description: Optional[str] = Field(None, description="Department description")
    settings: Optional[Dict] = Field(default=None, description="Department settings")

class DepartmentCreate(DepartmentBase):
    """Schema for creating a department."""
    pass

class DepartmentResponse(DepartmentBase):
    """Schema for department response."""
    id: int = Field(..., description="Department ID")
    organization_id: int = Field(..., description="Organization ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True

class CollaborationBase(BaseModel):
    """Base collaboration schema."""
    source_org_id: str = Field(..., description="Source organization ID")
    target_org_id: str = Field(..., description="Target organization ID")
    type: str = Field(..., description="Collaboration type")
    settings: Optional[Dict] = Field(default=None, description="Collaboration settings")

class CollaborationCreate(CollaborationBase):
    """Schema for creating a collaboration."""
    pass

class CollaborationResponse(CollaborationBase):
    """Schema for collaboration response."""
    id: str = Field(..., description="Collaboration ID")
    status: str = Field(..., description="Collaboration status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True

class SharedResourceUpdate(BaseModel):
    """Schema for updating a shared resource."""
    status: str
    settings: Optional[Dict[str, Any]] = None 