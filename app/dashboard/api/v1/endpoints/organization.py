"""
Organization API Endpoints

This module provides the API endpoints for managing organizations and cross-organization
collaboration in the Faraday AI Dashboard.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....dependencies import get_db, get_current_user
from ....services.organization_service import OrganizationService
from ....services.resource_sharing_service import ResourceSharingService
from ....schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    MemberCreate,
    MemberResponse,
    DepartmentCreate,
    DepartmentResponse,
    CollaborationCreate,
    CollaborationResponse,
    SharedResourceUpdate
)
from ....schemas.collaboration import (
    ResourceSharingRequest,
    ResourceSharingMetrics,
    BatchResourceSharingRequest,
    BatchResourceUpdateRequest,
    BatchResourcesRequest,
    BatchOperationResponse
)

router = APIRouter()

@router.post("/organizations", response_model=OrganizationResponse)
async def create_organization(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization: OrganizationCreate
):
    """Create a new organization."""
    org_service = OrganizationService(db)
    return await org_service.create_organization(
        name=organization.name,
        org_type=organization.type,
        subscription_tier=organization.subscription_tier,
        settings=organization.settings
    )

@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get organization details."""
    org_service = OrganizationService(db)
    return await org_service.get_organization(org_id)

@router.put("/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    organization: OrganizationUpdate
):
    """Update organization details."""
    org_service = OrganizationService(db)
    return await org_service.update_organization(
        org_id=org_id,
        name=organization.name,
        org_type=organization.type,
        subscription_tier=organization.subscription_tier,
        settings=organization.settings
    )

@router.post("/organizations/{org_id}/members", response_model=MemberResponse)
async def add_organization_member(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    member: MemberCreate
):
    """Add a member to an organization."""
    org_service = OrganizationService(db)
    return await org_service.add_member(
        org_id=org_id,
        user_id=member.user_id,
        role=member.role,
        permissions=member.permissions
    )

@router.post("/organizations/{org_id}/departments", response_model=DepartmentResponse)
async def create_department(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    department: DepartmentCreate
):
    """Create a new department in an organization."""
    org_service = OrganizationService(db)
    return await org_service.create_department(
        org_id=org_id,
        name=department.name,
        description=department.description,
        settings=department.settings
    )

@router.post("/collaborations", response_model=CollaborationResponse)
async def initiate_collaboration(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    collaboration: CollaborationCreate
):
    """Initiate collaboration between organizations."""
    org_service = OrganizationService(db)
    return await org_service.initiate_collaboration(
        source_org_id=collaboration.source_org_id,
        target_org_id=collaboration.target_org_id,
        collab_type=collaboration.type,
        settings=collaboration.settings
    )

@router.get("/organizations/{org_id}/collaborations", response_model=List[CollaborationResponse])
async def get_organization_collaborations(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by collaboration status")
):
    """Get organization's collaborations."""
    org_service = OrganizationService(db)
    return await org_service.get_collaborations(
        org_id=org_id,
        status=status
    )

@router.put("/collaborations/{collaboration_id}/status", response_model=CollaborationResponse)
async def update_collaboration_status(
    collaboration_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    status: str = Query(..., description="New collaboration status")
):
    """Update collaboration status."""
    org_service = OrganizationService(db)
    return await org_service.update_collaboration_status(
        collaboration_id=collaboration_id,
        status=status
    )

@router.post("/organizations/{org_id}/share-resource", response_model=Dict[str, Any])
async def share_resource(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: ResourceSharingRequest
):
    """Share a resource with another organization."""
    sharing_service = ResourceSharingService(db)
    return await sharing_service.share_resource(
        source_org_id=org_id,
        target_org_id=request.target_org_id,
        resource_type=request.resource_type,
        resource_id=request.resource_id,
        access_level=request.access_level,
        settings=request.settings
    )

@router.get("/organizations/{org_id}/shared-resources", response_model=List[Dict[str, Any]])
async def get_shared_resources(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by resource status")
):
    """Get resources shared with an organization."""
    sharing_service = ResourceSharingService(db)
    return await sharing_service.get_shared_resources(
        org_id=org_id,
        status=status
    )

@router.put("/organizations/{org_id}/shared-resources/{share_id}", response_model=Dict[str, Any])
async def update_shared_resource(
    org_id: str,
    share_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    update: SharedResourceUpdate
):
    """Update a shared resource's status or settings."""
    sharing_service = ResourceSharingService(db)
    return await sharing_service.update_shared_resource(
        share_id=share_id,
        status=update.status,
        settings=update.settings
    )

@router.get("/organizations/{org_id}/sharing-metrics", response_model=ResourceSharingMetrics)
async def get_sharing_metrics(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    time_range: str = Query("24h", description="Time range for metrics (e.g., 24h, 7d, 30d)")
):
    """Get resource sharing metrics for an organization."""
    sharing_service = ResourceSharingService(db)
    return await sharing_service.get_sharing_metrics(
        org_id=org_id,
        time_range=time_range
    )

@router.post("/organizations/{org_id}/share-resources-batch", response_model=BatchOperationResponse)
async def share_resources_batch(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: BatchResourceSharingRequest
):
    """
    Share multiple resources with other organizations in a single batch operation.

    Args:
        org_id: The ID of the source organization
        request: Batch resource sharing request containing multiple sharing requests
    """
    sharing_service = ResourceSharingService(db)
    
    try:
        # Execute batch sharing operation
        results = await sharing_service.share_resources_batch(
            source_org_id=org_id,
            sharing_requests=request.sharing_requests
        )

        # Get performance metrics
        metrics = await sharing_service.performance_service.get_performance_metrics()

        return BatchOperationResponse(
            results=results,
            metrics={
                "batch_size": len(request.sharing_requests),
                "processing_time": metrics["batch_operations"]["average_processing_time"],
                "success_rate": metrics["batch_operations"]["average_success_rate"],
                "cache_hits": metrics["cache_operations"]["hits"]
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch resource sharing: {str(e)}"
        )

@router.put("/organizations/{org_id}/shared-resources-batch", response_model=BatchOperationResponse)
async def update_resources_batch(
    org_id: str,
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: BatchResourceUpdateRequest
):
    """
    Update multiple shared resources in a single batch operation.

    Args:
        org_id: The ID of the organization
        request: Batch resource update request containing multiple update requests
    """
    sharing_service = ResourceSharingService(db)
    
    try:
        # Execute batch update operation
        results = await sharing_service.update_resources_batch(
            updates=request.updates
        )

        # Get performance metrics
        metrics = await sharing_service.performance_service.get_performance_metrics()

        return BatchOperationResponse(
            results=results,
            metrics={
                "batch_size": len(request.updates),
                "processing_time": metrics["batch_operations"]["average_processing_time"],
                "success_rate": metrics["batch_operations"]["average_success_rate"],
                "cache_hits": metrics["cache_operations"]["hits"]
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch resource update: {str(e)}"
        )

@router.post("/organizations/shared-resources-batch", response_model=Dict[str, List[Dict[str, Any]]])
async def get_resources_batch(
    *,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    request: BatchResourcesRequest
):
    """
    Get shared resources for multiple organizations in a single batch operation.

    Args:
        request: Batch resources request containing list of organization IDs and optional status filter
    """
    sharing_service = ResourceSharingService(db)
    
    try:
        # Execute batch get operation
        results = await sharing_service.get_resources_batch(
            org_ids=request.org_ids,
            status=request.status
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch resource retrieval: {str(e)}"
        ) 