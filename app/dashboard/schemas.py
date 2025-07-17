"""
Dashboard Pydantic Schemas

This module defines the Pydantic schemas for request/response validation
in the Faraday AI Dashboard.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, HttpUrl, constr, conint, confloat, ConfigDict
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """User roles enum."""
    ADMIN = "admin"
    USER = "user"
    TEAM_LEAD = "team_lead"
    DEVELOPER = "developer"

class GPTPreferences(BaseModel):
    """Preferences for a GPT subscription."""
    default_difficulty: str = Field(..., enum=["beginner", "intermediate", "advanced"])
    preferred_activities: List[str] = Field(..., min_items=1)
    notification_settings: Dict[str, bool] = Field(
        default_factory=lambda: {
            "email_notifications": True,
            "push_notifications": False
        }
    )
    rate_limit: Optional[int] = Field(default=100)
    webhook_url: Optional[str] = None
    webhook_events: Optional[List[str]] = None

class GPTSubscriptionBase(BaseModel):
    """Base schema for GPT subscription."""
    gpt_id: str
    status: str = Field(..., enum=["active", "inactive", "paused"])
    preferences: GPTPreferences
    version: Optional[str] = None
    categories: Optional[List[str]] = None

class GPTSubscriptionCreate(GPTSubscriptionBase):
    """Schema for creating a new GPT subscription."""
    pass

class GPTSubscriptionUpdate(GPTSubscriptionBase):
    """Schema for updating an existing GPT subscription."""
    pass

class GPTSubscriptionResponse(GPTSubscriptionBase):
    """Schema for GPT subscription response."""
    id: str
    user_id: str
    subscription_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
    usage_count: int
    last_used: Optional[datetime]
    shared_with: List[str] = []

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    """Base schema for project."""
    name: str
    description: Optional[str] = None
    active_gpt_id: Optional[str] = None
    configuration: Dict = Field(default_factory=dict)
    status: str = Field(..., enum=["active", "inactive", "archived"])
    team_id: Optional[str] = None
    is_template: bool = False

class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass

class ProjectUpdate(ProjectBase):
    """Schema for updating an existing project."""
    pass

class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    team: Optional["TeamResponse"] = None
    comments: List["CommentResponse"] = []

    class Config:
        from_attributes = True

class GPTPerformanceMetrics(BaseModel):
    """Schema for GPT performance metrics."""
    response_times: Dict[str, float]
    accuracy_metrics: Dict[str, float]
    usage_patterns: Dict[str, int]
    error_rate: float
    total_usage: int

class GPTPerformanceResponse(BaseModel):
    """Schema for GPT performance response."""
    id: str
    subscription_id: str
    metrics: GPTPerformanceMetrics
    timestamp: datetime
    response_time: float
    error_rate: float
    usage_count: int

    class Config:
        from_attributes = True

class FeedbackBase(BaseModel):
    """Base schema for feedback."""
    gpt_id: str
    feedback_type: str = Field(..., enum=["general", "bug", "feature", "performance"])
    content: Dict
    rating: Optional[int] = Field(None, ge=1, le=5)
    status: str = Field(default="open", enum=["open", "in_progress", "resolved", "closed"])
    priority: Optional[str] = Field(None, enum=["low", "medium", "high", "critical"])

class FeedbackCreate(FeedbackBase):
    """Schema for creating new feedback."""
    pass

class FeedbackResponse(FeedbackBase):
    """Schema for feedback response."""
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardAnalyticsMetrics(BaseModel):
    """Schema for dashboard analytics metrics."""
    usage_stats: Dict[str, int]
    performance_metrics: Dict[str, float]
    gpt_activity: Dict[str, int]
    gpt_usage: Dict[str, Dict[str, int]]
    api_calls: Dict[str, int]
    error_logs: List[Dict[str, str]]

class DashboardAnalyticsResponse(BaseModel):
    """Schema for dashboard analytics response."""
    id: str
    user_id: str
    metrics: DashboardAnalyticsMetrics
    timestamp: datetime
    period: str = Field(..., enum=["daily", "weekly", "monthly"])

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    """Base schema for user."""
    email: EmailStr
    subscription_status: str = Field(..., enum=["active", "inactive", "trial"])
    role: UserRole = Field(default=UserRole.USER)
    user_type: str
    billing_tier: str
    is_active: bool
    preferences: Dict = Field(default_factory=dict)

class UserCreate(UserBase):
    """Schema for creating a new user."""
    organization_id: Optional[str] = None
    department_id: Optional[str] = None

class UserUpdate(UserBase):
    """Schema for updating an existing user."""
    pass

class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    credits_balance: float
    organization: Optional["OrganizationResponse"] = None
    department: Optional["DepartmentResponse"] = None
    ai_suite: Optional["AISuiteResponse"] = None
    assigned_tools: List["AIToolResponse"] = []

    class Config:
        from_attributes = True

# New schemas for additional features
class CategoryBase(BaseModel):
    """Base schema for GPT categories."""
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass

class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: str
    created_at: datetime
    gpt_count: int

    class Config:
        from_attributes = True

class GPTVersionBase(BaseModel):
    """Base schema for GPT versions."""
    version_number: str
    configuration: Dict
    is_active: bool = False

class GPTVersionCreate(GPTVersionBase):
    """Schema for creating a new GPT version."""
    pass

class GPTVersionResponse(GPTVersionBase):
    """Schema for GPT version response."""
    id: str
    subscription_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WebhookBase(BaseModel):
    """Base schema for webhooks."""
    url: str
    events: List[str]
    is_active: bool = True

class WebhookCreate(WebhookBase):
    """Schema for creating a new webhook."""
    pass

class WebhookResponse(WebhookBase):
    """Schema for webhook response."""
    id: str
    subscription_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TeamBase(BaseModel):
    """Base schema for teams."""
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    """Schema for creating a new team."""
    pass

class TeamResponse(TeamBase):
    """Schema for team response."""
    id: str
    created_at: datetime
    updated_at: datetime
    member_count: int
    project_count: int

    class Config:
        from_attributes = True

class TeamMemberBase(BaseModel):
    """Base schema for team members."""
    role: str = Field(..., enum=["owner", "admin", "member"])
    user_id: str

class TeamMemberCreate(TeamMemberBase):
    """Schema for adding a team member."""
    pass

class TeamMemberResponse(TeamMemberBase):
    """Schema for team member response."""
    id: str
    team_id: str
    joined_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    """Base schema for comments."""
    content: str

class CommentCreate(CommentBase):
    """Schema for creating a new comment."""
    pass

class CommentResponse(CommentBase):
    """Schema for comment response."""
    id: str
    project_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict
    created_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True

# New schemas for AI Suite
class AISuiteBase(BaseModel):
    """Base schema for AI suite."""
    name: str
    description: Optional[str] = None
    configuration: Dict = Field(default_factory=dict)
    is_active: bool = True

class AISuiteCreate(AISuiteBase):
    """Schema for creating a new AI suite."""
    pass

class AISuiteUpdate(AISuiteBase):
    """Schema for updating an AI suite."""
    pass

class AISuiteResponse(AISuiteBase):
    """Schema for AI suite response."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    tools: List["AIToolResponse"] = []

    class Config:
        from_attributes = True

