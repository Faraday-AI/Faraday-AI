"""
General Widget Service
Handles all GPT function calling widgets (Teams, Analytics, Safety, etc.)
Uses focused prompt and optimized model for widget operations.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from openai import OpenAI
import logging
import os

from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService

logger = logging.getLogger(__name__)


class GeneralWidgetService(BaseSpecializedService):
    """
    General service for GPT function calling widgets.
    Handles Teams, Adaptive PE, Analytics, Safety, Class Insights, etc.
    Uses focused prompt (~400 tokens) and gpt-4o-mini for faster responses.
    """
    
    def get_system_prompt(self) -> str:
        """Load the focused general widgets prompt."""
        try:
            from app.core.prompt_loader import load_raw_module
            return load_raw_module("specialized_general_widgets.txt")
        except Exception as e:
            logger.warning(f"⚠️ Could not load specialized general widgets prompt: {e}")
            # Fallback to minimal prompt
            return """You are Jasper's Widget Specialist. Handle widget requests using GPT function calling to execute backend operations."""
    
    def get_supported_intents(self) -> List[str]:
        """General widget service handles all GPT function calling widgets."""
        return [
            "widget",  # General widget intent
            "teams", "squad", "balanced teams",
            "adaptive", "adaptive_pe",
            "analytics", "performance", "predict",
            "safety", "risk",
            "class_insights", "insight",
            "parent_communication", "communication",
            "game_predictions", "predictions",
            "skill_assessment", "assessment",
            "health_metrics", "health",
            "drivers_ed", "driver",
            "equipment",
            "activity_scheduling", "activity_tracking", "activity_planning",
            "fitness_goals", "goals",
            "collaboration",
            "notifications",
            "progress_tracking", "progress",
            "class_management", "student_management",
            "engagement",
            "safety_reports",
            "movement_analysis", "movement",
            # Additional widget intents
            "schedule", "tracking", "progress", "capabilities", "features"
        ]
    
    def get_model(self) -> str:
        """Use gpt-4o-mini for general widgets (faster, cheaper, sufficient quality)."""
        return os.getenv("JASPER_MINI_MODEL", "gpt-4o-mini")
    
    def extract_widget_data(self, response_text: str, intent: str, original_message: str = "") -> Dict[str, Any]:
        """
        Extract widget data from response.
        General widgets use GPT function calling, so widget data comes from backend.
        """
        return {
            "type": "general_widget",
            "data": response_text,
            "widget_type": intent
        }

