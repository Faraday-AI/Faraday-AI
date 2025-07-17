"""
Base Service Module

This module provides base service classes for business logic in the Faraday AI Dashboard.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from redis import Redis
import json
import logging
from pydantic import BaseModel as PydanticBaseModel
from uuid import UUID

from app.core.database import Base
from app.repositories.base import BaseRepository
from app.core.exceptions import (
    DatabaseException,
    NotFoundException,
    ValidationException,
    BusinessLogicException,
    NotFoundError,
    ValidationError
)
from app.core.logging import log_activity

# Type variables
T = TypeVar('T', bound=Base)
P = TypeVar('P', bound=PydanticBaseModel)
R = TypeVar('R', bound=BaseRepository)

class BaseService(Generic[T, P, R]):
    """Base service class for business logic."""

    def __init__(
        self,
        repository: R,
        cache: Optional[Redis] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize service with repository and optional cache."""
        self.repository = repository
        self.cache = cache
        self.logger = logger or logging.getLogger(__name__)
        self.model = repository.model

    # CRUD Operations
    async def get(self, db: Session, id: UUID) -> Optional[T]:
        """Get a single record by ID."""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            self.logger.error(f"Error getting record {id}: {str(e)}")
            raise

    async def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        include_deleted: bool = False
    ) -> List[T]:
        """Get multiple records with filtering, pagination, and sorting."""
        try:
            query = db.query(self.model)
            if filters:
                query = query.filter_by(**filters)
            if sort_by:
                query = query.order_by(getattr(self.model, sort_by) if sort_order == "asc" else getattr(self.model, sort_by).desc())
            if include_deleted:
                query = query.filter(self.model.is_deleted == False)
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            self.logger.error(f"Error getting multiple records: {str(e)}")
            raise

    async def create(self, db: Session, obj_in: P) -> T:
        """Create a new record."""
        try:
            # Validate input
            self.validate(obj_in)
            
            # Create record
            db_obj = self.model(**obj_in.dict())
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            # Log activity
            await log_activity(
                self.repository.db,
                "create",
                self.repository.model.__tablename__,
                db_obj.id
            )
            
            return db_obj
        except Exception as e:
            self.logger.error(f"Error creating record: {str(e)}")
            raise

    async def update(self, db: Session, id: UUID, obj_in: P) -> T:
        """Update a record."""
        try:
            # Validate input
            self.validate(obj_in)
            
            # Update record
            db_obj = self.get(db, id)
            if not db_obj:
                raise NotFoundError(f"{self.model.__name__} with id {id} not found")
            
            for field, value in obj_in.dict(exclude_unset=True).items():
                setattr(db_obj, field, value)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            # Log activity
            await log_activity(
                self.repository.db,
                "update",
                self.repository.model.__tablename__,
                id
            )
            
            return db_obj
        except Exception as e:
            self.logger.error(f"Error updating record {id}: {str(e)}")
            raise

    async def delete(self, db: Session, id: UUID) -> T:
        """Delete a record."""
        try:
            # Delete record
            db_obj = self.get(db, id)
            if not db_obj:
                raise NotFoundError(f"{self.model.__name__} with id {id} not found")
            
            db.delete(db_obj)
            db.commit()
            
            # Log activity
            await log_activity(
                self.repository.db,
                "delete",
                self.repository.model.__tablename__,
                id
            )
            
            return db_obj
        except Exception as e:
            self.logger.error(f"Error deleting record {id}: {str(e)}")
            raise

    async def restore(self, db: Session, id: UUID) -> Optional[T]:
        """Restore a soft-deleted record."""
        try:
            # Restore record
            db_obj = self.get(db, id)
            if not db_obj:
                raise NotFoundError(f"{self.model.__name__} with id {id} not found")
            
            db_obj.is_deleted = False
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            # Log activity
            await log_activity(
                self.repository.db,
                "restore",
                self.repository.model.__tablename__,
                id
            )
            
            return db_obj
        except Exception as e:
            self.logger.error(f"Error restoring record {id}: {str(e)}")
            raise

    # Validation Methods
    def validate(self, obj_in: P) -> List[str]:
        """Validate input data."""
        errors = []
        if not obj_in:
            errors.append("Input data is required")
        return errors

    def is_valid(self, obj_in: P) -> bool:
        """Check if input data is valid."""
        return len(self.validate(obj_in)) == 0

    # Business Logic Methods
    async def activate(self, db: Session, id: UUID) -> Optional[T]:
        """Activate a record."""
        try:
            return await self.update(db, id, {"is_active": True})
        except Exception as e:
            self.logger.error(f"Error activating record {id}: {str(e)}")
            raise

    async def deactivate(self, db: Session, id: UUID) -> Optional[T]:
        """Deactivate a record."""
        try:
            return await self.update(db, id, {"is_active": False})
        except Exception as e:
            self.logger.error(f"Error deactivating record {id}: {str(e)}")
            raise

    async def archive(self, db: Session, id: UUID) -> Optional[T]:
        """Archive a record."""
        try:
            return await self.update(db, id, {"is_archived": True})
        except Exception as e:
            self.logger.error(f"Error archiving record {id}: {str(e)}")
            raise

    async def unarchive(self, db: Session, id: UUID) -> Optional[T]:
        """Unarchive a record."""
        try:
            return await self.update(db, id, {"is_archived": False})
        except Exception as e:
            self.logger.error(f"Error unarchiving record {id}: {str(e)}")
            raise

    # Caching Methods
    async def get_cached(self, db: Session, id: UUID) -> Optional[T]:
        """Get a record from cache or database."""
        try:
            return await self.repository.get_cached(id)
        except Exception as e:
            self.logger.error(f"Error getting cached record {id}: {str(e)}")
            raise

    async def invalidate_cache(self, db: Session, id: UUID) -> None:
        """Invalidate cache for a record."""
        try:
            await self.repository.invalidate_cache(id)
        except Exception as e:
            self.logger.error(f"Error invalidating cache for record {id}: {str(e)}")
            raise

    # Bulk Operations
    async def bulk_create(self, db: Session, objects: List[P]) -> List[T]:
        """Create multiple records."""
        try:
            # Validate inputs
            for obj in objects:
                self.validate(obj)
            
            # Create records
            db_objects = [self.model(**obj.dict()) for obj in objects]
            db.add_all(db_objects)
            db.commit()
            
            # Log activity
            for db_obj in db_objects:
                await log_activity(
                    self.repository.db,
                    "create",
                    self.repository.model.__tablename__,
                    db_obj.id
                )
            
            return db_objects
        except Exception as e:
            self.logger.error(f"Error bulk creating records: {str(e)}")
            raise

    async def bulk_update(self, db: Session, objects: List[Tuple[UUID, P]]) -> List[T]:
        """Update multiple records."""
        try:
            # Validate inputs
            for id, obj in objects:
                self.validate(obj)
            
            # Update records
            db_objects = [self.get(db, id) for id, _ in objects]
            for db_obj, obj in zip(db_objects, objects):
                if not db_obj:
                    raise NotFoundError(f"{self.model.__name__} with id {id} not found")
                for field, value in obj.dict(exclude_unset=True).items():
                    setattr(db_obj, field, value)
            
            db.add_all(db_objects)
            db.commit()
            
            # Log activity
            for id, _ in objects:
                await log_activity(
                    self.repository.db,
                    "update",
                    self.repository.model.__tablename__,
                    id
                )
            
            return db_objects
        except Exception as e:
            self.logger.error(f"Error bulk updating records: {str(e)}")
            raise

    async def bulk_delete(self, db: Session, ids: List[UUID], hard: bool = False) -> bool:
        """Delete multiple records."""
        try:
            # Delete records
            db_objects = [self.get(db, id) for id in ids]
            for db_obj in db_objects:
            # Validate deletions
            for id in ids:
                self._validate_delete(id)
            
            # Delete records
            result = await self.repository.bulk_delete(ids, hard=hard)
            
            if result:
                # Log activity
                for id in ids:
                    await log_activity(
                        self.repository.db,
                        "delete",
                        self.repository.model.__tablename__,
                        id
                    )
            
            return result
        except Exception as e:
            self.logger.error(f"Error bulk deleting records: {str(e)}")
            raise

    # Search Operations
    async def search(
        self,
        query: str,
        fields: List[str],
        *,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[T]:
        """Search records by text in specified fields."""
        try:
            return await self.repository.search(
                query=query,
                fields=fields,
                skip=skip,
                limit=limit,
                include_deleted=include_deleted
            )
        except Exception as e:
            self.logger.error(f"Error searching records: {str(e)}")
            raise

    # Count Operations
    async def count(
        self,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> int:
        """Count records matching filters."""
        try:
            return await self.repository.count(
                filters=filters,
                include_deleted=include_deleted
            )
        except Exception as e:
            self.logger.error(f"Error counting records: {str(e)}")
            raise 