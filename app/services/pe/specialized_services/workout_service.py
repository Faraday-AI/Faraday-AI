"""
Specialized Workout Service
Handles all workout plan creation with focused prompt and optimized model.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from openai import OpenAI
import logging
import os

from app.services.pe.base_widget_service import BaseWidgetService
from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService
from app.services.pe import widget_handler

logger = logging.getLogger(__name__)


class WorkoutService(BaseWidgetService, BaseSpecializedService):
    """
    Specialized service for Workout Plan widget.
    Uses focused prompt (~300 tokens) and gpt-4o for high-quality workout plans.
    Supports both simplified BaseWidgetService interface and BaseSpecializedService interface.
    """

    def __init__(self, db: Session = None, openai_client: OpenAI = None):
        # Initialize BaseWidgetService first (simpler interface)
        BaseWidgetService.__init__(self, db, openai_client)
        # Initialize BaseSpecializedService (for registry compatibility)
        if db and openai_client:
            BaseSpecializedService.__init__(self, db, openai_client)
        else:
            # Allow initialization without db/openai_client for simplified usage
            self.db = db
            self.openai_client = openai_client
            self.service_name = self.__class__.__name__
        
        self.prompt_file = "prompts/workout.txt"
        self.model = os.getenv("JASPER_MODEL", "gpt-4o")
        self.widget_type = "workout"
    
    def get_system_prompt(self) -> str:
        """Load the focused workout prompt (BaseSpecializedService interface)."""
        return self.load_prompt()
    
    def get_supported_intents(self) -> List[str]:
        """Workout service handles workout-related intents."""
        return ["workout", "training", "exercise_plan", "fitness_plan"]
    
    def get_model(self) -> str:
        """Use gpt-4o for workout plans (high quality required)."""
        return self.model
    
    def extract_widget_data(self, response_text: str, intent: str, original_message: str = "") -> Dict[str, Any]:
        """
        Extract workout widget data from response.
        Workouts use response-based extraction.
        """
        return widget_handler._extract_workout_data(response_text)
    
    def process(self, user_request: str, context: dict = None) -> dict:
        """Generate workout response."""
        if context is None:
            context = {}
        prompt = self.load_prompt()
        return self.generate_response(prompt, user_request, context)

