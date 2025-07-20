"""
Team Management Schemas

This module defines Pydantic schemas for team management.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TeamRole(str, Enum):
    """Team roles."""
    OWNER = "owner"
    ADMIN = "admin"
    LEADER = "leader"
    MEMBER = "member"
    GUEST = "guest"


class TeamStatus(str, Enum):
    """Team status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"


class TeamBase(BaseModel):
    """Base team schema."""
    name: str = Field(..., description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    settings: Optional[Dict[str, Any]] = Field(None, description="Team settings")


class TeamCreate(TeamBase):
    """Schema for creating a team."""
    pass


class TeamUpdate(BaseModel):
    """Schema for updating a team."""
    name: Optional[str] = Field(None, description="Team name")
    description: Optional[str] = Field(None, description="Team description")
    settings: Optional[Dict[str, Any]] = Field(None, description="Team settings")
    is_active: Optional[bool] = Field(None, description="Team active status")


class TeamResponse(TeamBase):
    """Schema for team responses."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamMemberBase(BaseModel):
    """Base team member schema."""
    user_id: int = Field(..., description="User ID")
    role: TeamRole = Field(TeamRole.MEMBER, description="Team role")
    permissions: Optional[Dict[str, Any]] = Field(None, description="Member permissions")


class TeamMemberCreate(TeamMemberBase):
    """Schema for creating a team member."""
    pass


class TeamMemberUpdate(BaseModel):
    """Schema for updating a team member."""
    role: Optional[TeamRole] = Field(None, description="Team role")
    permissions: Optional[Dict[str, Any]] = Field(None, description="Member permissions")


class TeamMemberResponse(TeamMemberBase):
    """Schema for team member responses."""
    id: int
    team_id: int
    joined_at: datetime
    last_active: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamInvitation(BaseModel):
    """Schema for team invitation."""
    email: str = Field(..., description="Invitee email")
    role: TeamRole = Field(TeamRole.MEMBER, description="Invitee role")
    permissions: Optional[Dict[str, Any]] = Field(None, description="Invitee permissions")
    message: Optional[str] = Field(None, description="Invitation message")
    expires_at: Optional[datetime] = Field(None, description="Invitation expiration")


class TeamSummary(BaseModel):
    """Schema for team summary."""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    member_count: int
    role_distribution: Dict[str, int]
    created_at: datetime
    updated_at: datetime


class TeamSearch(BaseModel):
    """Schema for team search."""
    query: Optional[str] = Field(None, description="Search query")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    limit: int = Field(10, description="Maximum number of results")


class TeamFilter(BaseModel):
    """Schema for team filtering."""
    name_contains: Optional[str] = Field(None, description="Team name contains")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    min_members: Optional[int] = Field(None, description="Minimum member count")
    max_members: Optional[int] = Field(None, description="Maximum member count")
    has_role: Optional[str] = Field(None, description="Teams with specific role")
    created_after: Optional[datetime] = Field(None, description="Created after date")
    created_before: Optional[datetime] = Field(None, description="Created before date")


class TeamCollaboration(BaseModel):
    """Schema for team collaboration."""
    team_id: int = Field(..., description="Team ID")
    collaborator_team_id: int = Field(..., description="Collaborator team ID")
    collaboration_type: str = Field(..., description="Type of collaboration")
    permissions: Optional[Dict[str, Any]] = Field(None, description="Collaboration permissions")
    settings: Optional[Dict[str, Any]] = Field(None, description="Collaboration settings")


class TeamActivity(BaseModel):
    """Schema for team activity."""
    team_id: int = Field(..., description="Team ID")
    user_id: int = Field(..., description="User ID")
    activity_type: str = Field(..., description="Activity type")
    description: str = Field(..., description="Activity description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Activity metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TeamBulkOperation(BaseModel):
    """Schema for bulk team operations."""
    operation: str = Field(..., description="Operation type")
    team_ids: List[int] = Field(..., description="Team IDs")
    data: Optional[Dict[str, Any]] = Field(None, description="Operation data")


class TeamMemberBulkOperation(BaseModel):
    """Schema for bulk team member operations."""
    operation: str = Field(..., description="Operation type")
    team_id: int = Field(..., description="Team ID")
    user_ids: List[int] = Field(..., description="User IDs")
    data: Optional[Dict[str, Any]] = Field(None, description="Operation data")


class TeamAnalytics(BaseModel):
    """Schema for team analytics."""
    team_id: int
    total_members: int
    active_members: int
    inactive_members: int
    role_distribution: Dict[str, int]
    average_activity_days: float
    most_active_members: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]
    collaboration_metrics: Dict[str, Any]


class TeamTemplate(BaseModel):
    """Schema for team templates."""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    default_roles: List[Dict[str, Any]] = Field(..., description="Default roles")
    default_settings: Optional[Dict[str, Any]] = Field(None, description="Default settings")
    is_system: bool = Field(False, description="Whether this is a system template")


class TeamTemplateCreate(BaseModel):
    """Schema for creating team templates."""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    default_roles: List[Dict[str, Any]] = Field(..., description="Default roles")
    default_settings: Optional[Dict[str, Any]] = Field(None, description="Default settings")


class TeamTemplateUpdate(BaseModel):
    """Schema for updating team templates."""
    name: Optional[str] = Field(None, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    default_roles: Optional[List[Dict[str, Any]]] = Field(None, description="Default roles")
    default_settings: Optional[Dict[str, Any]] = Field(None, description="Default settings")


class TeamTemplateResponse(BaseModel):
    """Schema for team template responses."""
    id: int
    name: str
    description: Optional[str]
    default_roles: List[Dict[str, Any]]
    default_settings: Optional[Dict[str, Any]]
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TeamStatistics(BaseModel):
    """Schema for team statistics."""
    total_teams: int
    active_teams: int
    inactive_teams: int
    total_members: int
    average_members_per_team: float
    teams_by_role: Dict[str, int]
    most_popular_roles: List[str]
    average_team_age_days: float
    teams_created_this_month: int
    teams_created_this_year: int 