# New schemas for AI Tools
class AIToolBase(BaseModel):
    """Base schema for AI tool."""
    name: str
    description: Optional[str] = None
    tool_type: str
    version: Optional[str] = None
    configuration: Dict = Field(default_factory=dict)
    pricing_tier: str
    credits_cost: float = Field(ge=0)
    is_active: bool = True
    requires_approval: bool = False

class AIToolCreate(AIToolBase):
    """Schema for creating a new AI tool."""
    suite_id: Optional[str] = None

class AIToolUpdate(AIToolBase):
    """Schema for updating an AI tool."""
    pass

class AIToolResponse(AIToolBase):
    """Schema for AI tool response."""
    id: str
    created_at: datetime
    updated_at: datetime
    suite: Optional[AISuiteResponse] = None
    marketplace_listing: Optional["MarketplaceListingResponse"] = None
    usage_stats: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

# New schemas for Marketplace
class MarketplaceListingBase(BaseModel):
    """Base schema for marketplace listing."""
    title: str
    description: str
    features: List[str] = Field(default_factory=list)
    pricing_details: Dict = Field(default_factory=dict)
    category: str
    tags: List[str] = Field(default_factory=list)
    preview_url: Optional[HttpUrl] = None
    documentation_url: Optional[HttpUrl] = None
    is_featured: bool = False
    is_public: bool = True

