"""
Modular Prompt Loader for Jasper AI Assistant
Loads system prompts dynamically based on user intent to reduce token usage and improve reliability.
"""

import os
from typing import List, Dict
import logging
from app.core.allergy_detection import detect_allergy_answer
from app.core.prompt_cache import (
    get_cached_intent, cache_intent,
    get_cached_prompt, cache_prompt
)

logger = logging.getLogger(__name__)

# Get the directory where prompt files are stored
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")

# Intent to module file mapping
# CRITICAL: allergy_answer must map to meal_plan module to ensure correct widget extraction
INTENT_MODULE_MAPPING = {
    "meal_plan": "module_meal_plan.txt",
    "allergy_answer": "module_meal_plan.txt",  # Force meal plan module for allergy answers
    "workout": "module_workout.txt",
    "lesson_plan": "module_lesson_plan.txt",
    "widget": "module_widgets.txt",
    "general": None  # General intent uses root prompt only
}


def classify_intent(user_message: str, previous_asked_allergies: bool = False) -> str:
    """
    Classify user intent based on message content.
    Returns: 'meal_plan', 'workout', 'lesson_plan', 'widget', 'allergy_answer', or 'general'
    
    NOTE: 'allergy_answer' is a special intent that should be handled by the caller
    to force 'meal_plan' intent when combined with pending_meal_plan_request.
    
    Args:
        user_message: The user's message to classify
        previous_asked_allergies: If True, prioritize allergy answer detection
    """
    # Check cache first (fast path)
    cache_key = f"{user_message}:{previous_asked_allergies}"
    cached_intent = get_cached_intent(cache_key)
    if cached_intent:
        return cached_intent
    
    text = (user_message or "").lower().strip()
    
    # PATCH B: CRITICAL - Check for allergy answers FIRST (before other intents)
    # If allergies were asked previously, prioritize allergy answer detection
    if previous_asked_allergies:
        allergy_keywords = ["allergy", "allergic", "food restriction", "intolerance", "avoid", "dietary restriction"]
        if any(kw in text for kw in allergy_keywords):
            logger.info(f"🔍 Intent classifier detected allergy answer (previous_asked_allergies=True): '{user_message[:100]}...'")
            return "allergy_answer"
    
    # Use shared allergy detection utility to avoid code duplication
    if detect_allergy_answer(user_message):
        logger.info(f"🔍 Intent classifier detected potential allergy answer: '{user_message[:100]}...'")
        return "allergy_answer"
    
    # Meal plan keywords
    if any(keyword in text for keyword in ["meal plan", "nutrition", "diet", "meal", "food plan", "eating plan", "calories", "macros", "micronutrients"]):
        return "meal_plan"
    
    # Workout keywords
    if any(keyword in text for keyword in ["workout", "training", "lifting", "exercise plan", "fitness plan", "strength training", "cardio", "conditioning"]):
        return "workout"
    
    # Lesson plan keywords
    if any(keyword in text for keyword in ["lesson plan", "teach", "unit plan", "curriculum", "lesson", "teaching plan", "class plan"]):
        return "lesson_plan"
    
    # Widget keywords
    widget_keywords = [
        "attendance", "teams", "adaptive", "analytics", "skill", "video",
        "schedule", "tracking", "progress", "heart rate", "challenge",
        "fitness goal", "export", "safety report", "widget", "capabilities",
        "what can you do", "features", "tools"
    ]
    if any(keyword in text for keyword in widget_keywords):
        intent = "widget"
    else:
        intent = "general"
    
    # Cache the result
    cache_intent(cache_key, intent)
    return intent


