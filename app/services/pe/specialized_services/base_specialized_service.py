"""
Base class for specialized widget services.
Each widget service has its own focused prompt and handles specific widget types.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class BaseSpecializedService(ABC):
    """
    Base class for specialized widget services.
    
    Each specialized service:
    - Has its own focused system prompt (~200-500 tokens)
    - Handles one or a few related widget types
    - Can use different models (gpt-4o-mini for simple, gpt-4 for complex)
    - Is optimized for its specific use case
    """
    
    def __init__(self, db: Session, openai_client: OpenAI):
        self.db = db
        self.openai_client = openai_client
        self.service_name = self.__class__.__name__
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the focused system prompt for this service.
        Should be concise and focused on the specific widget type(s).
        
        Returns:
            System prompt string (~200-500 tokens)
        """
        pass
    
    @abstractmethod
    def get_supported_intents(self) -> List[str]:
        """
        Get list of intents this service handles.
        
        Returns:
            List of intent strings (e.g., ['attendance', 'attendance_patterns'])
        """
        pass
    
    @abstractmethod
    def get_model(self) -> str:
        """
        Get the OpenAI model to use for this service.
        Can use gpt-4o-mini for simple queries, gpt-4 for complex ones.
        
        Returns:
            Model name string (e.g., 'gpt-4o-mini' or 'gpt-4')
        """
        pass
    
    def should_handle(self, intent: str) -> bool:
        """
        Check if this service should handle the given intent.
        
        Args:
            intent: The classified intent string
            
        Returns:
            True if this service handles this intent
        """
        return intent in self.get_supported_intents()
    
    def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None,
        user_first_name: Optional[str] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Generate response using OpenAI API with this service's model and prompt.
        
        Args:
            messages: List of message dicts (will have system prompt prepended)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            response_format: Optional response format (e.g., JSON schema)
            
        Returns:
            Tuple of (response_text, usage_metadata)
        """
        # Prepend system prompt
        system_prompt = self.get_system_prompt()
        
        # Add user name requirement if provided
        if user_first_name:
            name_instruction = f"\n\n🚨 USER NAME REQUIREMENT: The user's first name is {user_first_name}. You MUST use their name ({user_first_name}) in your response. This is MANDATORY."
            system_prompt = system_prompt + name_instruction
        
        full_messages = [
            {"role": "system", "content": system_prompt}
        ] + messages
        
        model = self.get_model()
        
        logger.info(f"🎯 {self.service_name}: Generating response with model {model}")
        logger.debug(f"📝 System prompt length: {len(system_prompt)} chars")
        
        try:
            request_params = {
                "model": model,
                "messages": full_messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            if response_format:
                request_params["response_format"] = response_format
            
            response = self.openai_client.chat.completions.create(**request_params)
            
            response_text = response.choices[0].message.content
            usage_metadata = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "model": model
            }
            
            logger.info(f"✅ {self.service_name}: Response generated ({usage_metadata['total_tokens']} tokens)")
            
            return response_text, usage_metadata
            
        except Exception as e:
            logger.error(f"❌ {self.service_name}: Error generating response: {e}", exc_info=True)
            raise
    
    def extract_widget_data(self, response_text: str, intent: str, original_message: str = "") -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Extract widget-specific data from the response.
        Override in subclasses for widget-specific extraction.
        
        Can return either:
        - Single widget: Dict[str, Any] with {"type": "...", "data": {...}}
        - Multiple widgets: List[Dict[str, Any]] with multiple widget dicts
        
        Args:
            response_text: The AI response text
            intent: The classified intent
            original_message: The original user message (for context in extraction)
            intent: The intent that triggered this service
            
        Returns:
            Dictionary with widget data (or list of dictionaries for multiple widgets)
        """
        # Default: return general response
        return {"type": "general_response", "data": response_text}
    
    def extract_multiple_widgets(self, response_text: str, intent: str) -> List[Dict[str, Any]]:
        """
        Extract all widgets from response (optional method for multi-widget extraction).
        Override in subclasses if service can extract multiple widgets.
        
        Args:
            response_text: The AI response text
            intent: The intent that triggered this service
            
        Returns:
            List of widget dictionaries, each with {"type": "...", "data": {...}}
        """
        # Default: return single widget as list
        widget = self.extract_widget_data(response_text, intent)
        if isinstance(widget, list):
            return widget
        return [widget] if widget else []
    
    def process(self, user_request: str, context: dict = None) -> dict:
        """
        Process user request and generate response.
        This is the main entry point called by ModelRouter.
        
        Args:
            user_request: User's request message
            context: Optional context dictionary (may include conversation_messages for history)
            
        Returns:
            Dictionary with response data: {"response": str, "widget_data": dict, "usage": dict}
        """
        if context is None:
            context = {}
        
        # Get user first name from context if available
        user_first_name = context.get("user_first_name")
        
        # Build messages list - use conversation history if available, otherwise just current request
        conversation_messages = context.get("conversation_messages", [])
        if conversation_messages:
            # Keep more conversation history (25 messages = ~12-13 exchanges)
            # Use intelligent truncation to stay within context limits
            max_history_messages = 25
            if len(conversation_messages) > max_history_messages:
                # Keep the most recent messages
                conversation_messages = conversation_messages[-max_history_messages:]
                logger.info(f"⚠️ Truncated conversation history from {len(context.get('conversation_messages', []))} to {max_history_messages} messages")
            
            # Intelligent message truncation with sliding window approach
            # Older messages get truncated more aggressively, recent messages keep more context
            # Estimate: ~4 chars per token
            messages = []
            total_messages = len(conversation_messages)
            
            for idx, msg in enumerate(conversation_messages):
                content = msg.get("content", "")
                original_length = len(content)
                
                # Calculate truncation based on message age (older = more aggressive)
                # Recent messages (last 10): keep up to 500 chars
                # Middle messages (10-20): keep up to 300 chars  
                # Older messages (20+): keep up to 200 chars
                if idx >= total_messages - 10:
                    # Recent messages - keep more context
                    max_length = 500
                elif idx >= total_messages - 20:
                    # Middle messages - moderate truncation
                    max_length = 300
                else:
                    # Older messages - aggressive truncation
                    max_length = 200
                
                if len(content) > max_length:
                    # Smart truncation: keep beginning (context) and end (conclusion) if very long
                    if len(content) > max_length * 2:
                        # Very long message: keep start and end
                        start_chars = int(max_length * 0.6)
                        end_chars = int(max_length * 0.4)
                        truncated = content[:start_chars] + "...[truncated]..." + content[-end_chars:]
                    else:
                        # Moderately long: just truncate end
                        truncated = content[:max_length] + "..."
                    
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": truncated
                    })
                    logger.debug(f"Truncated history message {idx+1}/{total_messages} from {original_length} to {len(truncated)} chars (age-based)")
                else:
                    messages.append(msg)
            
            # Ensure current user_request is the last message (in case it's not in history yet)
            if not messages or messages[-1].get("role") != "user" or messages[-1].get("content") != user_request:
                messages.append({"role": "user", "content": user_request})
        else:
            # No conversation history - just use current request
            messages = [{"role": "user", "content": user_request}]
        
        # Generate response with full conversation context
        # Set max_tokens to prevent completion from being too long
        # With 25 messages (intelligently truncated): system ~2000 tokens, messages ~3000-4000 tokens, completion ~2000 tokens
        # For gpt-4o (128k context) or gpt-4-turbo (128k context), we have plenty of room
        # For older models with 8k context, the intelligent truncation above should keep us safe
        max_completion_tokens = 2000  # Reasonable limit for detailed responses
        
        response_text, usage_metadata = self.generate_response(
            messages=messages,
            temperature=0.2,
            max_tokens=max_completion_tokens,
            user_first_name=user_first_name
        )
        
        # Extract widget data
        intent = context.get("intent", "general")
        original_message = user_request  # Pass original message for title extraction
        widget_data = self.extract_widget_data(response_text, intent, original_message)
        
        return {
            "response": response_text,
            "widget_data": widget_data,
            "usage": usage_metadata
        }

