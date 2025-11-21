"""
AI Assistant Integration Service
Handles AI assistant integration for beta teachers
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
import uuid
import json
import os
import openai
import re
import asyncio
import logging
from openai import OpenAI

from app.models.ai_assistant import (
    AIAssistantConfig,
    AIAssistantConversation,
    AIAssistantMessage,
    AIAssistantUsage,
    AIAssistantTemplate,
    AIAssistantFeedback,
    AIAssistantAnalytics
)
from app.schemas.ai_assistant import (
    AIAssistantConfigCreate,
    AIAssistantConfigUpdate,
    AIAssistantConfigResponse,
    AIAssistantConversationCreate,
    AIAssistantConversationResponse,
    AIAssistantMessageCreate,
    AIAssistantMessageResponse,
    AIAssistantUsageResponse,
    AIAssistantTemplateResponse,
    AIAssistantFeedbackCreate,
    AIAssistantFeedbackResponse,
    AIAssistantAnalyticsResponse,
    AIAssistantChatRequest,
    AIAssistantChatResponse
)


logger = logging.getLogger(__name__)

class AIAssistantService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    # ==================== CONFIGURATION MANAGEMENT ====================
    
    def create_assistant_config(
        self, 
        teacher_id: str, 
        config_data: AIAssistantConfigCreate
    ) -> AIAssistantConfigResponse:
        """Create a new AI assistant configuration"""
        try:
            config = AIAssistantConfig(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                config_name=config_data.config_name,
                config_description=config_data.config_description,
                assistant_type=config_data.assistant_type,
                is_active=config_data.is_active,
                config_data=config_data.config_data
            )
            
            self.db.add(config)
            self.db.commit()
            
            return self._config_to_response(config)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create AI assistant config: {str(e)}")

    def get_teacher_assistant_configs(
        self, 
        teacher_id: str, 
        assistant_type: Optional[str] = None
    ) -> List[AIAssistantConfigResponse]:
        """Get AI assistant configurations for a teacher"""
        query = self.db.query(AIAssistantConfig).filter(
            AIAssistantConfig.teacher_id == teacher_id
        )
        
        if assistant_type:
            query = query.filter(AIAssistantConfig.assistant_type == assistant_type)
        
        configs = query.filter(AIAssistantConfig.is_active == True).order_by(asc(AIAssistantConfig.config_name)).all()
        
        return [self._config_to_response(config) for config in configs]

    def update_assistant_config(
        self, 
        config_id: str, 
        teacher_id: str, 
        update_data: AIAssistantConfigUpdate
    ) -> Optional[AIAssistantConfigResponse]:
        """Update an AI assistant configuration"""
        config = self.db.query(AIAssistantConfig).filter(
            and_(
                AIAssistantConfig.id == config_id,
                AIAssistantConfig.teacher_id == teacher_id
            )
        ).first()
        
        if not config:
            return None
        
        # Update config fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(config, field, value)
        
        config.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._config_to_response(config)

    def delete_assistant_config(self, config_id: str, teacher_id: str) -> bool:
        """Delete an AI assistant configuration"""
        config = self.db.query(AIAssistantConfig).filter(
            and_(
                AIAssistantConfig.id == config_id,
                AIAssistantConfig.teacher_id == teacher_id
            )
        ).first()
        
        if not config:
            return False
        
        self.db.delete(config)
        self.db.commit()
        
        return True

    # ==================== CONVERSATION MANAGEMENT ====================
    
    def create_conversation(
        self, 
        teacher_id: str, 
        conversation_data: AIAssistantConversationCreate
    ) -> AIAssistantConversationResponse:
        """Create a new AI assistant conversation"""
        conversation = AIAssistantConversation(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            config_id=conversation_data.config_id,
            conversation_title=conversation_data.conversation_title,
            conversation_type=conversation_data.conversation_type,
            metadata=conversation_data.metadata
        )
        
        self.db.add(conversation)
        self.db.commit()
        
        return self._conversation_to_response(conversation)

    def get_teacher_conversations(
        self, 
        teacher_id: str, 
        conversation_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AIAssistantConversationResponse]:
        """Get conversations for a teacher"""
        query = self.db.query(AIAssistantConversation).filter(
            AIAssistantConversation.teacher_id == teacher_id
        )
        
        if conversation_type:
            query = query.filter(AIAssistantConversation.conversation_type == conversation_type)
        
        conversations = query.filter(AIAssistantConversation.is_active == True).order_by(desc(AIAssistantConversation.updated_at)).offset(offset).limit(limit).all()
        
        return [self._conversation_to_response(conversation) for conversation in conversations]

    def get_conversation_messages(
        self, 
        conversation_id: str, 
        teacher_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[AIAssistantMessageResponse]:
        """Get messages for a conversation"""
        # Verify conversation ownership
        conversation = self.db.query(AIAssistantConversation).filter(
            and_(
                AIAssistantConversation.id == conversation_id,
                AIAssistantConversation.teacher_id == teacher_id
            )
        ).first()
        
        if not conversation:
            return []
        
        messages = self.db.query(AIAssistantMessage).filter(
            AIAssistantMessage.conversation_id == conversation_id
        ).order_by(asc(AIAssistantMessage.created_at)).offset(offset).limit(limit).all()
        
        return [self._message_to_response(message) for message in messages]

    # ==================== HELPER FUNCTIONS FOR WIDGET DETECTION ====================
    
    def _extract_workout_data(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract structured workout data from AI response text.
        Returns a dict with workout plan information if found.
        Handles multiple formats: numbered lists, bullet points, bold text, plain text.
        """
        if not response_text:
            return None
        
        workout_data = {
            "exercises": [],
            "strength_training": [],  # Separate strength training exercises
            "cardio": [],  # Separate cardio exercises
            "plan_name": "Workout Plan",
            "description": ""
        }
        
        # Try to extract exercises from numbered lists or bullet points
        lines = response_text.split('\n')
        current_exercise = None
        current_section = None  # "strength", "cardio", or None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # CRITICAL: Skip placeholder text and general advice that's not workout content
            placeholder_patterns = [
                "the same structure can be followed", "repeat similar meal structures",
                "repeat for following days", "you can follow a similar pattern",
                "different food options like", "similar options", "follow a similar structure",
                "remember that portion control", "regular exercise and drinking",
                "it's always a good idea to consult", "consult with a healthcare provider",
                "it's always important to consult", "always a good idea to consult"
            ]
            if any(pattern in line_lower for pattern in placeholder_patterns):
                continue
            
            # Detect section headers (Strength Training, Cardio, etc.)
            # Format 1: **Strength Training:** or **Strength Training**
            strength_match = re.search(r'\*\*Strength\s+Training\s*:?\s*\*\*', line, re.IGNORECASE)
            # Format 2: Strength Training: (without bold)
            if not strength_match:
                strength_match = re.search(r'^Strength\s+Training\s*:?\s*$', line, re.IGNORECASE)
            # Format 3: *Strength Training:* (single asterisk)
            if not strength_match:
                strength_match = re.search(r'^\*Strength\s+Training\s*:?\s*\*', line, re.IGNORECASE)
            
            if strength_match:
                current_section = "strength"
                continue
            
            # Format 1: **Cardio:** or **Cardio** or **Cardiovascular Training:**
            cardio_match = re.search(r'\*\*Cardio(?:vascular)?\s+Training?\s*:?\s*\*\*', line, re.IGNORECASE)
            # Format 2: Cardio: or Cardiovascular Training: (without bold)
            if not cardio_match:
                cardio_match = re.search(r'^Cardio(?:vascular)?\s+Training?\s*:?\s*$', line, re.IGNORECASE)
            # Format 3: *Cardio:* (single asterisk)
            if not cardio_match:
                cardio_match = re.search(r'^\*Cardio(?:vascular)?\s+Training?\s*:?\s*\*', line, re.IGNORECASE)
            
            if cardio_match:
                current_section = "cardio"
                continue
            
            # CRITICAL: Skip meal plan day headers FIRST (before any other processing)
            # Pattern: "**Day 1:**", "Day 1:", "*Day 1:*", "Day 1", etc.
            if re.match(r'^\*?\*?Day\s+\d+\s*:?\s*\*?\*?$', line, re.IGNORECASE):
                continue
            # Skip meal plan section headers (e.g., "**Meal Plan**", "MEAL PLAN", etc.)
            if re.search(r'^\*?\*?(meal\s+plan|nutrition\s+plan|diet\s+plan)\s*:?\s*\*?\*?$', line_lower):
                continue
            # Skip meal section headers (Breakfast, Lunch, Dinner, Snack) - including "Mid-Morning Snack:", "Afternoon Snack:", "Evening Snack:"
            if re.match(r'^(breakfast|lunch|dinner|snack|snacks|mid-morning\s+snack|afternoon\s+snack|evening\s+snack|morning\s+snack)\s*(?:\(.*?\))?:?\s*$', line_lower):
                continue
            # Skip bold meal headers
            if re.search(r'\*\*(breakfast|lunch|dinner|snack|snacks|mid-morning\s+snack|afternoon\s+snack|evening\s+snack|morning\s+snack)\s*(?:\(.*?\))?\*\*', line_lower):
                continue
            # Skip lines that are just calorie totals (e.g., "Total Calories: 2100 Calories", "Total: 2100 calories")
            if re.match(r'^(total\s+calories?|total:)\s*:?\s*\d+', line_lower):
                continue
            # Skip food items (common patterns)
            if any(food in line_lower for food in ['oatmeal', 'banana', 'milk', 'turkey', 'sandwich', 'apple', 'yogurt', 'almond', 'chicken', 'broccoli', 'potato', 'egg', 'toast', 'orange', 'tuna', 'cracker', 'cheese', 'blueberry', 'salmon', 'salad', 'quinoa', 'cereal', 'bread', 'rice', 'pasta']):
                # But allow if it's clearly an exercise (e.g., "chicken wing exercise")
                if not ('exercise' in line_lower or 'workout' in line_lower or 'training' in line_lower or 'practice' in line_lower):
                    continue
            # Skip lines that are clearly food items with calories (e.g., "Oatmeal (1 cup cooked): 150 calories")
            if re.search(r'\(.*?(?:cup|oz|slice|piece|medium|large|small).*?\)\s*:?\s*\d+\s*(?:cal|kcal)', line_lower):
                continue
            
            # Pattern 1: Numbered list with bold (e.g., "1. **Push-ups**: 3 sets of 10")
            numbered_bold_match = re.match(r'^\d+\.\s*\*\*(.*?)\*\*', line)
            if numbered_bold_match:
                exercise_name = numbered_bold_match.group(1).strip()
                # Skip if it's a food item (check for food keywords and calorie patterns)
                exercise_name_lower = exercise_name.lower()
                # Check for food items with calories pattern: "Food name - XXX calories" or "Food name (amount) - XXX calories"
                if re.search(r'-\s*\d+\s*(?:cal|kcal|calories)', exercise_name_lower):
                    food_keywords = ['avocado', 'toast', 'egg', 'banana', 'milk', 'oatmeal', 'turkey', 'sandwich', 'apple', 'yogurt', 'almond', 'chicken', 'broccoli', 'potato', 'orange', 'tuna', 'cracker', 'cheese', 'blueberry', 'salmon', 'salad', 'quinoa', 'cereal', 'bread', 'rice', 'pasta', 'spinach', 'cottage', 'slice', 'cup', 'oz', 'medium', 'large', 'small']
                    if any(food in exercise_name_lower for food in food_keywords):
                        continue
                # CRITICAL: Skip if it's a meal plan day header (with or without formatting)
                if re.match(r'^Day\s+\d+\s*:?\s*$', exercise_name, re.IGNORECASE):
                    continue
                # Skip if exercise name contains meal plan content (e.g., "Day 1: Breakfast...")
                if re.search(r'^Day\s+\d+.*(?:breakfast|lunch|dinner|snack|calories?|meal)', exercise_name_lower):
                    continue
                if current_exercise:
                    # Add to appropriate section
                    if current_section == "strength":
                        workout_data["strength_training"].append(current_exercise)
                    elif current_section == "cardio":
                        workout_data["cardio"].append(current_exercise)
                    else:
                        workout_data["exercises"].append(current_exercise)
                current_exercise = {
                    "name": exercise_name,
                    "sets": None,
                    "reps": None,
                    "description": ""
                }
                # Remove the numbered prefix and bold markers
                line = re.sub(r'^\d+\.\s*\*\*.*?\*\*:?\s*', '', line)
            
            # Pattern 2: Numbered list without bold (e.g., "1. Push-ups: 3 sets of 10")
            elif re.match(r'^\d+\.\s+[A-Z]', line):
                numbered_match = re.match(r'^\d+\.\s+(.+?)(?::|$)', line)
                if numbered_match:
                    exercise_name = numbered_match.group(1).strip()
                    # Remove common prefixes
                    exercise_name = re.sub(r'^\*\*|\*\*$', '', exercise_name).strip()
                    # Skip meal/snack headers (including "Mid-Morning Snack:", "Afternoon Snack:", etc.)
                    exercise_name_lower = exercise_name.lower()
                    if re.search(r'^(mid-morning|afternoon|evening|morning)\s+snack', exercise_name_lower):
                        continue
                    # Skip if it's a food item (check for food keywords and calorie patterns)
                    # Check for food items with calories pattern: "Food name - XXX calories" or "Food name (amount) - XXX calories"
                    if re.search(r'-\s*\d+\s*(?:cal|kcal|calories)', exercise_name_lower):
                        food_keywords = ['avocado', 'toast', 'egg', 'banana', 'milk', 'oatmeal', 'turkey', 'sandwich', 'apple', 'yogurt', 'almond', 'chicken', 'broccoli', 'potato', 'orange', 'tuna', 'cracker', 'cheese', 'blueberry', 'salmon', 'salad', 'quinoa', 'cereal', 'bread', 'rice', 'pasta', 'spinach', 'cottage', 'slice', 'cup', 'oz', 'medium', 'large', 'small']
                        if any(food in exercise_name_lower for food in food_keywords):
                            continue
                    # CRITICAL: Skip if it's a meal plan day header (with or without formatting)
                    if re.match(r'^Day\s+\d+\s*:?\s*$', exercise_name, re.IGNORECASE):
                        continue
                    # Skip if exercise name contains meal plan content (e.g., "Day 1: Breakfast...")
                    exercise_name_lower = exercise_name.lower()
                    if re.search(r'^Day\s+\d+.*(?:breakfast|lunch|dinner|snack|calories?|meal)', exercise_name_lower):
                        continue
                    if current_exercise:
                        # Add to appropriate section
                        if current_section == "strength":
                            workout_data["strength_training"].append(current_exercise)
                        elif current_section == "cardio":
                            workout_data["cardio"].append(current_exercise)
                        else:
                            workout_data["exercises"].append(current_exercise)
                    current_exercise = {
                        "name": exercise_name,
                        "sets": None,
                        "reps": None,
                        "description": ""
                    }
                    line = re.sub(r'^\d+\.\s+.*?:?\s*', '', line)
            
            # Pattern 2.5: Time-based sections (e.g., "*Morning:*", "*Afternoon/Evening:*", "Morning:", "Afternoon:")
            time_section_match = re.search(r'^\*(Morning|Afternoon|Evening|Afternoon/Evening|AM|PM)\s*:?\s*\*', line, re.IGNORECASE)
            if not time_section_match:
                time_section_match = re.search(r'^(Morning|Afternoon|Evening|Afternoon/Evening|AM|PM)\s*:?\s*$', line, re.IGNORECASE)
            if time_section_match:
                time_section = time_section_match.group(1).strip()
                if current_exercise:
                    # Add to appropriate section
                    if current_section == "strength":
                        workout_data["strength_training"].append(current_exercise)
                    elif current_section == "cardio":
                        workout_data["cardio"].append(current_exercise)
                    else:
                        workout_data["exercises"].append(current_exercise)
                current_exercise = {
                    "name": f"{time_section} Workout",
                    "sets": None,
                    "reps": None,
                    "description": ""
                }
                # Extract exercise type from time section if applicable
                if "morning" in time_section.lower():
                    current_exercise["exercise_type"] = "Cardio"
                    if not current_section:
                        current_section = "cardio"
                elif "afternoon" in time_section.lower() or "evening" in time_section.lower():
                    current_exercise["exercise_type"] = "Wrestling"
                continue
            
            # Pattern 3: Bold text (without numbers) (e.g., "**Push-ups**: 3 sets of 10")
            # BUT skip meal plan headers (Breakfast, Lunch, Dinner, Snack)
            elif '**' in line and not current_exercise:
                bold_text = re.findall(r'\*\*(.*?)\*\*', line)
                if bold_text:
                    exercise_name = bold_text[0].strip()
                    exercise_name_lower = exercise_name.lower()
                    # Skip meal plan headers (with or without calories/parentheses/colons)
                    # Also skip snack headers: "Mid-Morning Snack:", "Afternoon Snack:", "Evening Snack:"
                    if re.search(r'^(breakfast|lunch|dinner|snack|snacks|meal\s+plan|nutrition|mid-morning\s+snack|afternoon\s+snack|evening\s+snack|morning\s+snack)', exercise_name_lower) or re.search(r'^(breakfast|lunch|dinner|snack|snacks|mid-morning\s+snack|afternoon\s+snack|evening\s+snack|morning\s+snack)\s*\(', exercise_name_lower):
                        continue
                    # Skip food items with calories pattern: "Food name - XXX calories"
                    if re.search(r'-\s*\d+\s*(?:cal|kcal|calories)', exercise_name_lower):
                        food_keywords = ['avocado', 'toast', 'egg', 'banana', 'milk', 'oatmeal', 'turkey', 'sandwich', 'apple', 'yogurt', 'almond', 'chicken', 'broccoli', 'potato', 'orange', 'tuna', 'cracker', 'cheese', 'blueberry', 'salmon', 'salad', 'quinoa', 'cereal', 'bread', 'rice', 'pasta', 'spinach', 'cottage', 'slice', 'cup', 'oz', 'medium', 'large', 'small', 'fruit', 'vegetable']
                        if any(food in exercise_name_lower for food in food_keywords):
                            continue
                    # Skip food items (common food keywords)
                    if any(food in exercise_name_lower for food in ['oatmeal', 'banana', 'milk', 'turkey', 'sandwich', 'apple', 'yogurt', 'almond', 'chicken', 'broccoli', 'potato', 'egg', 'toast', 'orange', 'tuna', 'cracker', 'cheese', 'blueberry', 'salmon', 'salad', 'quinoa', 'cereal', 'bread', 'rice', 'pasta', 'fruit', 'vegetable', 'avocado', 'spinach', 'cottage']):
                        continue
                    # Skip if it contains calorie information (likely a meal, not exercise)
                    if re.search(r'\(.*?\d+\s*(?:cal|kcal|calories?)', exercise_name_lower):
                        continue
                    if current_exercise:
                        # Add to appropriate section
                        if current_section == "strength":
                            workout_data["strength_training"].append(current_exercise)
                        elif current_section == "cardio":
                            workout_data["cardio"].append(current_exercise)
                        else:
                            workout_data["exercises"].append(current_exercise)
                    current_exercise = {
                        "name": exercise_name,
                        "sets": None,
                        "reps": None,
                        "description": ""
                    }
                    line = re.sub(r'\*\*.*?\*\*:?\s*', '', line)
            
            # Pattern 4: Lines starting with exercise-like text (e.g., "Push-ups: 3 sets of 10")
            elif not current_exercise and re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Press|Push|Pull|Squat|Lift|Curl|Extension|Raise|Fly|Row|Press|Dip|Extension):', line):
                exercise_match = re.match(r'^(.+?):', line)
                if exercise_match:
                    exercise_name = exercise_match.group(1).strip()
                    if current_exercise:
                        # Add to appropriate section
                        if current_section == "strength":
                            workout_data["strength_training"].append(current_exercise)
                        elif current_section == "cardio":
                            workout_data["cardio"].append(current_exercise)
                        else:
                            workout_data["exercises"].append(current_exercise)
                    current_exercise = {
                        "name": exercise_name,
                        "sets": None,
                        "reps": None,
                        "description": ""
                    }
                    line = re.sub(r'^.+?:\s*', '', line)
            
            # Extract sets/reps from current line (multiple patterns)
            if current_exercise:
                # Pattern: "3 sets of 10 reps" or "3x10" or "3 sets x 10 reps"
                sets_reps_match = re.search(r'(\d+)\s*(?:sets?\s*(?:of\s*|x\s*)?|x\s*)(\d+)\s*(?:reps?|times?)?', line, re.IGNORECASE)
                if sets_reps_match:
                    current_exercise["sets"] = int(sets_reps_match.group(1))
                    current_exercise["reps"] = int(sets_reps_match.group(2))
                
                # Pattern: "10 reps x 3 sets"
                reps_sets_match = re.search(r'(\d+)\s*reps?\s*(?:x|×)\s*(\d+)\s*sets?', line, re.IGNORECASE)
                if reps_sets_match:
                    current_exercise["reps"] = int(reps_sets_match.group(1))
                    current_exercise["sets"] = int(reps_sets_match.group(2))
                
                # Extract calories burned (e.g., "burns 500 calories", "500 cal", "~500 calories per hour", "burn around 500 calories")
                calories_match = re.search(r'(?:burn|burns?|burning|burned|burn)\s+(?:around\s+|approximately\s+|about\s+|~)?(\d+(?:,\d+)?)\s*(?:calories?|cal|kcal)(?:\s+per\s+(?:day|hour|minute|session))?', line, re.IGNORECASE)
                if calories_match:
                    current_exercise["calories_burned"] = calories_match.group(1).strip()
                # Also check for "500 calories" without "burn" (if line mentions exercise)
                elif "calorie" in line.lower() and ("exercise" in line.lower() or "workout" in line.lower() or "practice" in line.lower()):
                    cal_only_match = re.search(r'(\d+(?:,\d+)?)\s*(?:calories?|cal|kcal)(?:\s+per\s+(?:day|hour|minute|session))?', line, re.IGNORECASE)
                    if cal_only_match:
                        current_exercise["calories_burned"] = cal_only_match.group(1).strip()
                
                # Extract duration (e.g., "60 minutes", "1 hour", "60 minutes of intense wrestling practice")
                duration_match = re.search(r'(\d+)\s*(?:minutes?|mins?|hours?|hrs?)(?:\s+of\s+.*?)?', line, re.IGNORECASE)
                if duration_match:
                    current_exercise["duration"] = duration_match.group(0).strip()
                
                # Extract exercise types mentioned (e.g., "wrestling practice", "strength training", "cardio workouts")
                line_lower_current = line.lower()
                if "wrestling" in line_lower_current:
                    current_exercise["exercise_type"] = "Wrestling"
                elif "strength" in line_lower_current and "training" in line_lower_current:
                    current_exercise["exercise_type"] = "Strength Training"
                elif "cardio" in line_lower_current:
                    current_exercise["exercise_type"] = "Cardio"
                
                # Add description if it's not an exercise name and contains useful info
                if not re.match(r'^\d+\.\s*\*\*', line) and not sets_reps_match and not reps_sets_match:
                    # CRITICAL: Skip meal plan content - check for food items with calories first
                    # Pattern: "Food name (amount) - XXX calories" or "Food name - XXX calories"
                    if re.search(r'^[A-Z][a-z]+(?:\s+[a-z]+)*\s*(?:\([^)]+\))?\s*-?\s*\d+\s*(?:cal|kcal|calories)', line, re.IGNORECASE):
                        # Check if it's a food item (not an exercise)
                        food_indicators = ['avocado', 'toast', 'egg', 'banana', 'milk', 'chicken', 'quinoa', 'broccoli', 'apple', 'yogurt', 'almond', 'salmon', 'potato', 'spinach', 'cottage', 'cheese', 'blueberry', 'slice', 'cup', 'oz', 'medium', 'large', 'small']
                        if any(food in line_lower for food in food_indicators):
                            continue
                    # Skip lines that are just dashes, bullets, or common workout section headers
                    skip_patterns = ['warm', 'cool', 'rest', 'notes', 'tips', 'instructions', '---', '===', 'day', 'gradual', 'calorie deficit', 'maintaining weight', 'meal plan', 'nutrition plan', 'diet plan', 'total:', 'daily total', 'total calories', 'calories:']
                    # Skip lines that are just calorie totals (e.g., "Total Calories: 2100 Calories")
                    if re.match(r'^(total\s+calories?|total:)\s*:?\s*\d+', line_lower):
                        continue
                    # Skip food items (common food keywords)
                    food_keywords = ['oatmeal', 'banana', 'milk', 'turkey', 'sandwich', 'apple', 'yogurt', 'almond', 'chicken', 'broccoli', 'potato', 'egg', 'toast', 'orange', 'tuna', 'cracker', 'cheese', 'blueberry', 'salmon', 'salad', 'quinoa', 'cereal', 'bread', 'rice', 'pasta', 'fruit', 'vegetable', 'calories per food', 'calories per item', 'avocado', 'spinach', 'cottage']
                    # Skip time section headers (already processed)
                    if re.search(r'^\*(Morning|Afternoon|Evening|Afternoon/Evening|AM|PM)\s*:?\s*\*', line, re.IGNORECASE) or re.search(r'^(Morning|Afternoon|Evening|Afternoon/Evening|AM|PM)\s*:?\s*$', line, re.IGNORECASE):
                        continue
                    # Allow lines starting with "-" or "•" if they're exercise descriptions (not food items)
                    is_exercise_line = line.startswith('-') or line.startswith('•')
                    if is_exercise_line:
                        # Check if it's an exercise (contains exercise keywords) or food (contains food keywords)
                        line_content = re.sub(r'^[-•]\s+', '', line).strip()
                        if any(exercise_keyword in line_content.lower() for exercise_keyword in ['minutes', 'cardio', 'running', 'cycling', 'wrestling', 'exercise', 'workout', 'training', 'burn', 'intensity']):
                            # It's an exercise description - process it
                            clean_line = re.sub(r'\*\*?', '', line_content).strip()
                            if clean_line:
                                if current_exercise["description"]:
                                    current_exercise["description"] += " " + clean_line
                                else:
                                    current_exercise["description"] = clean_line
                            continue
                        # If it's a food item, skip it (should be in meal plan, not workout)
                        elif any(food in line_content.lower() for food in food_keywords):
                            continue
                    
                    if line and not is_exercise_line and not any(pattern in line.lower() for pattern in skip_patterns) and not any(food in line.lower() for food in food_keywords):
                        # Don't add if it's a meal section header
                        if not re.match(r'^(breakfast|lunch|dinner|snack)', line.lower()):
                            # Don't add if it's a day section header
                            if not re.match(r'^day\s+\d+', line.lower()):
                                # Don't add if it's a food item with calories (e.g., "Oatmeal (1 cup cooked): 150 calories")
                                if not re.search(r'\(.*?\)\s*:?\s*\d+\s*(?:cal|kcal)', line, re.IGNORECASE):
                                    # Remove bold markers if present
                                    clean_line = re.sub(r'\*\*?', '', line).strip()
                                    if clean_line:
                                        if current_exercise["description"]:
                                            current_exercise["description"] += " " + clean_line
                                        else:
                                            current_exercise["description"] = clean_line
        
        # Add last exercise if exists
        if current_exercise:
            # Add to appropriate section
            if current_section == "strength":
                workout_data["strength_training"].append(current_exercise)
            elif current_section == "cardio":
                workout_data["cardio"].append(current_exercise)
            else:
                # Add to general exercises list (backward compatibility)
                workout_data["exercises"].append(current_exercise)
        
        # Also add exercises from sections to main exercises list for backward compatibility
        if workout_data["strength_training"]:
            workout_data["exercises"].extend(workout_data["strength_training"])
        if workout_data["cardio"]:
            workout_data["exercises"].extend(workout_data["cardio"])
        
        # FINAL FILTER: Remove food items from exercises list
        if workout_data["exercises"]:
            filtered_exercises = []
            for ex in workout_data["exercises"]:
                if not ex.get("name"):
                    continue
                ex_name_lower = ex["name"].lower()
                # CRITICAL: Skip meal plan day headers (e.g., "Day 1:", "Day 1", "**Day 1:**")
                if re.match(r'^day\s+\d+\s*:?\s*$', ex_name_lower):
                    continue
                # Skip if exercise name contains meal plan content (e.g., "Day 1: Breakfast...")
                if re.search(r'^day\s+\d+.*(?:breakfast|lunch|dinner|snack|calories?|meal)', ex_name_lower):
                    continue
                # Skip meal plan headers (including snack headers and calorie totals)
                if any(meal in ex_name_lower for meal in ['breakfast', 'lunch', 'dinner', 'snack', 'meal', 'calories per food', 'calories per item', 'total:', 'daily total', 'mid-morning snack', 'afternoon snack', 'evening snack', 'morning snack', 'total calories', 'calories:', 'calories']):
                    # But allow if it's clearly an exercise (e.g., "Burns 500 calories")
                    if not ('burn' in ex_name_lower or 'exercise' in ex_name_lower or 'workout' in ex_name_lower):
                        continue
                # Also check description for meal plan content
                if ex.get("description"):
                    desc_lower = ex["description"].lower()
                    # If description contains meal plan content (breakfast, lunch, dinner, calories per food), skip
                    if re.search(r'(breakfast|lunch|dinner|snack).*calories?|calories?.*(breakfast|lunch|dinner|snack)', desc_lower):
                        # But allow if it's clearly an exercise description
                        if not ('exercise' in desc_lower or 'workout' in desc_lower or 'training' in desc_lower or 'burn' in desc_lower):
                            continue
                # Skip food items with calorie patterns: "Food name - XXX calories"
                if re.search(r'-\s*\d+\s*(?:cal|kcal|calories)', ex_name_lower):
                    food_indicators = ['avocado', 'toast', 'egg', 'banana', 'milk', 'chicken', 'quinoa', 'broccoli', 'apple', 'yogurt', 'almond', 'salmon', 'potato', 'spinach', 'cottage', 'cheese', 'blueberry', 'slice', 'cup', 'oz', 'medium', 'large', 'small', 'steamed', 'baked', 'grilled', 'scrambled', 'whole grain', 'skim']
                    if any(food in ex_name_lower for food in food_indicators):
                        continue
                filtered_exercises.append(ex)
            workout_data["exercises"] = filtered_exercises
        
        # If we found exercises, return the data
        if workout_data["exercises"] or workout_data["strength_training"] or workout_data["cardio"]:
            return workout_data
        
        return None

    def _extract_meal_plan_data(self, response_text: str, original_message: str = "") -> Optional[Dict[str, Any]]:
        """
        Extract structured meal plan data from AI response text.
        Returns a dict with meal plan information including meals, calories, and macros.
        """
        if not response_text:
            return None
        
        meal_plan_data = {
            "title": "",
            "description": "",
            "daily_calories": "",
            "macros": {
                "protein": "",
                "carbs": "",
                "fat": ""
            },
            "meals": [],  # For backward compatibility - single day format
            "days": [],  # Multi-day format: [{"day": "Day 1", "meals": [...]}, ...]
            "exercise_calories": ""  # Calories to burn through exercise
        }
        
        lines = response_text.split('\n')
        current_meal = None
        current_day = None
        current_day_data = None  # For multi-day plans: {"day": "Day 1", "meals": []}
        in_meal_section = False
        has_multi_day_structure = False  # Track if we detect day-by-day structure
        
        # Extract title from original message
        if original_message:
            # Try various patterns for meal plan requests
            # Pattern 1: "create meal plan for [person/description]"
            title_match = re.search(r'meal\s+plan\s+(?:for|on|about)\s+(.+?)(?:\.|$|please|in|that|who|that)', original_message, flags=re.IGNORECASE)
            # Pattern 2: "create [type] plan for [person/description]"
            if not title_match:
                title_match = re.search(r'(?:make|create|generate|give|i\s+need|i\s+want)\s+(?:me\s+)?(?:a\s+)?(?:meal\s+plan|nutrition\s+plan|diet\s+plan|weight\s+loss\s+plan|weight\s+gain\s+plan|bulking\s+plan|cutting\s+plan)\s+(?:for|on|about)?\s*(.+?)(?:\.|$|please|in|that|who|that)', original_message, flags=re.IGNORECASE)
            # Pattern 3: Extract person/description from common phrases
            if not title_match:
                # "for a 180-pound male 16-year-old wrestler"
                title_match = re.search(r'(?:for|about)\s+(?:a\s+)?(.+?)(?:\s+who\s+|\s+that\s+|\s+wants\s+|\.|$|please)', original_message, flags=re.IGNORECASE)
            if title_match:
                topic = title_match.group(1).strip()
                # Determine plan type from message
                plan_type = "Meal Plan"
                if "weight loss" in original_message.lower():
                    plan_type = "Weight Loss Plan"
                elif "weight gain" in original_message.lower():
                    plan_type = "Weight Gain Plan"
                elif "bulking" in original_message.lower():
                    plan_type = "Bulking Plan"
                elif "cutting" in original_message.lower():
                    plan_type = "Cutting Plan"
                elif "nutrition" in original_message.lower():
                    plan_type = "Nutrition Plan"
                elif "diet" in original_message.lower():
                    plan_type = "Diet Plan"
                
                # Clean up topic (remove common prefixes)
                topic = re.sub(r'^(a|an|the)\s+', '', topic, flags=re.IGNORECASE)
                # If topic is descriptive, use it; otherwise use plan type
                if len(topic) > 20:  # Descriptive topic
                    meal_plan_data["title"] = topic.title() + f" - {plan_type}"
                else:
                    meal_plan_data["title"] = topic.title() + f" {plan_type}"
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Detect day sections FIRST (before meal sections) - multiple formats
            day_detected = False
            current_day = None
            
            # Format 1: **Day 1:** or **Day 1: Monday** or **Day 1-7:**
            day_match = re.search(r'\*\*Day\s+(\d+(?:-\d+)?)\s*:?\s*(.+?)?\*\*', line, re.IGNORECASE)
            # Format 2: Day 1: or Day 1: Monday (without bold)
            if not day_match:
                day_match = re.search(r'^Day\s+(\d+(?:-\d+)?)\s*:?\s*(.+?)?\s*$', line, re.IGNORECASE)
            # Format 3: *Day 1:* (single asterisk)
            if not day_match:
                day_match = re.search(r'^\*Day\s+(\d+(?:-\d+)?)\s*:?\s*(.+?)?\s*\*', line, re.IGNORECASE)
            # Format 4: Day names (Monday, Tuesday, etc.) - with or without bold
            if not day_match:
                day_name_match = re.search(r'^\*\*(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s*:?\s*\*\*', line, re.IGNORECASE)
                if not day_name_match:
                    day_name_match = re.search(r'^\*(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s*:?\s*\*', line, re.IGNORECASE)
                if not day_name_match:
                    day_name_match = re.search(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s*:?\s*$', line, re.IGNORECASE)
            
            if day_match:
                day_detected = True
                day_number = day_match.group(1).strip() if day_match.group(1) else ""
                day_label = day_match.group(2).strip() if len(day_match.groups()) > 1 and day_match.group(2) else ""
                current_day = f"Day {day_number}" if day_number else "Day"
                if day_label:
                    current_day += f": {day_label}"
            elif day_name_match:
                day_detected = True
                current_day = day_name_match.group(1).strip()
            
            if day_detected:
                has_multi_day_structure = True
                
                # Save previous day if exists
                if current_day_data and current_day_data.get("meals"):
                    meal_plan_data["days"].append(current_day_data)
                
                # Create new day entry
                current_day_data = {
                    "day": current_day,
                    "meals": []
                }
                current_meal = None  # Reset current meal when starting new day
                continue
            
            # Skip placeholder text that indicates incomplete meal plans
            if any(placeholder in line_lower for placeholder in [
                "the same structure can be followed", "repeat similar meal structures",
                "repeat for following days", "you can follow a similar pattern",
                "different food options like", "similar options", "follow a similar structure"
            ]):
                # This is placeholder text - stop parsing meal plan data from this point
                # But continue to look for workout plans
                in_meal_section = False
                current_meal = None
                continue
            
            # Detect meal sections (Breakfast, Lunch, Dinner, Snack, Dessert as Snack) - multiple formats
            # Format 1: **Breakfast:** or **Breakfast:** (Approx. 600 calories) or **Breakfast (400 Cal):**
            meal_match = re.search(r'\*\*(Breakfast|Lunch|Dinner|Snack|Snacks|Dessert|Evening\s+Snack|After-Dinner\s+Snack|Mid-Morning\s+Snack|Morning\s+Snack|Afternoon\s+Snack)\s*(?:\([^)]*\))?\s*:?\s*\*\*', line, re.IGNORECASE)
            # Format 1b: **Breakfast:** followed by text (e.g., "**Breakfast:** (Approx. 600 calories)")
            if not meal_match:
                meal_match = re.search(r'\*\*(Breakfast|Lunch|Dinner|Snack|Snacks|Dessert|Evening\s+Snack|After-Dinner\s+Snack|Mid-Morning\s+Snack|Morning\s+Snack|Afternoon\s+Snack)\s*:?\s*\*\*\s*\(', line, re.IGNORECASE)
            # Format 2: Breakfast: or Breakfast (400 Cal) or Breakfast (400 Cal): (without bold)
            if not meal_match:
                meal_match = re.search(r'^(Breakfast|Lunch|Dinner|Snack|Snacks|Dessert|Evening\s+Snack|After-Dinner\s+Snack|Mid-Morning\s+Snack|Morning\s+Snack|Afternoon\s+Snack)\s*(?:\([^)]*\))?\s*:?\s*$', line, re.IGNORECASE)
            # Format 3: *Breakfast* or *Breakfast (400 Cal):* (single asterisk)
            if not meal_match:
                meal_match = re.search(r'^\*(Breakfast|Lunch|Dinner|Snack|Snacks|Dessert|Evening\s+Snack|After-Dinner\s+Snack|Mid-Morning\s+Snack|Morning\s+Snack|Afternoon\s+Snack)\s*(?:\([^)]*\))?\s*:?\s*\*', line, re.IGNORECASE)
            # Format 4: - Breakfast: ... or • Breakfast: ... (bullet point with meal name)
            if not meal_match:
                meal_match = re.search(r'^[-•]\s+(Breakfast|Lunch|Dinner|Snack|Snacks|Dessert|Evening\s+Snack|After-Dinner\s+Snack|Mid-Morning\s+Snack|Morning\s+Snack|Afternoon\s+Snack)\s*:\s*(.+)$', line, re.IGNORECASE)
            # Format 5: 1. Breakfast: ... or 2. Morning Snack: ... (numbered format)
            if not meal_match:
                meal_match = re.search(r'^\d+\.\s+(Breakfast|Lunch|Dinner|Snack|Snacks|Dessert|Evening\s+Snack|After-Dinner\s+Snack|Mid-Morning\s+Snack|Morning\s+Snack|Afternoon\s+Snack)\s*:\s*(.+)$', line, re.IGNORECASE)
            
            if meal_match:
                meal_type = meal_match.group(1).strip()
                # Normalize snack names
                if meal_type.lower() == "dessert":
                    meal_type = "Evening Snack"
                elif meal_type.lower() == "morning snack":
                    meal_type = "Mid-Morning Snack"
                elif meal_type.lower() in ["snack", "snacks"] and current_meal and current_meal.get("meal") == "Lunch":
                    # If we just had lunch, this is likely afternoon snack
                    meal_type = "Afternoon Snack"
                elif meal_type.lower() in ["snack", "snacks"] and current_meal and current_meal.get("meal") == "Breakfast":
                    # If we just had breakfast, this is likely mid-morning snack
                    meal_type = "Mid-Morning Snack"
                elif meal_type.lower() in ["snack", "snacks"] and current_meal and current_meal.get("meal") == "Dinner":
                    # If we just had dinner, this is likely evening snack
                    meal_type = "Evening Snack"
                # Extract calories if present (e.g., "Breakfast (400-500 Cal)")
                cal_match = re.search(r'\(([^)]*cal[^)]*)\)', line, re.IGNORECASE)
                calories = cal_match.group(1).strip() if cal_match else ""
                
                # Check if Format 4 or Format 5 (bullet/numbered point with food on same line)
                food_items_on_line = None
                if len(meal_match.groups()) > 1 and meal_match.group(2):
                    # Format 4/5: meal and food items are on the same line
                    food_items_on_line = meal_match.group(2).strip()
                
                # Save previous meal
                if current_meal:
                    if has_multi_day_structure and current_day_data:
                        # Add to current day's meals
                        current_day_data["meals"].append(current_meal)
                    else:
                        # Single day format - add to meals array
                        meal_plan_data["meals"].append(current_meal)
                
                current_meal = {
                    "meal": meal_type,
                    "calories": calories,
                    "foods": []
                }
                
                # If food items are on the same line (Format 4), add them immediately
                if food_items_on_line:
                    # Split by comma or period to get individual food items
                    food_items = re.split(r'[,.]\s+(?=[A-Z])|\.\s*$', food_items_on_line)
                    for food_item in food_items:
                        food_item = food_item.strip()
                        if food_item and not any(exercise_keyword in food_item.lower() for exercise_keyword in ['minutes', 'cardio', 'running', 'cycling', 'wrestling', 'exercise', 'workout', 'burn']):
                            current_meal["foods"].append(food_item)
                
                in_meal_section = True
                continue
            
            # Extract daily calories
            if "calorie" in line_lower and ("per day" in line_lower or "daily" in line_lower or "day" in line_lower):
                cal_match = re.search(r'(\d+(?:,\d+)?(?:-\d+(?:,\d+)?)?)\s*calories?', line, re.IGNORECASE)
                if cal_match:
                    meal_plan_data["daily_calories"] = cal_match.group(1).strip()
            
            # Extract exercise calories to burn
            if "burn" in line_lower and "calorie" in line_lower:
                burn_match = re.search(r'burn\s+(?:around\s+)?(\d+(?:,\d+)?)\s*calories?', line, re.IGNORECASE)
                if burn_match:
                    meal_plan_data["exercise_calories"] = burn_match.group(1).strip()
            
            # Extract macros (protein, carbs, fat)
            if "protein" in line_lower:
                protein_match = re.search(r'protein[:\s]+(\d+(?:g|grams?)?)', line, re.IGNORECASE)
                if protein_match:
                    meal_plan_data["macros"]["protein"] = protein_match.group(1).strip()
            if "carb" in line_lower or "carbohydrate" in line_lower:
                carb_match = re.search(r'carb(?:ohydrate)?s?[:\s]+(\d+(?:g|grams?)?)', line, re.IGNORECASE)
                if carb_match:
                    meal_plan_data["macros"]["carbs"] = carb_match.group(1).strip()
            if "fat" in line_lower and "calorie" not in line_lower:
                fat_match = re.search(r'fat[:\s]+(\d+(?:g|grams?)?)', line, re.IGNORECASE)
                if fat_match:
                    meal_plan_data["macros"]["fat"] = fat_match.group(1).strip()
            
            # Extract food items with calories - multiple formats
            if current_meal:
                # Skip exercise-related content (should be in workout widget, not meal plan)
                if any(exercise_keyword in line_lower for exercise_keyword in ['minutes of', 'cardio', 'running', 'cycling', 'wrestling training', 'exercise', 'workout', 'burn around', 'should burn']):
                    continue
                
                # Format 1: "- Whole grain cereal (200 Cal)" or "• Whole grain cereal (200 Cal)"
                # Also handles: "- Scrambled eggs (2 large eggs: 140 calories)"
                if line.startswith('-') or line.startswith('•'):
                    # Remove bullet/dash
                    food_line = re.sub(r'^[-•]\s+', '', line).strip()
                    # Skip if it's clearly exercise content
                    if any(exercise_keyword in food_line.lower() for exercise_keyword in ['minutes of', 'cardio', 'running', 'cycling', 'wrestling', 'exercise', 'workout', 'burn']):
                        continue
                    # Try format: "Food name (description: XXX calories)" first
                    food_match = re.search(r'^(.+?)\s*\(([^:]+):\s*(\d+(?:\s*-\s*\d+)?)\s*(?:calories?|cal|kcal)\)', food_line, re.IGNORECASE)
                    if food_match:
                        food_name = food_match.group(1).strip()
                        food_description = food_match.group(2).strip()
                        food_calories = food_match.group(3).strip()
                        current_meal["foods"].append(f"{food_name} ({food_description}: {food_calories} Cal)")
                    else:
                        # Try format: "Food name (XXX Cal)" or "Food name (XXX calories)"
                        food_match = re.search(r'^(.+?)\s*\((\d+(?:\s*-\s*\d+)?)\s*(?:Cal|calories?|kcal)\)', food_line, re.IGNORECASE)
                        if food_match:
                            food_name = food_match.group(1).strip()
                            food_calories = food_match.group(2).strip()
                            current_meal["foods"].append(f"{food_name} ({food_calories} Cal)")
                        else:
                            # Just the food name, no calories specified (but skip if it's exercise)
                            if not any(exercise_keyword in food_line.lower() for exercise_keyword in ['minutes', 'cardio', 'running', 'cycling', 'wrestling', 'exercise', 'workout']):
                                current_meal["foods"].append(food_line)
                # Format 2: "Oatmeal (1 cup cooked): 150 calories" (with colon)
                elif ':' in line and ('calorie' in line_lower or re.search(r'\d+\s*(?:cal|kcal)', line_lower)):
                    food_match = re.search(r'^(.+?):\s*(\d+(?:\s*-\s*\d+)?)\s*(?:calories?|cal|kcal)', line, re.IGNORECASE)
                    if food_match:
                        food_name = food_match.group(1).strip()
                        food_calories = food_match.group(2).strip()
                        current_meal["foods"].append(f"{food_name} ({food_calories} Cal)")
                # Format 3: "Oatmeal (1 cup cooked) - 150 calories" (with dash)
                elif ' - ' in line and ('calorie' in line_lower or re.search(r'\d+\s*(?:cal|kcal)', line_lower)):
                    food_match = re.search(r'^(.+?)\s*-\s*(\d+(?:\s*-\s*\d+)?)\s*(?:calories?|cal|kcal)', line, re.IGNORECASE)
                    if food_match:
                        food_name = food_match.group(1).strip()
                        food_calories = food_match.group(2).strip()
                        current_meal["foods"].append(f"{food_name} ({food_calories} Cal)")
                # Format 4: Just food name with calories in parentheses anywhere in line
                elif re.search(r'\((\d+(?:\s*-\s*\d+)?)\s*(?:Cal|calories?|kcal)\)', line, re.IGNORECASE):
                    food_match = re.search(r'^(.+?)\s*\((\d+(?:\s*-\s*\d+)?)\s*(?:Cal|calories?|kcal)\)', line, re.IGNORECASE)
                    if food_match:
                        food_name = food_match.group(1).strip()
                        food_calories = food_match.group(2).strip()
                        # Skip if it's a meal section header
                        if not re.match(r'^(breakfast|lunch|dinner|snack)', food_name.lower()):
                            current_meal["foods"].append(f"{food_name} ({food_calories} Cal)")
            
            # Extract exercise information (for calorie burn)
            if "exercise" in line_lower and "burn" in line_lower:
                # This will be captured above, but also add to description
                if meal_plan_data["description"]:
                    meal_plan_data["description"] += line + "\n"
                else:
                    meal_plan_data["description"] = line + "\n"
        
        # Add last meal if exists
        if current_meal:
            if has_multi_day_structure and current_day_data:
                current_day_data["meals"].append(current_meal)
            else:
                meal_plan_data["meals"].append(current_meal)
        
        # Add last day if exists
        if has_multi_day_structure and current_day_data and current_day_data.get("meals"):
            meal_plan_data["days"].append(current_day_data)
        
        # Format meals for display
        if has_multi_day_structure and meal_plan_data["days"]:
            # Format multi-day structure
            formatted_days = []
            for day_data in meal_plan_data["days"]:
                formatted_day_meals = []
                for meal in day_data.get("meals", []):
                    if meal.get("foods"):
                        foods_text = ", ".join(meal["foods"])
                        formatted_day_meals.append({
                            "meal": meal["meal"],
                            "foods": foods_text,
                            "calories": meal.get("calories", "")
                        })
                formatted_days.append({
                    "day": day_data["day"],
                    "meals": formatted_day_meals
                })
            meal_plan_data["days"] = formatted_days
        
        # Single day format - format meals for backward compatibility
        formatted_meals = []
        for meal in meal_plan_data["meals"]:
            if meal.get("foods"):
                foods_text = ", ".join(meal["foods"])
                formatted_meals.append({
                    "meal": meal["meal"],
                    "foods": foods_text,
                    "calories": meal.get("calories", "")
                })
        
        meal_plan_data["meals"] = formatted_meals
        
        # Return meal plan data if we found any meals, days, or daily calories
        if meal_plan_data.get("meals") or meal_plan_data.get("days") or meal_plan_data.get("daily_calories"):
            return meal_plan_data
        
        return None

    def _extract_lesson_plan_data(self, response_text: str, original_message: str = "") -> Optional[Dict[str, Any]]:
        """
        Extract structured lesson plan data from AI response text.
        Returns a dict with lesson plan information if found.
        
        Args:
            response_text: The AI's response text
            original_message: The original user message (used for title extraction)
        """
        if not response_text:
            return None
        
        lesson_data = {
            "title": "",
            "description": "",  # Detailed description of what the lesson is
            "objectives": [],
            "grade_level": "",
            "subject": "",
            "duration": "",
            "materials": [],
            "activities": [],
            "assessment": "",
            "introduction": "",
            "content": "",
            "danielson_framework": "",
            "costas_questioning": "",
            "curriculum_standards": "",
            "exit_ticket": "",
            "worksheets": "",
            "assessments": "",
            "rubrics": ""
        }
        
        lines = response_text.split('\n')
        current_section = None
        skip_next_empty = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            line_lower = line.lower()
            
            # Skip empty lines (but allow one empty line between sections)
            if not line:
                if skip_next_empty:
                    current_section = None  # Reset section on double empty line
                skip_next_empty = True
                continue
            skip_next_empty = False
            
            # CRITICAL: Detect new numbered sections (e.g., "1. **Introduction**:", "2. **Warm-up** - 10-15 minutes...")
            # This must come BEFORE other section detection to reset current_section
            numbered_section_match = None
            if current_section and len(line) < 100 and re.match(r'^\d+\.\s+[a-z]', line):
                # This is likely a numbered sub-item within the current section, not a new section
                pass
            else:
                numbered_section_match = re.match(r'^(\d+)\.\s*\*\*([^*]+)\*\*\s*[-:]?\s*(.*)', line)
            if numbered_section_match:
                section_num = numbered_section_match.group(1)
                section_header = numbered_section_match.group(2).strip()
                section_content = numbered_section_match.group(3).strip()
                section_header_lower = section_header.lower()
                
                # Reset current_section when a new numbered section starts
                if any(keyword in section_header_lower for keyword in ['introduction', 'intro', 'overview']):
                    current_section = "introduction"
                    if section_content and len(section_content) > 5:
                        section_content = re.sub(r'^-\s*', '', section_content).strip()
                        lesson_data["introduction"] = section_content
                elif any(keyword in section_header_lower for keyword in ['objective', 'goal', 'learning outcome']):
                    current_section = "objectives"
                    if section_content and len(section_content) > 10:
                        section_content = re.sub(r'^-\s*', '', section_content).strip()
                        lesson_data["objectives"].append(section_content)
                elif any(keyword in section_header_lower for keyword in ['material', 'supply', 'resource', 'equipment']):
                    current_section = "materials"
                    if section_content:
                        for material in section_content.split(','):
                            material = material.strip()
                            material = re.sub(r'^-\s*', '', material).strip()
                            if material and len(material) > 2:
                                lesson_data["materials"].append(material)
                elif any(keyword in section_header_lower for keyword in ['warm-up', 'warmup', 'warm', 'practice', 'drill', 'skill', 'demonstration', 'demo', 'activity', 'procedure', 'step', 'pathway', 'flow', 'structure', 'vessel', 'heartbeat', 'sound', 'importance', 'conclusion', 'wrap', 'cool-down', 'cooldown', 'cool', 'recap', 'homework']):
                    current_section = "activities"
                    activity_text = section_header
                    if section_content:
                        section_content = re.sub(r'^-\s*', '', section_content).strip()
                        activity_text += ": " + section_content
                    if activity_text and len(activity_text) > 10:
                        lesson_data["activities"].append(activity_text)
                elif any(keyword in section_header_lower for keyword in ['assessment', 'evaluation', 'homework', 'assignment']):
                    current_section = "assessment"
                    if section_content and len(section_content) > 10:
                        section_content = re.sub(r'^-\s*', '', section_content).strip()
                        lesson_data["assessment"] = section_content
                else:
                    current_section = "activities"
                    activity_text = section_header
                    if section_content:
                        section_content = re.sub(r'^-\s*', '', section_content).strip()
                        activity_text += ": " + section_content
                    if activity_text and len(activity_text) > 10:
                        lesson_data["activities"].append(activity_text)
            
            # Title detection
            if "title:" in line_lower and i < 5:
                title_match = re.search(r'title[:\s]+(.+)', line, flags=re.IGNORECASE)
                if title_match:
                    lesson_data["title"] = re.sub(r'\*\*', '', title_match.group(1)).strip()
                continue
            
            # Lesson Description detection - must come early, before objectives
            if (re.search(r'(lesson\s+description|description|overview|lesson\s+overview|what\s+is\s+this\s+lesson)', line_lower) and i < 30) or \
               (re.search(r'\*\*.*?(lesson\s+description|description)[:\s]', line_lower, flags=re.IGNORECASE) and i < 30):
                current_section = "description"
                desc_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                desc_text = re.sub(r'\*\*?', '', desc_text)
                desc_text = re.sub(r'(lesson\s+description|description|overview|lesson\s+overview|what\s+is\s+this\s+lesson)[:\s]+', '', desc_text, flags=re.IGNORECASE).strip()
                if desc_text and len(desc_text) > 20:
                    if lesson_data["description"]:
                        lesson_data["description"] += " " + desc_text
                    else:
                        lesson_data["description"] = desc_text
                continue
            
            # Objective detection
            if re.search(r'(objective|objectives|learning\s+objective)', line_lower):
                current_section = "objectives"
                if re.search(r'(detailed|using|bloom|taxonomy|learning\s+objectives?)[:\s]*$', line_lower):
                    continue
                
                objective_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                objective_text = re.sub(r'\*\*?', '', objective_text)
                objective_text = re.sub(r'(objective|objectives|learning\s+objective)(\s+of\s+the\s+lesson)?[:\s]+', '', objective_text, flags=re.IGNORECASE).strip()
                
                if re.match(r'^[-•]\s*(remember|understand|apply|analyze|evaluate|create)[:\s]*$', objective_text.lower()):
                    continue
                
                objective_text = re.sub(r'^[-•]\s*', '', objective_text).strip()
                
                if objective_text and len(objective_text) > 10 and not re.match(r'^(detailed|using|bloom|taxonomy)', objective_text.lower()):
                    if re.search(r'(will|can|should|students?\s+will|students?\s+can|students?\s+should|recall|explain|perform|demonstrate|identify|analyze|create|evaluate)', objective_text.lower()):
                        lesson_data["objectives"].append(objective_text)
                continue
            
            # Materials detection
            elif re.search(r'(material|materials|supplies|resources|equipment)(\s+needed)?', line_lower):
                current_section = "materials"
                materials_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                materials_text = re.sub(r'\*\*?', '', materials_text)
                materials_text = re.sub(r'(material|materials|supplies|resources|equipment)(\s+needed)?[:\s]+', '', materials_text, flags=re.IGNORECASE).strip()
                if materials_text and len(materials_text) > 5:
                    for material in materials_text.split(','):
                        material = material.strip()
                        if material and len(material) > 2:
                            lesson_data["materials"].append(material)
                continue
            
            # Introduction detection
            elif re.match(r'^(introduction|intro)(\s+to\s+[^:]+)?\s*\(?\d+\s*minutes?\)?\s*[:\-]?', line_lower) or \
                 (re.search(r'^(introduction|intro)(\s+to\s+[^:]+)?[:\-]', line_lower) and i < 20):
                current_section = "introduction"
                intro_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                intro_text = re.sub(r'\*\*?', '', intro_text)
                intro_text = re.sub(r'(introduction|intro)(\s+to\s+[^-]+)?\s*\(?\d+\s*minutes?\)?\s*[:\-]?\s*', '', intro_text, flags=re.IGNORECASE)
                intro_text = re.sub(r'(introduction|intro)[:\s]+', '', intro_text, flags=re.IGNORECASE).strip()
                if intro_text and len(intro_text) > 10:
                    lesson_data["introduction"] = intro_text
            
            # Activity/Activities detection
            elif re.search(r'activity\s+\d+[:\-]', line_lower):
                current_section = "activities"
                activity_match = re.search(r'activity\s+\d+[:\-]\s*(.+)', line, flags=re.IGNORECASE)
                if activity_match:
                    activity_content = activity_match.group(1).strip()
                    activity_content = re.sub(r'\*\*?', '', activity_content).strip()
                    activity_content = re.sub(r'^[-•]\s*', '', activity_content).strip()
                    if activity_content and len(activity_content) > 5:
                        lesson_data["activities"].append(activity_content)
            elif re.match(r'^activities?[:\-]?\s*$', line_lower) or (re.match(r'^activities?[:\-]', line_lower) and i > 5):
                current_section = "activities"
                activities_match = re.match(r'^activities?[:\-]\s*(.+)', line, flags=re.IGNORECASE)
                if activities_match and activities_match.group(1).strip():
                    activity_content = activities_match.group(1).strip()
                    activity_content = re.sub(r'\*\*?', '', activity_content).strip()
                    if activity_content and len(activity_content) > 5:
                        lesson_data["activities"].append(activity_content)
            elif re.match(r'^(warmup|warm-up|warm\s+up|cool\s+down|cooldown|cool-down|homework)[:\-]', line_lower):
                current_section = "activities"
                header_match = re.match(r'^(warmup|warm-up|warm\s+up|cool\s+down|cooldown|cool-down|homework)[:\-]\s*(.+)', line, flags=re.IGNORECASE)
                if header_match:
                    header_name = header_match.group(1).strip()
                    header_content = header_match.group(2).strip() if header_match.lastindex >= 2 else ""
                    header_content = re.sub(r'\*\*?', '', header_content).strip()
                    if header_content and len(header_content) > 5:
                        lesson_data["activities"].append(f"{header_name.title()}: {header_content}")
            elif re.match(r'^\d*\.?\s*(activity|activities|procedure|lesson\s+procedure)', line_lower):
                if "procedure" in line_lower and "lesson" in line_lower:
                    current_section = None
                else:
                    current_section = "activities"
                continue
            
            # Step-by-step format detection
            elif re.search(r'step\s+\d+[:\-]', line_lower):
                current_section = "activities"
                step_text = re.sub(r'^[-•*]\s*', '', line, flags=re.IGNORECASE)
                step_text = re.sub(r'\*\*?step\s+\d+[:\-]\s*\*\*?', '', step_text, flags=re.IGNORECASE)
                step_text = re.sub(r'step\s+\d+[:\-]\s*', '', step_text, flags=re.IGNORECASE)
                step_text = re.sub(r'\*\*?', '', step_text).strip()
                if step_text and len(step_text) > 10:
                    lesson_data["activities"].append(step_text)
                continue
            
            # Numbered items that are likely activities
            elif re.match(r'^\d+\.', line) and current_section is None:
                if re.search(r'(minutes?|hours?|discussion|demonstration|simulation|exercise|review|practice|assignment|assessment)', line_lower):
                    current_section = "activities"
            elif re.match(r'^\d+\.', line) and current_section in ["danielson_framework", "costas_questioning", "curriculum_standards", "description"]:
                continue
            
            # Section headers with time markers
            elif re.match(r'^[A-Z][a-z]+\s+(Content|Practice|Review|Assessment|Evaluation|Discussion|Demonstration|Instruction|Activity)\s*\(?\d+\s*minutes?\)?\s*[:\-]?', line, re.IGNORECASE):
                current_section = "activities"
                section_match = re.match(r'^([A-Z][a-z]+\s+(?:Content|Practice|Review|Assessment|Evaluation|Discussion|Demonstration|Instruction|Activity))\s*\(?\d+\s*minutes?\)?\s*[:\-]?\s*(.*)', line, re.IGNORECASE)
                if section_match:
                    section_name = section_match.group(1).strip()
                    section_content = section_match.group(2).strip() if section_match.lastindex >= 2 else ""
                    if section_content and len(section_content) > 5:
                        lesson_data["activities"].append(f"{section_name}: {section_content}")
            elif re.search(r'^(discussion|demonstration|simulation|exercise|review|q&a|qa)\s*\(?\d+\s*minutes?\)?\s*[:\-]', line_lower):
                current_section = "activities"
                activity_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                activity_text = re.sub(r'\*\*?', '', activity_text)
                activity_text = re.sub(r'\s*\(?\d+\s*minutes?\)?\s*[:\-]?\s*', '', activity_text, flags=re.IGNORECASE)
                activity_text = re.sub(r'(discussion|demonstration|simulation|exercise|review|q&a|qa)[:\s]+', '', activity_text, flags=re.IGNORECASE).strip()
                if activity_text and len(activity_text) > 10:
                    lesson_data["activities"].append(activity_text)
            
            # Danielson Framework detection
            elif re.search(r'danielson\s+framework|domain\s+[1234]|framework\s+alignment', line_lower):
                current_section = "danielson_framework"
                framework_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                framework_text = re.sub(r'\*\*?', '', framework_text)
                framework_text = re.sub(r'(danielson\s+framework|framework\s+alignment)[:\s]+', '', framework_text, flags=re.IGNORECASE).strip()
                if framework_text and len(framework_text) > 10:
                    if lesson_data["danielson_framework"]:
                        lesson_data["danielson_framework"] += "\n\n" + framework_text
                    else:
                        lesson_data["danielson_framework"] = framework_text
            
            # Costa's Levels of Questioning detection
            elif re.search(r"costa'?s\s+level|level\s+[123]\s+question|questioning\s+level", line_lower):
                current_section = "costas_questioning"
                questioning_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                questioning_text = re.sub(r'\*\*?', '', questioning_text)
                questioning_text = re.sub(r"(costa'?s\s+level|questioning\s+level)[:\s]+", '', questioning_text, flags=re.IGNORECASE).strip()
                if questioning_text and len(questioning_text) > 10:
                    if lesson_data["costas_questioning"]:
                        lesson_data["costas_questioning"] += " " + questioning_text
                    else:
                        lesson_data["costas_questioning"] = questioning_text
            
            # Curriculum Standards detection
            elif re.search(r'(curriculum\s+standard|core\s+curriculum\s+standard|common\s+core|ngss|standard\s+[a-z0-9\.]+|state\s+standard|standards\s+alignment|aligned\s+with\s+standard)', line_lower):
                current_section = "curriculum_standards"
                standards_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                standards_text = re.sub(r'\*\*?', '', standards_text)
                standards_text = re.sub(r'(curriculum\s+standard|core\s+curriculum\s+standard|common\s+core|ngss|state\s+standard|standards\s+alignment|aligned\s+with\s+standard)[:\s]+', '', standards_text, flags=re.IGNORECASE).strip()
                if standards_text and len(standards_text) > 10:
                    if lesson_data["curriculum_standards"]:
                        lesson_data["curriculum_standards"] += "\n\n" + standards_text
                    else:
                        lesson_data["curriculum_standards"] = standards_text
            
            # Exit Ticket detection
            elif re.search(r'exit\s+ticket|exit\s+slip|formative\s+assessment\s+\(exit', line_lower):
                current_section = "exit_ticket"
                exit_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                exit_text = re.sub(r'\*\*?', '', exit_text)
                exit_text = re.sub(r'(exit\s+ticket|exit\s+slip|formative\s+assessment)[:\s]+', '', exit_text, flags=re.IGNORECASE).strip()
                if exit_text and len(exit_text) > 10:
                    if lesson_data["exit_ticket"]:
                        lesson_data["exit_ticket"] += " " + exit_text
                    else:
                        lesson_data["exit_ticket"] = exit_text
            
            # Worksheets detection
            elif (re.search(r'^\s*(worksheet|worksheets|activity\s+sheet|student\s+worksheet|worksheet\s+title|worksheet\s+instructions)', line_lower) and not re.search(r'(material|supply|equipment|resource)', line_lower)) or \
                 (re.match(r'^\s*\d+[\.\)]\s+', line) and current_section == "worksheets"):
                if current_section != "worksheets":
                    current_section = "worksheets"
                    worksheet_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                    worksheet_text = re.sub(r'\*\*?', '', worksheet_text)
                    worksheet_text = re.sub(r'(worksheet|worksheets|activity\s+sheet|student\s+worksheet|worksheet\s+title|worksheet\s+instructions)[:\s]+', '', worksheet_text, flags=re.IGNORECASE).strip()
                    if worksheet_text and len(worksheet_text) > 5:
                        if lesson_data["worksheets"]:
                            lesson_data["worksheets"] += "\n\n" + worksheet_text
                        else:
                            lesson_data["worksheets"] = worksheet_text
            
            # Rubrics detection
            elif re.search(r'^\s*(rubric|rubrics|assessment\s+rubric|scoring\s+rubric|evaluation\s+rubric)', line_lower):
                current_section = "rubrics"
                rubric_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                rubric_text = re.sub(r'\*\*?', '', rubric_text)
                rubric_text = re.sub(r'(rubric|rubrics|assessment\s+rubric|scoring\s+rubric|evaluation\s+rubric)[:\s]+', '', rubric_text, flags=re.IGNORECASE).strip()
                if rubric_text and len(rubric_text) > 5:
                    if lesson_data["rubrics"]:
                        lesson_data["rubrics"] += "\n\n" + rubric_text
                    else:
                        lesson_data["rubrics"] = rubric_text
            
            # Assessments detection
            elif re.search(r'(summative\s+assessment|formative\s+assessment|assessment\s+criteria|assessment\s+questions)', line_lower) and current_section != "rubrics":
                current_section = "assessments"
                assessment_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                assessment_text = re.sub(r'\*\*?', '', assessment_text)
                assessment_text = re.sub(r'(summative\s+assessment|formative\s+assessment|assessment\s+criteria|assessment\s+questions)[:\s]+', '', assessment_text, flags=re.IGNORECASE).strip()
                if assessment_text and len(assessment_text) > 10:
                    if lesson_data["assessments"]:
                        lesson_data["assessments"] += " " + assessment_text
                    else:
                        lesson_data["assessments"] = assessment_text
            
            # Assessment detection
            elif re.search(r'(assessment|evaluation|homework|assignment)', line_lower):
                current_section = "assessment"
                assessment_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                assessment_text = re.sub(r'\*\*?', '', assessment_text)
                assessment_text = re.sub(r'(assessment|evaluation|homework|assignment)[:\s]+', '', assessment_text, flags=re.IGNORECASE).strip()
                if assessment_text and len(assessment_text) > 10:
                    lesson_data["assessment"] = assessment_text
                continue
            
            # Grade level detection
            elif "grade" in line_lower and ("level" in line_lower or "class" in line_lower or "suitable" in line_lower):
                grade_match = re.search(r'grade[s]?\s+(?:level[s]?[:\s]+)?([\w-]+)', line_lower)
                if grade_match:
                    lesson_data["grade_level"] = grade_match.group(1).upper()
                continue
            
            # Subject detection
            elif "subject" in line_lower:
                subject_match = re.search(r'subject[:\s]+(.+)', line_lower)
                if subject_match:
                    lesson_data["subject"] = subject_match.group(1).strip()
                continue
            
            # Duration detection
            elif "duration" in line_lower:
                duration_match = re.search(r'duration[:\s]+(.+)', line_lower)
                if duration_match:
                    lesson_data["duration"] = duration_match.group(1).strip()
                continue
            
            # Body/Content section - reset section
            elif re.match(r'^\d*\.?\s*(body|content|main)', line_lower):
                current_section = None
                continue
            
            # Add content to current section
            if current_section:
                if re.match(r'^\d+\.\s*\*\*[^*]+\*\*', line):
                    continue
                
                if re.match(r'^\d+\.\s*\*\*', line):
                    colon_match = re.search(r':\s*(.+)', line)
                    if colon_match:
                        clean_line = colon_match.group(1).strip()
                        clean_line = re.sub(r'\*\*?', '', clean_line)
                        clean_line = re.sub(r'\s*-\s*\d+\s*minutes?[:\s]*', '', clean_line, flags=re.IGNORECASE).strip()
                    else:
                        clean_line = re.sub(r'^\d+\.\s*\*\*[^*]+\*\*[:\s]*', '', line)
                        clean_line = re.sub(r'\*\*?', '', clean_line).strip()
                else:
                    if re.match(r'^step\s+\d+[:\-]', line_lower):
                        step_text = re.sub(r'^step\s+\d+[:\-]\s*', '', line, flags=re.IGNORECASE)
                        step_text = re.sub(r'\*\*?', '', step_text).strip()
                        clean_line = step_text
                    else:
                        clean_line = re.sub(r'^\d+\.?\s*\*\*?', '', line)
                        clean_line = re.sub(r'\*\*?', '', clean_line)
                        clean_line = re.sub(r'^\d+\.?\s*[-•*]?\s*', '', clean_line)
                        clean_line = clean_line.strip()
                
                if not clean_line or len(clean_line) < 3:
                    continue
                
                if re.match(r'^(introduction|objective|material|activity|assessment|discussion|conclusion|procedure|video|simulation|review|assignment|demonstration|exercise|q&a|qa)[:\s]*$', clean_line.lower()):
                    continue
                
                if current_section == "description":
                    if clean_line and len(clean_line) > 10:
                        if not re.match(r'^(description|overview|lesson|introduction|objective|material|activity|assessment)[:\s]*$', clean_line.lower()):
                            if lesson_data["description"]:
                                lesson_data["description"] += " " + clean_line
                            else:
                                lesson_data["description"] = clean_line
                elif current_section == "introduction":
                    if re.match(r'^\d+\.\s+', clean_line):
                        numbered_item = re.sub(r'^\d+\.\s+', '', clean_line).strip()
                        if lesson_data["introduction"]:
                            lesson_data["introduction"] += " " + numbered_item
                        else:
                            lesson_data["introduction"] = numbered_item
                    else:
                        if lesson_data["introduction"]:
                            lesson_data["introduction"] += " " + clean_line
                        else:
                            lesson_data["introduction"] = clean_line
                elif current_section == "objectives":
                    clean_line = re.sub(r'^objective[:\s]+', '', clean_line, flags=re.IGNORECASE)
                    if re.match(r'^(detailed|using|bloom|taxonomy)[:\s]*$', clean_line.lower()):
                        continue
                    if re.match(r'^[-•]\s*(remember|understand|apply|analyze|evaluate|create)[:\s]*$', clean_line.lower()):
                        continue
                    if clean_line and len(clean_line) > 10:
                        if re.search(r'(will|can|should|students?\s+will|students?\s+can|students?\s+should|recall|explain|perform|demonstrate|identify|analyze|create|evaluate|understand|apply|remember)', clean_line.lower()):
                            lesson_data["objectives"].append(clean_line)
                elif current_section == "activities":
                    if clean_line and len(clean_line) > 5:
                        if re.match(r'^\(?\d+\s*(minutes?|mins?|hours?|hrs?)\)?\s*$', clean_line, re.IGNORECASE):
                            if lesson_data["activities"]:
                                last_activity = lesson_data["activities"][-1]
                                if not re.search(r'\(\d+\s*(minutes?|mins?|hours?|hrs?)\)', last_activity, re.IGNORECASE):
                                    lesson_data["activities"][-1] = last_activity + " " + clean_line
                            continue
                        if re.match(r'^(warmup|warm-up|warm\s+up|cool\s+down|cooldown|cool-down|homework|assessment|activity|introduction|demonstration|practice|drill)[:\-]?\s*$', clean_line, re.IGNORECASE):
                            continue
                        if re.match(r'^\d+\.\s+', clean_line):
                            numbered_item = re.sub(r'^\d+\.\s+', '', clean_line).strip()
                            numbered_item = re.sub(r'^[-•]\s*', '', numbered_item).strip()
                            if lesson_data["activities"]:
                                last_activity = lesson_data["activities"][-1]
                                if re.search(r'\(?\d+\s*minutes?\)?[:\-]?$', last_activity):
                                    lesson_data["activities"][-1] = last_activity + " " + numbered_item
                                elif len(last_activity) < 100:
                                    lesson_data["activities"][-1] = last_activity + " " + numbered_item
                                else:
                                    lesson_data["activities"].append(numbered_item)
                            else:
                                lesson_data["activities"].append(numbered_item)
                        else:
                            is_incomplete = (
                                clean_line.startswith('-') or
                                clean_line.startswith('•') or
                                (len(clean_line) < 60 and lesson_data["activities"] and (
                                    not re.match(r'^[A-Z]', clean_line) or
                                    re.match(r'^(A|An|The|And|Of|To|In|On|At|For|With|By)\s+', clean_line, re.IGNORECASE)
                                ))
                            )
                            if is_incomplete and lesson_data["activities"]:
                                last_activity = lesson_data["activities"][-1]
                                continuation = re.sub(r'^[-•]\s*', '', clean_line).strip()
                                lesson_data["activities"][-1] = last_activity + " " + continuation
                            else:
                                if len(clean_line) < 30 and lesson_data["activities"]:
                                    last_activity = lesson_data["activities"][-1]
                                    lesson_data["activities"][-1] = last_activity + " " + clean_line
                                else:
                                    lesson_data["activities"].append(clean_line)
                elif current_section == "assessment":
                    if lesson_data["assessment"]:
                        lesson_data["assessment"] += " " + clean_line
                    else:
                        lesson_data["assessment"] = clean_line
                elif current_section == "exit_ticket":
                    if lesson_data["exit_ticket"]:
                        lesson_data["exit_ticket"] += " " + clean_line
                    else:
                        lesson_data["exit_ticket"] = clean_line
                elif current_section == "worksheets":
                    if re.match(r'^(materials|activities|instruction|procedure|introduction|body|activity|discussion|conclusion|assessment|homework|danielson|costas|exit\s+ticket|assessments|begin\s+with|present\s+the|show\s+a|discuss|pair\s+students|circulate|i\s+hope|let\s+me\s+know)', clean_line.lower()):
                        current_section = None
                    elif re.match(r'^(a\s+worksheet|students\s+should|the\s+worksheet|this\s+worksheet)', clean_line.lower()):
                        continue
                    elif clean_line and len(clean_line) > 3:
                        if not re.match(r'^(lesson|procedure|introduction|body|activity|discussion|conclusion|assessment|homework|this\s+is|always\s+remember|feel\s+free)', clean_line.lower()):
                            if not re.match(r'^[-•]\s+(cpr|safety|step-by-step|instructional)', clean_line.lower()):
                                if not re.match(r'^(a\s+worksheet|students\s+should|the\s+key\s+should|the\s+worksheet)', clean_line.lower()):
                                    if lesson_data["worksheets"]:
                                        if re.match(r'^\d+[\.\)]', clean_line) or re.match(r'^[A-Z][a-z]+:', clean_line):
                                            lesson_data["worksheets"] += "\n\n" + clean_line
                                        else:
                                            lesson_data["worksheets"] += "\n" + clean_line
                                    else:
                                        lesson_data["worksheets"] = clean_line
                elif current_section == "assessments":
                    if lesson_data["assessments"]:
                        lesson_data["assessments"] += " " + clean_line
                    else:
                        lesson_data["assessments"] = clean_line
                elif current_section == "danielson_framework":
                    if re.match(r'^\d+\.', clean_line):
                        content = re.sub(r'^\d+\.\s*', '', clean_line).strip()
                        content = re.sub(r'::\s*', ': ', content)
                        content = re.sub(r'\*\*?', '', content).strip()
                        if content and len(content) > 5:
                            if lesson_data["danielson_framework"]:
                                lesson_data["danielson_framework"] += "\n\n" + content
                            else:
                                lesson_data["danielson_framework"] = content
                    else:
                        if clean_line and len(clean_line) > 3:
                            if lesson_data["danielson_framework"]:
                                lesson_data["danielson_framework"] += " " + clean_line
                            else:
                                lesson_data["danielson_framework"] = clean_line
                elif current_section == "costas_questioning":
                    if re.match(r'^\d+\.', clean_line):
                        content = re.sub(r'^\d+\.\s*', '', clean_line).strip()
                        content = re.sub(r'::\s*', ': ', content)
                        content = re.sub(r'\*\*?', '', content).strip()
                        if content and len(content) > 5:
                            if lesson_data["costas_questioning"]:
                                lesson_data["costas_questioning"] += "\n\n" + content
                            else:
                                lesson_data["costas_questioning"] = content
                    else:
                        if clean_line and len(clean_line) > 3:
                            if lesson_data["costas_questioning"]:
                                lesson_data["costas_questioning"] += " " + clean_line
                            else:
                                lesson_data["costas_questioning"] = clean_line
                elif current_section == "curriculum_standards":
                    if lesson_data["curriculum_standards"]:
                        lesson_data["curriculum_standards"] += " " + clean_line
                    else:
                        lesson_data["curriculum_standards"] = clean_line
                elif current_section == "materials":
                    if not re.match(r'^(\d+\.?\s+)?(lesson|procedure|introduction|body|activity|discussion|conclusion|assessment|homework|materials|this\s+is|always\s+remember)', clean_line.lower()):
                        if clean_line and not re.match(r'^\d+\.?\s*$', clean_line) and len(clean_line) > 3:
                            lesson_data["materials"].append(clean_line)
        
        # Extract title from original message or response
        if not lesson_data["title"]:
            if original_message:
                title_match = re.search(r'lesson\s+plan\s+(?:on|for|about)\s+(.+?)(?:\.|$|please)', original_message, flags=re.IGNORECASE)
                if not title_match:
                    title_match = re.search(r'lesson\s+(?:on|for|about)\s+(.+?)(?:\.|$|please)', original_message, flags=re.IGNORECASE)
                if title_match:
                    topic = title_match.group(1).strip()
                    topic = re.sub(r'^(a|an|the)\s+', '', topic, flags=re.IGNORECASE)
                    lesson_data["title"] = topic.title() + " Lesson Plan"
            
            if not lesson_data["title"]:
                for line in lines[:10]:
                    line = line.strip()
                    if not line:
                        continue
                    title_match = re.search(r'title[:\s]+(.+)', line, flags=re.IGNORECASE)
                    if title_match:
                        lesson_data["title"] = re.sub(r'\*\*', '', title_match.group(1)).strip()
                        break
                    title_match = re.search(r'lesson\s+plan\s+(?:on|for)\s+(.+?)(?:\.|$)', line, flags=re.IGNORECASE)
                    if title_match:
                        lesson_data["title"] = title_match.group(1).strip().title()
                        break
                    title_match = re.search(r'(?:lesson\s+plan|create|help)\s+(?:on|for|about)\s+(.+?)(?:\.|$)', line, flags=re.IGNORECASE)
                    if title_match:
                        topic = title_match.group(1).strip()
                        topic = re.sub(r'^(a|an|the)\s+', '', topic, flags=re.IGNORECASE)
                        lesson_data["title"] = topic.title()
                        break
                    elif len(line) < 100 and not re.match(r'^(absolutely|sure|here|i\s+can|i\s+apologize)', line.lower()):
                        clean_title = re.sub(r'\*\*', '', line).strip()
                        if not re.match(r'^(absolutely|sure|here|i\s+can|i\s+apologize)', clean_title.lower()):
                            lesson_data["title"] = clean_title
                            break
        
        # Clean up objectives
        lesson_data["objectives"] = [
            re.sub(r'^objective[:\s]+', '', obj, flags=re.IGNORECASE).strip()
            for obj in lesson_data["objectives"]
            if obj and len(obj) > 10
        ]
        
        # If we found meaningful data, return it
        has_activities = len(lesson_data["activities"]) > 0
        has_objectives = len(lesson_data["objectives"]) > 0
        has_introduction = bool(lesson_data["introduction"])
        has_title = bool(lesson_data["title"])
        
        # If we have activities (like step-by-step), create a basic lesson plan
        if has_activities and not (has_objectives or has_introduction or has_title):
            if original_message:
                title_match = re.search(r'lesson\s+(?:plan\s+)?(?:on|for|about)\s+(.+?)(?:\.|$|please)', original_message, flags=re.IGNORECASE)
                if title_match:
                    topic = title_match.group(1).strip()
                    topic = re.sub(r'^(a|an|the)\s+', '', topic, flags=re.IGNORECASE)
                    lesson_data["title"] = topic.title() + " Lesson Plan"
                else:
                    lesson_data["title"] = "Lesson Plan"
            
            if not lesson_data["objectives"]:
                lesson_data["objectives"].append("Understand the key concepts and steps presented in this lesson.")
            
            if not lesson_data["introduction"] and lesson_data["activities"]:
                first_activity = lesson_data["activities"][0]
                lesson_data["introduction"] = first_activity[:200] + "..." if len(first_activity) > 200 else first_activity
        
        if has_activities or has_objectives or has_introduction or has_title:
            return lesson_data
        
        return None

    # ==================== AI CHAT FUNCTIONALITY ====================
    
    def send_chat_message(
        self, 
        teacher_id: str, 
        chat_request: AIAssistantChatRequest
    ) -> AIAssistantChatResponse:
        """Send a message to the AI assistant and get a response"""
        try:
            # Get or create conversation
            conversation = None
            if chat_request.conversation_id:
                conversation = self.db.query(AIAssistantConversation).filter(
                    and_(
                        AIAssistantConversation.id == chat_request.conversation_id,
                        AIAssistantConversation.teacher_id == teacher_id
                    )
                ).first()
            
            if not conversation:
                # Create new conversation
                conversation_data = AIAssistantConversationCreate(
                    config_id=chat_request.config_id,
                    conversation_title=chat_request.conversation_title or "New Conversation",
                    conversation_type=chat_request.conversation_type or "general_chat",
                    metadata=chat_request.metadata or {}
                )
                conversation = self.create_conversation(teacher_id, conversation_data)
                conversation = self.db.query(AIAssistantConversation).filter(
                    AIAssistantConversation.id == conversation.id
                ).first()
            
            # Get AI configuration
            config = None
            if chat_request.config_id:
                config = self.db.query(AIAssistantConfig).filter(
                    and_(
                        AIAssistantConfig.id == chat_request.config_id,
                        AIAssistantConfig.teacher_id == teacher_id
                    )
                ).first()
            
            if not config:
                # Use default configuration
                config = self._get_default_config(teacher_id, chat_request.conversation_type)
            
            # Save user message
            user_message = AIAssistantMessage(
                id=str(uuid.uuid4()),
                conversation_id=conversation.id,
                message_type="user",
                content=chat_request.message,
                metadata=chat_request.metadata or {}
            )
            self.db.add(user_message)
            self.db.flush()
            
            # Get conversation history for context
            recent_messages = self.db.query(AIAssistantMessage).filter(
                AIAssistantMessage.conversation_id == conversation.id
            ).order_by(desc(AIAssistantMessage.created_at)).limit(10).all()
            
            # Prepare messages for OpenAI
            messages = []
            
            # Add system message from config
            if config.config_data.get('system_prompt'):
                messages.append({
                    "role": "system",
                    "content": config.config_data['system_prompt']
                })
            
            # Add conversation history (reverse order for proper context)
            for msg in reversed(recent_messages):
                messages.append({
                    "role": msg.message_type,
                    "content": msg.content
                })
            
            # Call OpenAI API
            start_time = datetime.utcnow()
            # For lesson plans, increase max_tokens to allow comprehensive content
            is_lesson_request_check = any(keyword in chat_request.message.lower() for keyword in ["lesson", "lesson plan", "curriculum", "teaching", "class", "student", "grade", "objective", "learning", "education", "pedagogy", "instruction"])
            max_tokens = config.config_data.get('max_tokens', 2000)
            if is_lesson_request_check:
                max_tokens = max(max_tokens, 3000)  # Ensure enough tokens for comprehensive lesson plans
            
            response = self.openai_client.chat.completions.create(
                model=config.config_data.get('model', 'gpt-4'),
                messages=messages,
                temperature=config.config_data.get('temperature', 0.7),
                max_tokens=max_tokens
            )
            end_time = datetime.utcnow()
            
            # Extract response
            ai_response = response.choices[0].message.content
            token_count = response.usage.total_tokens
            processing_time = int((end_time - start_time).total_seconds() * 1000)
            
            # Save AI response
            ai_message = AIAssistantMessage(
                id=str(uuid.uuid4()),
                conversation_id=conversation.id,
                message_type="assistant",
                content=ai_response,
                metadata={
                    "model": config.config_data.get('model', 'gpt-4'),
                    "temperature": config.config_data.get('temperature', 0.7),
                    "max_tokens": config.config_data.get('max_tokens', 2000)
                },
                token_count=token_count,
                processing_time_ms=processing_time
            )
            self.db.add(ai_message)
            
            # Update conversation
            conversation.updated_at = datetime.utcnow()
            
            # Track usage
            self._track_usage(
                teacher_id=teacher_id,
                config_id=config.id,
                usage_type=conversation.conversation_type,
                tokens_used=token_count,
                processing_time_ms=processing_time,
                success=True
            )
            
            self.db.commit()
            
            # Detect widget type and extract structured data (same logic as guest_chat)
            widget_data = None
            widgets = None  # Initialize widgets to avoid "referenced before assignment" error
            message_lower = chat_request.message.lower()
            response_lower = (ai_response or "").lower()
            
            # Check for lesson plan requests FIRST (before fitness, since "plan" is in both)
            lesson_keywords = ["lesson", "lesson plan", "curriculum", "teaching", "class", "student", "grade", "objective", "learning", "education", "pedagogy", "instruction"]
            is_lesson_request = any(keyword in message_lower for keyword in lesson_keywords) or any(keyword in response_lower for keyword in ["lesson", "objective", "students will", "learning objective", "grade level", "curriculum"])
            
            if is_lesson_request:
                logger.info(f"Detected lesson plan request (message: '{chat_request.message[:50]}...'), extracting data from response")
                # Extract lesson plan data from the response
                lesson_data = self._extract_lesson_plan_data(ai_response or "", chat_request.message)
                if lesson_data:
                    # Clear worksheets/rubrics from initial response - they'll be added in separate calls
                    lesson_data["worksheets"] = ""
                    lesson_data["rubrics"] = ""
                    # Also clear assessments if it contains worksheet/rubric content
                    if lesson_data.get("assessments", ""):
                        assessments_lower = lesson_data["assessments"].lower()
                        if "worksheet" in assessments_lower or "rubric" in assessments_lower or "separate call" in assessments_lower:
                            lesson_data["assessments"] = ""
                    if lesson_data.get("assessment", ""):
                        assessment_lower = lesson_data["assessment"].lower()
                        if "worksheet" in assessment_lower or "rubric" in assessment_lower or "separate call" in assessment_lower:
                            lesson_data["assessment"] = ""
                
                logger.info(f"Extracted lesson plan data: {lesson_data}")
                
                if lesson_data:
                    # STEP 2: Generate worksheets in a separate call
                    import time
                    step2_start = time.time()
                    logger.info("📝 Step 2: Generating worksheets...")
                    try:
                        worksheet_prompt = f"""Based on the following lesson plan, create ACTUAL, COMPLETE worksheets that students can use.

Lesson Plan Title: {lesson_data.get('title', 'N/A')}
Subject: {lesson_data.get('subject', 'N/A')}
Grade Level: {lesson_data.get('grade_level', 'N/A')}
Objectives: {', '.join(lesson_data.get('objectives', [])[:3]) if isinstance(lesson_data.get('objectives'), list) else 'N/A'}

CRITICAL REQUIREMENTS:
- Create ACTUAL worksheets with numbered questions, NOT descriptions
- ABSOLUTE MINIMUM 10 QUESTIONS REQUIRED - you MUST create at least 10 questions. If you create fewer than 10, the worksheet is incomplete and will be rejected.
- Include a variety of question types: fill-in-the-blank, multiple choice, short answer, matching, or labeling questions
- Provide a complete Answer Key with all answers for ALL questions
- Each worksheet must be ready to print and use
- Do NOT write "A worksheet with..." - write the actual questions directly
- Questions should cover all key concepts from the lesson objectives
- Count your questions before submitting - ensure you have at least 10 numbered questions (1, 2, 3, ... 10, 11, etc.)
- If you create fewer than 10 questions, you MUST add more questions to reach the minimum of 10
- Example: If you have 7 questions, you need to add 3 more questions to reach 10 minimum

Generate comprehensive, detailed worksheets now:"""
                        
                        worksheet_messages = [
                            {"role": "system", "content": "You are an expert educator creating printable worksheets for students. Always provide actual questions and answer keys, never descriptions."},
                            {"role": "user", "content": worksheet_prompt}
                        ]
                        
                        # Call OpenAI synchronously (this is a sync method)
                        worksheet_response = self.openai_client.chat.completions.create(
                            model="gpt-4",
                            messages=worksheet_messages,
                            temperature=0.7,
                            max_tokens=2000
                        )
                        
                        worksheet_content = worksheet_response.choices[0].message.content
                        logger.info(f"✅ Step 2 complete: Worksheets generated ({len(worksheet_content)} characters)")
                        
                        # Extract worksheet content (filter out descriptions, keep actual questions)
                        if worksheet_content:
                            worksheet_lines = worksheet_content.split('\n')
                            actual_worksheet_lines = []
                            
                            for i, line in enumerate(worksheet_lines):
                                line_lower = line.lower().strip()
                                
                                # Skip description/intro lines
                                if re.search(r'^(a\s+worksheet|students\s+should|the\s+worksheet|this\s+worksheet|i\s+hope|let\s+me\s+know|here\s+is|below\s+is)', line_lower):
                                    continue
                                
                                # Skip lines that are just descriptions
                                if re.search(r'^(this|these|the)\s+(worksheet|questions|activities)\s+(will|should|can|is|are)', line_lower):
                                    continue
                                
                                # Keep actual content (questions, instructions, answer keys)
                                if re.search(r'^(worksheet|instructions|answer\s+key|questions?|activities?|\d+[\.\)\-\*]|fill|match|label|multiple\s+choice)', line_lower, re.IGNORECASE):
                                    actual_worksheet_lines.append(line)
                                elif line.strip() and len(line.strip()) > 10:  # Keep substantial lines
                                    # Check if it looks like a question or answer
                                    if re.search(r'[?]|^[A-D][\.\)]|^[a-z][\.\)]|blank|______', line, re.IGNORECASE):
                                        actual_worksheet_lines.append(line)
                                    elif i > 0 and actual_worksheet_lines:  # Continuation of previous content
                                        actual_worksheet_lines.append(line)
                            
                            if actual_worksheet_lines:
                                lesson_data["worksheets"] = '\n'.join(actual_worksheet_lines)
                            else:
                                # Fallback: use content but remove obvious description lines
                                cleaned = '\n'.join([l for l in worksheet_lines if not re.search(r'^(a\s+worksheet|students\s+should|i\s+hope|let\s+me\s+know)', l.lower().strip())])
                                lesson_data["worksheets"] = cleaned if cleaned else worksheet_content
                    
                    except Exception as worksheet_error:
                        logger.error(f"Error generating worksheets: {worksheet_error}")
                        # Continue without worksheets - don't fail the whole request
                    
                    # STEP 3: Generate rubrics in a separate call
                    logger.info("📋 Step 3: Generating rubrics...")
                    try:
                        rubric_prompt = f"""Based on the following lesson plan, create a DETAILED, COMPLETE rubric for assessing student performance.

Lesson Plan Title: {lesson_data.get('title', 'N/A')}
Subject: {lesson_data.get('subject', 'N/A')}
Grade Level: {lesson_data.get('grade_level', 'N/A')}
Objectives: {', '.join(lesson_data.get('objectives', [])[:3]) if isinstance(lesson_data.get('objectives'), list) else 'N/A'}

CRITICAL REQUIREMENTS:
- Include clear assessment criteria (what students are being evaluated on)
- Provide performance levels (Excellent, Proficient, Developing, Beginning, or 4, 3, 2, 1)
- Describe what each performance level looks like
- Include point values for each criterion
- Provide total points possible
- Make it specific, measurable, and aligned with learning objectives

Generate a comprehensive rubric now:"""
                        
                        rubric_messages = [
                            {"role": "system", "content": "You are an expert educator creating assessment rubrics. Always provide detailed criteria with performance levels and point values."},
                            {"role": "user", "content": rubric_prompt}
                        ]
                        
                        # Call OpenAI synchronously (this is a sync method)
                        rubric_response = self.openai_client.chat.completions.create(
                            model="gpt-4",
                            messages=rubric_messages,
                            temperature=0.7,
                            max_tokens=2000
                        )
                        
                        rubric_content = rubric_response.choices[0].message.content
                        logger.info(f"✅ Step 3 complete: Rubrics generated ({len(rubric_content)} characters)")
                        
                        # Extract rubric content (filter out descriptions, keep actual criteria)
                        if rubric_content:
                            rubric_lines = rubric_content.split('\n')
                            actual_rubric_lines = []
                            
                            for i, line in enumerate(rubric_lines):
                                line_lower = line.lower().strip()
                                
                                # Skip description/intro lines
                                if re.search(r'^(a\s+rubric|students\s+should|the\s+rubric|this\s+rubric|i\s+hope|let\s+me\s+know|here\s+is|below\s+is)', line_lower):
                                    continue
                                
                                # Skip lines that are just descriptions
                                if re.search(r'^(this|these|the)\s+(rubric|criteria|assessment)\s+(will|should|can|is|are)', line_lower):
                                    continue
                                
                                # Keep actual rubric content (criteria, performance levels, points)
                                if re.search(r'^(rubric|criteria|criterion|excellent|proficient|developing|beginning|advanced|novice|\d+[\.\)]|points?|pts?|total)', line_lower, re.IGNORECASE):
                                    actual_rubric_lines.append(line)
                                elif line.strip() and len(line.strip()) > 10:  # Keep substantial lines
                                    # Check if it looks like rubric content (performance level descriptions)
                                    if re.search(r'[:\-]\s|points?|pts?|level|score', line, re.IGNORECASE):
                                        actual_rubric_lines.append(line)
                                    elif i > 0 and actual_rubric_lines:  # Continuation of previous content
                                        actual_rubric_lines.append(line)
                            
                            if actual_rubric_lines:
                                lesson_data["rubrics"] = '\n'.join(actual_rubric_lines)
                            else:
                                # Fallback: use content but remove obvious description lines
                                cleaned = '\n'.join([l for l in rubric_lines if not re.search(r'^(a\s+rubric|students\s+should|i\s+hope|let\s+me\s+know)', l.lower().strip())])
                                lesson_data["rubrics"] = cleaned if cleaned else rubric_content
                    
                    except Exception as rubric_error:
                        logger.error(f"Error generating rubrics: {rubric_error}")
                        # Continue without rubrics - don't fail the whole request
                    
                    logger.info("✅ All 3 steps complete: Lesson plan, worksheets, and rubrics generated")
                    
                    widget_data = {
                        "type": "lesson-planning",
                        "data": lesson_data
                    }
                    # Ensure is_preview is NOT set for authenticated users
                    if "is_preview" in widget_data.get("data", {}):
                        del widget_data["data"]["is_preview"]
                    if "preview_message" in widget_data.get("data", {}):
                        del widget_data["data"]["preview_message"]
                    logger.info(f"✅ Created comprehensive lesson plan widget_data with worksheets and rubrics")
                    logger.info(f"📊 Widget data keys: {list(widget_data.get('data', {}).keys())}")
                    logger.info(f"📊 Has is_preview: {'is_preview' in widget_data.get('data', {})}")
                else:
                    logger.warning(f"⚠️ Failed to extract lesson plan data")
            else:
                # Widget detection - check in priority order
                # 1. Health/Nutrition/Meal Plan requests (BEFORE fitness to avoid false matches)
                # 2. Fitness/workout requests
                
                # Health/Nutrition keywords - check FIRST
                health_keywords = ["meal plan", "meal planning", "nutrition plan", "nutrition planning", "nutrition", "diet", "diet plan", "calorie", "calories", "protein", "carb", "macros", "meal prep", "eating plan", "food plan", "wrestler", "weight loss plan", "weight loss", "weight gain plan", "weight gain", "cutting plan", "cutting", "bulking plan", "bulking", "meal", "breakfast", "lunch", "dinner", "snack", "nutritional"]
                is_health_request = any(keyword in message_lower for keyword in health_keywords) or any(keyword in response_lower for keyword in ["meal", "nutrition", "diet", "calorie", "protein", "carb", "macro", "breakfast", "lunch", "dinner"])
                
                # Fitness keywords - exclude "weight" alone to avoid matching "weight loss" as fitness
                fitness_keywords = ["workout", "exercise", "fitness", "chest", "training", "routine", "muscle", "strength", "cardio", "gym", "lifting", "squat", "bench", "deadlift"]
                # Check if request includes exercise/workout keywords (even if it's also a health request)
                has_exercise_keywords = any(keyword in message_lower for keyword in fitness_keywords) or any(keyword in response_lower for keyword in ["exercise", "workout", "sets", "reps", "push", "pull", "squat", "bench", "deadlift", "burn", "burning", "calories per day"])
                is_fitness_request = has_exercise_keywords and not is_health_request
                
                # Track widgets to return (can be multiple)
                widgets_list = []
                
                if is_health_request:
                    logger.info(f"Detected health/nutrition/meal plan request (message: '{chat_request.message[:50]}...'), extracting data from response")
                    # Try to extract meal plan data from the response
                    meal_plan_data = self._extract_meal_plan_data(ai_response or "", chat_request.message)
                    logger.info(f"Extracted meal plan data: {meal_plan_data}")
                    # Check for single-day format (meals), multi-day format (days), or daily calories
                    has_meals = meal_plan_data and (meal_plan_data.get("meals") and len(meal_plan_data.get("meals", [])) > 0)
                    has_days = meal_plan_data and (meal_plan_data.get("days") and len(meal_plan_data.get("days", [])) > 0)
                    has_calories = meal_plan_data and meal_plan_data.get("daily_calories")
                    if meal_plan_data and (has_meals or has_days or has_calories):
                        health_widget = {
                            "type": "health",
                            "data": meal_plan_data
                        }
                        widgets_list.append(health_widget)
                        logger.info(f"✅ Created health widget_data with meal plan (meals: {has_meals}, days: {has_days}, calories: {has_calories})")
                    
                    # If request also includes exercise/workout, extract and create separate fitness widget
                    if has_exercise_keywords:
                        logger.info(f"Request also includes exercise/workout - extracting workout data for separate fitness widget")
                        workout_data = self._extract_workout_data(ai_response or "")
                        logger.info(f"Extracted workout data: {workout_data}")
                        if workout_data and workout_data.get("exercises") and len(workout_data["exercises"]) > 0:
                            fitness_widget = {
                                "type": "fitness",
                                "data": workout_data
                            }
                            widgets_list.append(fitness_widget)
                            logger.info(f"✅ Created separate fitness widget_data with {len(workout_data['exercises'])} exercises")
                        else:
                            # Try to extract exercise info from meal plan data (exercise_calories)
                            if meal_plan_data and meal_plan_data.get("exercise_calories"):
                                # Create a minimal fitness widget with exercise calories info
                                exercise_widget_data = {
                                    "exercises": [{
                                        "name": "Daily Exercise Goal",
                                        "description": f"Aim to burn {meal_plan_data.get('exercise_calories')} calories per day through exercise",
                                        "calories_burned": meal_plan_data.get("exercise_calories")
                                    }],
                                    "plan_name": "Exercise Plan",
                                    "description": f"Daily exercise goal: Burn {meal_plan_data.get('exercise_calories')} calories per day"
                                }
                                fitness_widget = {
                                    "type": "fitness",
                                    "data": exercise_widget_data
                                }
                                widgets_list.append(fitness_widget)
                                logger.info(f"✅ Created fitness widget with exercise calories from meal plan")
                elif is_fitness_request:
                    logger.info(f"Detected workout/fitness request (message: '{chat_request.message[:50]}...'), extracting data from response")
                    # Try to extract workout plan data from the response
                    workout_data = self._extract_workout_data(ai_response or "")
                    logger.info(f"Extracted workout data: {workout_data}")
                    if workout_data and workout_data.get("exercises") and len(workout_data["exercises"]) > 0:
                        fitness_widget = {
                            "type": "fitness",
                            "data": workout_data
                        }
                        widgets_list.append(fitness_widget)
                        logger.info(f"✅ Created widget_data with {len(workout_data['exercises'])} exercises")
                
                # Set widget_data and widgets based on what we found
                if len(widgets_list) == 1:
                    # Single widget - use widget_data for backward compatibility
                    widget_data = widgets_list[0]
                    widgets = None
                elif len(widgets_list) > 1:
                    # Multiple widgets - use widgets list, set first as widget_data for compatibility
                    widget_data = widgets_list[0]
                    widgets = widgets_list
                    logger.info(f"✅ Returning {len(widgets_list)} widgets: {[w.get('type') for w in widgets_list]}")
                else:
                    widget_data = None
                    widgets = None
            
            return AIAssistantChatResponse(
                conversation_id=str(conversation.id) if conversation.id else None,
                message_id=str(ai_message.id) if ai_message.id else None,
                response=ai_response,
                token_count=token_count,
                processing_time_ms=processing_time,
                model_used=config.config_data.get('model', 'gpt-4'),
                widget_data=widget_data,
                widgets=widgets
            )
            
        except Exception as e:
            self.db.rollback()
            
            # Track failed usage
            if 'config' in locals() and config:
                self._track_usage(
                    teacher_id=teacher_id,
                    config_id=config.id,
                    usage_type=chat_request.conversation_type or "general_chat",
                    tokens_used=0,
                    processing_time_ms=0,
                    success=False,
                    error_message=str(e)
                )
            
            raise Exception(f"Failed to process AI chat request: {str(e)}")

    # ==================== TEMPLATE MANAGEMENT ====================
    
    def get_available_templates(
        self, 
        template_type: Optional[str] = None
    ) -> List[AIAssistantTemplateResponse]:
        """Get available AI assistant templates"""
        query = self.db.query(AIAssistantTemplate).filter(
            AIAssistantTemplate.is_active == True
        )
        
        if template_type:
            query = query.filter(AIAssistantTemplate.template_type == template_type)
        
        templates = query.order_by(asc(AIAssistantTemplate.template_name)).all()
        
        return [self._template_to_response(template) for template in templates]

    def use_template(
        self, 
        template_id: str, 
        variables: Dict[str, Any]
    ) -> str:
        """Use a template with variables to generate content"""
        template = self.db.query(AIAssistantTemplate).filter(
            AIAssistantTemplate.id == template_id
        ).first()
        
        if not template:
            raise Exception("Template not found")
        
        # Replace variables in template content
        content = template.template_content
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", str(value))
        
        # Update usage count
        template.usage_count += 1
        self.db.commit()
        
        return content

    # ==================== FEEDBACK MANAGEMENT ====================
    
    def submit_feedback(
        self, 
        teacher_id: str, 
        feedback_data: AIAssistantFeedbackCreate
    ) -> AIAssistantFeedbackResponse:
        """Submit feedback for an AI assistant interaction"""
        feedback = AIAssistantFeedback(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            conversation_id=feedback_data.conversation_id,
            message_id=feedback_data.message_id,
            feedback_type=feedback_data.feedback_type,
            feedback_value=feedback_data.feedback_value,
            feedback_text=feedback_data.feedback_text,
            is_helpful=feedback_data.is_helpful
        )
        
        self.db.add(feedback)
        self.db.commit()
        
        return self._feedback_to_response(feedback)

    def get_conversation_feedback(
        self, 
        conversation_id: str, 
        teacher_id: str
    ) -> List[AIAssistantFeedbackResponse]:
        """Get feedback for a conversation"""
        # Verify conversation ownership
        conversation = self.db.query(AIAssistantConversation).filter(
            and_(
                AIAssistantConversation.id == conversation_id,
                AIAssistantConversation.teacher_id == teacher_id
            )
        ).first()
        
        if not conversation:
            return []
        
        feedback = self.db.query(AIAssistantFeedback).filter(
            AIAssistantFeedback.conversation_id == conversation_id
        ).order_by(desc(AIAssistantFeedback.created_at)).all()
        
        return [self._feedback_to_response(f) for f in feedback]

    # ==================== ANALYTICS ====================
    
    def get_teacher_analytics(
        self, 
        teacher_id: str, 
        days: int = 30
    ) -> List[AIAssistantAnalyticsResponse]:
        """Get AI assistant analytics for a teacher"""
        start_date = date.today() - timedelta(days=days)
        
        analytics = self.db.query(AIAssistantAnalytics).filter(
            and_(
                AIAssistantAnalytics.teacher_id == teacher_id,
                AIAssistantAnalytics.analytics_date >= start_date
            )
        ).order_by(desc(AIAssistantAnalytics.analytics_date)).all()
        
        return [self._analytics_to_response(stat) for stat in analytics]

    def get_usage_summary(
        self, 
        teacher_id: str, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get usage summary for a teacher"""
        start_date = date.today() - timedelta(days=days)
        
        # Get total usage
        total_usage = self.db.query(
            func.sum(AIAssistantUsage.tokens_used).label('total_tokens'),
            func.sum(AIAssistantUsage.requests_count).label('total_requests'),
            func.sum(AIAssistantUsage.processing_time_ms).label('total_time'),
            func.avg(AIAssistantUsage.processing_time_ms).label('avg_time')
        ).filter(
            and_(
                AIAssistantUsage.teacher_id == teacher_id,
                AIAssistantUsage.usage_date >= start_date,
                AIAssistantUsage.success == True
            )
        ).first()
        
        # Get usage by type
        usage_by_type = self.db.query(
            AIAssistantUsage.usage_type,
            func.sum(AIAssistantUsage.requests_count).label('requests'),
            func.sum(AIAssistantUsage.tokens_used).label('tokens')
        ).filter(
            and_(
                AIAssistantUsage.teacher_id == teacher_id,
                AIAssistantUsage.usage_date >= start_date,
                AIAssistantUsage.success == True
            )
        ).group_by(AIAssistantUsage.usage_type).all()
        
        # Get satisfaction score
        satisfaction = self.db.query(
            func.avg(AIAssistantFeedback.feedback_value).label('avg_satisfaction')
        ).filter(
            and_(
                AIAssistantFeedback.teacher_id == teacher_id,
                AIAssistantFeedback.feedback_type == 'rating',
                AIAssistantFeedback.created_at >= datetime.utcnow() - timedelta(days=days)
            )
        ).scalar()
        
        return {
            "total_tokens": total_usage.total_tokens or 0,
            "total_requests": total_usage.total_requests or 0,
            "total_processing_time_ms": total_usage.total_time or 0,
            "average_response_time_ms": float(total_usage.avg_time or 0),
            "usage_by_type": {item.usage_type: {"requests": item.requests, "tokens": item.tokens} for item in usage_by_type},
            "satisfaction_score": float(satisfaction or 0),
            "period_days": days
        }

    # ==================== HELPER METHODS ====================
    
    def _get_default_config(
        self, 
        teacher_id: str, 
        conversation_type: str
    ) -> AIAssistantConfig:
        """Get or create default configuration for a teacher"""
        # Map conversation_type to assistant_type (database constraint uses 'general_assistant' not 'general_chat')
        assistant_type_map = {
            "general_chat": "general_assistant",
            "lesson_planning": "lesson_planning",
            "assessment_creation": "assessment_creation",
            "resource_generation": "resource_generation",
            "content_analysis": "content_analysis"
        }
        assistant_type = assistant_type_map.get(conversation_type, conversation_type)
        
        config = self.db.query(AIAssistantConfig).filter(
            and_(
                AIAssistantConfig.teacher_id == teacher_id,
                AIAssistantConfig.assistant_type == assistant_type,
                AIAssistantConfig.is_active == True
            )
        ).first()
        
        if not config:
            # Create default config with comprehensive system prompt
            # Import the enhanced system prompt (same as guest_chat.py and gpt_function_service.py)
            from app.core.ai_system_prompts import ENHANCED_SYSTEM_PROMPT
            comprehensive_system_prompt = ENHANCED_SYSTEM_PROMPT
            
            default_config_data = {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000,
                "system_prompt": comprehensive_system_prompt
            }
            
            config = AIAssistantConfig(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                config_name=f"Default {assistant_type.replace('_', ' ').title()} Config",
                config_description=f"Default configuration for {assistant_type.replace('_', ' ')}",
                assistant_type=assistant_type,
                is_active=True,
                config_data=default_config_data
            )
            
            self.db.add(config)
            self.db.commit()
        
        return config

    def _track_usage(
        self, 
        teacher_id: str, 
        config_id: str,
        usage_type: str,
        tokens_used: int,
        processing_time_ms: int,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """Track AI assistant usage"""
        usage = AIAssistantUsage(
            id=str(uuid.uuid4()),
            teacher_id=teacher_id,
            config_id=config_id,
            usage_type=usage_type,
            tokens_used=tokens_used,
            requests_count=1,
            processing_time_ms=processing_time_ms,
            success=success,
            error_message=error_message
        )
        
        self.db.add(usage)
        
        # Update daily analytics
        self._update_daily_analytics(teacher_id, usage_type, tokens_used, processing_time_ms, success)

    def _update_daily_analytics(
        self, 
        teacher_id: str, 
        usage_type: str,
        tokens_used: int,
        processing_time_ms: int,
        success: bool
    ) -> None:
        """Update daily analytics for AI assistant usage"""
        today = date.today()
        
        analytics = self.db.query(AIAssistantAnalytics).filter(
            and_(
                AIAssistantAnalytics.teacher_id == teacher_id,
                AIAssistantAnalytics.analytics_date == today
            )
        ).first()
        
        if analytics:
            # Update existing analytics
            analytics.total_requests += 1
            analytics.total_tokens_used += tokens_used
            analytics.total_processing_time_ms += processing_time_ms
            
            if success:
                analytics.successful_requests += 1
            else:
                analytics.failed_requests += 1
            
            analytics.average_response_time_ms = analytics.total_processing_time_ms / analytics.total_requests
            analytics.updated_at = datetime.utcnow()
        else:
            # Create new analytics
            analytics = AIAssistantAnalytics(
                id=str(uuid.uuid4()),
                teacher_id=teacher_id,
                analytics_date=today,
                total_requests=1,
                successful_requests=1 if success else 0,
                failed_requests=0 if success else 1,
                total_tokens_used=tokens_used,
                total_processing_time_ms=processing_time_ms,
                average_response_time_ms=processing_time_ms,
                most_used_type=usage_type
            )
            
            self.db.add(analytics)
        
        self.db.commit()

    # ==================== RESPONSE CONVERTERS ====================
    
    def _config_to_response(self, config: AIAssistantConfig) -> AIAssistantConfigResponse:
        """Convert config model to response"""
        return AIAssistantConfigResponse(
            id=str(config.id) if config.id else None,
            teacher_id=str(config.teacher_id) if config.teacher_id else None,
            config_name=config.config_name,
            config_description=config.config_description,
            assistant_type=config.assistant_type,
            is_active=config.is_active,
            config_data=config.config_data,
            created_at=config.created_at,
            updated_at=config.updated_at
        )

    def _conversation_to_response(self, conversation: AIAssistantConversation) -> AIAssistantConversationResponse:
        """Convert conversation model to response"""
        return AIAssistantConversationResponse(
            id=str(conversation.id) if conversation.id else None,
            teacher_id=str(conversation.teacher_id) if conversation.teacher_id else None,
            config_id=str(conversation.config_id) if conversation.config_id else None,
            conversation_title=conversation.conversation_title,
            conversation_type=conversation.conversation_type,
            is_active=conversation.is_active,
            metadata=conversation.metadata,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )

    def _message_to_response(self, message: AIAssistantMessage) -> AIAssistantMessageResponse:
        """Convert message model to response"""
        return AIAssistantMessageResponse(
            id=str(message.id) if message.id else None,
            conversation_id=str(message.conversation_id) if message.conversation_id else None,
            message_type=message.message_type,
            content=message.content,
            metadata=message.metadata,
            token_count=message.token_count,
            processing_time_ms=message.processing_time_ms,
            created_at=message.created_at
        )

    def _template_to_response(self, template: AIAssistantTemplate) -> AIAssistantTemplateResponse:
        """Convert template model to response"""
        return AIAssistantTemplateResponse(
            id=str(template.id) if template.id else None,
            template_name=template.template_name,
            template_description=template.template_description,
            template_type=template.template_type,
            template_content=template.template_content,
            template_variables=template.template_variables,
            is_system_template=template.is_system_template,
            is_active=template.is_active,
            usage_count=template.usage_count,
            created_at=template.created_at,
            updated_at=template.updated_at
        )

    def _feedback_to_response(self, feedback: AIAssistantFeedback) -> AIAssistantFeedbackResponse:
        """Convert feedback model to response"""
        return AIAssistantFeedbackResponse(
            id=str(feedback.id) if feedback.id else None,
            teacher_id=str(feedback.teacher_id) if feedback.teacher_id else None,
            conversation_id=str(feedback.conversation_id) if feedback.conversation_id else None,
            message_id=str(feedback.message_id) if feedback.message_id else None,
            feedback_type=feedback.feedback_type,
            feedback_value=feedback.feedback_value,
            feedback_text=feedback.feedback_text,
            is_helpful=feedback.is_helpful,
            created_at=feedback.created_at
        )

    def _analytics_to_response(self, analytics: AIAssistantAnalytics) -> AIAssistantAnalyticsResponse:
        """Convert analytics model to response"""
        return AIAssistantAnalyticsResponse(
            id=str(analytics.id) if analytics.id else None,
            teacher_id=str(analytics.teacher_id) if analytics.teacher_id else None,
            analytics_date=analytics.analytics_date,
            total_requests=analytics.total_requests,
            successful_requests=analytics.successful_requests,
            failed_requests=analytics.failed_requests,
            total_tokens_used=analytics.total_tokens_used,
            total_processing_time_ms=analytics.total_processing_time_ms,
            average_response_time_ms=analytics.average_response_time_ms,
            most_used_type=analytics.most_used_type,
            satisfaction_score=analytics.satisfaction_score,
            created_at=analytics.created_at,
            updated_at=analytics.updated_at
        )
