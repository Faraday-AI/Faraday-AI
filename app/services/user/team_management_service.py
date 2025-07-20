"""
Team Management Service

This module provides comprehensive team management functionality
including CRUD operations, member management, and team collaboration.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.organization.team import Team, TeamMember
from app.models.core.user import User
from app.schemas.team_management import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamMemberCreate,
    TeamMemberUpdate,
    TeamInvitation
)


class TeamManagementService:
    """Service for managing teams."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_team_by_id(self, team_id: int) -> Optional[Team]:
        """Get team by ID."""
        return self.db.query(Team).filter(Team.id == team_id).first()
    
    def get_team_by_name(self, name: str) -> Optional[Team]:
        """Get team by name."""
        return self.db.query(Team).filter(Team.name == name).first()
    
    def get_all_teams(self) -> List[Team]:
        """Get all teams."""
        return self.db.query(Team).all()
    
    def get_active_teams(self) -> List[Team]:
        """Get all active teams."""
        return self.db.query(Team).filter(Team.is_active == True).all()
    
    def create_team(self, team_data: TeamCreate) -> Team:
        """Create a new team."""
        # Check if team already exists
        existing_team = self.get_team_by_name(team_data.name)
        if existing_team:
            raise HTTPException(status_code=400, detail="Team already exists")
        
        # Create new team
        team = Team(
            name=team_data.name,
            description=team_data.description,
            settings=team_data.settings,
            is_active=True
        )
        
        try:
            self.db.add(team)
            self.db.commit()
            self.db.refresh(team)
            return team
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to create team")
    
    def update_team(self, team_id: int, team_data: TeamUpdate) -> Team:
        """Update team."""
        team = self.get_team_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Update team fields
        update_data = team_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(team, field, value)
        
        team.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(team)
            return team
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update team")
    
    def delete_team(self, team_id: int) -> bool:
        """Delete team."""
        team = self.get_team_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Check if team has members
        if team.members:
            raise HTTPException(status_code=400, detail="Cannot delete team with members")
        
        try:
            self.db.delete(team)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to delete team")
    
    def add_member_to_team(self, team_id: int, member_data: TeamMemberCreate) -> TeamMember:
        """Add member to team."""
        team = self.get_team_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        user = self.db.query(User).filter(User.id == member_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is already a member
        existing_member = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == member_data.user_id
        ).first()
        
        if existing_member:
            raise HTTPException(status_code=400, detail="User is already a member of this team")
        
        # Create member
        member = TeamMember(
            team_id=team_id,
            user_id=member_data.user_id,
            role=member_data.role,
            permissions=member_data.permissions,
            joined_at=datetime.utcnow()
        )
        
        try:
            self.db.add(member)
            self.db.commit()
            self.db.refresh(member)
            return member
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to add member to team")
    
    def remove_member_from_team(self, team_id: int, user_id: int) -> bool:
        """Remove member from team."""
        member = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        try:
            self.db.delete(member)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to remove member from team")
    
    def update_team_member_role(self, team_id: int, user_id: int, new_role: str) -> TeamMember:
        """Update team member role."""
        member = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        member.role = new_role
        member.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(member)
            return member
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update member role")
    
    def get_team_members(self, team_id: int) -> List[TeamMember]:
        """Get all members of a team."""
        team = self.get_team_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return list(team.members)
    
    def get_user_teams(self, user_id: int) -> List[Team]:
        """Get all teams a user belongs to."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        memberships = self.db.query(TeamMember).filter(
            TeamMember.user_id == user_id
        ).all()
        
        return [membership.team for membership in memberships]
    
    def get_team_by_member_role(self, user_id: int, role: str) -> List[Team]:
        """Get teams where user has a specific role."""
        memberships = self.db.query(TeamMember).filter(
            TeamMember.user_id == user_id,
            TeamMember.role == role
        ).all()
        
        return [membership.team for membership in memberships]
    
    def update_member_activity(self, team_id: int, user_id: int) -> bool:
        """Update member's last activity timestamp."""
        member = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        member.last_active = datetime.utcnow()
        
        try:
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update member activity")
    
    def get_team_summary(self, team_id: int) -> Dict[str, Any]:
        """Get comprehensive team summary."""
        team = self.get_team_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Count members by role
        role_counts = {}
        for member in team.members:
            role = member.role
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "is_active": team.is_active,
            "member_count": len(team.members),
            "role_distribution": role_counts,
            "created_at": team.created_at.isoformat() if team.created_at else None,
            "updated_at": team.updated_at.isoformat() if team.updated_at else None
        }
    
    def search_teams(self, query: str, limit: int = 10) -> List[Team]:
        """Search teams by name or description."""
        teams = self.db.query(Team).filter(
            Team.name.ilike(f"%{query}%") | Team.description.ilike(f"%{query}%")
        ).limit(limit).all()
        
        return teams
    
    def get_inactive_members(self, team_id: int, days_inactive: int = 30) -> List[TeamMember]:
        """Get team members who haven't been active for specified days."""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        members = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            (TeamMember.last_active < cutoff_date) | (TeamMember.last_active.is_(None))
        ).all()
        
        return members
    
    def bulk_add_members(self, team_id: int, user_ids: List[int], role: str = "member") -> Dict[str, Any]:
        """Bulk add members to team."""
        results = {
            "success": [],
            "failed": []
        }
        
        for user_id in user_ids:
            try:
                member_data = TeamMemberCreate(
                    user_id=user_id,
                    role=role,
                    permissions=None
                )
                self.add_member_to_team(team_id, member_data)
                results["success"].append(user_id)
            except Exception as e:
                results["failed"].append({
                    "user_id": user_id,
                    "error": str(e)
                })
        
        return results


def get_team_management_service(db: Session) -> TeamManagementService:
    """Dependency to get team management service."""
    return TeamManagementService(db) 