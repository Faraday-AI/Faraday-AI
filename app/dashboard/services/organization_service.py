"""
Organization Service

This module provides services for managing organizations and cross-organization collaboration
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..models.organization_models import (
    Organization,
    Department,
    OrganizationMember,
    DepartmentMember,
    OrganizationResource,
    OrganizationCollaboration
)
from ..models import DashboardUser

class OrganizationService:
    def __init__(self, db: Session):
        self.db = db

    async def create_organization(
        self,
        name: str,
        org_type: str,
        subscription_tier: str,
        settings: Optional[Dict] = None
    ) -> Dict:
        """Create a new organization."""
        try:
            org = Organization(
                name=name,
                type=org_type,
                subscription_tier=subscription_tier,
                settings=settings or {}
            )
            self.db.add(org)
            self.db.commit()
            self.db.refresh(org)
            return self._format_organization(org)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error creating organization: {str(e)}"
            )

    async def get_organization(self, org_id: int) -> Dict:
        """Get organization details."""
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return self._format_organization(org)

    async def update_organization(
        self,
        org_id: str,
        name: Optional[str] = None,
        org_type: Optional[str] = None,
        subscription_tier: Optional[str] = None,
        settings: Optional[Dict] = None
    ) -> Dict:
        """Update organization details."""
        try:
            org = self.db.query(Organization).filter(Organization.id == org_id).first()
            if not org:
                raise HTTPException(status_code=404, detail="Organization not found")

            if name:
                org.name = name
            if org_type:
                org.type = org_type
            if subscription_tier:
                org.subscription_tier = subscription_tier
            if settings:
                org.settings = {**org.settings, **settings}

            org.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(org)
            return self._format_organization(org)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating organization: {str(e)}"
            )

    async def add_member(
        self,
        org_id: str,
        user_id: str,
        role: str,
        permissions: Optional[Dict] = None
    ) -> Dict:
        """Add a member to an organization."""
        try:
            # Check if user exists
            user = self.db.query(DashboardUser).filter(DashboardUser.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Check if already a member
            existing_member = self.db.query(OrganizationMember).filter(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user_id
            ).first()
            if existing_member:
                raise HTTPException(
                    status_code=400,
                    detail="User is already a member of this organization"
                )

            member = OrganizationMember(
                id=str(uuid.uuid4()),
                organization_id=org_id,
                user_id=user_id,
                role=role,
                permissions=permissions or {},
                status="active"
            )
            self.db.add(member)
            self.db.commit()
            self.db.refresh(member)
            return self._format_member(member)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error adding member: {str(e)}"
            )

    async def create_department(
        self,
        org_id: str,
        name: str,
        description: Optional[str] = None,
        settings: Optional[Dict] = None
    ) -> Dict:
        """Create a new department in an organization."""
        try:
            department = Department(
                id=str(uuid.uuid4()),
                organization_id=org_id,
                name=name,
                description=description,
                settings=settings or {}
            )
            self.db.add(department)
            self.db.commit()
            self.db.refresh(department)
            return self._format_department(department)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error creating department: {str(e)}"
            )

    async def initiate_collaboration(
        self,
        source_org_id: str,
        target_org_id: str,
        collab_type: str,
        settings: Optional[Dict] = None
    ) -> Dict:
        """Initiate collaboration between organizations."""
        try:
            # Verify organizations exist
            source_org = self.db.query(Organization).filter(
                Organization.id == source_org_id
            ).first()
            target_org = self.db.query(Organization).filter(
                Organization.id == target_org_id
            ).first()

            if not source_org or not target_org:
                raise HTTPException(
                    status_code=404,
                    detail="One or both organizations not found"
                )

            collaboration = OrganizationCollaboration(
                id=str(uuid.uuid4()),
                source_org_id=source_org_id,
                target_org_id=target_org_id,
                type=collab_type,
                status="pending",
                settings=settings or {}
            )
            self.db.add(collaboration)
            self.db.commit()
            self.db.refresh(collaboration)
            return self._format_collaboration(collaboration)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error initiating collaboration: {str(e)}"
            )

    async def get_collaborations(
        self,
        org_id: str,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get organization's collaborations."""
        try:
            query = self.db.query(OrganizationCollaboration).filter(
                (OrganizationCollaboration.source_org_id == org_id) |
                (OrganizationCollaboration.target_org_id == org_id)
            )
            
            if status:
                query = query.filter(OrganizationCollaboration.status == status)
                
            collaborations = query.all()
            return [self._format_collaboration(c) for c in collaborations]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving collaborations: {str(e)}"
            )

    async def update_collaboration_status(
        self,
        collaboration_id: str,
        status: str
    ) -> Dict:
        """Update collaboration status."""
        try:
            collaboration = self.db.query(OrganizationCollaboration).filter(
                OrganizationCollaboration.id == collaboration_id
            ).first()
            
            if not collaboration:
                raise HTTPException(
                    status_code=404,
                    detail="Collaboration not found"
                )
                
            collaboration.status = status
            collaboration.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(collaboration)
            return self._format_collaboration(collaboration)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error updating collaboration status: {str(e)}"
            )

    def _format_organization(self, org: Organization) -> Dict:
        """Format organization data."""
        return {
            "id": org.id,
            "name": org.name,
            "type": org.type,
            "subscription_tier": org.subscription_tier,
            "settings": org.settings,
            "created_at": org.created_at.isoformat(),
            "updated_at": org.updated_at.isoformat()
        }

    def _format_member(self, member: OrganizationMember) -> Dict:
        """Format member data."""
        return {
            "id": member.id,
            "organization_id": member.organization_id,
            "user_id": member.user_id,
            "role": member.role,
            "permissions": member.permissions,
            "status": member.status,
            "created_at": member.created_at.isoformat(),
            "updated_at": member.updated_at.isoformat()
        }

    def _format_department(self, department: Department) -> Dict:
        """Format department data."""
        return {
            "id": department.id,
            "organization_id": department.organization_id,
            "name": department.name,
            "description": department.description,
            "settings": department.settings,
            "created_at": department.created_at.isoformat(),
            "updated_at": department.updated_at.isoformat()
        }

    def _format_collaboration(self, collab: OrganizationCollaboration) -> Dict:
        """Format collaboration data."""
        return {
            "id": collab.id,
            "source_org_id": collab.source_org_id,
            "target_org_id": collab.target_org_id,
            "type": collab.type,
            "status": collab.status,
            "settings": collab.settings,
            "created_at": collab.created_at.isoformat(),
            "updated_at": collab.updated_at.isoformat()
        } 