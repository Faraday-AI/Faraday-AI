"""
Specialized Workout Service
Handles all workout plan creation with focused prompt and optimized model.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from openai import OpenAI
import logging
import os
import json
import re

from app.services.pe.base_widget_service import BaseWidgetService
from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService

logger = logging.getLogger(__name__)


def extract_workout_data(response_text: str) -> Dict[str, Any]:
    """
    Extracts workout plan structured data.
    Handles JSON from markdown code blocks first, then falls back to regex patterns.
    Handles multiple formats: "Bench Press: 3x10", "Bench Press: 3 sets of 10 reps", 
    "Bench Press (3 sets, 10 reps)", etc.
    
    Args:
        response_text: AI's response text containing workout plan
        
    Returns:
        Dictionary with structured workout data
    """
    if not response_text:
        return {}
    
    json_pattern = re.compile(r'```(?:json)?\s*(\{.*?\})\s*```', re.DOTALL | re.IGNORECASE)
    json_match = json_pattern.search(response_text)
    parsed_json_data = None
    if json_match:
        try:
            json_str = json_match.group(1)
            parsed_json_data = json.loads(json_str)
            logger.info(f"✅ Parsed JSON successfully from markdown code block, keys: {list(parsed_json_data.keys()) if isinstance(parsed_json_data, dict) else 'not a dict'}")
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"⚠️ Failed to parse JSON from markdown code block: {e}")
            parsed_json_data = None
    
    if parsed_json_data is None:
        json_marker_pattern = re.compile(r'```(?:json)?', re.IGNORECASE)
        json_marker_match = json_marker_pattern.search(response_text)
        
        if json_marker_match:
            try:
                marker_start = json_marker_match.start()
                marker_end = json_marker_match.end()
                
                brace_start = None
                for i in range(marker_end, min(marker_end + 100, len(response_text))):
                    if response_text[i] == '{':
                        brace_start = i
                        break
                
                if brace_start is None:
                    logger.warning(f"⚠️ Found ```json marker at {marker_start} but no opening brace found")
                else:
                    brace_count = 0
                    json_end_pos = None
                    json_str = None
                    
                    for i in range(brace_start, len(response_text)):
                        char = response_text[i]
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                json_end_pos = i + 1
                                break
                    
                    if json_end_pos is None:
                        closing_marker = response_text.find('```', brace_start)
                        if closing_marker > brace_start:
                            potential_json = response_text[brace_start:closing_marker].rstrip()
                            last_brace = potential_json.rfind('}')
                            if last_brace > 0:
                                json_str = potential_json[:last_brace + 1]
                                json_end_pos = brace_start + len(json_str)
                            else:
                                json_str = potential_json
                                json_end_pos = closing_marker
                        else:
                            potential_json = response_text[brace_start:].rstrip()
                            last_brace = potential_json.rfind('}')
                            if last_brace > 0:
                                json_str = potential_json[:last_brace + 1]
                                open_braces = json_str.count('{')
                                close_braces = json_str.count('}')
                                open_brackets = json_str.count('[')
                                close_brackets = json_str.count(']')
                                
                                missing_braces = open_braces - close_braces
                                missing_brackets = open_brackets - close_brackets
                                
                                if missing_braces > 0 or missing_brackets > 0:
                                    json_str += ']' * missing_brackets
                                    json_str += '}' * missing_braces
                                
                                json_end_pos = brace_start + len(json_str)
                    
                    if json_end_pos is not None and json_str is not None:
                        try:
                            parsed_json_data = json.loads(json_str)
                            logger.info(f"✅ Parsed JSON successfully, keys: {list(parsed_json_data.keys()) if isinstance(parsed_json_data, dict) else 'not a dict'}")
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ JSON parsing failed: {e}")
                            parsed_json_data = None
            except Exception as e:
                logger.error(f"❌ Error during JSON extraction: {e}", exc_info=True)
                parsed_json_data = None
    
    if isinstance(parsed_json_data, dict):
        workout_plan = parsed_json_data.get("workout_plan") or parsed_json_data.get("workoutplan")
        if workout_plan:
            plan_name = parsed_json_data.get("plan_name") or parsed_json_data.get("planname") or "Week-Long Workout Plan"
            description = parsed_json_data.get("description") or ""
            workout_data = {
                "plan_name": plan_name,
                "description": description,
                "days": []
            }
            for day_key, day_data in workout_plan.items():
                if isinstance(day_data, dict):
                    day_entry = {
                        "day": day_key,
                        "focus": day_data.get("focus", ""),
                        "exercises": [],
                        "activities": []
                    }
                    if day_data.get("exercises"):
                        for ex in day_data["exercises"]:
                            if isinstance(ex, str):
                                day_entry["exercises"].append({"name": ex, "description": ex})
                            elif isinstance(ex, dict):
                                day_entry["exercises"].append(ex)
                    if day_data.get("activities"):
                        day_entry["activities"] = day_data["activities"]
                    workout_data["days"].append(day_entry)
            return workout_data
        
        strength_training = parsed_json_data.get("strength_training") or parsed_json_data.get("strengthtraining")
        cardio = parsed_json_data.get("cardio")
        exercises = parsed_json_data.get("exercises")
        
        if strength_training or cardio or exercises:
            workout_data = {}
            plan_name = parsed_json_data.get("plan_name") or parsed_json_data.get("planname")
            description = parsed_json_data.get("description")
            
            if plan_name:
                workout_data["plan_name"] = plan_name
            if description:
                workout_data["description"] = description
            if strength_training:
                workout_data["strength_training"] = strength_training
                logger.info(f"✅ Found {len(strength_training)} strength training exercises")
            if cardio:
                workout_data["cardio"] = cardio
                logger.info(f"✅ Found {len(cardio)} cardio exercises")
            if exercises:
                workout_data["exercises"] = exercises
                logger.info(f"✅ Found {len(exercises)} exercises")
            logger.info(f"✅ Returning workout_data with keys: {list(workout_data.keys())}")
            return workout_data
    
    exercises = []
    
    pattern0 = re.compile(r"[-•]\s*([^(]+?)\s*\((\d+)\s*sets?,\s*(\d+)\s*reps?\)", re.I)
    for match in pattern0.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip()
        })
    
    pattern0b = re.compile(r"[-•]\s*([^(]+?)\s*\((\d+)\s*sets?,\s*(\d+)\s*reps?\s+[^)]+\)", re.I)
    for match in pattern0b.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip()
        })
    
    pattern0c = re.compile(r"[-•]\s*([^(]+?)\s*\((\d+)\s*sets?,\s*(\d+)\s*seconds?\)", re.I)
    for match in pattern0c.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip() + " seconds"
        })
    
    pattern1 = re.compile(r"[-•]\s*([^:]+?):\s*(\d+)x(\d+)(?:\s|$)", re.I)
    for match in pattern1.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip()
        })
    
    pattern2 = re.compile(r"[-•]\s*([^:]+?):\s*(\d+)\s*sets?\s*(?:of\s*)?(\d+)\s*reps?", re.I)
    for match in pattern2.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip()
        })
    
    pattern2b = re.compile(r"[-•]\s*(\d+)\s*sets?\s+of\s+([^(]+?)\s*\((\d+)(?:-\d+)?\s*reps?\)", re.I)
    for match in pattern2b.finditer(response_text):
        exercises.append({
            "name": match.group(2).strip(),
            "sets": match.group(1).strip(),
            "reps": match.group(3).strip()
        })
    
    pattern3 = re.compile(r"[-•]\s*([^-:]+?)\s*-\s*Sets?:\s*(\d+)\s*Reps?:\s*(\d+)", re.I)
    for match in pattern3.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip()
        })
    
    pattern4 = re.compile(r"(\d+)\.\s*([^:]+?):\s*(\d+)x(\d+)(?:\s|$)", re.I)
    for match in pattern4.finditer(response_text):
        exercises.append({
            "name": match.group(2).strip(),
            "sets": match.group(3).strip(),
            "reps": match.group(4).strip()
        })
    
    seen = set()
    unique_exercises = []
    for ex in exercises:
        name_lower = ex["name"].lower()
        if name_lower not in seen:
            seen.add(name_lower)
            unique_exercises.append(ex)
    
    if parsed_json_data and isinstance(parsed_json_data, dict):
        workout_data = parsed_json_data.copy()
        if unique_exercises:
            if not workout_data.get("exercises") and not workout_data.get("strength_training") and not workout_data.get("cardio"):
                workout_data["exercises"] = unique_exercises
        return workout_data
    
    if unique_exercises:
        return {"exercises": unique_exercises}
    
    return {}


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
        workout_data = extract_workout_data(response_text)
        logger.info(f"🔍 extract_workout_data returned: {type(workout_data)}, keys: {list(workout_data.keys()) if isinstance(workout_data, dict) else 'not a dict'}")
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

