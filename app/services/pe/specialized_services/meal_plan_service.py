"""
Specialized Meal Plan Service
Handles all meal plan creation with focused prompt and optimized model.
"""

from typing import List, Dict, Any, Union
from sqlalchemy.orm import Session
from openai import OpenAI
import logging
import os
import json
import re

from app.services.pe.base_widget_service import BaseWidgetService
from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService
from app.services.pe.specialized_services.workout_service import extract_workout_data
from app.services.pe.specialized_services.lesson_plan_service import extract_lesson_plan_data

logger = logging.getLogger(__name__)


def extract_meal_plan_data(response_text: str) -> Dict[str, Any]:
    """
    Extracts meal plan structured data from text.
    Handles JSON from markdown code blocks first, then falls back to regex patterns.
    Handles multiple formats: "**DAY 1:**", "**Day 1:**", "Day 1:", etc.
    
    Args:
        response_text: AI's response text containing meal plan
        
    Returns:
        Dictionary with structured meal plan data
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
            if isinstance(parsed_json_data, dict):
                if parsed_json_data.get("days") or parsed_json_data.get("meals"):
                    return parsed_json_data
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"⚠️ Failed to parse JSON from markdown code block: {e}")
    
    days = []
    day_patterns = [
        re.compile(r"\*\*DAY (\d+)\*\*[:-]?\s*(.*?)(?=\*\*DAY|\*\*Day|Day \d+|\Z)", re.S | re.I),
        re.compile(r"\*\*Day (\d+)\*\*[:-]?\s*(.*?)(?=\*\*DAY|\*\*Day|Day \d+|\Z)", re.S | re.I),
        re.compile(r"Day (\d+):\s*(.*?)(?=Day \d+|\Z)", re.S | re.I)
    ]
    
    for day_pattern in day_patterns:
        for day_match in day_pattern.finditer(response_text):
            day_num = day_match.group(1)
            day_content = day_match.group(2)
            meals = {}
            
            meal_patterns = {
                "breakfast": [
                    r"\*\*Breakfast:\*\*\s*(.*?)(?=\*\*(?:Lunch|Dinner|Snack)|$)",
                    r"Breakfast:\s*(.*?)(?=\n(?:Lunch|Dinner|Snack):|$)",
                    r"Breakfast:\s*\n(.*?)(?=\n(?:Lunch|Dinner|Snack):|$)",
                    r"Breakfast:\s*([^\n]+?)(?=\s*(?:Snack|Lunch|Dinner):|$)",
                    r"-\s*Breakfast:\s*([^\n]+?)(?=\s*-\s*(?:Snack|Lunch|Dinner):|\n|$)"
                ],
                "lunch": [
                    r"\*\*Lunch:\*\*\s*(.*?)(?=\*\*(?:Dinner|Snack|Breakfast)|$)",
                    r"Lunch:\s*(.*?)(?=\n(?:Dinner|Snack|Breakfast):|$)",
                    r"Lunch:\s*\n(.*?)(?=\n(?:Dinner|Snack|Breakfast):|$)",
                    r"Lunch:\s*([^\n]+?)(?=\s*(?:Snack|Dinner|Breakfast):|$)",
                    r"-\s*Lunch:\s*([^\n]+?)(?=\s*-\s*(?:Snack|Dinner|Breakfast):|\n|$)"
                ],
                "dinner": [
                    r"\*\*Dinner:\*\*\s*(.*?)(?=\*\*(?:Snack|Breakfast|Lunch)|$)",
                    r"Dinner:\s*(.*?)(?=\n(?:Snack|Breakfast|Lunch):|$)",
                    r"Dinner:\s*\n(.*?)(?=\n(?:Snack|Breakfast|Lunch):|$)",
                    r"Dinner:\s*([^\n]+?)(?=\s*(?:Snack|Breakfast|Lunch):|$)",
                    r"-\s*Dinner:\s*([^\n]+?)(?=\s*-\s*(?:Snack|Breakfast|Lunch):|\n|$)"
                ],
                "snack": [
                    r"\*\*Snack:\*\*\s*(.*?)(?=\*\*(?:Breakfast|Lunch|Dinner)|$)",
                    r"Snack:\s*(.*?)(?=\n(?:Breakfast|Lunch|Dinner):|$)",
                    r"Snack:\s*\n(.*?)(?=\n(?:Breakfast|Lunch|Dinner):|$)",
                    r"Snack:\s*([^\n]+?)(?=\s*(?:Breakfast|Lunch|Dinner):|$)",
                    r"-\s*Snack:\s*([^\n]+?)(?=\s*-\s*(?:Breakfast|Lunch|Dinner):|\n|$)"
                ]
            }
            
            for meal_type, patterns in meal_patterns.items():
                for pattern in patterns:
                    meal_match = re.search(pattern, day_content, re.S | re.I)
                    if meal_match:
                        meal_text = meal_match.group(1).strip()
                        lines = meal_text.split('\n')
                        cleaned_lines = []
                        for line in lines:
                            line = re.sub(r'^[-•]\s*', '', line.strip())
                            if line:
                                cleaned_lines.append(line)
                        meal_text = ' '.join(cleaned_lines)
                        meal_text = re.sub(r'\s+', ' ', meal_text).strip()
                        if meal_text and len(meal_text) > 3:
                            meals[meal_type] = meal_text
                            break
            
            daily_totals = {}
            macros = {}
            micronutrients = {}
            
            macro_patterns = {
                "protein": [r"Protein[:\s]+(\d+(?:\.\d+)?)\s*g", r"Protein[:\s]+(\d+(?:\.\d+)?)\s*grams"],
                "carbs": [r"Carbs[:\s]+(\d+(?:\.\d+)?)\s*g", r"Carbohydrates[:\s]+(\d+(?:\.\d+)?)\s*g", r"Carbs[:\s]+(\d+(?:\.\d+)?)\s*grams"],
                "fat": [r"Fat[:\s]+(\d+(?:\.\d+)?)\s*g", r"Fat[:\s]+(\d+(?:\.\d+)?)\s*grams"],
                "fiber": [r"Fiber[:\s]+(\d+(?:\.\d+)?)\s*g", r"Fiber[:\s]+(\d+(?:\.\d+)?)\s*grams"],
                "sugar": [r"Sugar[:\s]+(\d+(?:\.\d+)?)\s*g", r"Sugar[:\s]+(\d+(?:\.\d+)?)\s*grams"]
            }
            
            for macro_name, patterns in macro_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, day_content, re.I)
                    if match:
                        macros[macro_name] = match.group(1)
                        break
            
            vitamin_patterns = {
                "vitamin_a": [r"Vitamin\s*A[:\s]+(\d+(?:\.\d+)?)\s*(?:IU|mcg|μg)"],
                "vitamin_b1": [r"Vitamin\s*B1[:\s]+(\d+(?:\.\d+)?)\s*mg", r"Thiamine[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "vitamin_b2": [r"Vitamin\s*B2[:\s]+(\d+(?:\.\d+)?)\s*mg", r"Riboflavin[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "vitamin_b3": [r"Vitamin\s*B3[:\s]+(\d+(?:\.\d+)?)\s*mg", r"Niacin[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "vitamin_b6": [r"Vitamin\s*B6[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "vitamin_b12": [r"Vitamin\s*B12[:\s]+(\d+(?:\.\d+)?)\s*(?:mcg|μg)"],
                "vitamin_c": [r"Vitamin\s*C[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "vitamin_d": [r"Vitamin\s*D[:\s]+(\d+(?:\.\d+)?)\s*(?:IU|mcg|μg)"],
                "vitamin_e": [r"Vitamin\s*E[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "vitamin_k": [r"Vitamin\s*K[:\s]+(\d+(?:\.\d+)?)\s*(?:mcg|μg)"],
                "folate": [r"Folate[:\s]+(\d+(?:\.\d+)?)\s*(?:mcg|μg)"]
            }
            
            vitamins = {}
            for vitamin_name, patterns in vitamin_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, day_content, re.I)
                    if match:
                        vitamins[vitamin_name] = match.group(1)
                        break
            
            mineral_patterns = {
                "calcium": [r"Calcium[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "iron": [r"Iron[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "magnesium": [r"Magnesium[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "phosphorus": [r"Phosphorus[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "potassium": [r"Potassium[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "sodium": [r"Sodium[:\s]+(\d+(?:\.\d+)?)\s*mg"],
                "zinc": [r"Zinc[:\s]+(\d+(?:\.\d+)?)\s*mg"]
            }
            
            minerals = {}
            for mineral_name, patterns in mineral_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, day_content, re.I)
                    if match:
                        minerals[mineral_name] = match.group(1)
                        break
            
            other_patterns = {
                "omega_3": [r"Omega-3[:\s]+(\d+(?:\.\d+)?)\s*g", r"Omega\s*3[:\s]+(\d+(?:\.\d+)?)\s*g"],
                "omega_6": [r"Omega-6[:\s]+(\d+(?:\.\d+)?)\s*g", r"Omega\s*6[:\s]+(\d+(?:\.\d+)?)\s*g"],
                "choline": [r"Choline[:\s]+(\d+(?:\.\d+)?)\s*mg"]
            }
            
            other = {}
            for other_name, patterns in other_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, day_content, re.I)
                    if match:
                        other[other_name] = match.group(1)
                        break
            
            if macros:
                daily_totals["macros"] = macros
            if vitamins or minerals or other:
                micronutrients = {}
                if vitamins:
                    micronutrients["vitamins"] = vitamins
                if minerals:
                    micronutrients["minerals"] = minerals
                if other:
                    micronutrients["other"] = other
                if micronutrients:
                    daily_totals["micronutrients"] = micronutrients
            
            day_data = {"day": f"Day {day_num}", "meals": meals}
            if daily_totals:
                day_data["daily_totals"] = daily_totals
            
            if meals:
                days.append(day_data)
        
        if days:
            break
    
    if parsed_json_data and isinstance(parsed_json_data, dict):
        meal_data = parsed_json_data.copy()
        if days:
            if not meal_data.get("days"):
                meal_data["days"] = days
        return meal_data
    
    if days:
        return {"days": days}
    
    return {}


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
        meal_data = extract_meal_plan_data(response_text)
        if meal_data.get("days"):
            widgets.append({
                "type": "meal_plan",
                "data": meal_data
            })
        
        # Check for workout plan in same response
        workout_data = extract_workout_data(response_text)
        if workout_data.get("exercises"):
            widgets.append({
                "type": "workout",
                "data": workout_data
            })
        
        # Check for lesson plan in same response (pass original_message for better title extraction)
        lesson_data = extract_lesson_plan_data(response_text, original_message)
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

