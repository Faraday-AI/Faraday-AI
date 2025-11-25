"""
Allergy Detection Utility

Detects if a user message contains allergy information or dietary restrictions.
Used for multi-step meal plan workflows where Jasper needs to identify allergy answers.
"""

import logging

logger = logging.getLogger(__name__)


def detect_allergy_answer(message: str) -> bool:
    """
    Detect if a user message is an allergy answer.
    
    Returns True if the message contains allergy information or
    dietary restrictions, otherwise False.
    
    Examples:
        >>> detect_allergy_answer("he is allergic to tree nuts")
        True
        >>> detect_allergy_answer("student has no allergies")
        True
        >>> detect_allergy_answer("I avoid peanuts and shellfish")
        True
        >>> detect_allergy_answer("none")
        True
        >>> detect_allergy_answer("I need a meal plan")
        False
    """
    if not message:
        return False
    
    msg_lower = message.lower().strip()
    
    # Common keywords
    allergy_keywords = [
        "allerg", "allergic", "dietary", "restriction", "avoid",
        "tree nuts", "tree nut", "peanuts", "peanut", "shellfish",
        "dairy", "eggs", "soy", "wheat", "gluten",
        "fish", "sesame", "milk", "lactose", "celiac",
        "nuts", "nut", "intolerant", "intolerance"
    ]
    
    # Common phrases
    allergy_phrases = [
        "i am allergic", "i'm allergic", "i have an allergy", "i have allergies",
        "allergic to", "allergy to", "i avoid", "i can't eat", "i cannot eat",
        "no allergies", "no allerg", "not allergic", "no restrictions",
        "student is allergic", "he is allergic", "she is allergic", "they are allergic",
        "the student is allergic", "the student has an allergy", "student has allergies",
        "is allergic to", "has an allergy", "has allergies"
    ]
    
    # Check for keywords or phrases
    contains_keyword = any(keyword in msg_lower for keyword in allergy_keywords)
    contains_phrase = any(phrase in msg_lower for phrase in allergy_phrases)
    
    # Short answers like "none" or "no" might indicate no allergies
    short_no_answer = msg_lower in ["none", "no", "nothing", "no allergies", "no restrictions"]
    
    # Consider as allergy answer if keywords/phrases present or short answer
    is_allergy_answer = contains_keyword or contains_phrase or short_no_answer
    
    if is_allergy_answer:
        logger.debug(f"🔍 Detected allergy answer: '{message[:100]}...'")
    
    return is_allergy_answer

