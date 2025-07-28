"""
Service integration layer for physical education services.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db

# Import models
from app.models.physical_education.activity import Activity
from app.models.physical_education.exercise.models import Exercise
from app.models.physical_education.safety import (
    RiskAssessment,
    SafetyIncident,
    EquipmentCheck,
    EnvironmentalCheck,
    SafetyCheck,
    SafetyProtocol
)
from app.models.physical_education.student.models import Student
from app.models.physical_education.class_.models import PhysicalEducationClass

class ServiceIntegration:
    """Service integration layer for physical education services."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ServiceIntegration, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.logger = logging.getLogger("service_integration")
            self.services: Dict[str, Any] = {}
            self._initialized = True
    
    async def initialize(self, db: Optional[Session] = None) -> None:
        """Initialize all services in the correct order."""
        try:
            if db is None:
                db = next(get_db())
            
            # Import services here to avoid circular imports
            from .security_service import SecurityService
            from .equipment_manager import EquipmentManager
            from .student_manager import StudentManager
            from .assessment_system import AssessmentSystem
            from .movement_analyzer import MovementAnalyzer
            from .lesson_planner import LessonPlanner
            from .safety_manager import SafetyManager
            from .activity_manager import ActivityManager
            from .activity_analysis_manager import ActivityAnalysisManager
            from .activity_visualization_manager import ActivityVisualizationManager
            from .activity_export_manager import ActivityExportManager
            from .activity_collaboration_manager import ActivityCollaborationManager
            from .activity_adaptation_manager import ActivityAdaptationManager
            from .activity_assessment_manager import ActivityAssessmentManager
            from .activity_security_manager import ActivitySecurityManager
            from .activity_cache_manager import ActivityCacheManager
            from .activity_rate_limit_manager import ActivityRateLimitManager
            from .activity_circuit_breaker_manager import ActivityCircuitBreakerManager
            from .safety_incident_manager import SafetyIncidentManager
            from .safety_report_generator import SafetyReportGenerator
            from .risk_assessment_manager import RiskAssessmentManager
            from .video_processor import VideoProcessor
            from .ai_assistant import AIAssistant
            
            # Initialize core services first
            self.services['security_service'] = SecurityService()
            self.services['equipment_manager'] = EquipmentManager()
            self.services['student_manager'] = StudentManager()
            
            # Initialize assessment and analysis services
            self.services['assessment_system'] = AssessmentSystem()
            self.services['movement_analyzer'] = MovementAnalyzer()
            self.services['lesson_planner'] = LessonPlanner()
            self.services['safety_manager'] = SafetyManager()
            
            # Initialize activity-related services
            self.services['activity_manager'] = ActivityManager()
            self.services['activity_analysis_manager'] = ActivityAnalysisManager()
            self.services['activity_visualization_manager'] = ActivityVisualizationManager()
            self.services['activity_export_manager'] = ActivityExportManager()
            self.services['activity_collaboration_manager'] = ActivityCollaborationManager()
            self.services['activity_adaptation_manager'] = ActivityAdaptationManager()
            self.services['activity_assessment_manager'] = ActivityAssessmentManager()
            self.services['activity_security_manager'] = ActivitySecurityManager()
            self.services['activity_cache_manager'] = ActivityCacheManager()
            self.services['activity_rate_limit_manager'] = ActivityRateLimitManager()
            self.services['activity_circuit_breaker_manager'] = ActivityCircuitBreakerManager()
            
            # Initialize safety-related services
            self.services['safety_incident_manager'] = SafetyIncidentManager()
            self.services['safety_report_generator'] = SafetyReportGenerator()
            self.services['risk_assessment_manager'] = RiskAssessmentManager()
            
            # Initialize video processing services
            self.services['video_processor'] = VideoProcessor()
            
            # Initialize AI assistant last since it depends on other services
            self.services['ai_assistant'] = AIAssistant()
            
            # Initialize all services in the correct order
            initialization_order = [
                'security_service',
                'equipment_manager',
                'student_manager',
                'assessment_system',
                'movement_analyzer',
                'lesson_planner',
                'safety_manager',
                'activity_manager',
                'activity_analysis_manager',
                'activity_visualization_manager',
                'activity_export_manager',
                'activity_collaboration_manager',
                'activity_adaptation_manager',
                'activity_assessment_manager',
                'activity_security_manager',
                'activity_cache_manager',
                'activity_rate_limit_manager',
                'activity_circuit_breaker_manager',
                'safety_incident_manager',
                'safety_report_generator',
                'risk_assessment_manager',
                'video_processor',
                'ai_assistant'
            ]
            
            for service_name in initialization_order:
                if service_name in self.services:
                    try:
                        await self.services[service_name].initialize()
                        self.logger.info(f"Initialized service: {service_name}")
                    except Exception as e:
                        self.logger.error(f"Error initializing service {service_name}: {str(e)}")
                        # Continue with other services even if one fails
                        continue
            
            self._initialized = True
            self.logger.info("Service integration layer initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing service integration layer: {str(e)}")
            raise
    
    def get_service(self, service_name: str) -> Any:
        """Get a service by name."""
        if not self._initialized:
            # Try to initialize if not already done
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're in an async context, we can't initialize here
                    raise RuntimeError("Service integration layer not initialized")
                else:
                    # Initialize synchronously
                    loop.run_until_complete(self.initialize())
            except Exception as e:
                raise RuntimeError(f"Service integration layer not initialized: {str(e)}")
        
        if service_name not in self.services:
            raise ValueError(f"Service not found: {service_name}")
        return self.services[service_name]
    
    async def cleanup(self) -> None:
        """Clean up all services."""
        try:
            # Clean up services in reverse order
            for service_name in reversed(list(self.services.keys())):
                try:
                    await self.services[service_name].cleanup()
                    self.logger.info(f"Cleaned up service: {service_name}")
                except Exception as e:
                    self.logger.error(f"Error cleaning up service {service_name}: {str(e)}")
            
            self.services.clear()
            self._initialized = False
            self.logger.info("Service integration layer cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up service integration layer: {str(e)}")
            raise

# Create a global instance of the service integration layer
service_integration = ServiceIntegration() 