"""
FastAPI endpoints for Resource Management
Provides REST API for educational resource management, sharing, and collaboration
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.pe.resource_management_service import ResourceManagementService
from app.schemas.resource_management import (
    EducationalResourceCreate,
    EducationalResourceUpdate,
    EducationalResourceResponse,
    ResourceCategoryResponse,
    ResourceCollectionCreate,
    ResourceCollectionUpdate,
    ResourceCollectionResponse,
    ResourceSharingCreate,
    ResourceSharingResponse,
    ResourceDownloadResponse,
    ResourceFavoriteResponse,
    ResourceReviewCreate,
    ResourceReviewResponse,
    ResourceUsageCreate,
    ResourceUsageResponse,
    ResourceSearchRequest,
    ResourceSearchResponse,
    ResourceAnalyticsResponse
)
from app.core.auth import get_current_user
from app.models.teacher_registration import TeacherRegistration

router = APIRouter(prefix="/resources", tags=["Resource Management"])


# ==================== RESOURCE MANAGEMENT ====================

@router.post("", response_model=EducationalResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource_data: EducationalResourceCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new educational resource"""
    try:
        service = ResourceManagementService(db)
        return service.create_resource(current_teacher.id, resource_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create resource: {str(e)}"
        )


@router.get("", response_model=List[EducationalResourceResponse])
async def get_resources(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    is_public: Optional[bool] = Query(None, description="Filter by public status"),
    limit: int = Query(50, ge=1, le=100, description="Number of resources to return"),
    offset: int = Query(0, ge=0, description="Number of resources to skip"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get educational resources"""
    service = ResourceManagementService(db)
    return service.get_resources(current_teacher.id, subject, resource_type, is_public, limit, offset)


@router.get("/{resource_id}", response_model=EducationalResourceResponse)
async def get_resource(
    resource_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific educational resource by ID"""
    service = ResourceManagementService(db)
    resource = service.get_resource(resource_id, current_teacher.id)
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found or access denied"
        )
    
    return resource


@router.put("/{resource_id}", response_model=EducationalResourceResponse)
async def update_resource(
    resource_id: str,
    update_data: EducationalResourceUpdate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing educational resource"""
    service = ResourceManagementService(db)
    resource = service.update_resource(resource_id, current_teacher.id, update_data)
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found or access denied"
        )
    
    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an educational resource"""
    service = ResourceManagementService(db)
    success = service.delete_resource(resource_id, current_teacher.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found or access denied"
        )


@router.post("/{resource_id}/duplicate", response_model=EducationalResourceResponse)
async def duplicate_resource(
    resource_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Duplicate an existing educational resource"""
    service = ResourceManagementService(db)
    resource = service.duplicate_resource(resource_id, current_teacher.id)
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found or access denied"
        )
    
    return resource


# ==================== RESOURCE SHARING ====================

@router.post("/{resource_id}/share", response_model=ResourceSharingResponse, status_code=status.HTTP_201_CREATED)
async def share_resource(
    resource_id: str,
    sharing_data: ResourceSharingCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share an educational resource with other teachers"""
    try:
        service = ResourceManagementService(db)
        return service.share_resource(resource_id, current_teacher.id, sharing_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to share resource: {str(e)}"
        )


@router.get("/shared", response_model=List[EducationalResourceResponse])
async def get_shared_resources(
    sharing_type: Optional[str] = Query(None, description="Filter by sharing type"),
    limit: int = Query(50, ge=1, le=100, description="Number of resources to return"),
    offset: int = Query(0, ge=0, description="Number of resources to skip"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resources shared with the current teacher"""
    service = ResourceManagementService(db)
    return service.get_shared_resources(current_teacher.id, sharing_type, limit, offset)


# ==================== RESOURCE DOWNLOADS ====================

@router.post("/{resource_id}/download", response_model=ResourceDownloadResponse, status_code=status.HTTP_200_OK)
async def download_resource(
    resource_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download an educational resource"""
    try:
        service = ResourceManagementService(db)
        return service.download_resource(resource_id, current_teacher.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to download resource: {str(e)}"
        )


@router.get("/downloads", response_model=List[ResourceDownloadResponse])
async def get_downloads(
    limit: int = Query(50, ge=1, le=100, description="Number of downloads to return"),
    offset: int = Query(0, ge=0, description="Number of downloads to skip"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resource downloads for the current teacher"""
    service = ResourceManagementService(db)
    return service.get_downloads(current_teacher.id, limit, offset)


# ==================== RESOURCE FAVORITES ====================

@router.post("/{resource_id}/favorite", response_model=ResourceFavoriteResponse, status_code=status.HTTP_201_CREATED)
async def favorite_resource(
    resource_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an educational resource as favorite"""
    try:
        service = ResourceManagementService(db)
        return service.favorite_resource(resource_id, current_teacher.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to favorite resource: {str(e)}"
        )


@router.delete("/{resource_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def unfavorite_resource(
    resource_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an educational resource from favorites"""
    service = ResourceManagementService(db)
    success = service.unfavorite_resource(resource_id, current_teacher.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )


@router.get("/favorites", response_model=List[EducationalResourceResponse])
async def get_favorites(
    limit: int = Query(50, ge=1, le=100, description="Number of favorites to return"),
    offset: int = Query(0, ge=0, description="Number of favorites to skip"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get favorite resources for the current teacher"""
    service = ResourceManagementService(db)
    return service.get_favorites(current_teacher.id, limit, offset)


# ==================== RESOURCE REVIEWS ====================

@router.post("/{resource_id}/review", response_model=ResourceReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    resource_id: str,
    review_data: ResourceReviewCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a review for an educational resource"""
    try:
        service = ResourceManagementService(db)
        return service.create_review(resource_id, current_teacher.id, review_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create review: {str(e)}"
        )


@router.get("/{resource_id}/reviews", response_model=List[ResourceReviewResponse])
async def get_reviews(
    resource_id: str,
    limit: int = Query(20, ge=1, le=100, description="Number of reviews to return"),
    offset: int = Query(0, ge=0, description="Number of reviews to skip"),
    db: Session = Depends(get_db)
):
    """Get reviews for an educational resource"""
    service = ResourceManagementService(db)
    return service.get_reviews(resource_id, limit, offset)


# ==================== RESOURCE USAGE ====================

@router.post("/{resource_id}/usage", response_model=ResourceUsageResponse, status_code=status.HTTP_201_CREATED)
async def log_usage(
    resource_id: str,
    usage_data: ResourceUsageCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log usage of an educational resource"""
    try:
        service = ResourceManagementService(db)
        return service.log_usage(resource_id, current_teacher.id, usage_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to log usage: {str(e)}"
        )


@router.get("/usage", response_model=List[ResourceUsageResponse])
async def get_usage(
    resource_id: Optional[str] = Query(None, description="Filter by resource ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of usage records to return"),
    offset: int = Query(0, ge=0, description="Number of usage records to skip"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resource usage for the current teacher"""
    service = ResourceManagementService(db)
    return service.get_usage(current_teacher.id, resource_id, limit, offset)


# ==================== RESOURCE CATEGORIES ====================

@router.get("/categories", response_model=List[ResourceCategoryResponse])
async def get_categories(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    grade_level: Optional[str] = Query(None, description="Filter by grade level"),
    db: Session = Depends(get_db)
):
    """Get resource categories"""
    service = ResourceManagementService(db)
    return service.get_categories(subject, grade_level)


# ==================== RESOURCE COLLECTIONS ====================

@router.post("/collections", response_model=ResourceCollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_data: ResourceCollectionCreate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new resource collection"""
    try:
        service = ResourceManagementService(db)
        return service.create_collection(current_teacher.id, collection_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create collection: {str(e)}"
        )


@router.get("/collections", response_model=List[ResourceCollectionResponse])
async def get_collections(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    is_public: Optional[bool] = Query(None, description="Filter by public status"),
    limit: int = Query(50, ge=1, le=100, description="Number of collections to return"),
    offset: int = Query(0, ge=0, description="Number of collections to skip"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resource collections"""
    service = ResourceManagementService(db)
    return service.get_collections(current_teacher.id, subject, is_public, limit, offset)


@router.get("/collections/{collection_id}", response_model=ResourceCollectionResponse)
async def get_collection(
    collection_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific resource collection"""
    service = ResourceManagementService(db)
    collection = service.get_collection(collection_id, current_teacher.id)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found or access denied"
        )
    
    return collection


@router.put("/collections/{collection_id}", response_model=ResourceCollectionResponse)
async def update_collection(
    collection_id: str,
    update_data: ResourceCollectionUpdate,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a resource collection"""
    service = ResourceManagementService(db)
    collection = service.update_collection(collection_id, current_teacher.id, update_data)
    
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found or access denied"
        )
    
    return collection


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a resource collection"""
    service = ResourceManagementService(db)
    success = service.delete_collection(collection_id, current_teacher.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found or access denied"
        )


@router.post("/collections/{collection_id}/resources/{resource_id}", status_code=status.HTTP_201_CREATED)
async def add_resource_to_collection(
    collection_id: str,
    resource_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a resource to a collection"""
    try:
        service = ResourceManagementService(db)
        return service.add_resource_to_collection(collection_id, resource_id, current_teacher.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add resource to collection: {str(e)}"
        )


@router.delete("/collections/{collection_id}/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_resource_from_collection(
    collection_id: str,
    resource_id: str,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a resource from a collection"""
    service = ResourceManagementService(db)
    success = service.remove_resource_from_collection(collection_id, resource_id, current_teacher.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to remove resource from collection"
        )


# ==================== SEARCH ====================

@router.post("/search", response_model=ResourceSearchResponse)
async def search_resources(
    search_request: ResourceSearchRequest,
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for educational resources"""
    service = ResourceManagementService(db)
    return service.search_resources(current_teacher.id, search_request)


# ==================== ANALYTICS ====================

@router.get("/analytics", response_model=ResourceAnalyticsResponse)
async def get_resource_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_teacher: TeacherRegistration = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for educational resources"""
    service = ResourceManagementService(db)
    return service.get_resource_analytics(current_teacher.id, days)


# ==================== HEALTH CHECK ====================

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for resource management"""
    return {
        "status": "healthy",
        "service": "resource-management",
        "version": "1.0.0"
    }

