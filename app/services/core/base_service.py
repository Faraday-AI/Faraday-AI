from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from fastapi import HTTPException
from app.core.config import get_settings
from app.core.monitoring import track_metrics
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class BaseService(ABC):
    """Base class for all GPT services."""
    
    def __init__(self, service_type: str):
        self.service_type = service_type
        self.logger = logging.getLogger(f"{service_type}_service")
        
    @abstractmethod
    async def initialize(self):
        """Initialize service-specific resources."""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup service-specific resources."""
        pass
    
    @track_metrics
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming requests with common error handling and logging."""
        try:
            self.logger.info(f"Processing {self.service_type} request: {request_data}")
            result = await self.process_request(request_data)
            self.logger.info(f"Successfully processed {self.service_type} request")
            return result
        except Exception as e:
            self.logger.error(f"Error processing {self.service_type} request: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @abstractmethod
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the actual request - to be implemented by specific services."""
        pass
    
    async def validate_request(self, request_data: Dict[str, Any]) -> bool:
        """Validate incoming request data."""
        return True
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get current service status and metrics."""
        return {
            "service_type": self.service_type,
            "status": "operational",
            "metrics": await self.get_service_metrics()
        }
    
    @abstractmethod
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get service-specific metrics."""
        pass 