"""
Service Registry for Specialized Widget Services
Routes intents to appropriate specialized services.
"""

from typing import Dict, Optional, List, Type
from sqlalchemy.orm import Session
from openai import OpenAI
import logging

from app.services.pe.specialized_services import (
    AttendanceService,
    LessonPlanService,
    MealPlanService,
    WorkoutService,
    SMSService,
    GeneralWidgetService,
    GeneralResponseService,
    ContentGenerationService,
    BaseSpecializedService
)

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Registry mapping intents to specialized services.
    Routes intents to appropriate specialized services for the hybrid architecture.
    """
    
    def __init__(self, db: Session, openai_client: OpenAI):
        self.db = db
        self.openai_client = openai_client
        self._services: Dict[str, Type[BaseSpecializedService]] = {}
        self._service_instances: Dict[str, BaseSpecializedService] = {}
        self.register_defaults()
        logger.info(f"✅ ServiceRegistry initialized with {len(self._services)} specialized services")
    
    def register_defaults(self):
        """Register default specialized services."""
        self._services.update({
            # Core specialized services
            "attendance": AttendanceService,
            "lesson_plan": LessonPlanService,
            "meal_plan": MealPlanService,
            "workout": WorkoutService,
            "sms": SMSService,
            # Content generation service
            "content_generation": ContentGenerationService,
            "generate_image": ContentGenerationService,
            "create_powerpoint": ContentGenerationService,
            "create_presentation": ContentGenerationService,
            "create_word": ContentGenerationService,
            "create_document": ContentGenerationService,
            "create_pdf": ContentGenerationService,
            "create_excel": ContentGenerationService,
            "create_spreadsheet": ContentGenerationService,
            "generate_artwork": ContentGenerationService,
            # General services for fallback
            "widget": GeneralWidgetService,  # Also register "widget" intent
            "general_widget": GeneralWidgetService,
            "general": GeneralResponseService,  # Also register "general" intent
            "general_response": GeneralResponseService,
        })
    
    def get_service(self, intent: str) -> Optional[BaseSpecializedService]:
        """
        Get the specialized service instance for a given intent.
        
        Args:
            intent: The classified intent string
            
        Returns:
            Specialized service instance or None if no service handles this intent
        """
        # Check if we have a direct mapping
        service_cls = self._services.get(intent)
        if service_cls:
            # Return cached instance or create new one
            if intent not in self._service_instances:
                self._service_instances[intent] = service_cls(self.db, self.openai_client)
            return self._service_instances[intent]
        
        # Check if any registered service supports this intent
        for service_name, service_cls in self._services.items():
            # Get or create instance
            if service_name not in self._service_instances:
                self._service_instances[service_name] = service_cls(self.db, self.openai_client)
            service = self._service_instances[service_name]
            
            if service.should_handle(intent):
                return service
        
        # Last resort fallbacks:
        # - Use general_widget for widget-related intents
        # - Use general_response for general/conversational intents
        if intent == "widget" or "widget" in intent.lower():
            if "general_widget" not in self._service_instances:
                self._service_instances["general_widget"] = GeneralWidgetService(self.db, self.openai_client)
            return self._service_instances["general_widget"]
        
        if intent == "general" or intent == "general_response":
            if "general_response" not in self._service_instances:
                self._service_instances["general_response"] = GeneralResponseService(self.db, self.openai_client)
            return self._service_instances["general_response"]
        
        return None
    
    def has_service(self, intent: str) -> bool:
        """Check if a specialized service exists for the given intent."""
        return self.get_service(intent) is not None
    
    def get_all_services(self) -> List[BaseSpecializedService]:
        """Get all registered specialized service instances."""
        # Ensure all services are instantiated
        for service_name in self._services.keys():
            if service_name not in self._service_instances:
                self._service_instances[service_name] = self._services[service_name](self.db, self.openai_client)
        return list(self._service_instances.values())

