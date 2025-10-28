"""
Resource Management Service
Handles educational resource upload, organization, and sharing for beta teachers
"""

from typing import List, Optional, Dict, Any, Tuple, BinaryIO
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
import uuid
import os
import mimetypes
from pathlib import Path

from app.models.resource_management import (
    EducationalResource,
    ResourceCategory,
    ResourceCategoryAssociation,
    ResourceSharing,
    ResourceUsage,
    ResourceCollection,
    CollectionResourceAssociation,
    CollectionSharing,
    ResourceReview,
    ResourceFavorite,
    ResourceDownload
)
from app.schemas.resource_management import (
    EducationalResourceCreate,
    EducationalResourceUpdate,
    EducationalResourceResponse,
    ResourceCategoryResponse,
    ResourceSharingCreate,
    ResourceSharingResponse,
    ResourceUsageCreate,
    ResourceUsageResponse,
    ResourceCollectionCreate,
    ResourceCollectionUpdate,
    ResourceCollectionResponse,
    ResourceReviewCreate,
    ResourceReviewResponse,
    ResourceSearchRequest,
    ResourceSearchResponse,
    ResourceUploadResponse,
    ResourceAnalyticsResponse
)


class ResourceManagementService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_base_path = "/app/uploads/resources"
        self.thumbnail_base_path = "/app/uploads/thumbnails"

    # ==================== RESOURCE MANAGEMENT ====================
    
    def create_resource(
        self, 
        teacher_id: str, 
        resource_data: EducationalResourceCreate,
        file_content: Optional[bytes] = None,
        file_name: Optional[str] = None
    ) -> EducationalResourceResponse:
        """Create a new educational resource"""
        try:
            # Handle file upload if provided
            file_path = None
            file_size = 0
            mime_type = None
            
            if file_content and file_name:
                file_path, file_size, mime_type = self._save_uploaded_file(
                    file_content, file_name, teacher_id
                )
            
            # Create the resource
            resource = EducationalResource(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                title=resource_data.title,
                description=resource_data.description,
                resource_type=resource_data.resource_type,
                file_path=file_path,
                file_name=file_name,
                file_size_bytes=file_size,
                mime_type=mime_type,
                external_url=resource_data.external_url,
                subject=resource_data.subject,
                grade_level=resource_data.grade_level,
                tags=resource_data.tags,
                keywords=resource_data.keywords,
                difficulty_level=resource_data.difficulty_level,
                duration_minutes=resource_data.duration_minutes,
                language=resource_data.language,
                accessibility_features=resource_data.accessibility_features,
                copyright_info=resource_data.copyright_info,
                license_type=resource_data.license_type,
                attribution_required=resource_data.attribution_required,
                attribution_text=resource_data.attribution_text,
                is_public=resource_data.is_public,
                is_featured=resource_data.is_featured,
                ai_generated=resource_data.ai_generated
            )
            
            self.db.add(resource)
            self.db.flush()  # Get the ID
            
            # Add category associations if provided
            if resource_data.category_ids:
                for category_id in resource_data.category_ids:
                    association = ResourceCategoryAssociation(
                        id=str(uuid.uuid4()),
                        resource_id=resource.id,
                        category_id=category_id
                    )
                    self.db.add(association)
            
            self.db.commit()
            
            # Log usage
            self._log_resource_usage(
                resource_id=resource.id,
                teacher_id=teacher_id,
                usage_type="created"
            )
            
            return self._resource_to_response(resource)
            
        except Exception as e:
            self.db.rollback()
            # Clean up uploaded file if creation failed
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            raise Exception(f"Failed to create resource: {str(e)}")

    def get_resource(self, resource_id: str, teacher_id: str) -> Optional[EducationalResourceResponse]:
        """Get a specific resource by ID"""
        resource = self.db.query(EducationalResource).filter(
            and_(
                EducationalResource.id == resource_id,
                or_(
                    EducationalResource.teacher_id == teacher_id,
                    EducationalResource.is_public == True
                )
            )
        ).first()
        
        if not resource:
            return None
        
        # Log view
        self._log_resource_usage(
            resource_id=resource_id,
            teacher_id=teacher_id,
            usage_type="viewed"
        )
        
        return self._resource_to_response(resource)

    def get_teacher_resources(
        self, 
        teacher_id: str, 
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[EducationalResourceResponse]:
        """Get resources created by a specific teacher"""
        query = self.db.query(EducationalResource).filter(
            EducationalResource.teacher_id == teacher_id
        )
        
        if subject:
            query = query.filter(EducationalResource.subject == subject)
        if grade_level:
            query = query.filter(EducationalResource.grade_level == grade_level)
        if resource_type:
            query = query.filter(EducationalResource.resource_type == resource_type)
        
        resources = query.order_by(desc(EducationalResource.created_at)).offset(offset).limit(limit).all()
        
        return [self._resource_to_response(resource) for resource in resources]

    def get_public_resources(
        self,
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        resource_type: Optional[str] = None,
        difficulty_level: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[EducationalResourceResponse]:
        """Get public resources available to all teachers"""
        query = self.db.query(EducationalResource).filter(
            EducationalResource.is_public == True
        )
        
        if subject:
            query = query.filter(EducationalResource.subject == subject)
        if grade_level:
            query = query.filter(EducationalResource.grade_level == grade_level)
        if resource_type:
            query = query.filter(EducationalResource.resource_type == resource_type)
        if difficulty_level:
            query = query.filter(EducationalResource.difficulty_level == difficulty_level)
        
        resources = query.order_by(desc(EducationalResource.rating_average)).offset(offset).limit(limit).all()
        
        return [self._resource_to_response(resource) for resource in resources]

    def search_resources(
        self,
        search_request: ResourceSearchRequest,
        teacher_id: str
    ) -> ResourceSearchResponse:
        """Search for resources using various criteria"""
        query = self.db.query(EducationalResource).filter(
            EducationalResource.is_public == True
        )
        
        # Text search
        if search_request.query:
            search_terms = search_request.query.split()
            for term in search_terms:
                query = query.filter(
                    or_(
                        EducationalResource.title.ilike(f"%{term}%"),
                        EducationalResource.description.ilike(f"%{term}%"),
                        EducationalResource.tags.op('&&')([term]),
                        EducationalResource.keywords.op('&&')([term])
                    )
                )
        
        # Filters
        if search_request.subject:
            query = query.filter(EducationalResource.subject == search_request.subject)
        if search_request.grade_level:
            query = query.filter(EducationalResource.grade_level == search_request.grade_level)
        if search_request.resource_type:
            query = query.filter(EducationalResource.resource_type == search_request.resource_type)
        if search_request.difficulty_level:
            query = query.filter(EducationalResource.difficulty_level == search_request.difficulty_level)
        if search_request.duration_min:
            query = query.filter(EducationalResource.duration_minutes >= search_request.duration_min)
        if search_request.duration_max:
            query = query.filter(EducationalResource.duration_minutes <= search_request.duration_max)
        if search_request.tags:
            query = query.filter(EducationalResource.tags.op('&&')(search_request.tags))
        if search_request.min_rating:
            query = query.filter(EducationalResource.rating_average >= search_request.min_rating)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        resources = query.order_by(desc(EducationalResource.rating_average)).offset(
            search_request.offset
        ).limit(search_request.limit).all()
        
        return ResourceSearchResponse(
            resources=[self._resource_to_response(resource) for resource in resources],
            total_count=total_count,
            has_more=(search_request.offset + len(resources)) < total_count
        )

    def update_resource(
        self, 
        resource_id: str, 
        teacher_id: str, 
        update_data: EducationalResourceUpdate
    ) -> Optional[EducationalResourceResponse]:
        """Update an existing resource"""
        resource = self.db.query(EducationalResource).filter(
            and_(
                EducationalResource.id == resource_id,
                EducationalResource.teacher_id == teacher_id
            )
        ).first()
        
        if not resource:
            return None
        
        # Update resource fields
        for field, value in update_data.dict(exclude_unset=True).items():
            if field != "category_ids":
                setattr(resource, field, value)
        
        # Update category associations if provided
        if update_data.category_ids is not None:
            # Delete existing associations
            self.db.query(ResourceCategoryAssociation).filter(
                ResourceCategoryAssociation.resource_id == resource_id
            ).delete()
            
            # Add new associations
            for category_id in update_data.category_ids:
                association = ResourceCategoryAssociation(
                    id=str(uuid.uuid4()),
                    resource_id=resource.id,
                    category_id=category_id
                )
                self.db.add(association)
        
        resource.updated_at = datetime.utcnow()
        self.db.commit()
        
        # Log usage
        self._log_resource_usage(
            resource_id=resource_id,
            teacher_id=teacher_id,
            usage_type="modified"
        )
        
        return self._resource_to_response(resource)

    def delete_resource(self, resource_id: str, teacher_id: str) -> bool:
        """Delete a resource"""
        resource = self.db.query(EducationalResource).filter(
            and_(
                EducationalResource.id == resource_id,
                EducationalResource.teacher_id == teacher_id
            )
        ).first()
        
        if not resource:
            return False
        
        # Delete associated file
        if resource.file_path and os.path.exists(resource.file_path):
            os.remove(resource.file_path)
        
        # Delete thumbnail if exists
        if resource.thumbnail_path and os.path.exists(resource.thumbnail_path):
            os.remove(resource.thumbnail_path)
        
        self.db.delete(resource)
        self.db.commit()
        
        return True

    def download_resource(self, resource_id: str, teacher_id: str) -> Optional[Tuple[str, bytes]]:
        """Download a resource file"""
        resource = self.db.query(EducationalResource).filter(
            and_(
                EducationalResource.id == resource_id,
                or_(
                    EducationalResource.teacher_id == teacher_id,
                    EducationalResource.is_public == True
                )
            )
        ).first()
        
        if not resource or not resource.file_path:
            return None
        
        # Check if file exists
        if not os.path.exists(resource.file_path):
            return None
        
        # Log download
        self._log_resource_download(resource_id, teacher_id, resource.file_size_bytes)
        
        # Read file content
        with open(resource.file_path, 'rb') as f:
            file_content = f.read()
        
        return resource.file_name, file_content

    # ==================== COLLECTIONS ====================
    
    def create_collection(
        self, 
        teacher_id: str, 
        collection_data: ResourceCollectionCreate
    ) -> ResourceCollectionResponse:
        """Create a new resource collection"""
        try:
            collection = ResourceCollection(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                title=collection_data.title,
                description=collection_data.description,
                subject=collection_data.subject,
                grade_level=collection_data.grade_level,
                collection_type=collection_data.collection_type,
                is_public=collection_data.is_public,
                is_featured=collection_data.is_featured
            )
            
            self.db.add(collection)
            self.db.flush()  # Get the ID
            
            # Add resources if provided
            if collection_data.resource_ids:
                for i, resource_id in enumerate(collection_data.resource_ids):
                    association = CollectionResourceAssociation(
                        id=str(uuid.uuid4()),
                        collection_id=collection.id,
                        resource_id=resource_id,
                        order_index=i + 1
                    )
                    self.db.add(association)
            
            self.db.commit()
            
            return self._collection_to_response(collection)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create collection: {str(e)}")

    def get_collection(self, collection_id: str, teacher_id: str) -> Optional[ResourceCollectionResponse]:
        """Get a specific collection by ID"""
        collection = self.db.query(ResourceCollection).filter(
            and_(
                ResourceCollection.id == collection_id,
                or_(
                    ResourceCollection.teacher_id == teacher_id,
                    ResourceCollection.is_public == True
                )
            )
        ).first()
        
        if not collection:
            return None
            
        return self._collection_to_response(collection)

    def get_teacher_collections(
        self, 
        teacher_id: str, 
        subject: Optional[str] = None,
        grade_level: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ResourceCollectionResponse]:
        """Get collections created by a specific teacher"""
        query = self.db.query(ResourceCollection).filter(
            ResourceCollection.teacher_id == teacher_id
        )
        
        if subject:
            query = query.filter(ResourceCollection.subject == subject)
        if grade_level:
            query = query.filter(ResourceCollection.grade_level == grade_level)
        
        collections = query.order_by(desc(ResourceCollection.created_at)).offset(offset).limit(limit).all()
        
        return [self._collection_to_response(collection) for collection in collections]

    def add_resource_to_collection(
        self, 
        collection_id: str, 
        resource_id: str, 
        teacher_id: str
    ) -> bool:
        """Add a resource to a collection"""
        # Verify collection ownership
        collection = self.db.query(ResourceCollection).filter(
            and_(
                ResourceCollection.id == collection_id,
                ResourceCollection.teacher_id == teacher_id
            )
        ).first()
        
        if not collection:
            return False
        
        # Check if resource exists and is accessible
        resource = self.db.query(EducationalResource).filter(
            and_(
                EducationalResource.id == resource_id,
                or_(
                    EducationalResource.teacher_id == teacher_id,
                    EducationalResource.is_public == True
                )
            )
        ).first()
        
        if not resource:
            return False
        
        # Check if already in collection
        existing = self.db.query(CollectionResourceAssociation).filter(
            and_(
                CollectionResourceAssociation.collection_id == collection_id,
                CollectionResourceAssociation.resource_id == resource_id
            )
        ).first()
        
        if existing:
            return True  # Already in collection
        
        # Add to collection
        association = CollectionResourceAssociation(
            id=str(uuid.uuid4()),
            collection_id=collection_id,
            resource_id=resource_id,
            order_index=collection.resource_count + 1
        )
        
        self.db.add(association)
        
        # Update collection resource count
        collection.resource_count += 1
        
        self.db.commit()
        
        return True

    def remove_resource_from_collection(
        self, 
        collection_id: str, 
        resource_id: str, 
        teacher_id: str
    ) -> bool:
        """Remove a resource from a collection"""
        # Verify collection ownership
        collection = self.db.query(ResourceCollection).filter(
            and_(
                ResourceCollection.id == collection_id,
                ResourceCollection.teacher_id == teacher_id
            )
        ).first()
        
        if not collection:
            return False
        
        # Remove association
        association = self.db.query(CollectionResourceAssociation).filter(
            and_(
                CollectionResourceAssociation.collection_id == collection_id,
                CollectionResourceAssociation.resource_id == resource_id
            )
        ).first()
        
        if not association:
            return False
        
        self.db.delete(association)
        
        # Update collection resource count
        collection.resource_count -= 1
        
        self.db.commit()
        
        return True

    # ==================== REVIEWS AND RATINGS ====================
    
    def create_review(
        self, 
        resource_id: str, 
        teacher_id: str, 
        review_data: ResourceReviewCreate
    ) -> ResourceReviewResponse:
        """Create a review for a resource"""
        # Check if resource exists and is accessible
        resource = self.db.query(EducationalResource).filter(
            and_(
                EducationalResource.id == resource_id,
                or_(
                    EducationalResource.teacher_id == teacher_id,
                    EducationalResource.is_public == True
                )
            )
        ).first()
        
        if not resource:
            raise Exception("Resource not found or access denied")
        
        # Check if review already exists
        existing_review = self.db.query(ResourceReview).filter(
            and_(
                ResourceReview.resource_id == resource_id,
                ResourceReview.teacher_id == teacher_id
            )
        ).first()
        
        if existing_review:
            # Update existing review
            existing_review.rating = review_data.rating
            existing_review.review_text = review_data.review_text
            existing_review.pros = review_data.pros
            existing_review.cons = review_data.cons
            existing_review.suggestions = review_data.suggestions
            existing_review.would_recommend = review_data.would_recommend
            existing_review.used_in_class = review_data.used_in_class
            existing_review.student_feedback = review_data.student_feedback
            existing_review.updated_at = datetime.utcnow()
            
            self.db.commit()
            return self._review_to_response(existing_review)
        
        # Create new review
        review = ResourceReview(
            id=str(uuid.uuid4()),
            resource_id=resource_id,
            teacher_id=teacher_id,
            rating=review_data.rating,
            review_text=review_data.review_text,
            pros=review_data.pros,
            cons=review_data.cons,
            suggestions=review_data.suggestions,
            would_recommend=review_data.would_recommend,
            used_in_class=review_data.used_in_class,
            student_feedback=review_data.student_feedback
        )
        
        self.db.add(review)
        self.db.commit()
        
        return self._review_to_response(review)

    def get_resource_reviews(
        self, 
        resource_id: str, 
        limit: int = 20,
        offset: int = 0
    ) -> List[ResourceReviewResponse]:
        """Get reviews for a specific resource"""
        reviews = self.db.query(ResourceReview).filter(
            ResourceReview.resource_id == resource_id
        ).order_by(desc(ResourceReview.created_at)).offset(offset).limit(limit).all()
        
        return [self._review_to_response(review) for review in reviews]

    def add_to_favorites(self, resource_id: str, teacher_id: str) -> bool:
        """Add a resource to teacher's favorites"""
        # Check if resource exists and is accessible
        resource = self.db.query(EducationalResource).filter(
            and_(
                EducationalResource.id == resource_id,
                or_(
                    EducationalResource.teacher_id == teacher_id,
                    EducationalResource.is_public == True
                )
            )
        ).first()
        
        if not resource:
            return False
        
        # Check if already in favorites
        existing = self.db.query(ResourceFavorite).filter(
            and_(
                ResourceFavorite.resource_id == resource_id,
                ResourceFavorite.teacher_id == teacher_id
            )
        ).first()
        
        if existing:
            return True  # Already in favorites
        
        # Add to favorites
        favorite = ResourceFavorite(
            id=str(uuid.uuid4()),
            resource_id=resource_id,
            teacher_id=teacher_id
        )
        
        self.db.add(favorite)
        self.db.commit()
        
        return True

    def remove_from_favorites(self, resource_id: str, teacher_id: str) -> bool:
        """Remove a resource from teacher's favorites"""
        favorite = self.db.query(ResourceFavorite).filter(
            and_(
                ResourceFavorite.resource_id == resource_id,
                ResourceFavorite.teacher_id == teacher_id
            )
        ).first()
        
        if not favorite:
            return False
        
        self.db.delete(favorite)
        self.db.commit()
        
        return True

    def get_teacher_favorites(
        self, 
        teacher_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[EducationalResourceResponse]:
        """Get teacher's favorite resources"""
        resources = self.db.query(EducationalResource).join(ResourceFavorite).filter(
            ResourceFavorite.teacher_id == teacher_id
        ).order_by(desc(ResourceFavorite.created_at)).offset(offset).limit(limit).all()
        
        return [self._resource_to_response(resource) for resource in resources]

    # ==================== CATEGORIES ====================
    
    def get_resource_categories(
        self, 
        subject: Optional[str] = None,
        grade_level: Optional[str] = None
    ) -> List[ResourceCategoryResponse]:
        """Get resource categories"""
        query = self.db.query(ResourceCategory).filter(
            ResourceCategory.is_active == True
        )
        
        if subject:
            query = query.filter(ResourceCategory.subject == subject)
        if grade_level:
            query = query.filter(ResourceCategory.grade_level_range.contains(grade_level))
        
        categories = query.order_by(asc(ResourceCategory.name)).all()
        
        return [self._category_to_response(category) for category in categories]

    # ==================== ANALYTICS ====================
    
    def get_resource_analytics(
        self, 
        teacher_id: str, 
        days: int = 30
    ) -> ResourceAnalyticsResponse:
        """Get analytics for a teacher's resources"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Resource creation stats
        resources_created = self.db.query(EducationalResource).filter(
            and_(
                EducationalResource.teacher_id == teacher_id,
                EducationalResource.created_at >= start_date
            )
        ).count()
        
        # Usage stats
        usage_stats = self.db.query(
            ResourceUsage.usage_type,
            func.count(ResourceUsage.id).label('count')
        ).join(EducationalResource).filter(
            and_(
                EducationalResource.teacher_id == teacher_id,
                ResourceUsage.usage_date >= start_date
            )
        ).group_by(ResourceUsage.usage_type).all()
        
        # Popular resources
        popular_resources = self.db.query(
            EducationalResource.id,
            EducationalResource.title,
            func.count(ResourceUsage.id).label('usage_count')
        ).join(ResourceUsage).filter(
            EducationalResource.teacher_id == teacher_id
        ).group_by(
            EducationalResource.id, 
            EducationalResource.title
        ).order_by(desc('usage_count')).limit(5).all()
        
        # Download stats
        total_downloads = self.db.query(func.count(ResourceDownload.id)).join(EducationalResource).filter(
            EducationalResource.teacher_id == teacher_id
        ).scalar()
        
        return ResourceAnalyticsResponse(
            resources_created=resources_created,
            usage_by_type={stat.usage_type: stat.count for stat in usage_stats},
            popular_resources=[
                {
                    "id": resource.id,
                    "title": resource.title,
                    "usage_count": resource.usage_count
                }
                for resource in popular_resources
            ],
            total_downloads=total_downloads,
            total_views=self.db.query(func.sum(EducationalResource.view_count)).filter(
                EducationalResource.teacher_id == teacher_id
            ).scalar() or 0
        )

    # ==================== HELPER METHODS ====================
    
    def _save_uploaded_file(
        self, 
        file_content: bytes, 
        file_name: str, 
        teacher_id: str
    ) -> Tuple[str, int, str]:
        """Save uploaded file and return path, size, and MIME type"""
        # Create teacher-specific directory
        teacher_dir = os.path.join(self.upload_base_path, teacher_id)
        os.makedirs(teacher_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(file_name).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(teacher_dir, unique_filename)
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        return file_path, len(file_content), mime_type

    def _log_resource_usage(
        self, 
        resource_id: str, 
        teacher_id: str, 
        usage_type: str
    ) -> None:
        """Log resource usage for analytics"""
        usage = ResourceUsage(
            id=str(uuid.uuid4()),
            resource_id=resource_id,
            teacher_id=teacher_id,
            usage_type=usage_type
        )
        self.db.add(usage)
        self.db.commit()

    def _log_resource_download(
        self, 
        resource_id: str, 
        teacher_id: str, 
        file_size: int
    ) -> None:
        """Log resource download"""
        download = ResourceDownload(
            id=str(uuid.uuid4()),
            resource_id=resource_id,
            teacher_id=teacher_id,
            file_size_bytes=file_size
        )
        self.db.add(download)
        self.db.commit()

    def _resource_to_response(self, resource: EducationalResource) -> EducationalResourceResponse:
        """Convert resource model to response"""
        # Get categories
        categories = self.db.query(ResourceCategory).join(ResourceCategoryAssociation).filter(
            ResourceCategoryAssociation.resource_id == resource.id
        ).all()
        
        return EducationalResourceResponse(
            id=resource.id,
            teacher_id=resource.teacher_id,
            title=resource.title,
            description=resource.description,
            resource_type=resource.resource_type,
            file_path=resource.file_path,
            file_name=resource.file_name,
            file_size_bytes=resource.file_size_bytes,
            mime_type=resource.mime_type,
            external_url=resource.external_url,
            thumbnail_path=resource.thumbnail_path,
            subject=resource.subject,
            grade_level=resource.grade_level,
            tags=resource.tags,
            keywords=resource.keywords,
            difficulty_level=resource.difficulty_level,
            duration_minutes=resource.duration_minutes,
            language=resource.language,
            accessibility_features=resource.accessibility_features,
            copyright_info=resource.copyright_info,
            license_type=resource.license_type,
            attribution_required=resource.attribution_required,
            attribution_text=resource.attribution_text,
            is_public=resource.is_public,
            is_featured=resource.is_featured,
            download_count=resource.download_count,
            view_count=resource.view_count,
            rating_average=resource.rating_average,
            rating_count=resource.rating_count,
            ai_generated=resource.ai_generated,
            created_at=resource.created_at,
            updated_at=resource.updated_at,
            categories=[self._category_to_response(category) for category in categories]
        )

    def _collection_to_response(self, collection: ResourceCollection) -> ResourceCollectionResponse:
        """Convert collection model to response"""
        # Get resources in collection
        resources = self.db.query(EducationalResource).join(CollectionResourceAssociation).filter(
            CollectionResourceAssociation.collection_id == collection.id
        ).order_by(CollectionResourceAssociation.order_index).all()
        
        return ResourceCollectionResponse(
            id=collection.id,
            teacher_id=collection.teacher_id,
            title=collection.title,
            description=collection.description,
            subject=collection.subject,
            grade_level=collection.grade_level,
            collection_type=collection.collection_type,
            is_public=collection.is_public,
            is_featured=collection.is_featured,
            resource_count=collection.resource_count,
            view_count=collection.view_count,
            download_count=collection.download_count,
            rating_average=collection.rating_average,
            rating_count=collection.rating_count,
            created_at=collection.created_at,
            updated_at=collection.updated_at,
            resources=[self._resource_to_response(resource) for resource in resources]
        )

    def _review_to_response(self, review: ResourceReview) -> ResourceReviewResponse:
        """Convert review model to response"""
        return ResourceReviewResponse(
            id=review.id,
            resource_id=review.resource_id,
            teacher_id=review.teacher_id,
            rating=review.rating,
            review_text=review.review_text,
            pros=review.pros,
            cons=review.cons,
            suggestions=review.suggestions,
            would_recommend=review.would_recommend,
            used_in_class=review.used_in_class,
            student_feedback=review.student_feedback,
            created_at=review.created_at,
            updated_at=review.updated_at
        )

    def _category_to_response(self, category: ResourceCategory) -> ResourceCategoryResponse:
        """Convert category model to response"""
        return ResourceCategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_category_id=category.parent_category_id,
            subject=category.subject,
            grade_level_range=category.grade_level_range,
            icon_name=category.icon_name,
            color_code=category.color_code,
            is_active=category.is_active,
            created_at=category.created_at
        )
