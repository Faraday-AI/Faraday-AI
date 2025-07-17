"""
Base Repository Module

This module provides base repository classes for database operations in the Faraday AI Dashboard.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union, Tuple
from datetime import datetime
from sqlalchemy import select, update, delete, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from redis import Redis
import json

from app.models.base import BaseModel
from app.core.exceptions import DatabaseException, NotFoundException

# Type variables
T = TypeVar('T', bound=BaseModel)
P = TypeVar('P')

class BaseRepository(Generic[T]):
    """Base repository class for database operations."""

    def __init__(self, model: Type[T], db: Union[Session, AsyncSession], cache: Optional[Redis] = None):
        """Initialize repository with model and database session."""
        self.model = model
        self.db = db
        self.cache = cache
        self._is_async = isinstance(db, AsyncSession)

    # CRUD Operations
    async def get(self, id: str) -> Optional[T]:
        """Get a single record by ID."""
        try:
            if self._is_async:
                result = await self.db.execute(
                    select(self.model).filter(
                        self.model.id == id,
                        self.model.is_deleted == False
                    )
                )
                return result.scalar_one_or_none()
            else:
                return self.db.query(self.model).filter(
                    self.model.id == id,
                    self.model.is_deleted == False
                ).first()
        except SQLAlchemyError as e:
            raise DatabaseException(str(e))

    async def get_multi(
        self,
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
            query = select(self.model) if self._is_async else self.db.query(self.model)
            
            # Apply filters
            if filters:
                conditions = []
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        if isinstance(value, (list, tuple)):
                            conditions.append(getattr(self.model, key).in_(value))
                        else:
                            conditions.append(getattr(self.model, key) == value)
                if conditions:
                    query = query.filter(and_(*conditions))
            
            # Apply soft delete filter
            if not include_deleted:
                query = query.filter(self.model.is_deleted == False)
            
            # Apply sorting
            if sort_by and hasattr(self.model, sort_by):
                sort_column = getattr(self.model, sort_by)
                if sort_order.lower() == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            # Execute query
            if self._is_async:
                result = await self.db.execute(query)
                return result.scalars().all()
            else:
                return query.all()
        except SQLAlchemyError as e:
            raise DatabaseException(str(e))

    async def create(self, obj_in: Dict[str, Any]) -> T:
        """Create a new record."""
        try:
            db_obj = self.model(**obj_in)
            if self._is_async:
                self.db.add(db_obj)
                await self.db.commit()
                await self.db.refresh(db_obj)
            else:
                self.db.add(db_obj)
                self.db.commit()
                self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            if self._is_async:
                await self.db.rollback()
            else:
                self.db.rollback()
            raise DatabaseException(str(e))

    async def update(self, id: str, obj_in: Dict[str, Any]) -> Optional[T]:
        """Update a record."""
        try:
            if self._is_async:
                result = await self.db.execute(
                    update(self.model)
                    .where(self.model.id == id)
                    .values(**obj_in)
                    .execution_options(synchronize_session="fetch")
                )
                await self.db.commit()
                return await self.get(id)
            else:
                self.db.query(self.model).filter(self.model.id == id).update(obj_in)
                self.db.commit()
                return self.get(id)
        except SQLAlchemyError as e:
            if self._is_async:
                await self.db.rollback()
            else:
                self.db.rollback()
            raise DatabaseException(str(e))

    async def delete(self, id: str, hard: bool = False) -> bool:
        """Delete a record."""
        try:
            if hard:
                if self._is_async:
                    result = await self.db.execute(
                        delete(self.model).where(self.model.id == id)
                    )
                    await self.db.commit()
                    return result.rowcount > 0
                else:
                    result = self.db.query(self.model).filter(self.model.id == id).delete()
                    self.db.commit()
                    return result > 0
            else:
                return await self.update(id, {
                    "is_deleted": True,
                    "deleted_at": datetime.utcnow()
                }) is not None
        except SQLAlchemyError as e:
            if self._is_async:
                await self.db.rollback()
            else:
                self.db.rollback()
            raise DatabaseException(str(e))

    async def restore(self, id: str) -> Optional[T]:
        """Restore a soft-deleted record."""
        return await self.update(id, {
            "is_deleted": False,
            "deleted_at": None
        })

    # Relationship Operations
    async def get_with_relationships(
        self,
        id: str,
        relationships: List[str]
    ) -> Optional[T]:
        """Get a record with specified relationships."""
        try:
            query = select(self.model) if self._is_async else self.db.query(self.model)
            
            # Add relationship loading
            for rel in relationships:
                if hasattr(self.model, rel):
                    query = query.options(joinedload(getattr(self.model, rel)))
            
            # Add ID filter
            query = query.filter(
                self.model.id == id,
                self.model.is_deleted == False
            )
            
            # Execute query
            if self._is_async:
                result = await self.db.execute(query)
                return result.unique().scalar_one_or_none()
            else:
                return query.first()
        except SQLAlchemyError as e:
            raise DatabaseException(str(e))

    # Transaction Support
    async def transaction(self):
        """Get a transaction context."""
        if self._is_async:
            return self.db.begin()
        else:
            return self.db.begin_nested()

    # Caching Support
    def _get_cache_key(self, id: str) -> str:
        """Generate cache key for a record."""
        return f"{self.model.__tablename__}:{id}"

    async def get_cached(self, id: str) -> Optional[T]:
        """Get a record from cache or database."""
        if not self.cache:
            return await self.get(id)
        
        cache_key = self._get_cache_key(id)
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            return self.model(**json.loads(cached_data))
        
        db_obj = await self.get(id)
        if db_obj:
            self.cache.setex(
                cache_key,
                3600,  # 1 hour
                json.dumps(db_obj.to_dict())
            )
        return db_obj

    async def invalidate_cache(self, id: str) -> None:
        """Invalidate cache for a record."""
        if self.cache:
            cache_key = self._get_cache_key(id)
            self.cache.delete(cache_key)

    # Bulk Operations
    async def bulk_create(self, objects: List[Dict[str, Any]]) -> List[T]:
        """Create multiple records."""
        try:
            db_objects = [self.model(**obj) for obj in objects]
            if self._is_async:
                self.db.add_all(db_objects)
                await self.db.commit()
                for obj in db_objects:
                    await self.db.refresh(obj)
            else:
                self.db.add_all(db_objects)
                self.db.commit()
                for obj in db_objects:
                    self.db.refresh(obj)
            return db_objects
        except SQLAlchemyError as e:
            if self._is_async:
                await self.db.rollback()
            else:
                self.db.rollback()
            raise DatabaseException(str(e))

    async def bulk_update(self, objects: List[Tuple[str, Dict[str, Any]]]) -> List[T]:
        """Update multiple records."""
        try:
            updated_objects = []
            for id, obj_in in objects:
                updated = await self.update(id, obj_in)
                if updated:
                    updated_objects.append(updated)
            return updated_objects
        except SQLAlchemyError as e:
            if self._is_async:
                await self.db.rollback()
            else:
                self.db.rollback()
            raise DatabaseException(str(e))

    async def bulk_delete(self, ids: List[str], hard: bool = False) -> bool:
        """Delete multiple records."""
        try:
            if hard:
                if self._is_async:
                    result = await self.db.execute(
                        delete(self.model).where(self.model.id.in_(ids))
                    )
                    await self.db.commit()
                    return result.rowcount > 0
                else:
                    result = self.db.query(self.model).filter(self.model.id.in_(ids)).delete()
                    self.db.commit()
                    return result > 0
            else:
                return await self.bulk_update([
                    (id, {"is_deleted": True, "deleted_at": datetime.utcnow()})
                    for id in ids
                ]) is not None
        except SQLAlchemyError as e:
            if self._is_async:
                await self.db.rollback()
            else:
                self.db.rollback()
            raise DatabaseException(str(e))

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
            search_conditions = []
            for field in fields:
                if hasattr(self.model, field):
                    search_conditions.append(
                        getattr(self.model, field).ilike(f"%{query}%")
                    )
            
            if not search_conditions:
                return []
            
            db_query = select(self.model) if self._is_async else self.db.query(self.model)
            db_query = db_query.filter(or_(*search_conditions))
            
            if not include_deleted:
                db_query = db_query.filter(self.model.is_deleted == False)
            
            db_query = db_query.offset(skip).limit(limit)
            
            if self._is_async:
                result = await self.db.execute(db_query)
                return result.scalars().all()
            else:
                return db_query.all()
        except SQLAlchemyError as e:
            raise DatabaseException(str(e))

    # Count Operations
    async def count(
        self,
        filters: Optional[Dict[str, Any]] = None,
        include_deleted: bool = False
    ) -> int:
        """Count records matching filters."""
        try:
            query = select(self.model) if self._is_async else self.db.query(self.model)
            
            if filters:
                conditions = []
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        if isinstance(value, (list, tuple)):
                            conditions.append(getattr(self.model, key).in_(value))
                        else:
                            conditions.append(getattr(self.model, key) == value)
                if conditions:
                    query = query.filter(and_(*conditions))
            
            if not include_deleted:
                query = query.filter(self.model.is_deleted == False)
            
            if self._is_async:
                result = await self.db.execute(query)
                return len(result.all())
            else:
                return query.count()
        except SQLAlchemyError as e:
            raise DatabaseException(str(e)) 