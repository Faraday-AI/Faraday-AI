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
import json
import asyncio

from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService
from app.dashboard.services.gpt_function_service import GPTFunctionService
from app.dashboard.services.widget_function_schemas import WidgetFunctionSchemas

logger = logging.getLogger(__name__)


class GeneralWidgetService(BaseSpecializedService):
    """
    General service for GPT function calling widgets.
    Handles Teams, Adaptive PE, Analytics, Safety, Class Insights, etc.
    Uses focused prompt (~400 tokens) and gpt-4o-mini for faster responses.
    Supports function calling for SMS and other widget operations.
    """
    
    def get_system_prompt(self) -> str:
        """Load the focused general widgets prompt."""
        try:
            from app.core.prompt_loader import load_raw_module
            return load_raw_module("specialized_general_widgets.txt")
        except Exception as e:
            logger.warning(f"⚠️ Could not load specialized general widgets prompt: {e}")
            # Fallback to minimal prompt
            return """You are Jasper's Widget Specialist. Handle widget requests using GPT function calling to execute backend operations. You can send SMS messages using the send_sms function."""
    
    def get_supported_intents(self) -> List[str]:
        """General widget service handles all GPT function calling widgets."""
        return [
            "widget",  # General widget intent
            "sms",  # SMS sending
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
    
    def process(self, user_request: str, context: dict = None) -> dict:
        """
        Override process to add function calling support for SMS and other widget operations.
        """
        # Check if this is an SMS request (has phone number and SMS keywords)
        import re
        msg_lower = user_request.lower()
        phone_pattern = r'\+?\d{10,}'
        has_phone_number = bool(re.search(phone_pattern, msg_lower))
        has_sms_keyword = any(kw in msg_lower for kw in ["text", "sms", "message", "send"])
        
        # If it's an SMS request, use function calling
        if has_phone_number and has_sms_keyword:
            try:
                # Handle event loop properly (same pattern as ContentGenerationService)
                try:
                    loop = asyncio.get_running_loop()
                    # If we're in an async context, we need to run in a thread
                    import concurrent.futures
                    import threading
                    
                    # Create a new event loop in a thread
                    def run_in_thread():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            return new_loop.run_until_complete(self._process_with_function_calling(user_request, context))
                        finally:
                            new_loop.close()
                    
                    # Run in a thread pool
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_thread)
                        return future.result(timeout=60)  # 1 minute timeout for SMS
                except RuntimeError:
                    # No event loop running, we can use run_until_complete
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    return loop.run_until_complete(self._process_with_function_calling(user_request, context))
            except Exception as e:
                logger.error(f"Error in function calling for SMS: {e}", exc_info=True)
                # Fallback to regular processing
                return super().process(user_request, context)
        
        # For other requests, use regular processing
        return super().process(user_request, context)
    
    async def _process_with_function_calling(self, user_request: str, context: dict) -> dict:
        """Process request with function calling support (for SMS and other operations)."""
        # Get user_id from context
        teacher_id = context.get("teacher_id")
        user_id = str(teacher_id) if teacher_id else context.get("user_id", "guest")
        
        # Initialize GPTFunctionService
        gpt_function_service = GPTFunctionService(
            db=self.db,
            user_id=user_id
        )
        
        # Get all widget function schemas (includes send_sms)
        all_schemas = WidgetFunctionSchemas.get_all_schemas()
        
        # Get conversation history
        conversation_messages = context.get("conversation_messages", [])
        if not conversation_messages:
            conversation_messages = [{"role": "user", "content": user_request}]
        
        # Build messages with system prompt
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        messages.extend(conversation_messages)
        
        # Generate response with function calling (OpenAI client is synchronous, not async)
        response = self.openai_client.chat.completions.create(
            model=self.get_model(),
            messages=messages,
            tools=[{"type": "function", "function": schema} for schema in all_schemas],
            tool_choice="auto",
            temperature=0.2,
            max_tokens=2000
        )
        
        message = response.choices[0].message
        ai_response = message.content or ""
        
        # Handle function calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
                
                logger.info(f"🎯 GeneralWidgetService: Executing function {function_name}")
                
                # Execute the function
                result = await gpt_function_service._execute_function_call(
                    function_name=function_name,
                    arguments=function_args,
                    user_id=user_id
                )
                
                # Handle SMS function results (success or error)
                if function_name == "send_sms":
                    if result.get("status") == "success":
                        phone = result.get("to", "the number")
                        ai_response = f"I've sent the SMS message to {phone}. Message SID: {result.get('message_sid', 'N/A')}"
                    else:
                        # Handle error cases - check both "error" and "message" fields
                        error_msg = result.get("error") or result.get("message", "Unknown error")
                        error_details = result.get("details", "")
                        phone = result.get("to") or function_args.get("to_number") or function_args.get("phone_number", "the number")
                        
                        logger.warning(f"⚠️ SMS send failed - result: {result}, error_msg: {error_msg}, phone: {phone}")
                        
                        # Provide user-friendly error message
                        if "unverified" in error_msg.lower():
                            ai_response = f"I couldn't send the SMS to {phone}. This number is not verified in your Twilio account. Trial accounts can only send messages to verified numbers. Please verify this number in your Twilio console or upgrade your account."
                        elif "invalid phone number" in error_msg.lower() or "invalid" in error_msg.lower():
                            ai_response = f"I couldn't send the SMS to {phone}. The phone number format is invalid. Please use E.164 format (e.g., +1234567890) with the country code."
                        else:
                            ai_response = f"I encountered an error sending the SMS to {phone}: {error_msg}"
                            if error_details:
                                ai_response += f" {error_details}"
                        
                        # Ensure we always have a response
                        if not ai_response or ai_response.strip() == "":
                            ai_response = f"I couldn't send the SMS to {phone}. Please check the phone number format and your Twilio account settings."
        
        # Extract widget data
        intent = context.get("intent", "general")
        widget_data = self.extract_widget_data(ai_response, intent, user_request)
        
        return {
            "response": ai_response,
            "widget_data": widget_data,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "model": self.get_model()
            }
        }
    
    def extract_widget_data(self, response_text: str, intent: str, original_message: str = "") -> Dict[str, Any]:
        """
        Extract widget data from response.
        General widgets use GPT function calling, but may also have JSON in responses.
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
                        "type": "general_widget",
                        "data": parsed_data,
                        "widget_type": intent
                    }
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"⚠️ Failed to parse JSON from markdown code block: {e}")
        
        # Fallback: return text response
        return {
            "type": "general_widget",
            "data": {"response": response_text},
            "widget_type": intent
        }

