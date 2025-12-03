"""
SMS Message Service
Handles AI-generated SMS message content creation.
Uses focused prompt and optimized model for SMS message generation.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI
import logging
import os
import re
import json

from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService
from app.services.pe.base_widget_service import BaseWidgetService

logger = logging.getLogger(__name__)


def extract_sms_data(response_text: str) -> Dict[str, Any]:
    """
    Extract SMS message data from AI response.
    Looks for JSON block at the end, or parses the message text directly.
    """
    try:
        # Try to extract JSON block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            try:
                data = json.loads(json_str)
                return data
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from SMS response")
        
        # If no JSON, extract the message text (first non-empty line or section)
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        if lines:
            # Find the actual message (skip headers like "[SMS Message - X characters]")
            message_text = None
            for line in lines:
                if not line.startswith('[') and not line.startswith('{') and len(line) > 10:
                    message_text = line
                    break
            
            if not message_text:
                # Use first substantial line
                message_text = lines[0] if lines else response_text.strip()
            
            # Count characters
            char_count = len(message_text)
            
            # Check for compliance elements
            has_opt_out = 'STOP' in message_text.upper() or 'opt out' in message_text.lower()
            
            return {
                "message_text": message_text,
                "character_count": char_count,
                "compliance_included": has_opt_out,
                "message_type": "general",
                "language": "en"
            }
        
        return {}
    except Exception as e:
        logger.error(f"Error extracting SMS data: {str(e)}")
        return {}


class SMSService(BaseWidgetService, BaseSpecializedService):
    """
    Specialized service for SMS Message generation.
    Uses focused prompt (~400 tokens) and gpt-4o-mini for fast, concise message generation.
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
        
        self.prompt_file = "prompts/sms.txt"
        self.model = os.getenv("JASPER_MODEL", "gpt-4o-mini")  # Use mini for faster, cheaper SMS generation
        self.widget_type = "sms"
    
    def get_system_prompt(self) -> str:
        """Load the focused SMS prompt (BaseSpecializedService interface)."""
        try:
            from app.core.prompt_loader import load_raw_module
            return load_raw_module("specialized_sms.txt")
        except Exception as e:
            logger.warning(f"⚠️ Could not load specialized SMS prompt: {e}")
            # Fallback to minimal prompt
            return """You are Jasper's SMS Specialist. Generate concise, compliant SMS messages (160-320 chars) with opt-out instructions."""
    
    def get_supported_intents(self) -> List[str]:
        """SMS service handles SMS-related intents."""
        return [
            "sms",
            "text_message",
            "send_sms",
            "sms_message",
            "text",
            "message",
            "send_text",
            "parent_communication",
            "student_communication",
            "notification"
        ]
    
    def get_model(self) -> str:
        """Use gpt-4o-mini for SMS messages (fast, cost-effective, sufficient quality)."""
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
        This ensures proper method resolution when SMSService inherits from both classes.
        """
        # Explicitly call BaseSpecializedService's generate_response
        return BaseSpecializedService.generate_response(
            self,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens or 200,  # SMS messages are short, limit tokens
            response_format=response_format,
            user_first_name=user_first_name
        )
    
    def extract_widget_data(self, response_text: str, intent: str, original_message: str = "") -> Dict[str, Any]:
        """
        Extract SMS message data from response.
        Returns SMS data directly (same pattern as lesson plan/workout).
        BaseSpecializedService.process() will wrap it in {type: "sms", data: {...}} format.
        """
        logger.info(f"🔍 SMSService.extract_widget_data called, response_text length: {len(response_text)}")
        sms_data = extract_sms_data(response_text)
        logger.info(f"🔍 extract_sms_data returned: {type(sms_data)}, keys: {list(sms_data.keys()) if isinstance(sms_data, dict) else 'not a dict'}")
        # Return data directly
        # BaseSpecializedService.process() will wrap it in {type: "sms", data: {...}} format
        return sms_data
    
    def process(self, user_request: str, context: dict = None) -> dict:
        """
        Generate SMS message response with widget extraction.
        Uses BaseSpecializedService.process() to handle conversation history and extraction.
        """
        # Call parent's process method which handles conversation history and extraction
        # This already extracts widget_data and puts it in result["widget_data"]
        return BaseSpecializedService.process(self, user_request, context)

