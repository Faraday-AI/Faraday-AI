"""
Specialized Attendance Service
Handles all attendance-related queries with focused prompt and optimized model.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from openai import OpenAI
import logging
import os

from app.services.pe.base_widget_service import BaseWidgetService
from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService

logger = logging.getLogger(__name__)


class AttendanceService(BaseWidgetService, BaseSpecializedService):
    """
    Specialized service for attendance queries.
    Uses focused prompt (~300 tokens) and gpt-4o-mini for faster, cheaper responses.
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
        
        self.prompt_file = "prompts/attendance.txt"
        self.model = os.getenv("JASPER_MINI_MODEL", "gpt-4o-mini")
        self.widget_type = "attendance"
    
    def get_system_prompt(self) -> str:
        """Load the focused attendance prompt (BaseSpecializedService interface)."""
        return self.load_prompt()
    
    def get_supported_intents(self) -> List[str]:
        """Attendance service handles attendance-related intents."""
        return ["attendance", "attendance_patterns", "attendance_analysis"]
    
    def get_model(self) -> str:
        """Use gpt-4o-mini for attendance queries (faster, cheaper, sufficient quality)."""
        return self.model
    
    def extract_widget_data(self, response_text: str, intent: str, original_message: str = "") -> Dict[str, Any]:
        """
        Extract attendance widget data from response.
        Handles JSON in markdown code blocks.
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
                # Extract attendance_patterns if present, otherwise use the whole object
                if isinstance(parsed_data, dict):
                    if "attendance_patterns" in parsed_data:
                        return {
                            "type": "attendance",
                            "data": parsed_data["attendance_patterns"]
                        }
                    else:
                        # Return the whole parsed JSON
                        return {
                            "type": "attendance",
                            "data": parsed_data
                        }
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"⚠️ Failed to parse JSON from markdown code block: {e}")
        
        # Fallback: return raw response text
        return {
            "type": "attendance",
            "data": {"raw_response": response_text}
        }
    
    def generate_response(
        self,
        messages=None,
        temperature: float = 0.7,
        max_tokens=None,
        response_format=None,
        user_first_name=None,
        prompt=None,
        user_request=None,
        context=None
    ):
        """
        Override generate_response to use BaseSpecializedService's version.
        Handles both BaseSpecializedService signature (messages) and BaseWidgetService signature (prompt, user_request, context).
        """
        # If called with BaseSpecializedService signature (messages parameter)
        if messages is not None:
            return BaseSpecializedService.generate_response(
                self, messages, temperature, max_tokens, response_format, user_first_name
            )
        # If called with BaseWidgetService signature (prompt, user_request, context)
        elif prompt is not None and user_request is not None:
            # Convert to BaseSpecializedService format
            messages = [{"role": "user", "content": user_request}]
            return BaseSpecializedService.generate_response(
                self, messages, temperature, max_tokens, response_format, 
                user_first_name=context.get("user_first_name") if context else None
            )
        else:
            raise ValueError("generate_response() requires either 'messages' or 'prompt'/'user_request' parameters")
    
    def process(self, user_request: str, context: dict = None) -> dict:
        """
        Generate attendance response with widget extraction.
        Uses BaseSpecializedService.process() to handle conversation history and extraction.
        """
        # Call parent's process method which handles conversation history and extraction
        return BaseSpecializedService.process(self, user_request, context)
    
    def process(self, user_request: str, context: dict = None) -> dict:
        """
        Generate attendance response with widget extraction.
        Uses BaseSpecializedService.process() to handle conversation history and extraction.
        """
        # Call parent's process method which handles conversation history and extraction
        return BaseSpecializedService.process(self, user_request, context)

