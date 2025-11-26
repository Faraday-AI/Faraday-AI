"""
General Response Service
Handles widgets that provide text-based responses (Exercise Tracker, Fitness Challenges, etc.)
Uses focused prompt and optimized model for advice and recommendations.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from openai import OpenAI
import logging
import os

from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService

logger = logging.getLogger(__name__)


class GeneralResponseService(BaseSpecializedService):
    """
    General service for text-based response widgets.
    Handles Exercise Tracker, Fitness Challenges, Heart Rate, Sports Psychology, etc.
    Uses focused prompt (~300 tokens) and gpt-4o-mini for faster responses.
    """
    
    def get_system_prompt(self) -> str:
        """Load the focused general response prompt."""
        try:
            from app.core.prompt_loader import load_raw_module
            return load_raw_module("specialized_general_response.txt")
        except Exception as e:
            logger.warning(f"⚠️ Could not load specialized general response prompt: {e}")
            # Fallback to minimal prompt
            return """You are Jasper's General Response Specialist. Provide helpful text responses and recommendations for PE activities."""
    
    def get_supported_intents(self) -> List[str]:
        """General response service handles text-based response widgets and general queries."""
        return [
            "general",  # General conversational queries
            "general_response",  # Explicit general response intent
            "exercise_tracker", "exercise",
            "fitness_challenges", "challenges",
            "heart_rate", "heart_rate_zones",
            "sports_psychology", "psychology",
            "timers", "timer",
            "warmups", "warmup",
            "weather",
            "video_analysis", "video",
            "routines", "routine"
        ]
    
    def get_model(self) -> str:
        """Use gpt-4o-mini for general responses (faster, cheaper, sufficient quality)."""
        return os.getenv("JASPER_MINI_MODEL", "gpt-4o-mini")
    
    def extract_widget_data(self, response_text: str, intent: str, original_message: str = "") -> Dict[str, Any]:
        """
        Extract widget data from response.
        General response widgets may have JSON in responses.
        Tries to extract JSON from markdown code blocks first.
        """
        import json
        import re
        
        # First, try to extract JSON from markdown code blocks
        json_pattern = re.compile(r'```(?:json)?\s*(\{.*?\})\s*```', re.DOTALL | re.IGNORECASE)
        json_match = json_pattern.search(response_text)
        if json_match:
            try:
                json_str = json_match.group(1)
                parsed_data = json.loads(json_str)
                # Return structured data if JSON found
                if isinstance(parsed_data, dict):
                    return {
                        "type": "general_response",
                        "data": parsed_data,
                        "widget_type": intent
                    }
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"⚠️ Failed to parse JSON from markdown code block: {e}")
        
        # Fallback: return text response
        return {
            "type": "general_response",
            "data": {"response": response_text},
            "widget_type": intent
        }

