import logging
from typing import Dict, Any, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
import redis.asyncio as redis
import os
from app.core.database import get_db
from app.services.physical_education.services.security_service import SecurityService
from app.services.physical_education.services.activity_manager import ActivityManager

logger = logging.getLogger(__name__)

class ActivitySecurityManager:
    """Service for managing activity-specific security concerns."""
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.logger = logging.getLogger(__name__)
        # Initialize Redis client
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            password=os.getenv('REDIS_PASSWORD', None)
        )
        self.security_service = SecurityService(redis_client)
        self.activity_manager = ActivityManager(db) 