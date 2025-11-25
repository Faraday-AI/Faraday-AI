"""
Specialized Lesson Plan Service
Handles all lesson plan creation with focused prompt and optimized model.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from openai import OpenAI
import logging
import os
import re

from app.services.pe.base_widget_service import BaseWidgetService
from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService
from app.services.pe import widget_handler

logger = logging.getLogger(__name__)


class LessonPlanService(BaseWidgetService, BaseSpecializedService):
    """
    Specialized service for Lesson Plan widget.
    Uses focused prompt (~400 tokens) and gpt-4o for quality lesson plans.
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
        
        self.prompt_file = "prompts/lesson_plan.txt"
        self.model = os.getenv("JASPER_MODEL", "gpt-4o")
        self.widget_type = "lesson_plan"
    
    def get_system_prompt(self) -> str:
        """Load the focused lesson plan prompt (BaseSpecializedService interface)."""
        return self.load_prompt()
    
    def get_supported_intents(self) -> List[str]:
        """Lesson plan service handles lesson plan intents."""
        return ["lesson_plan", "lesson", "unit_plan", "curriculum"]
    
    def get_model(self) -> str:
        """Use gpt-4o for lesson plans (high quality required)."""
        return self.model
    
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
    
    def extract_widget_data(self, response_text: str, intent: str, original_message: str = "") -> Dict[str, Any]:
        """
        Extract lesson plan widget data from response.
        Lesson plans use response-based extraction with comprehensive parsing.
        """
        return widget_handler._extract_lesson_plan_data(response_text, original_message)
    
    def process(self, user_request: str, context: dict = None) -> dict:
        """
        Generate lesson plan response with widget extraction.
        Uses BaseSpecializedService.process() to handle conversation history and extraction.
        Also processes response to separate markdown from JSON for better chat display.
        CRITICAL: Preserves widget_data that was already extracted.
        """
        # Call parent's process method which handles conversation history and extraction
        # This already extracts widget_data and puts it in result["widget_data"]
        result = BaseSpecializedService.process(self, user_request, context)
        
        # IMPORTANT: widget_data is already extracted and in result["widget_data"]
        # We just need to clean up the response text for chat display
        
        # Process response text: if it contains JSON at the end, separate it
        # The markdown part should be shown in chat, JSON is for extraction only
        response_text = result.get("response", "")
        widget_data = result.get("widget_data")  # Preserve existing widget_data
        json_data = None  # Initialize for scope
        
        # Check if response ends with JSON code block
        json_pattern = re.compile(r'```json\s*(\{.*?\})\s*```', re.DOTALL | re.IGNORECASE)
        json_match = json_pattern.search(response_text)
        
        if json_match:
            # Extract the markdown part (everything before the JSON)
            json_start = json_match.start()
            markdown_text = response_text[:json_start].strip()
            
            # Try to parse JSON to get complete data
            try:
                import json
                json_data = json.loads(json_match.group(1))
                
                # If markdown text is substantial, use it for chat display
                # But supplement it with missing sections from JSON if needed
                if len(markdown_text) > 100:
                    # Check if markdown is missing homework or exit_ticket
                    markdown_lower = markdown_text.lower()
                    has_homework = "homework" in markdown_lower and json_data.get("homework")
                    has_exit_ticket = "exit ticket" in markdown_lower or "exit_ticket" in markdown_lower
                    
                    # If missing, append from JSON
                    if json_data.get("homework") and not has_homework:
                        markdown_text += f"\n\n### Homework\n{json_data['homework']}\n"
                    if json_data.get("exit_ticket") and not has_exit_ticket:
                        markdown_text += f"\n\n### Exit Ticket\n{json_data['exit_ticket']}\n"
                    
                    result["response"] = markdown_text
                else:
                    # No markdown text, format JSON as readable markdown for chat
                    formatted_text = self._format_lesson_plan_as_markdown(json_data)
                    result["response"] = formatted_text
                
                # Use JSON data for widget_data (it has the most complete data)
                if json_data:
                    widget_data = json_data
            except Exception as e:
                logger.warning(f"⚠️ Could not parse JSON: {e}")
                # Fall back to using markdown text as-is
                if len(markdown_text) > 100:
                    result["response"] = markdown_text
        
        # CRITICAL: Ensure widget_data is preserved
        # BaseSpecializedService.process() returns widget_data as a plain dict (the lesson plan data)
        # ai_assistant_service.py will wrap it in {type: "lesson_plan", data: {...}} format
        # So we just need to preserve it as-is (don't double-wrap)
        # Prefer JSON data if available (most complete), otherwise use extracted widget_data
        if json_data:
            result["widget_data"] = json_data
        elif widget_data:
            result["widget_data"] = widget_data
        
        logger.info(f"✅ LessonPlanService.process() - widget_data preserved: {bool(result.get('widget_data'))}, type: {type(result.get('widget_data'))}")
        
        return result
    
    def _format_lesson_plan_as_markdown(self, data: Dict[str, Any]) -> str:
        """
        Format lesson plan JSON data as readable markdown text for chat display.
        """
        lines = []
        
        # Title
        if data.get("title"):
            lines.append(f"## {data['title']}\n")
        
        # Description
        if data.get("description"):
            lines.append(f"{data['description']}\n")
        
        # Learning Objectives
        if data.get("learning_objectives"):
            lines.append("### Learning Objectives")
            for obj in data["learning_objectives"]:
                lines.append(f"- {obj}")
            lines.append("")
        
        # Standards
        if data.get("standards"):
            lines.append("### Standards")
            for std in data["standards"]:
                if isinstance(std, dict):
                    lines.append(f"- **{std.get('code', '')}**: {std.get('description', '')}")
                else:
                    lines.append(f"- {std}")
            lines.append("")
        
        # Materials
        if data.get("materials_list"):
            lines.append("### Materials")
            for material in data["materials_list"]:
                lines.append(f"- {material}")
            lines.append("")
        
        # Introduction
        if data.get("introduction"):
            lines.append("### Introduction")
            lines.append(f"{data['introduction']}\n")
        
        # Activities
        if data.get("activities"):
            lines.append("### Activities")
            for i, activity in enumerate(data["activities"], 1):
                if isinstance(activity, dict):
                    name = activity.get("name", f"Activity {i}")
                    desc = activity.get("description", "")
                    time = activity.get("time_allocation", "")
                    lines.append(f"**{name}**" + (f" ({time})" if time else ""))
                    if desc:
                        lines.append(f"{desc}\n")
                else:
                    lines.append(f"{i}. {activity}\n")
        
        # Assessment
        if data.get("assessment"):
            lines.append("### Assessment")
            if isinstance(data["assessment"], dict):
                if data["assessment"].get("formative"):
                    lines.append(f"**Formative:** {data['assessment']['formative']}")
                if data["assessment"].get("summative"):
                    lines.append(f"**Summative:** {data['assessment']['summative']}")
            else:
                lines.append(str(data["assessment"]))
            lines.append("")
        
        # Exit Ticket
        if data.get("exit_ticket"):
            lines.append("### Exit Ticket")
            lines.append(f"{data['exit_ticket']}\n")
        
        # Extensions
        if data.get("extensions"):
            lines.append("### Extensions")
            for ext in data["extensions"]:
                lines.append(f"- {ext}")
            lines.append("")
        
        # Safety Considerations
        if data.get("safety_considerations"):
            lines.append("### Safety Considerations")
            for safety in data["safety_considerations"]:
                lines.append(f"- {safety}")
            lines.append("")
        
        # Homework
        if data.get("homework"):
            lines.append("### Homework")
            lines.append(f"{data['homework']}\n")
        
        # Danielson Framework
        if data.get("danielson_framework_alignment"):
            lines.append("### Danielson Framework Alignment")
            df = data["danielson_framework_alignment"]
            if isinstance(df, dict):
                for domain in ["domain_1", "domain_2", "domain_3", "domain_4"]:
                    if df.get(domain):
                        domain_name = domain.replace("_", " ").title()
                        lines.append(f"**{domain_name}:** {df[domain]}")
            lines.append("")
        
        # Costa's Levels
        if data.get("costas_levels_of_questioning"):
            lines.append("### Costa's Levels of Questioning")
            cl = data["costas_levels_of_questioning"]
            if isinstance(cl, dict):
                for level in ["level_1", "level_2", "level_3"]:
                    if cl.get(level):
                        level_name = level.replace("_", " ").title()
                        lines.append(f"**{level_name}:** {cl[level]}")
            lines.append("")
        
        return "\n".join(lines)

