"""
Resource Sharing Service

This module provides the service layer for handling resource sharing functionality
in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.core.user import User
from app.dashboard.models.organization_models import Organization, OrganizationResource
from app.core.security import verify_access
from app.core.logging import log_activity

class ResourceSharingService:
    def __init__(self, db: Session):
        self.db = db

    async def share_resource(
        self,
        source_org_id: str,
        target_org_id: str,
        resource_type: str,
        resource_id: str,
        access_level: str,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Share a resource with another organization.

        Args:
            source_org_id: ID of the source organization
            target_org_id: ID of the target organization
            resource_type: Type of resource being shared
            resource_id: ID of the resource
            access_level: Level of access to grant
            settings: Optional sharing settings
        """
        # Verify organizations exist
        source_org = self.db.query(Organization).filter(Organization.id == source_org_id).first()
        target_org = self.db.query(Organization).filter(Organization.id == target_org_id).first()
        if not source_org or not target_org:
            raise ValueError("Invalid organization ID")

        # Create sharing record
        sharing_record = {
            "source_org_id": source_org_id,
            "target_org_id": target_org_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "access_level": access_level,
            "settings": settings or {},
            "status": "active",
            "shared_at": datetime.utcnow()
        }

        # Log the sharing activity
        await log_activity(
            self.db,
            action="share_resource",
            resource_type=resource_type,
            resource_id=resource_id,
            details=sharing_record
        )

        return sharing_record

    async def get_shared_resources(
        self,
        org_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get resources shared with an organization.

        Args:
            org_id: Organization ID
            status: Optional status filter
        """
        # Build query filters
        filters = [
            or_(
                Organization.id == org_id,  # Resources shared by the org
                Organization.id == org_id   # Resources shared with the org
            )
        ]
        if status:
            filters.append(Organization.status == status)

        # Get sharing records
        sharing_records = []  # Query would go here
        return sharing_records

    async def update_shared_resource(
        self,
        share_id: str,
        status: str,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update a shared resource's status or settings.

        Args:
            share_id: ID of the sharing record
            status: New resource status
            settings: Updated resource settings
        """
        # Update sharing record
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if settings:
            update_data["settings"] = settings

        # Log the update
        await log_activity(
            self.db,
            action="update_shared_resource",
            resource_type="sharing_record",
            resource_id=share_id,
            details=update_data
        )

        return update_data

    async def get_sharing_metrics(
        self,
        org_id: str,
        time_range: str
    ) -> Dict[str, Any]:
        """
        Get resource sharing metrics for an organization.

        Args:
            org_id: Organization ID
            time_range: Time range for metrics
        """
        metrics = {
            "total_shared": 0,
            "total_received": 0,
            "by_resource_type": {},
            "by_access_level": {},
            "active_shares": 0,
            "sharing_patterns": [],
            "timestamp": datetime.utcnow()
        }
        return metrics

    async def share_resources_batch(
        self,
        source_org_id: str,
        sharing_requests: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Share multiple resources in a batch operation.

        Args:
            source_org_id: ID of the source organization
            sharing_requests: List of sharing requests
        """
        results = []
        for request in sharing_requests:
            try:
                result = await self.share_resource(
                    source_org_id=source_org_id,
                    target_org_id=request["target_org_id"],
                    resource_type=request["resource_type"],
                    resource_id=request["resource_id"],
                    access_level=request["access_level"],
                    settings=request.get("settings")
                )
                results.append({
                    "status": "success",
                    "request": request,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "status": "error",
                    "request": request,
                    "error": str(e)
                })
        return results

    async def update_resources_batch(
        self,
        updates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Update multiple shared resources in a batch operation.

        Args:
            updates: List of update requests
        """
        results = []
        for update in updates:
            try:
                result = await self.update_shared_resource(
                    share_id=update["share_id"],
                    status=update["status"],
                    settings=update.get("settings")
                )
                results.append({
                    "status": "success",
                    "update": update,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "status": "error",
                    "update": update,
                    "error": str(e)
                })
        return results

    async def get_resources_batch(
        self,
        org_ids: List[str],
        status: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get shared resources for multiple organizations.

        Args:
            org_ids: List of organization IDs
            status: Optional status filter
        """
        results = {}
        for org_id in org_ids:
            try:
                resources = await self.get_shared_resources(org_id, status)
                results[org_id] = resources
            except Exception as e:
                results[org_id] = {"error": str(e)}
        return results 