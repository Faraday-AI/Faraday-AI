"""
Specialized Meal Plan Service
Handles all meal plan creation with focused prompt and optimized model.
"""

from typing import List, Dict, Any, Union
from sqlalchemy.orm import Session
from openai import OpenAI
import logging
import os

from app.services.pe.base_widget_service import BaseWidgetService
from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService
from app.services.pe import widget_handler

logger = logging.getLogger(__name__)


class MealPlanService(BaseWidgetService, BaseSpecializedService):
    """
    Specialized service for Meal Plan widget.
    Uses focused prompt (~500 tokens) and gpt-4o for quality meal plans.
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
        
        self.prompt_file = "prompts/meal_plan.txt"
        self.model = os.getenv("JASPER_MODEL", "gpt-4o")
        self.widget_type = "meal_plan"
    
    def get_system_prompt(self) -> str:
        """Load the focused meal plan prompt (BaseSpecializedService interface)."""
        return self.load_prompt()
    
    def get_supported_intents(self) -> List[str]:
        """Meal plan service handles meal plan and allergy answer intents."""
        return ["meal_plan", "allergy_answer", "nutrition", "diet"]
    
    def get_model(self) -> str:
        """Use gpt-4o for meal plans (high quality required for safety)."""
        return self.model
    
    def extract_widget_data(self, response_text: str, intent: str, original_message: str = "") -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Extract meal plan widget data from response.
        Meal plans use response-based extraction.
        Can return multiple widgets if response contains meal plan + other widgets.
        """
        # Check if response contains multiple widget types
        widgets = []
        
        # Extract meal plan
        meal_data = widget_handler._extract_meal_plan_data(response_text)
        if meal_data.get("days"):
            widgets.append({
                "type": "meal_plan",
                "data": meal_data
            })
        
        # Check for workout plan in same response
        workout_data = widget_handler._extract_workout_data(response_text)
        if workout_data.get("exercises"):
            widgets.append({
                "type": "workout",
                "data": workout_data
            })
        
        # Check for lesson plan in same response (pass original_message for better title extraction)
        lesson_data = widget_handler._extract_lesson_plan_data(response_text, original_message)
        if lesson_data.get("title") or lesson_data.get("objectives"):
            widgets.append({
                "type": "lesson_plan",
                "data": lesson_data
            })
        
        # Return list if multiple widgets found, single dict if one, or empty dict if none
        if len(widgets) > 1:
            return widgets  # Return list for multiple widgets
        elif len(widgets) == 1:
            return widgets[0]  # Return single widget dict
        else:
            # No widgets extracted, return meal plan structure (may be empty)
            return {"type": "meal_plan", "data": meal_data}
    
    def process(self, user_request: str, context: dict = None) -> dict:
        """
        Generate meal plan response.
        Uses BaseSpecializedService.process() to get conversation history support.
        """
        if context is None:
            context = {}
        
        # Use BaseSpecializedService.process() for conversation history support
        # This ensures the meal plan service sees the full conversation context
        # (e.g., initial meal plan request + allergy answer)
        if self.db and self.openai_client:
            # Use BaseSpecializedService.process() which handles conversation history
            return BaseSpecializedService.process(self, user_request, context)
        else:
            # Fallback to BaseWidgetService if db/client not available
            prompt = self.load_prompt()
            return self.generate_response(prompt, user_request, context)

