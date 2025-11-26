"""
Specialized Workout Service
Handles all workout plan creation with focused prompt and optimized model.
"""

from typing import List, Dict, Any, Optional
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
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None,
        user_first_name: Optional[str] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Override to use BaseSpecializedService.generate_response() instead of BaseWidgetService.generate_response().
        This ensures proper method resolution when WorkoutService inherits from both classes.
        """
        # Explicitly call BaseSpecializedService's generate_response
        return BaseSpecializedService.generate_response(
            self,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
            user_first_name=user_first_name
        )
    
    def extract_widget_data(self, response_text: str, intent: str, original_message: str = "") -> Dict[str, Any]:
        """
        Extract workout widget data from response.
        Workouts use response-based extraction.
        Returns workout data directly (same pattern as lesson plan).
        BaseSpecializedService.process() will wrap it in {type: "workout", data: {...}} format.
        Handles both standard format (exercises, strength_training, cardio) and week-long format (days, workout_plan).
        """
        logger.info(f"🔍 WorkoutService.extract_widget_data called, response_text length: {len(response_text)}")
        workout_data = widget_handler._extract_workout_data(response_text)
        logger.info(f"🔍 _extract_workout_data returned: {type(workout_data)}, keys: {list(workout_data.keys()) if isinstance(workout_data, dict) else 'not a dict'}")
        # Return data directly (same pattern as lesson plan)
        # BaseSpecializedService.process() will wrap it in {type: "workout", data: {...}} format
        return workout_data
    
    def process(self, user_request: str, context: dict = None) -> dict:
        """
        Generate workout response with widget extraction.
        Uses BaseSpecializedService.process() to handle conversation history and extraction.
        """
        # Call parent's process method which handles conversation history and extraction
        # This already extracts widget_data and puts it in result["widget_data"]
        return BaseSpecializedService.process(self, user_request, context)