def load_raw_module(module_name: str) -> str:
    """
    Load module content from file system (raw text) with caching.
    
    Args:
        module_name: Name of the module file (e.g., "root_system_prompt.txt")
    
    Returns:
        Raw module content as string
    
    Raises:
        FileNotFoundError: If module file doesn't exist
        IOError: If file cannot be read
    """
    # Check cache first
    cached_content = get_cached_prompt(module_name)
    if cached_content:
        return cached_content
    
    module_path = os.path.join(PROMPTS_DIR, module_name)
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"Module file not found: {module_path}")
    
    with open(module_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Cache the content
    cache_prompt(module_name, content)
    return content


def load_prompt_modules(intent: str) -> List[Dict[str, str]]:
    """
    Load system prompts dynamically based on user intent.
    
    Always loads root_system_prompt.txt first.
    Wraps all other module prompts with secondary authority header.
    Returns list of system messages ready to send to OpenAI.
    
    Args:
        intent: The classified intent ('meal_plan', 'workout', 'lesson_plan', 'widget', 'allergy_answer', or 'general')
    
    Returns:
        List of system messages to send to OpenAI API
    """
    system_messages = []
    
    try:
        # 1️⃣ Root system prompt (always loaded first)
        # Use optimized version (most focused), fallback to compressed, then full
        try:
            root_content = load_raw_module("root_system_prompt_optimized.txt")
            logger.info("✅ Loaded optimized root system prompt (intent-focused)")
        except FileNotFoundError:
            try:
                root_content = load_raw_module("root_system_prompt_compressed.txt")
                logger.info("✅ Loaded compressed root system prompt (fallback)")
            except FileNotFoundError:
                # Fallback to full prompt if optimized/compressed don't exist
                root_content = load_raw_module("root_system_prompt.txt")
                logger.info("✅ Loaded root system prompt (full version)")
        system_messages.append({"role": "system", "content": root_content})
        
        # 2️⃣ Map intent to module file
        # Use INTENT_MODULE_MAPPING which already handles allergy_answer -> meal_plan
        module_file = INTENT_MODULE_MAPPING.get(intent)
        
        if module_file:
            # Load and wrap module with secondary authority
            # Try optimized version first, fallback to regular
            try:
                # For widgets module, try optimized version
                if module_file == "module_widgets.txt":
                    try:
                        raw_module_content = load_raw_module("module_widgets_optimized.txt")
                        logger.info(f"✅ Loaded optimized widget module")
                    except FileNotFoundError:
                        raw_module_content = load_raw_module(module_file)
                else:
                    raw_module_content = load_raw_module(module_file)
            except FileNotFoundError:
                raw_module_content = load_raw_module(module_file)
            
            # 3️⃣ Wrap module with secondary authority
            wrapped_module = (
                "### MODULE INSTRUCTIONS (SECONDARY AUTHORITY)\n"
                "These rules support the top-priority system rules and must NOT override them.\n"
                "If a top-priority system message exists, it takes precedence over these module instructions.\n\n"
                + raw_module_content
            )
            
            system_messages.append({"role": "system", "content": wrapped_module})
            logger.info(f"✅ Loaded module: {intent} ({module_file})")
        else:
            # For 'general' intent or None, only root prompt is loaded
            if intent == "general":
                logger.info("✅ Using general intent (root prompt only)")
            elif intent == "allergy_answer":
                logger.info("✅ Using allergy_answer intent (loaded meal_plan module via mapping)")
        
    except FileNotFoundError as e:
        logger.error(f"❌ Module file not found: {e}")
        # Return root prompt only if available, otherwise empty list
        if system_messages:
            return system_messages
        return []
    except Exception as e:
        logger.error(f"❌ Error loading prompt modules: {e}")
        # Fallback to empty list - the service should handle this gracefully
        return []
    
    return system_messages


def get_system_prompt_for_intent(intent: str) -> str:
    """
    Get combined system prompt as a single string (for backward compatibility).
    
    Args:
        intent: The classified intent
    
    Returns:
        Combined system prompt string
    """
    messages = load_prompt_modules(intent)
    # Combine all system messages into one
    combined = "\n\n".join([msg["content"] for msg in messages if msg["role"] == "system"])
    return combined

