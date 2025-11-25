"""
Base Widget Service
Simplified base class for widget services with process() method.
Supports both simple pattern (no db/openai_client) and registry pattern (with db/openai_client).
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)


class BaseWidgetService:
    """Base class for all specialized widget services."""

    def __init__(self, db: Session = None, openai_client: OpenAI = None):
        """
        Initialize BaseWidgetService.
        
        Args:
            db: Optional database session (for registry compatibility)
            openai_client: Optional OpenAI client (auto-created from env if not provided)
        """
        self.db = db
        self.prompt_file: str = ""
        self.model: str = "gpt-4o-mini"
        
        # Auto-create OpenAI client if not provided
        if openai_client:
            self.openai_client = openai_client
        else:
            # Create client from environment variable
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                self.openai_client = None
                logger.warning("⚠️ No OpenAI API key found - API calls will fail")

    def load_prompt(self) -> str:
        """
        Load prompt from file.
        Supports both direct file paths and prompt_loader system.
        """
        if not self.prompt_file:
            return ""
        
        # Try direct file path first (for simple pattern)
        path = Path(self.prompt_file)
        if path.exists():
            return path.read_text(encoding='utf-8')
        
        # Try with app/core/prompts/ prefix
        prompts_dir = Path(__file__).parent.parent.parent / "core" / "prompts"
        full_path = prompts_dir / self.prompt_file.replace("prompts/", "")
        if full_path.exists():
            return full_path.read_text(encoding='utf-8')
        
        # Fall back to prompt_loader system (for specialized prompts)
        try:
            from app.core.prompt_loader import load_raw_module
            # Map simple names to specialized names
            prompt_mapping = {
                "prompts/attendance.txt": "specialized_attendance.txt",
                "prompts/lesson_plan.txt": "specialized_lesson_plan.txt",
                "prompts/meal_plan.txt": "specialized_meal_plan.txt",
                "prompts/workout.txt": "specialized_workout.txt",
                "prompts/jasper_router.txt": "jasper_router.txt",
            }
            
            # Get the actual prompt file name
            actual_file = prompt_mapping.get(self.prompt_file, self.prompt_file)
            # Remove 'prompts/' prefix if present
            if actual_file.startswith("prompts/"):
                actual_file = actual_file.replace("prompts/", "")
            
            return load_raw_module(actual_file)
        except Exception as e:
            logger.warning(f"⚠️ Could not load prompt {self.prompt_file}: {e}")
            return ""

    def generate_response(self, prompt: str, user_request: str, context: dict) -> Dict[str, Any]:
        """
        Send request to OpenAI and return structured response.
        
        Args:
            prompt: System prompt
            user_request: User's request message
            context: Additional context dictionary
            
        Returns:
            Dictionary with response data
        """
        if not self.openai_client:
            raise ValueError("openai_client must be provided or OPENAI_API_KEY must be set")
        
        # Combine prompt and user request (simpler pattern)
        combined_prompt = f"{prompt}\n\nUser Request: {user_request}"
        
        # Add context if provided
        if context:
            context_str = str(context.get("widget_data", context))
            combined_prompt += f"\n\nContext: {context_str}"
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": combined_prompt}],
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            
            # Extract widget_data from context if available
            widget_data = context.get("widget_data", None)
            
            return {
                "response": content,
                "widget_data": widget_data
            }
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}", exc_info=True)
            raise

    def process(self, user_request: str, context: dict = None) -> dict:
        """
        Process user request and generate response.
        
        Args:
            user_request: User's request message
            context: Optional context dictionary
            
        Returns:
            Dictionary with response data
        """
        if context is None:
            context = {}
        
        prompt = self.load_prompt()
        return self.generate_response(prompt, user_request, context)