class MarketplaceListingCreate(MarketplaceListingBase):
    """Schema for creating a new marketplace listing."""
    tool_id: str

class MarketplaceListingUpdate(MarketplaceListingBase):
    """Schema for updating a marketplace listing."""
    pass

class MarketplaceListingResponse(MarketplaceListingBase):
    """Schema for marketplace listing response."""
    id: str
    tool_id: str
    created_at: datetime
    updated_at: datetime
    tool: AIToolResponse

    model_config = ConfigDict(from_attributes=True)

# New schemas for Tool Usage Logging
class ToolUsageLogBase(BaseModel):
    """Base schema for tool usage log."""
    session_id: Optional[str] = None
    module_id: Optional[str] = None
    action: str
    parameters: Dict = Field(default_factory=dict)
    status: Optional[str] = None
    error_message: Optional[str] = None

class ToolUsageLogCreate(ToolUsageLogBase):
    """Schema for creating a new tool usage log."""
    tool_id: str

class ToolUsageLogResponse(ToolUsageLogBase):
    """Schema for tool usage log response."""
    id: str
    user_id: str
    tool_id: str
    credits_used: float
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    tool: AIToolResponse
    user: UserResponse

    class Config:
        from_attributes = True

# New schemas for Organizations
class OrganizationBase(BaseModel):
    """Base schema for organization."""
    name: str
    type: str
    subscription_tier: str
    settings: Dict = Field(default_factory=dict)

class OrganizationCreate(OrganizationBase):
    """Schema for creating a new organization."""
    pass

class OrganizationUpdate(OrganizationBase):
    """Schema for updating an organization."""
    pass

class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""
    id: int
    credits_balance: float
    created_at: datetime
    updated_at: datetime
    departments: List["DepartmentResponse"] = []
    user_count: int

    class Config:
        from_attributes = True

# New schemas for Departments
class DepartmentBase(BaseModel):
    """Base schema for department."""
    name: str
    description: Optional[str] = None
    settings: Dict = Field(default_factory=dict)

class DepartmentCreate(DepartmentBase):
    """Schema for creating a new department."""
    organization_id: str

class DepartmentUpdate(DepartmentBase):
    """Schema for updating a department."""
    pass

class DepartmentResponse(DepartmentBase):
    """Schema for department response."""
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime
    organization: OrganizationResponse
    user_count: int

    class Config:
        from_attributes = True

# New schemas for Tool Assignment
class ToolAssignmentBase(BaseModel):
    """Base schema for tool assignment."""
    permissions: Dict = Field(default_factory=dict)
    expires_at: Optional[datetime] = None

class ToolAssignmentCreate(ToolAssignmentBase):
    """Schema for creating a new tool assignment."""
    tool_id: str
    user_id: str

class ToolAssignmentResponse(ToolAssignmentBase):
    """Schema for tool assignment response."""
    tool_id: str
    user_id: str
    assigned_by: str
    assigned_at: datetime
    tool: AIToolResponse
    user: UserResponse

    class Config:
        from_attributes = True 