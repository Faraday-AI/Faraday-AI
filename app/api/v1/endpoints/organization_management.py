"""
Organization Management API Endpoints

This module provides API endpoints for organization management.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.core.user import User
from app.services.user.organization_management_service import OrganizationManagementService, get_organization_management_service
from app.schemas.organization_management import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    OrganizationSummary,
    OrganizationSearch,
    OrganizationFilter
)

router = APIRouter()


@router.get("/organizations", response_model=List[OrganizationResponse])
async def get_all_organizations(
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Get all organizations."""
    # Check if user has permission to view organizations
    if not org_service.check_user_resource_permission(current_user.id, "organization", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return org_service.get_all_organizations()


@router.get("/organizations/active", response_model=List[OrganizationResponse])
async def get_active_organizations(
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Get all active organizations."""
    return org_service.get_active_organizations()


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization_by_id(
    org_id: int,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Get organization by ID."""
    organization = org_service.get_organization_by_id(org_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return organization


@router.post("/organizations", response_model=OrganizationResponse)
async def create_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Create a new organization."""
    # Check if user has permission to create organizations
    if not org_service.check_user_resource_permission(current_user.id, "organization", "create"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return org_service.create_organization(org_data)


@router.put("/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: int,
    org_data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Update organization."""
    # Check if user has permission to update organizations
    if not org_service.check_user_resource_permission(current_user.id, "organization", "write"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return org_service.update_organization(org_id, org_data)


@router.delete("/organizations/{org_id}")
async def delete_organization(
    org_id: int,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Delete organization."""
    # Check if user has permission to delete organizations
    if not org_service.check_user_resource_permission(current_user.id, "organization", "delete"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = org_service.delete_organization(org_id)
    return {"message": "Organization deleted successfully"}


@router.post("/organizations/{org_id}/members", response_model=OrganizationMemberResponse)
async def add_member_to_organization(
    org_id: int,
    member_data: OrganizationMemberCreate,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Add member to organization."""
    # Check if user has permission to manage organization members
    if not org_service.check_user_resource_permission(current_user.id, "organization", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return org_service.add_member_to_organization(org_id, member_data)


@router.delete("/organizations/{org_id}/members/{user_id}")
async def remove_member_from_organization(
    org_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Remove member from organization."""
    # Check if user has permission to manage organization members
    if not org_service.check_user_resource_permission(current_user.id, "organization", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = org_service.remove_member_from_organization(org_id, user_id)
    return {"message": "Member removed successfully"}


@router.get("/organizations/{org_id}/members", response_model=List[OrganizationMemberResponse])
async def get_organization_members(
    org_id: int,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Get all members of an organization."""
    return org_service.get_organization_members(org_id)


@router.get("/users/{user_id}/organizations", response_model=List[OrganizationResponse])
async def get_user_organizations(
    user_id: int,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Get all organizations a user belongs to."""
    # Users can view their own organizations, admins can view any user's organizations
    if user_id != current_user.id and not org_service.check_user_resource_permission(current_user.id, "user", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return org_service.get_user_organizations(user_id)


@router.post("/organizations/{org_id}/departments", response_model=DepartmentResponse)
async def create_department(
    org_id: int,
    dept_data: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Create a new department in an organization."""
    # Check if user has permission to manage departments
    if not org_service.check_user_resource_permission(current_user.id, "organization", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return org_service.create_department(org_id, dept_data)


@router.put("/departments/{dept_id}", response_model=DepartmentResponse)
async def update_department(
    dept_id: int,
    dept_data: DepartmentUpdate,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Update department."""
    # Check if user has permission to manage departments
    if not org_service.check_user_resource_permission(current_user.id, "organization", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return org_service.update_department(dept_id, dept_data)


@router.delete("/departments/{dept_id}")
async def delete_department(
    dept_id: int,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Delete department."""
    # Check if user has permission to manage departments
    if not org_service.check_user_resource_permission(current_user.id, "organization", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = org_service.delete_department(dept_id)
    return {"message": "Department deleted successfully"}


@router.post("/departments/{dept_id}/members")
async def add_member_to_department(
    dept_id: int,
    user_id: int,
    role: str = "member",
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Add member to department."""
    # Check if user has permission to manage departments
    if not org_service.check_user_resource_permission(current_user.id, "organization", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    member = org_service.add_member_to_department(dept_id, user_id, role)
    return {"message": "Member added to department successfully"}


@router.delete("/departments/{dept_id}/members/{user_id}")
async def remove_member_from_department(
    dept_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Remove member from department."""
    # Check if user has permission to manage departments
    if not org_service.check_user_resource_permission(current_user.id, "organization", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = org_service.remove_member_from_department(dept_id, user_id)
    return {"message": "Member removed from department successfully"}


@router.get("/departments/{dept_id}/members", response_model=List[DepartmentMemberResponse])
async def get_department_members(
    dept_id: int,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Get all members of a department."""
    return org_service.get_department_members(dept_id)


@router.get("/organizations/{org_id}/departments", response_model=List[DepartmentResponse])
async def get_organization_departments(
    org_id: int,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Get all departments in an organization."""
    return org_service.get_organization_departments(org_id)


@router.get("/organizations/{org_id}/summary", response_model=OrganizationSummary)
async def get_organization_summary(
    org_id: int,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Get comprehensive organization summary."""
    return org_service.get_organization_summary(org_id)


@router.post("/organizations/search", response_model=List[OrganizationResponse])
async def search_organizations(
    search: OrganizationSearch,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Search organizations."""
    # Check if user has permission to view organizations
    if not org_service.check_user_resource_permission(current_user.id, "organization", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    organizations = org_service.get_all_organizations()
    
    # Apply filters
    if search.query:
        organizations = [org for org in organizations if search.query.lower() in org.name.lower()]
    
    if search.type:
        organizations = [org for org in organizations if org.type == search.type]
    
    if search.subscription_tier:
        organizations = [org for org in organizations if org.subscription_tier == search.subscription_tier]
    
    return organizations[:search.limit]


@router.post("/organizations/filter", response_model=List[OrganizationSummary])
async def filter_organizations(
    filter_data: OrganizationFilter,
    current_user: User = Depends(get_current_user),
    org_service: OrganizationManagementService = Depends(get_organization_management_service)
):
    """Filter organizations."""
    # Check if user has permission to view organizations
    if not org_service.check_user_resource_permission(current_user.id, "organization", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    organizations = org_service.get_all_organizations()
    
    # Apply filters
    if filter_data.name_contains:
        organizations = [org for org in organizations if filter_data.name_contains.lower() in org.name.lower()]
    
    if filter_data.type:
        organizations = [org for org in organizations if org.type == filter_data.type]
    
    if filter_data.subscription_tier:
        organizations = [org for org in organizations if org.subscription_tier == filter_data.subscription_tier]
    
    if filter_data.min_members is not None:
        organizations = [org for org in organizations if len(org.members) >= filter_data.min_members]
    
    if filter_data.max_members is not None:
        organizations = [org for org in organizations if len(org.members) <= filter_data.max_members]
    
    if filter_data.min_credits is not None:
        organizations = [org for org in organizations if org.credits_balance >= filter_data.min_credits]
    
    if filter_data.max_credits is not None:
        organizations = [org for org in organizations if org.credits_balance <= filter_data.max_credits]
    
    return [
        OrganizationSummary(
            id=org.id,
            name=org.name,
            type=org.type,
            subscription_tier=org.subscription_tier,
            credits_balance=float(org.credits_balance) if org.credits_balance else 0,
            member_count=len(org.members),
            department_count=len(org.departments),
            created_at=org.created_at,
            updated_at=org.updated_at
        )
        for org in organizations
    ] 