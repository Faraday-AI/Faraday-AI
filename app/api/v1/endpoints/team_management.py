"""
Team Management API Endpoints

This module provides API endpoints for team management.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.core.user import User
from app.services.user.team_management_service import TeamManagementService, get_team_management_service
from app.schemas.team_management import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamSummary,
    TeamSearch,
    TeamFilter,
    TeamBulkOperation,
    TeamMemberBulkOperation
)

router = APIRouter()


@router.get("/teams", response_model=List[TeamResponse])
async def get_all_teams(
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Get all teams."""
    # Check if user has permission to view teams
    if not team_service.check_user_resource_permission(current_user.id, "team", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return team_service.get_all_teams()


@router.get("/teams/active", response_model=List[TeamResponse])
async def get_active_teams(
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Get all active teams."""
    return team_service.get_active_teams()


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team_by_id(
    team_id: int,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Get team by ID."""
    team = team_service.get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return team


@router.post("/teams", response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Create a new team."""
    # Check if user has permission to create teams
    if not team_service.check_user_resource_permission(current_user.id, "team", "create"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return team_service.create_team(team_data)


@router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Update team."""
    # Check if user has permission to update teams
    if not team_service.check_user_resource_permission(current_user.id, "team", "write"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return team_service.update_team(team_id, team_data)


@router.delete("/teams/{team_id}")
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Delete team."""
    # Check if user has permission to delete teams
    if not team_service.check_user_resource_permission(current_user.id, "team", "delete"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = team_service.delete_team(team_id)
    return {"message": "Team deleted successfully"}


@router.post("/teams/{team_id}/members", response_model=TeamMemberResponse)
async def add_member_to_team(
    team_id: int,
    member_data: TeamMemberCreate,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Add member to team."""
    # Check if user has permission to manage team members
    if not team_service.check_user_resource_permission(current_user.id, "team", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return team_service.add_member_to_team(team_id, member_data)


@router.delete("/teams/{team_id}/members/{user_id}")
async def remove_member_from_team(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Remove member from team."""
    # Check if user has permission to manage team members
    if not team_service.check_user_resource_permission(current_user.id, "team", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = team_service.remove_member_from_team(team_id, user_id)
    return {"message": "Member removed successfully"}


@router.put("/teams/{team_id}/members/{user_id}/role")
async def update_team_member_role(
    team_id: int,
    user_id: int,
    new_role: str,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Update team member role."""
    # Check if user has permission to manage team members
    if not team_service.check_user_resource_permission(current_user.id, "team", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    member = team_service.update_team_member_role(team_id, user_id, new_role)
    return {"message": "Member role updated successfully"}


@router.get("/teams/{team_id}/members", response_model=List[TeamMemberResponse])
async def get_team_members(
    team_id: int,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Get all members of a team."""
    return team_service.get_team_members(team_id)


@router.get("/users/{user_id}/teams", response_model=List[TeamResponse])
async def get_user_teams(
    user_id: int,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Get all teams a user belongs to."""
    # Users can view their own teams, admins can view any user's teams
    if user_id != current_user.id and not team_service.check_user_resource_permission(current_user.id, "user", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return team_service.get_user_teams(user_id)


@router.get("/teams/{team_id}/summary", response_model=TeamSummary)
async def get_team_summary(
    team_id: int,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Get comprehensive team summary."""
    return team_service.get_team_summary(team_id)


@router.post("/teams/search", response_model=List[TeamResponse])
async def search_teams(
    search: TeamSearch,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Search teams."""
    # Check if user has permission to view teams
    if not team_service.check_user_resource_permission(current_user.id, "team", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return team_service.search_teams(search.query, search.limit)


@router.post("/teams/filter", response_model=List[TeamSummary])
async def filter_teams(
    filter_data: TeamFilter,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Filter teams."""
    # Check if user has permission to view teams
    if not team_service.check_user_resource_permission(current_user.id, "team", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    teams = team_service.get_all_teams()
    
    # Apply filters
    if filter_data.name_contains:
        teams = [team for team in teams if filter_data.name_contains.lower() in team.name.lower()]
    
    if filter_data.is_active is not None:
        teams = [team for team in teams if team.is_active == filter_data.is_active]
    
    if filter_data.min_members is not None:
        teams = [team for team in teams if len(team.members) >= filter_data.min_members]
    
    if filter_data.max_members is not None:
        teams = [team for team in teams if len(team.members) <= filter_data.max_members]
    
    if filter_data.has_role:
        teams = [team for team in teams if any(member.role == filter_data.has_role for member in team.members)]
    
    if filter_data.created_after:
        teams = [team for team in teams if team.created_at >= filter_data.created_after]
    
    if filter_data.created_before:
        teams = [team for team in teams if team.created_at <= filter_data.created_before]
    
    return [
        TeamSummary(
            id=team.id,
            name=team.name,
            description=team.description,
            is_active=team.is_active,
            member_count=len(team.members),
            role_distribution={},
            created_at=team.created_at,
            updated_at=team.updated_at
        )
        for team in teams
    ]


@router.post("/teams/bulk-operations")
async def bulk_team_operations(
    operation: TeamBulkOperation,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Perform bulk operations on teams."""
    # Check if user has permission to manage teams
    if not team_service.check_user_resource_permission(current_user.id, "team", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    results = {
        "success": [],
        "failed": []
    }
    
    for team_id in operation.team_ids:
        try:
            if operation.operation == "activate":
                team_service.update_team(team_id, TeamUpdate(is_active=True))
            elif operation.operation == "deactivate":
                team_service.update_team(team_id, TeamUpdate(is_active=False))
            elif operation.operation == "delete":
                team_service.delete_team(team_id)
            
            results["success"].append(team_id)
        except Exception as e:
            results["failed"].append({
                "team_id": team_id,
                "error": str(e)
            })
    
    return {
        "message": f"Bulk operation completed. {len(results['success'])} successful, {len(results['failed'])} failed",
        "results": results
    }


@router.post("/teams/{team_id}/bulk-members")
async def bulk_team_member_operations(
    team_id: int,
    operation: TeamMemberBulkOperation,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Perform bulk operations on team members."""
    # Check if user has permission to manage team members
    if not team_service.check_user_resource_permission(current_user.id, "team", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if operation.operation == "add":
        results = team_service.bulk_add_members(team_id, operation.user_ids, operation.data.get("role", "member"))
    else:
        results = {
            "success": [],
            "failed": []
        }
        
        for user_id in operation.user_ids:
            try:
                if operation.operation == "remove":
                    team_service.remove_member_from_team(team_id, user_id)
                elif operation.operation == "update_role":
                    new_role = operation.data.get("role", "member")
                    team_service.update_team_member_role(team_id, user_id, new_role)
                
                results["success"].append(user_id)
            except Exception as e:
                results["failed"].append({
                    "user_id": user_id,
                    "error": str(e)
                })
    
    return {
        "message": f"Bulk member operation completed. {len(results['success'])} successful, {len(results['failed'])} failed",
        "results": results
    }


@router.post("/teams/{team_id}/members/{user_id}/activity")
async def update_member_activity(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Update member's last activity timestamp."""
    # Users can update their own activity, admins can update any member's activity
    if user_id != current_user.id and not team_service.check_user_resource_permission(current_user.id, "team", "manage"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    success = team_service.update_member_activity(team_id, user_id)
    return {"message": "Activity updated successfully"}


@router.get("/teams/{team_id}/inactive-members")
async def get_inactive_members(
    team_id: int,
    days_inactive: int = 30,
    current_user: User = Depends(get_current_user),
    team_service: TeamManagementService = Depends(get_team_management_service)
):
    """Get team members who haven't been active for specified days."""
    # Check if user has permission to view team members
    if not team_service.check_user_resource_permission(current_user.id, "team", "read"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return team_service.get_inactive_members(team_id, days_inactive) 