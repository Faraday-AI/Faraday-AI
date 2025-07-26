"""
Organization Management Service

This module provides comprehensive organization management functionality
including CRUD operations, member management, and organization hierarchy.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Depends

from app.models.organization.base.organization_management import (
    Organization,
    OrganizationMember,
    OrganizationRole,
    Department,
    DepartmentMember
)
from app.models.core.user import User
from app.core.database import get_db
from app.schemas.organization_management import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationMemberCreate,
    OrganizationMemberUpdate,
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)


class OrganizationManagementService:
    """Service for managing organizations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_organization_by_id(self, org_id: int) -> Optional[Organization]:
        """Get organization by ID."""
        return self.db.query(Organization).filter(Organization.id == org_id).first()
    
    def get_organization_by_name(self, name: str) -> Optional[Organization]:
        """Get organization by name."""
        return self.db.query(Organization).filter(Organization.name == name).first()
    
    def get_all_organizations(self) -> List[Organization]:
        """Get all organizations."""
        return self.db.query(Organization).all()
    
    def get_active_organizations(self) -> List[Organization]:
        """Get all active organizations."""
        return self.db.query(Organization).filter(Organization.status == "active").all()
    
    def create_organization(self, org_data: OrganizationCreate) -> Organization:
        """Create a new organization."""
        # Check if organization already exists
        existing_org = self.get_organization_by_name(org_data.name)
        if existing_org:
            raise HTTPException(status_code=400, detail="Organization already exists")
        
        # Create new organization
        organization = Organization(
            name=org_data.name,
            type=org_data.type,
            subscription_tier=org_data.subscription_tier,
            settings_data=org_data.settings_data,
            credits_balance=org_data.credits_balance or 0
        )
        
        try:
            self.db.add(organization)
            self.db.commit()
            self.db.refresh(organization)
            return organization
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to create organization")
    
    def update_organization(self, org_id: int, org_data: OrganizationUpdate) -> Organization:
        """Update organization."""
        organization = self.get_organization_by_id(org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Update organization fields
        update_data = org_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(organization, field, value)
        
        organization.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(organization)
            return organization
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update organization")
    
    def delete_organization(self, org_id: int) -> bool:
        """Delete organization."""
        organization = self.get_organization_by_id(org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Check if organization has members
        if organization.members:
            raise HTTPException(status_code=400, detail="Cannot delete organization with members")
        
        try:
            self.db.delete(organization)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to delete organization")
    
    def add_member_to_organization(self, org_id: int, member_data: OrganizationMemberCreate) -> OrganizationMember:
        """Add member to organization."""
        organization = self.get_organization_by_id(org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        user = self.db.query(User).filter(User.id == member_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is already a member
        existing_member = self.db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == member_data.user_id
        ).first()
        
        if existing_member:
            raise HTTPException(status_code=400, detail="User is already a member of this organization")
        
        # Get or create role
        role = None
        if member_data.role_id:
            role = self.db.query(OrganizationRole).filter(OrganizationRole.id == member_data.role_id).first()
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")
        
        # Create member
        member = OrganizationMember(
            organization_id=org_id,
            user_id=member_data.user_id,
            role_id=member_data.role_id,
            permissions=member_data.permissions
        )
        
        try:
            self.db.add(member)
            self.db.commit()
            self.db.refresh(member)
            return member
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to add member to organization")
    
    def remove_member_from_organization(self, org_id: int, user_id: int) -> bool:
        """Remove member from organization."""
        member = self.db.query(OrganizationMember).filter(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        try:
            self.db.delete(member)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to remove member from organization")
    
    def get_organization_members(self, org_id: int) -> List[OrganizationMember]:
        """Get all members of an organization."""
        organization = self.get_organization_by_id(org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return list(organization.members)
    
    def get_user_organizations(self, user_id: int) -> List[Organization]:
        """Get all organizations a user belongs to."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        memberships = self.db.query(OrganizationMember).filter(
            OrganizationMember.user_id == user_id
        ).all()
        
        return [membership.organization for membership in memberships]
    
    def create_department(self, org_id: int, dept_data: DepartmentCreate) -> Department:
        """Create a new department in an organization."""
        organization = self.get_organization_by_id(org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        # Check if department already exists
        existing_dept = self.db.query(Department).filter(
            Department.organization_id == org_id,
            Department.name == dept_data.name
        ).first()
        
        if existing_dept:
            raise HTTPException(status_code=400, detail="Department already exists")
        
        # Create department
        department = Department(
            organization_id=org_id,
            name=dept_data.name,
            description=dept_data.description,
            settings=dept_data.settings
        )
        
        try:
            self.db.add(department)
            self.db.commit()
            self.db.refresh(department)
            return department
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to create department")
    
    def update_department(self, dept_id: int, dept_data: DepartmentUpdate) -> Department:
        """Update department."""
        department = self.db.query(Department).filter(Department.id == dept_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        # Update department fields
        update_data = dept_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(department, field, value)
        
        department.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(department)
            return department
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update department")
    
    def delete_department(self, dept_id: int) -> bool:
        """Delete department."""
        department = self.db.query(Department).filter(Department.id == dept_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        # Check if department has members
        if department.members:
            raise HTTPException(status_code=400, detail="Cannot delete department with members")
        
        try:
            self.db.delete(department)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to delete department")
    
    def add_member_to_department(self, dept_id: int, user_id: int, role: str = "member") -> DepartmentMember:
        """Add member to department."""
        department = self.db.query(Department).filter(Department.id == dept_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is already a member
        existing_member = self.db.query(DepartmentMember).filter(
            DepartmentMember.department_id == dept_id,
            DepartmentMember.user_id == user_id
        ).first()
        
        if existing_member:
            raise HTTPException(status_code=400, detail="User is already a member of this department")
        
        # Create member
        member = DepartmentMember(
            department_id=dept_id,
            user_id=user_id,
            role=role
        )
        
        try:
            self.db.add(member)
            self.db.commit()
            self.db.refresh(member)
            return member
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to add member to department")
    
    def remove_member_from_department(self, dept_id: int, user_id: int) -> bool:
        """Remove member from department."""
        member = self.db.query(DepartmentMember).filter(
            DepartmentMember.department_id == dept_id,
            DepartmentMember.user_id == user_id
        ).first()
        
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        try:
            self.db.delete(member)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=400, detail="Failed to remove member from department")
    
    def get_department_members(self, dept_id: int) -> List[DepartmentMember]:
        """Get all members of a department."""
        department = self.db.query(Department).filter(Department.id == dept_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        return list(department.members)
    
    def get_organization_departments(self, org_id: int) -> List[Department]:
        """Get all departments in an organization."""
        organization = self.get_organization_by_id(org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return list(organization.departments)
    
    def get_organization_summary(self, org_id: int) -> Dict[str, Any]:
        """Get comprehensive organization summary."""
        organization = self.get_organization_by_id(org_id)
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return {
            "id": organization.id,
            "name": organization.name,
            "type": organization.type,
            "subscription_tier": organization.subscription_tier,
            "credits_balance": float(organization.credits_balance) if organization.credits_balance else 0,
            "member_count": len(organization.members),
            "department_count": len(organization.departments),
            "created_at": organization.created_at.isoformat() if organization.created_at else None,
            "updated_at": organization.updated_at.isoformat() if organization.updated_at else None
        }


def get_organization_management_service(db: Session = Depends(get_db)) -> OrganizationManagementService:
    """Dependency to get organization management service."""
    return OrganizationManagementService(db) 