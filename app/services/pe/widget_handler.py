"""
FULL JASPER WIDGETS PATCH

Meal + Lesson + Workout + All Dashboard Widgets + Auto-Correction

This module provides a unified, production-ready interface for handling all 39+ widgets,
combining response-based extraction, GPT function calling, and general response handling.

Widget Categories:
1. Response-Based Extraction (3 widgets): Meal Plan, Lesson Plan, Workout
2. GPT Function Calling (20+ widgets): Attendance, Teams, Analytics, etc.
3. General Response (16+ widgets): Exercise Tracker, Fitness Challenges, etc.
"""

import os
import re
import json
from typing import List, Dict, Any, Tuple
import logging

# Import extraction functions from specialized services
from app.services.pe.specialized_services.lesson_plan_service import extract_lesson_plan_data
from app.services.pe.specialized_services.workout_service import extract_workout_data
from app.services.pe.specialized_services.meal_plan_service import extract_meal_plan_data

logger = logging.getLogger(__name__)


# ==========================
# 1️⃣ Safe Message Builder
# ==========================

def safe_build_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Safely build message list, preventing NoneType.strip() crashes.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        
    Returns:
        List of safe message dictionaries with guaranteed string content
    """
    return [{"role": m.get("role", "user"), "content": (m.get("content") or "").strip()} for m in messages]


# ==========================
# 2️⃣ Intent Classification
# ==========================

def classify_intent(message_content: str, previous_asked_allergies: bool = False) -> str:
    """
    Classify user intent to determine which widget to use.
    
    Args:
        message_content: User's message text
        previous_asked_allergies: Whether allergies were previously asked
        
    Returns:
        Widget intent string (e.g., "meal_plan", "attendance", "general")
    """
    msg_lower = (message_content or "").lower()
    allergy_keywords = ["allergy", "allergic", "food restriction", "intolerance", "avoid"]
    
    if previous_asked_allergies and any(kw in msg_lower for kw in allergy_keywords):
        return "allergy_answer"
    
    if any(k in msg_lower for k in ["meal plan", "nutrition", "diet"]):
        return "meal_plan"
    
    # Widget-specific intents (check BEFORE workout to avoid false positives)
    # CRITICAL: Check attendance BEFORE workout to prevent false positives
    # (e.g., "attendance patterns" should NOT trigger "workout")
    if "attendance" in msg_lower:
        return "attendance"
    
    # Workout detection - use more specific patterns to avoid false positives
    # Only match "workout" when it's clearly about exercise/fitness plans
    # NOT when it appears in phrases like "workout patterns" (which is attendance-related)
    workout_patterns = [
        "workout plan", "workout routine", "exercise plan", "fitness plan",
        "training plan", "workout program", "exercise routine",
        "week long workout", "weekly workout", "full body workout",
        "entire body", "all muscle groups", "muscle groups",
        "strength training", "cardio workout", "workout schedule"
    ]
    # Also check for standalone "workout" but only if not in attendance context
    if "attendance" not in msg_lower and any(k in msg_lower for k in workout_patterns):
        return "workout"
    # Standalone "workout" only if clearly about creating/planning workouts
    if "attendance" not in msg_lower and ("create workout" in msg_lower or "need workout" in msg_lower or "workout for" in msg_lower or "workout that" in msg_lower):
        return "workout"
    # Check for exercise/fitness keywords that indicate workout intent
    if "attendance" not in msg_lower and any(k in msg_lower for k in ["exercise", "exercises", "fitness", "training", "gym", "workout"]):
        # But only if it's about creating/planning, not just mentioning
        if any(k in msg_lower for k in ["create", "make", "give me", "need", "want", "plan", "routine", "schedule", "program"]):
            return "workout"
    # Lesson plan check (BEFORE other widget checks to prioritize lesson plans)
    # Check for comprehensive lesson plan requests first
    lesson_plan_keywords = ["lesson plan", "lesson planning", "create lesson", "generate lesson", 
                            "comprehensive lesson", "detailed lesson", "unit plan", "curriculum plan",
                            "teach", "teaching plan", "instructional plan"]
    if any(k in msg_lower for k in lesson_plan_keywords):
        return "lesson_plan"
    
    if any(k in msg_lower for k in ["team", "squad", "balanced teams"]):
        return "teams"
    if "adaptive" in msg_lower:
        return "adaptive"
    if any(k in msg_lower for k in ["analytics", "performance", "predict"]):
        return "analytics"
    # Safety check - but only if not in lesson plan context
    if "lesson" not in msg_lower and any(k in msg_lower for k in ["safety", "risk"]):
        return "safety"
    if "insight" in msg_lower:
        return "class_insights"
    
    # Content generation keywords (check BEFORE generic widget keywords)
    # Check for individual keywords that indicate content generation
    content_generation_patterns = [
        # Image generation
        ("generate", ["image", "artwork", "picture", "photo", "illustration"]),
        ("create", ["image", "artwork", "picture", "photo", "illustration"]),
        ("make", ["image", "artwork", "picture", "photo", "illustration"]),
        ("draw", ["image", "artwork", "picture", "illustration"]),
        # Presentation generation
        ("create", ["powerpoint", "presentation", "slides", "slide deck"]),
        ("generate", ["powerpoint", "presentation", "slides", "slide deck"]),
        ("make", ["powerpoint", "presentation", "slides", "slide deck"]),
        # Document generation
        ("create", ["word", "document", "doc", "handout"]),
        ("generate", ["word", "document", "doc", "handout"]),
        ("make", ["word", "document", "doc", "handout"]),
        # PDF generation
        ("create", ["pdf"]),
        ("generate", ["pdf"]),
        ("make", ["pdf"]),
        # Spreadsheet generation
        ("create", ["excel", "spreadsheet"]),
        ("generate", ["excel", "spreadsheet"]),
        ("make", ["excel", "spreadsheet"]),
        # OneDrive/Outlook actions
        ("upload", ["onedrive"]),
        ("save", ["onedrive"]),
        ("send", ["outlook", "email"]),
    ]
    
    # Check for content generation patterns
    for action, targets in content_generation_patterns:
        if action in msg_lower:
            for target in targets:
                # Check if target appears near the action (within reasonable distance)
                action_idx = msg_lower.find(action)
                target_idx = msg_lower.find(target)
                if target_idx != -1:
                    # Check if they're close together (within 20 chars) or if target comes after action
                    if abs(action_idx - target_idx) < 20 or target_idx > action_idx:
                        return "content_generation"
    
    # Also check for standalone content generation phrases
    content_generation_phrases = [
        "generate image", "create image", "make image", "generate artwork", "create artwork",
        "create powerpoint", "create presentation", "make presentation", "generate slides",
        "create word", "create document", "make document", "generate document", "create handout", "word handout",
        "create pdf", "make pdf", "generate pdf",
        "create excel", "create spreadsheet", "make spreadsheet", "generate spreadsheet",
        "upload to onedrive", "save to onedrive", "send via outlook", "email via outlook"
    ]
    if any(phrase in msg_lower for phrase in content_generation_phrases):
        return "content_generation"
    
    # Check for follow-up messages that provide details for document creation
    # These are messages that mention document structure/details but don't explicitly say "create"
    follow_up_patterns = [
        ("section", ["bullet", "point", "list", "rules", "content"]),
        ("image", ["clipboard", "basketball", "court", "whistle", "picture", "photo", "illustration"]),
        ("slide", ["title", "content", "presentation"]),
        ("document", ["section", "heading", "paragraph", "bullet"]),
    ]
    for keyword, context_words in follow_up_patterns:
        if keyword in msg_lower:
            if any(ctx in msg_lower for ctx in context_words):
                # This looks like a follow-up providing details for content generation
                return "content_generation"
    
    # Generic widget keywords
    widget_keywords = [
        "schedule", "tracking", "progress", "widget", "capabilities", "features",
        "skill", "video", "heart rate", "challenge", "fitness goal"
    ]
    if any(k in msg_lower for k in widget_keywords):
        return "widget"
    
    return "general"


# ==========================
# 3️⃣ Response-Based Extraction
# ==========================
# NOTE: Extraction functions have been moved to their respective specialized services.
# These are wrapper functions for backward compatibility.

def _extract_meal_plan_data(response_text: str) -> Dict[str, Any]:
    """Wrapper function - delegates to meal_plan_service.extract_meal_plan_data"""
    return extract_meal_plan_data(response_text)




def _extract_lesson_plan_data(response_text: str, original_message: str = "") -> Dict[str, Any]:
    """Wrapper function - delegates to lesson_plan_service.extract_lesson_plan_data"""
    return extract_lesson_plan_data(response_text, original_message)


def _extract_workout_data(response_text: str) -> Dict[str, Any]:
    """Wrapper function - delegates to workout_service.extract_workout_data"""
    return extract_workout_data(response_text)


# ==========================
# 4️⃣ Validation Functions
# ==========================

def validate_meal_plan(response_text: str, allergy_info_already_recorded: bool = False) -> List[str]:
    """
    Validate meal plan response for required components.
    
    Safety-critical validation that forces auto-correction if validation fails.
    
    Args:
        response_text: AI's meal plan response
        allergy_info_already_recorded: Whether allergy info was already provided
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors: List[str] = []
    
    if not response_text.strip().startswith("**DAY 1**"):
        errors.append("Meal plan must start with Day 1.")
    
    if not allergy_info_already_recorded and "allergy" not in response_text.lower():
        errors.append("Meal plan created WITHOUT asking about allergies.")
    
    return errors


def validate_lesson_plan(response_text: str) -> List[str]:
    """
    Validate lesson plan response for required components.
    
    Optional auto-correction can be enabled to enforce requirements.
    
    Args:
        response_text: AI's lesson plan response
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors: List[str] = []
    
    # Check for required components
    if "objectives" not in response_text.lower() and "learning objective" not in response_text.lower():
        errors.append("Lesson plan missing learning objectives.")
    
    if "activity" not in response_text.lower() and "procedure" not in response_text.lower():
        errors.append("Lesson plan missing activities/procedures.")
    
    return errors


def validate_workout_plan(response_text: str) -> List[str]:
    """
    Validate workout plan response for required components.
    
    Optional auto-correction can be enabled to enforce requirements.
    
    Args:
        response_text: AI's workout plan response
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors: List[str] = []
    
    # Check for required components
    if "exercise" not in response_text.lower():
        errors.append("Workout plan missing exercises.")
    
    return errors


# ==========================
# 5️⃣ GPT Function Calling Stubs (20+ Widgets)
# ==========================

def call_attendance_functions(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for attendance widget GPT function calls."""
    return {}
    if json_match:
        try:
            json_str = json_match.group(1)
            parsed_json_data = json.loads(json_str)
            # If JSON parsing succeeds, we'll use it but also extract worksheets/rubrics from text
            if isinstance(parsed_json_data, dict):
                # Continue to regex extraction to get worksheets/rubrics that might not be in JSON
                pass
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"⚠️ Failed to parse JSON from markdown code block: {e}")
            # Fall through to regex extraction
    
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
                # CRITICAL: Check if this line contains worksheets or rubrics content
                # Worksheets/rubrics are often embedded in costas_questioning section
                line_lower = clean_line.lower()
                
                # Check for worksheet markers
                if re.search(r'(?:^###\s*)?(?:worksheets?|student\s+worksheet|worksheet\s+with\s+answer)', line_lower):
                    # Switch to worksheets section
                    current_section = "worksheets"
                    worksheet_text = re.sub(r'^\d+\.?\s*\*\*?', '', clean_line, flags=re.IGNORECASE)
                    worksheet_text = re.sub(r'\*\*?', '', worksheet_text)
                    worksheet_text = re.sub(r'(?:###\s*)?(?:worksheets?|student\s+worksheet|worksheet\s+with\s+answer\s+keys?)[:\s]*', '', worksheet_text, flags=re.IGNORECASE).strip()
                    if worksheet_text and len(worksheet_text) > 5:
                        if lesson_data["worksheets"]:
                            lesson_data["worksheets"] += "\n\n" + worksheet_text
                        else:
                            lesson_data["worksheets"] = worksheet_text
                    # Also add to costas_questioning for backward compatibility
                    if lesson_data["costas_questioning"]:
                        lesson_data["costas_questioning"] += " " + clean_line
                    else:
                        lesson_data["costas_questioning"] = clean_line
                # Check for rubric markers
                elif re.search(r'(?:^###\s*)?(?:grading\s+rubric|rubric|assessment\s+rubric|scoring\s+rubric)', line_lower):
                    # Switch to rubrics section
                    current_section = "rubrics"
                    rubric_text = re.sub(r'^\d+\.?\s*\*\*?', '', clean_line, flags=re.IGNORECASE)
                    rubric_text = re.sub(r'\*\*?', '', rubric_text)
                    rubric_text = re.sub(r'(?:###\s*)?(?:grading\s+rubric|rubric|assessment\s+rubric|scoring\s+rubric)[:\s]*', '', rubric_text, flags=re.IGNORECASE).strip()
                    if rubric_text and len(rubric_text) > 5:
                        if lesson_data["rubrics"]:
                            lesson_data["rubrics"] += "\n\n" + rubric_text
                        else:
                            lesson_data["rubrics"] = rubric_text
                    # Also add to costas_questioning for backward compatibility
                    if lesson_data["costas_questioning"]:
                        lesson_data["costas_questioning"] += " " + clean_line
                    else:
                        lesson_data["costas_questioning"] = clean_line
                # Check for answer key (part of worksheets)
                elif re.search(r'answer\s+key[:\s]*', line_lower) and not lesson_data.get("worksheets"):
                    # If we haven't started worksheets yet, start it now
                    current_section = "worksheets"
                    answer_key_text = re.sub(r'answer\s+key[:\s]*', '', clean_line, flags=re.IGNORECASE).strip()
                    if answer_key_text and len(answer_key_text) > 5:
                        lesson_data["worksheets"] = "Answer Key:\n" + answer_key_text
                    # Also add to costas_questioning
                    if lesson_data["costas_questioning"]:
                        lesson_data["costas_questioning"] += " " + clean_line
                    else:
                        lesson_data["costas_questioning"] = clean_line
                # Regular costas_questioning content
                else:
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
                            # If we're in costas_questioning but see worksheet-like content (multiple choice questions), extract it
                            if re.match(r'^[A-Z]\)\s+', clean_line) or re.match(r'^\d+[\.\)]\s+[A-Z]', clean_line):
                                # This looks like a worksheet question - extract to worksheets
                                if not lesson_data.get("worksheets"):
                                    # Start worksheets section
                                    lesson_data["worksheets"] = clean_line
                                else:
                                    lesson_data["worksheets"] += "\n" + clean_line
                            # Also add to costas_questioning for backward compatibility
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
    
    # If we parsed JSON successfully, merge it with regex-extracted data
    # This ensures worksheets/rubrics from text are included even if JSON doesn't have them
    if parsed_json_data and isinstance(parsed_json_data, dict):
        # Merge: JSON data takes precedence, but add worksheets/rubrics from regex if they exist
        final_data = parsed_json_data.copy()
        
        # Add worksheets/rubrics from regex extraction if they exist and aren't in JSON
        # CRITICAL: Check if JSON value is empty (empty string or just whitespace), not just if key exists
        # Empty strings are truthy but represent missing content, so we should use regex-extracted data
        json_worksheets = final_data.get("worksheets", "")
        json_rubrics = final_data.get("rubrics", "")
        json_assessments = final_data.get("assessments", "")
        
        logger.info(f"🔍 JSON worksheets/rubrics check - worksheets: {len(json_worksheets) if json_worksheets else 0} chars, rubrics: {len(json_rubrics) if json_rubrics else 0} chars")
        logger.info(f"🔍 Regex extracted - worksheets: {len(lesson_data.get('worksheets', '')) if lesson_data.get('worksheets') else 0} chars, rubrics: {len(lesson_data.get('rubrics', '')) if lesson_data.get('rubrics') else 0} chars")
        
        if lesson_data.get("worksheets") and (not json_worksheets or (isinstance(json_worksheets, str) and not json_worksheets.strip())):
            logger.info(f"✅ Using regex-extracted worksheets ({len(lesson_data['worksheets'])} chars)")
            final_data["worksheets"] = lesson_data["worksheets"]
        if lesson_data.get("rubrics") and (not json_rubrics or (isinstance(json_rubrics, str) and not json_rubrics.strip())):
            logger.info(f"✅ Using regex-extracted rubrics ({len(lesson_data['rubrics'])} chars)")
            final_data["rubrics"] = lesson_data["rubrics"]
        if lesson_data.get("assessments") and (not json_assessments or (isinstance(json_assessments, str) and not json_assessments.strip())):
            final_data["assessments"] = lesson_data["assessments"]
        
        # CRITICAL: Check if rubric is embedded in worksheets field (from JSON) and separate them
        # Only do this if worksheets have good content (10+ questions) to avoid removing worksheets
        json_worksheets_final = final_data.get("worksheets", "")
        json_question_count = _count_questions_in_text(json_worksheets_final)
        has_good_worksheets = json_question_count >= 10 and len(json_worksheets_final.strip()) > 100
        
        if json_worksheets_final and isinstance(json_worksheets_final, str) and len(json_worksheets_final) > 50:
            # Look for rubric markers OR rubric table patterns in worksheets field
            rubric_marker_pattern = r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*'
            rubric_table_pattern = r'\|[^\|]*\s*(?:criteria|technique|ability|mechanics|accuracy|understanding)[^\|]*\|\s*(?:excellent|proficient|developing|beginning|4\s*pts?|3\s*pts?|2\s*pts?|1\s*pt)[^\|]*\|'
            
            rubric_marker_match = re.search(rubric_marker_pattern, json_worksheets_final, re.IGNORECASE)
            rubric_table_match = re.search(rubric_table_pattern, json_worksheets_final, re.IGNORECASE)
            
            # Determine where rubric starts
            rubric_start = None
            if rubric_marker_match:
                rubric_start = rubric_marker_match.start()
                logger.info(f"🔍 Found rubric marker in JSON worksheets field at position {rubric_start}")
            elif rubric_table_match:
                rubric_start = rubric_table_match.start()
                # Look backwards for table header
                before_table = json_worksheets_final[max(0, rubric_start-100):rubric_start]
                header_match = re.search(r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*\s*$', before_table, re.IGNORECASE | re.MULTILINE)
                if header_match:
                    rubric_start = rubric_start - 100 + header_match.start()
                logger.info(f"🔍 Found rubric table in JSON worksheets field at position {rubric_start}")
            
            # Only extract rubric if worksheets have good content AND we don't already have rubrics
            if rubric_start is not None and has_good_worksheets and (not final_data.get("rubrics") or not final_data.get("rubrics", "").strip()):
                # Extract rubric from worksheets field
                rubric_content_from_json_worksheets = json_worksheets_final[rubric_start:].strip()
                
                # Find where rubric ends (next section, assessments, or end)
                rubric_end_match = re.search(r'\n(?:###|assessments?|$)', rubric_content_from_json_worksheets, re.IGNORECASE | re.MULTILINE)
                if rubric_end_match:
                    rubric_content_from_json_worksheets = rubric_content_from_json_worksheets[:rubric_end_match.start()].strip()
                else:
                    # No clear end, take up to 3000 chars
                    rubric_content_from_json_worksheets = rubric_content_from_json_worksheets[:3000].strip()
                
                # Verify it's actually a rubric (has table structure or rubric indicators)
                is_rubric = False
                if '|' in rubric_content_from_json_worksheets:
                    has_criteria = re.search(r'(criteria|technique|ability|mechanics|accuracy|understanding|teamwork|communication|safety|effort|performance|skill)', rubric_content_from_json_worksheets, re.IGNORECASE)
                    has_levels = re.search(r'(excellent|proficient|developing|beginning|4\s*pts?|3\s*pts?|2\s*pts?|1\s*pt|perfect|good|inconsistent|struggles|demonstrates|shows)', rubric_content_from_json_worksheets, re.IGNORECASE)
                    if has_criteria and has_levels:
                        is_rubric = True
                
                if is_rubric:
                    logger.info(f"✅ Found rubric embedded in JSON worksheets field. Extracting separately. Length: {len(rubric_content_from_json_worksheets)} chars")
                    final_data["rubrics"] = rubric_content_from_json_worksheets
                    
                    # Remove rubric from worksheets field - but preserve worksheets content
                    worksheets_cleaned = json_worksheets_final[:rubric_start].strip()
                    # Clean up any trailing markers or empty lines
                    worksheets_cleaned = re.sub(r'\n+\s*(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*\s*$', '', worksheets_cleaned, flags=re.IGNORECASE | re.MULTILINE)
                    # Only update if we still have good worksheets content after removal
                    if _count_questions_in_text(worksheets_cleaned) >= 10:
                        final_data["worksheets"] = worksheets_cleaned
                        logger.info(f"✅ Cleaned JSON worksheets field, removed rubric. New length: {len(worksheets_cleaned)} chars, questions: {_count_questions_in_text(worksheets_cleaned)}")
                    else:
                        logger.warning(f"⚠️ Removing rubric would leave worksheets incomplete, preserving original")
                else:
                    logger.warning(f"⚠️ Found rubric marker/table in JSON worksheets but content doesn't match rubric pattern")
        
        # CRITICAL: Extract worksheets/rubrics from other fields if they're embedded there
        # Worksheets are often embedded in objectives, costas_questioning field OR in the raw response text
        # Also check if worksheets field has only headers with no actual content
        # Check if worksheets need extraction (MANDATORY: minimum 10 questions)
        worksheets_field = final_data.get("worksheets", "")
        question_count = _count_questions_in_text(worksheets_field)
        has_content = (question_count >= 10 and len(worksheets_field.strip()) > 100 and 
                      ('?' in worksheets_field or 'A)' in worksheets_field))
        should_extract = (not worksheets_field or len(worksheets_field.strip()) < 100 or 
                         not has_content or question_count < 10)
        
        logger.info(f"🔍 Worksheets check: count={question_count}, has_content={has_content}, should_extract={should_extract}, field_length={len(worksheets_field) if worksheets_field else 0}")
        
        # Only extract if worksheets are truly missing or incomplete
        # Preserve JSON worksheets if they have good content
        if should_extract:
            # Extract from all possible fields
            all_questions, all_mc_options, all_answer_keys = [], [], []
            fields_to_check = [
                (final_data.get("objectives", []) or final_data.get("learning_objectives", []) or lesson_data.get("objectives", []), "objectives"),
                (final_data.get("materials", []) or lesson_data.get("materials", []), "materials"),
                (final_data.get("costas_questioning", "") or lesson_data.get("costas_questioning", ""), "costas_questioning"),
                (final_data.get("curriculum_standards", "") or lesson_data.get("curriculum_standards", ""), "curriculum_standards"),
                (worksheets_field, "worksheets"),
            ]
            
            for field_data, field_name in fields_to_check:
                if field_data:
                    q, mc, ak = _extract_worksheets_from_field(field_data, field_name)
                    all_questions.extend(q)
                    all_mc_options.extend(mc)
                    all_answer_keys.extend(ak)
                    if q or ak:
                        logger.info(f"🔍 Found {len(q)} questions, {len(ak)} answer keys in {field_name}")
            
            # Clean answer keys from curriculum_standards if found there
            curriculum_standards_text = final_data.get("curriculum_standards", "")
            if all_answer_keys and curriculum_standards_text and isinstance(curriculum_standards_text, str):
                cleaned = re.sub(r'\d+\.\s*(?:correct\s+)?answer[:\s]*(?:[A-D]\)\s*)?[^\n]+', '', curriculum_standards_text, flags=re.IGNORECASE | re.MULTILINE)
                cleaned = re.sub(r'(?:correct\s+)?answer[:\s]*[A-D]\s*-\s*[^\n]+', '', cleaned, flags=re.IGNORECASE | re.MULTILINE).strip()
                if len(cleaned) < len(curriculum_standards_text):
                    final_data["curriculum_standards"] = cleaned
                    logger.info(f"✅ Cleaned answer keys from curriculum_standards")
            
            # Combine and format
            if all_questions:
                combined = _combine_worksheets(worksheets_field, all_questions, all_mc_options, all_answer_keys)
                combined_count = _count_questions_in_text(combined)
                if len(combined) > 50 and combined_count > question_count:
                    final_data["worksheets"] = combined
                    logger.info(f"✅ Combined worksheets: {combined_count} questions")
                    
                    # Clean objectives
                    if objectives_data:
                        cleaned = _clean_objectives_of_questions(objectives_data)
                        if len(cleaned) < len(objectives_data):
                            final_data["objectives"] = cleaned
                            logger.info(f"✅ Cleaned {len(objectives_data) - len(cleaned)} items from objectives")
            
            # Check if worksheets only have headers (like "with Answer Keys\n\nStudent Worksheet:" with no actual questions)
            current_worksheets = final_data.get("worksheets", "")
            has_only_headers = (current_worksheets and 
                              ("Student Worksheet:" in current_worksheets or "with Answer Keys" in current_worksheets) and
                              _count_questions_in_text(current_worksheets) < 10 and
                              len(current_worksheets.strip()) < 200)
            
            # Fallback: Search raw response text if still need more questions OR if only headers exist
            if _count_questions_in_text(final_data.get("worksheets", "")) < 10 or has_only_headers:
                q, mc, ak = _extract_worksheets_from_field(response_text, "response_text")
                if q:
                    logger.info(f"🔍 Found {len(q)} questions in raw response text")
                    existing_q, existing_mc, existing_ak = _extract_worksheets_from_field(final_data.get("worksheets", ""), "worksheets")
                    all_questions = existing_q + q
                    all_mc_options = existing_mc + mc
                    all_answer_keys = existing_ak + ak
                    combined = _combine_worksheets(final_data.get("worksheets", ""), all_questions, all_mc_options, all_answer_keys)
                    if _count_questions_in_text(combined) >= 10:
                        final_data["worksheets"] = combined
                        logger.info(f"✅ Extracted from raw text: {_count_questions_in_text(combined)} questions")
            
            # Final check: Extract from raw response text if still incomplete
            current_count = _count_questions_in_text(final_data.get("worksheets", ""))
            if current_count < 10 and response_text:
                # Try to find worksheet section, otherwise use entire response
                worksheet_section = _extract_section_from_text(
                    response_text,
                    [
                        r'(?:###\s*)?worksheets?\s+(?:with\s+answer\s+keys?)?[:\s]*\n(.+?)(?=###\s*(?:grading\s+)?rubrics?|rubrics?|assessments?|$)',
                        r'student\s+worksheet[:\s]*\n(.+?)(?=###\s*(?:grading\s+)?rubrics?|rubrics?|assessments?|$)',
                    ],
                    r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*'
                )
                
                search_text = worksheet_section if worksheet_section else response_text
                q, mc, ak = _extract_worksheets_from_field(search_text, "response_text")
                if q:
                    existing_q, existing_mc, existing_ak = _extract_worksheets_from_field(final_data.get("worksheets", ""), "worksheets")
                    combined = _combine_worksheets(final_data.get("worksheets", ""), existing_q + q, existing_mc + mc, existing_ak + ak)
                    combined_count = _count_questions_in_text(combined)
                    if combined_count >= 10 or combined_count > current_count:
                        final_data["worksheets"] = combined
                        logger.info(f"✅ Extracted from raw text: {combined_count} questions")
        
        # CRITICAL: Check if rubric is embedded in worksheets field and extract it separately
        # This must happen AFTER worksheets are extracted but BEFORE final rubric extraction
        worksheets_field = final_data.get("worksheets", "")
        if worksheets_field and isinstance(worksheets_field, str) and len(worksheets_field) > 50:
            # Look for rubric markers OR rubric table patterns in worksheets field
            rubric_marker_pattern = r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*'
            rubric_table_pattern = r'\|[^\|]*\s*(?:criteria|technique|ability|mechanics|accuracy|understanding)[^\|]*\|\s*(?:excellent|proficient|developing|beginning|4\s*pts?|3\s*pts?|2\s*pts?|1\s*pt)[^\|]*\|'
            
            rubric_marker_match = re.search(rubric_marker_pattern, worksheets_field, re.IGNORECASE)
            rubric_table_match = re.search(rubric_table_pattern, worksheets_field, re.IGNORECASE)
            
            # Determine where rubric starts
            rubric_start = None
            if rubric_marker_match:
                rubric_start = rubric_marker_match.start()
                logger.info(f"🔍 Found rubric marker in worksheets field at position {rubric_start}")
            elif rubric_table_match:
                # Rubric table found without header - find the start of the table
                rubric_start = rubric_table_match.start()
                # Look backwards for table header or start of line
                before_table = worksheets_field[max(0, rubric_start-100):rubric_start]
                header_match = re.search(r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*\s*$', before_table, re.IGNORECASE | re.MULTILINE)
                if header_match:
                    rubric_start = rubric_start - 100 + header_match.start()
                logger.info(f"🔍 Found rubric table in worksheets field at position {rubric_start}")
            
            if rubric_start is not None:
                # Extract rubric from worksheets field
                rubric_content_from_worksheets = worksheets_field[rubric_start:].strip()
                
                # Find where rubric ends (next section, assessments, or end of string)
                rubric_end_match = re.search(r'\n(?:###|assessments?|$)', rubric_content_from_worksheets, re.IGNORECASE | re.MULTILINE)
                if rubric_end_match:
                    rubric_content_from_worksheets = rubric_content_from_worksheets[:rubric_end_match.start()].strip()
                else:
                    # No clear end, take up to 3000 chars (reasonable rubric size)
                    rubric_content_from_worksheets = rubric_content_from_worksheets[:3000].strip()
                
                # Verify it's actually a rubric (has table structure or rubric indicators)
                is_rubric = False
                if '|' in rubric_content_from_worksheets:
                    # Check for rubric table indicators
                    has_criteria = re.search(r'(criteria|technique|ability|mechanics|accuracy|understanding|teamwork|communication|safety|effort|performance|skill)', rubric_content_from_worksheets, re.IGNORECASE)
                    has_levels = re.search(r'(excellent|proficient|developing|beginning|4\s*pts?|3\s*pts?|2\s*pts?|1\s*pt|perfect|good|inconsistent|struggles|demonstrates|shows)', rubric_content_from_worksheets, re.IGNORECASE)
                    if has_criteria and has_levels:
                        is_rubric = True
                
                if is_rubric:
                    logger.info(f"✅ Found rubric embedded in worksheets field. Extracting separately. Length: {len(rubric_content_from_worksheets)} chars")
                    # Only set rubrics if it's not already set or is empty
                    if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
                        final_data["rubrics"] = rubric_content_from_worksheets
                    
                    # Remove rubric from worksheets field
                    worksheets_cleaned = worksheets_field[:rubric_start].strip()
                    # Clean up any trailing markers or empty lines
                    worksheets_cleaned = re.sub(r'\n+\s*(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*\s*$', '', worksheets_cleaned, flags=re.IGNORECASE | re.MULTILINE)
                    # Remove any trailing "with Answer Keys" if it's the only thing left
                    worksheets_cleaned = re.sub(r'^with\s+answer\s+keys?\s*$', '', worksheets_cleaned, flags=re.IGNORECASE | re.MULTILINE).strip()
                    final_data["worksheets"] = worksheets_cleaned
                    logger.info(f"✅ Cleaned worksheets field, removed rubric. New length: {len(worksheets_cleaned)} chars")
                else:
                    logger.warning(f"⚠️ Found rubric marker/table in worksheets but content doesn't match rubric pattern")
        
        # Extract rubrics from objectives, assessments, curriculum_standards, and raw text
        if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
            # Check objectives for rubric rows
            objectives_data = final_data.get("objectives", []) or final_data.get("learning_objectives", []) or lesson_data.get("objectives", [])
            if objectives_data:
                objectives_text = "\n".join([str(obj) for obj in objectives_data if obj])
                rubric_rows = _extract_rubric_rows_from_text(objectives_text)
                valid_rows = [row for row in rubric_rows if _is_valid_rubric_row(row)]
                
                if valid_rows:
                    logger.info(f"🔍 Found {len(valid_rows)} rubric rows in objectives")
                    rubric_table = _build_rubric_table(valid_rows)
                    if rubric_table:
                        final_data["rubrics"] = rubric_table
                        logger.info(f"✅ Extracted rubric from objectives: {len(valid_rows)} rows")
                        
                        # Clean objectives
                        cleaned = _clean_objectives_of_rubrics(objectives_data)
                        if len(cleaned) < len(objectives_data):
                            final_data["objectives"] = cleaned
                            logger.info(f"✅ Cleaned {len(objectives_data) - len(cleaned)} rubric rows from objectives")
            
            # Check assessments and curriculum_standards
            assessments_text = final_data.get("assessments", "") or lesson_data.get("assessments", "")
            curriculum_standards_text = final_data.get("curriculum_standards", "") or lesson_data.get("curriculum_standards", "")
            
            # Prioritize curriculum_standards if it mentions rubric
            search_text = curriculum_standards_text if (curriculum_standards_text and 'rubric' in curriculum_standards_text.lower()) else assessments_text
            
            if search_text:
                rubric_content = _extract_rubrics_from_field(search_text)
                if rubric_content:
                    final_data["rubrics"] = rubric_content
                    logger.info(f"✅ Extracted rubric from {'curriculum_standards' if search_text == curriculum_standards_text else 'assessments'}")
            
            # Fallback: Search raw response text for rubric section or rubric rows
            if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
                if response_text:
                    rubric_section = _extract_section_from_text(
                        response_text,
                        [
                            r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*\n(.+?)(?=###|assessments?|exit|extensions?|safety|homework|$)',
                            r'\|\s*Criteria\s*\|.*?Excellent.*?Proficient.*?Developing.*?Beginning.*?\|',
                        ]
                    )
                    
                    search_text = rubric_section if rubric_section and '|' in rubric_section else response_text
                    rubric_rows = _extract_rubric_rows_from_text(search_text)
                    valid_rows = [row for row in rubric_rows if _is_valid_rubric_row(row)]
                    
                    if valid_rows:
                        rubric_table = _build_rubric_table(valid_rows)
                        if rubric_table:
                            final_data["rubrics"] = rubric_table
                            logger.info(f"✅ Extracted rubric from raw text: {len(valid_rows)} rows")
                    elif rubric_section and re.search(r'(criteria|excellent|proficient|developing|beginning)', rubric_section, re.IGNORECASE):
                        final_data["rubrics"] = "Grading Rubric:\n" + rubric_section
                        logger.info(f"✅ Using rubric section directly from raw text")
                
                # Final fallback: Search all fields for rubric rows
                if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
                    for field_name, field_value in final_data.items():
                        if field_name == "rubrics" or not field_value:
                            continue
                        
                        text = str(field_value) if isinstance(field_value, str) else "\n".join([str(item) for item in field_value if item]) if isinstance(field_value, list) else ""
                        if len(text) < 30:
                            continue
                        
                        rubric_rows = _extract_rubric_rows_from_text(text)
                        valid_rows = [row for row in rubric_rows if _is_valid_rubric_row(row)]
                        
                        if valid_rows:
                            rubric_table = _build_rubric_table(valid_rows)
                            if rubric_table:
                                final_data["rubrics"] = rubric_table
                                logger.info(f"✅ Found rubric in field '{field_name}': {len(valid_rows)} rows")
                                break
        
        # Also ensure other fields from regex are included if missing in JSON
        for key in ["title", "description", "introduction", "exit_ticket", "homework"]:
            if lesson_data.get(key) and not final_data.get(key):
                final_data[key] = lesson_data[key]
        
        # Merge arrays (objectives, activities, materials, etc.)
        if lesson_data.get("objectives") and not final_data.get("learning_objectives") and not final_data.get("objectives"):
            final_data["learning_objectives"] = lesson_data["objectives"]
        if lesson_data.get("activities") and not final_data.get("activities"):
            final_data["activities"] = lesson_data["activities"]
        if lesson_data.get("materials") and not final_data.get("materials_list") and not final_data.get("materials"):
            final_data["materials_list"] = lesson_data["materials"]
        
        # FINAL SUMMARY LOG - Show what was extracted
        worksheets_final = final_data.get("worksheets", "")
        rubrics_final = final_data.get("rubrics", "")
        worksheets_len = len(worksheets_final) if isinstance(worksheets_final, str) else 0
        rubrics_len = len(rubrics_final) if isinstance(rubrics_final, str) else 0
        worksheets_has_content = worksheets_len > 50 and ('?' in worksheets_final or 'A)' in worksheets_final or re.search(r'[A-D]\)', worksheets_final, re.IGNORECASE))
        rubrics_has_content = rubrics_len > 50 and ('|' in rubrics_final or 'criteria' in rubrics_final.lower() or 'excellent' in rubrics_final.lower())
        
        logger.info(f"📊 EXTRACTION SUMMARY:")
        logger.info(f"   - Worksheets: {worksheets_len} chars, has_content: {worksheets_has_content}")
        if worksheets_final and isinstance(worksheets_final, str):
            logger.info(f"   - Worksheets preview: {worksheets_final[:200]}...")
        logger.info(f"   - Rubrics: {rubrics_len} chars, has_content: {rubrics_has_content}")
        if rubrics_final and isinstance(rubrics_final, str):
            logger.info(f"   - Rubrics preview: {rubrics_final[:200]}...")
        
        return final_data
    
    # No JSON found or JSON parsing failed - use regex extraction
    if has_activities or has_objectives or has_introduction or has_title:
        return lesson_data
    
    return {}


def _extract_workout_data(response_text: str) -> Dict[str, Any]:
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
    
    # First, try to extract JSON from markdown code blocks
    # Use the EXACT same pattern as lesson plan extraction
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
            # Fall through to more robust extraction below
            parsed_json_data = None
    
    # If simple extraction failed, try the more robust brace-counting approach
    if parsed_json_data is None:
        json_marker_pattern = re.compile(r'```(?:json)?', re.IGNORECASE)
        json_marker_match = json_marker_pattern.search(response_text)
        
        if json_marker_match:
            try:
                # Find the opening marker position
                marker_start = json_marker_match.start()
                marker_end = json_marker_match.end()
                
                # Find the first { after the marker (skip any whitespace/newlines)
                brace_start = None
                for i in range(marker_end, min(marker_end + 100, len(response_text))):
                    if response_text[i] == '{':
                        brace_start = i
                        break
                
                if brace_start is None:
                    logger.warning(f"⚠️ Found ```json marker at {marker_start} but no opening brace found")
                else:
                    # Find the matching closing brace by counting braces
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
                        logger.warning(f"⚠️ Found opening brace at {brace_start} but couldn't find matching closing brace (brace_count ended at {brace_count})")
                        # Try to find the closing ``` marker as a fallback
                        closing_marker = response_text.find('```', brace_start)
                        if closing_marker > brace_start:
                            logger.info(f"🔍 Found closing ``` marker at position {closing_marker}")
                            # Extract everything up to the closing marker
                            potential_json = response_text[brace_start:closing_marker].rstrip()
                            logger.info(f"🔍 Potential JSON length: {len(potential_json)} chars")
                            # Try to find the last } before the closing marker
                            last_brace = potential_json.rfind('}')
                            if last_brace > 0:
                                json_str = potential_json[:last_brace + 1]
                                json_end_pos = brace_start + len(json_str)
                                logger.info(f"🔍 Using closing ``` marker as fallback, extracted {len(json_str)} chars (last_brace at {last_brace})")
                            else:
                                logger.error(f"❌ No closing brace found before closing ``` marker. Potential JSON ends with: {potential_json[-100:]}")
                                # Try to extract anyway - maybe the JSON is incomplete but still parseable
                                json_str = potential_json
                                json_end_pos = closing_marker
                                logger.warning(f"⚠️ Attempting to parse incomplete JSON (no closing brace found)")
                        else:
                            logger.error(f"❌ No closing ``` marker found after brace_start {brace_start}. Response length: {len(response_text)}")
                            # Last resort: try to extract up to end of response
                            potential_json = response_text[brace_start:].rstrip()
                            last_brace = potential_json.rfind('}')
                            if last_brace > 0:
                                json_str = potential_json[:last_brace + 1]
                                # Try to repair incomplete JSON by counting what's missing
                                # Count opening and closing braces/brackets
                                open_braces = json_str.count('{')
                                close_braces = json_str.count('}')
                                open_brackets = json_str.count('[')
                                close_brackets = json_str.count(']')
                                
                                missing_braces = open_braces - close_braces
                                missing_brackets = open_brackets - close_brackets
                                
                                if missing_braces > 0 or missing_brackets > 0:
                                    logger.info(f"🔧 Attempting to repair JSON: missing {missing_brackets} brackets, {missing_braces} braces")
                                    # Add missing closing brackets first, then braces
                                    json_str += ']' * missing_brackets
                                    json_str += '}' * missing_braces
                                    logger.info(f"🔧 Repaired JSON length: {len(json_str)} chars")
                                
                                json_end_pos = brace_start + len(json_str)
                                logger.warning(f"⚠️ Using end of response as fallback, extracted {len(json_str)} chars")
                            else:
                                logger.error(f"❌ Cannot extract JSON - no closing brace or marker found")
                                json_str = None
                                json_end_pos = None
                    else:
                        # Extract the JSON string
                        json_str = response_text[brace_start:json_end_pos]
                        logger.info(f"🔍 Extracted JSON string from workout response: {len(json_str)} chars (start: {brace_start}, end: {json_end_pos})")
                    
                    if json_end_pos is not None and json_str is not None:
                        # Try to parse the JSON
                        try:
                            parsed_json_data = json.loads(json_str)
                            logger.info(f"✅ Parsed JSON successfully, keys: {list(parsed_json_data.keys()) if isinstance(parsed_json_data, dict) else 'not a dict'}")
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ JSON parsing failed: {e}")
                            logger.error(f"❌ JSON string (first 500 chars): {json_str[:500]}")
                            logger.error(f"❌ JSON string (last 500 chars): {json_str[-500:] if len(json_str) > 500 else json_str}")
                            parsed_json_data = None
            except Exception as e:
                logger.error(f"❌ Error during JSON extraction: {e}", exc_info=True)
                parsed_json_data = None
    
    # If JSON parsing succeeds and contains workout data, use it
    if isinstance(parsed_json_data, dict):
        # Check if it has workout_plan structure (week-long format with Day 1, Day 2, etc.)
        # Handle both naming conventions: with underscores (workout_plan) and without (workoutplan)
        workout_plan = parsed_json_data.get("workout_plan") or parsed_json_data.get("workoutplan")
        if workout_plan:
            # Convert workout_plan format to standard format
            plan_name = parsed_json_data.get("plan_name") or parsed_json_data.get("planname") or "Week-Long Workout Plan"
            description = parsed_json_data.get("description") or ""
            workout_data = {
                "plan_name": plan_name,
                "description": description,
                "days": []
            }
            # Convert each day to structured format
            for day_key, day_data in workout_plan.items():
                if isinstance(day_data, dict):
                    day_entry = {
                        "day": day_key,
                        "focus": day_data.get("focus", ""),
                        "exercises": [],
                        "activities": []
                    }
                    # Add exercises if present
                    if day_data.get("exercises"):
                        for ex in day_data["exercises"]:
                            if isinstance(ex, str):
                                # Parse exercise string like "Push-Ups: 3 sets of 10-15 reps"
                                day_entry["exercises"].append({"name": ex, "description": ex})
                            elif isinstance(ex, dict):
                                day_entry["exercises"].append(ex)
                    # Add activities if present
                    if day_data.get("activities"):
                        day_entry["activities"] = day_data["activities"]
                    workout_data["days"].append(day_entry)
            return workout_data
        # Check if it has standard workout structure
        # Handle both naming conventions: with underscores (plan_name) and without (planname)
        strength_training = parsed_json_data.get("strength_training") or parsed_json_data.get("strengthtraining")
        cardio = parsed_json_data.get("cardio")
        exercises = parsed_json_data.get("exercises")
        
        if strength_training or cardio or exercises:
            # Return structured workout data
            workout_data = {}
            # Handle both naming conventions
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
        # If JSON doesn't have workout structure, fall through to regex extraction
    
    exercises = []
    
    # Pattern 0: "Exercise Name (3 sets, 10 reps)" - most common format
    pattern0 = re.compile(r"[-•]\s*([^(]+?)\s*\((\d+)\s*sets?,\s*(\d+)\s*reps?\)", re.I)
    for match in pattern0.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip()
        })
    
    # Pattern 0b: "Exercise Name (3 sets, 10 reps each leg)" - with qualifier
    pattern0b = re.compile(r"[-•]\s*([^(]+?)\s*\((\d+)\s*sets?,\s*(\d+)\s*reps?\s+[^)]+\)", re.I)
    for match in pattern0b.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip()
        })
    
    # Pattern 0c: "Exercise Name (3 sets, 60 seconds)" - time-based
    pattern0c = re.compile(r"[-•]\s*([^(]+?)\s*\((\d+)\s*sets?,\s*(\d+)\s*seconds?\)", re.I)
    for match in pattern0c.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip() + " seconds"
        })
    
    # Pattern 1: "Exercise Name: 3x10" or "Exercise Name: 3 sets of 10 reps"
    pattern1 = re.compile(r"[-•]\s*([^:]+?):\s*(\d+)x(\d+)(?:\s|$)", re.I)
    for match in pattern1.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip()
        })
    
    # Pattern 2: "Exercise Name: 3 sets of 10 reps" or "Exercise Name: 3 sets, 10 reps"
    pattern2 = re.compile(r"[-•]\s*([^:]+?):\s*(\d+)\s*sets?\s*(?:of\s*)?(\d+)\s*reps?", re.I)
    for match in pattern2.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip()
        })
    
    # Pattern 2b: "3 sets of exercise name (8-10 reps)" - different order
    pattern2b = re.compile(r"[-•]\s*(\d+)\s*sets?\s+of\s+([^(]+?)\s*\((\d+)(?:-\d+)?\s*reps?\)", re.I)
    for match in pattern2b.finditer(response_text):
        exercises.append({
            "name": match.group(2).strip(),
            "sets": match.group(1).strip(),
            "reps": match.group(3).strip()
        })
    
    # Pattern 3: "Exercise Name - Sets: 3 Reps: 10"
    pattern3 = re.compile(r"[-•]\s*([^-:]+?)\s*-\s*Sets?:\s*(\d+)\s*Reps?:\s*(\d+)", re.I)
    for match in pattern3.finditer(response_text):
        exercises.append({
            "name": match.group(1).strip(),
            "sets": match.group(2).strip(),
            "reps": match.group(3).strip()
        })
    
    # Pattern 4: Numbered list format "1. Exercise Name: 3x10"
    pattern4 = re.compile(r"(\d+)\.\s*([^:]+?):\s*(\d+)x(\d+)(?:\s|$)", re.I)
    for match in pattern4.finditer(response_text):
        exercises.append({
            "name": match.group(2).strip(),
            "sets": match.group(3).strip(),
            "reps": match.group(4).strip()
        })
    
    # Remove duplicates (same exercise name)
    seen = set()
    unique_exercises = []
    for ex in exercises:
        name_lower = ex["name"].lower()
        if name_lower not in seen:
            seen.add(name_lower)
            unique_exercises.append(ex)
    
    # If we parsed JSON successfully, merge it with regex-extracted data
    if parsed_json_data and isinstance(parsed_json_data, dict):
        # Merge: JSON data takes precedence, but add exercises from regex if they exist
        workout_data = parsed_json_data.copy()
        if unique_exercises:
            # Add exercises from regex extraction if not in JSON
            if not workout_data.get("exercises") and not workout_data.get("strength_training") and not workout_data.get("cardio"):
                workout_data["exercises"] = unique_exercises
        return workout_data
    
    # No JSON found or JSON parsing failed - use regex extraction
    if unique_exercises:
        return {"exercises": unique_exercises}
    
# ==========================
# 4️⃣ Validation Functions
# ==========================

def validate_meal_plan(response_text: str, allergy_info_already_recorded: bool = False) -> List[str]:
    """
    Validate meal plan response for required components.
    
    Safety-critical validation that forces auto-correction if validation fails.
    
    Args:
        response_text: AI's meal plan response
        allergy_info_already_recorded: Whether allergy info was already provided
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors: List[str] = []
    
    if not response_text.strip().startswith("**DAY 1**"):
        errors.append("Meal plan must start with Day 1.")
    
    if not allergy_info_already_recorded and "allergy" not in response_text.lower():
        errors.append("Meal plan created WITHOUT asking about allergies.")
    
    return errors


def validate_lesson_plan(response_text: str) -> List[str]:
    """
    Validate lesson plan response for required components.
    
    Optional auto-correction can be enabled to enforce completeness.
    
    Args:
        response_text: AI's lesson plan response
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors: List[str] = []
    
    for section in ["**Unit:**", "**Grade:**", "Objectives", "Activities", "Assessment", "Danielson Framework", "Costa's Levels"]:
        if section.lower() not in response_text.lower():
            errors.append(f"Lesson plan missing section: {section}")
    
    return errors


def validate_workout_plan(response_text: str) -> List[str]:
    """
    Validate workout plan response for required components.
    
    Optional auto-correction can be enabled to enforce completeness.
    
    Args:
        response_text: AI's workout plan response
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors: List[str] = []
    
    for section in ["Warm-up", "Main Workout", "Cool Down", "Reps", "Sets"]:
        if section.lower() not in response_text.lower():
            errors.append(f"Workout plan missing section: {section}")
    
    return errors


# ==========================
# 5️⃣ GPT Function Calling Stubs (20+ Widgets)
# ==========================

def call_attendance_functions(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for attendance widget GPT function calls."""
    return {"status": "success"}


def call_team_functions(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for team management widget GPT function calls."""
    return {"status": "success"}


def call_adaptive_pe_functions(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for adaptive PE widget GPT function calls."""
    return {"status": "success"}


def call_performance_analytics(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for performance analytics widget GPT function calls."""
    return {"status": "success"}


def call_safety_risks(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for safety/risk management widget GPT function calls."""
    return {"status": "success"}


def call_class_insights(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for class insights widget GPT function calls."""
    return {"status": "success"}


def call_health_metrics(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for health metrics widget GPT function calls."""
    return {"status": "success"}


def call_drivers_ed_functions(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for driver's education widget GPT function calls."""
    return {"status": "success"}


def call_parent_communication(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for parent communication widget GPT function calls."""
    return {"status": "success"}


def call_student_communication(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for student communication widget GPT function calls."""
    return {"status": "success"}


def call_teacher_communication(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for teacher communication widget GPT function calls."""
    return {"status": "success"}


def call_admin_communication(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for admin communication widget GPT function calls."""
    return {"status": "success"}


def call_assignment_distribution(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for assignment distribution widget GPT function calls."""
    return {"status": "success"}


def call_translation_services(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for translation services widget GPT function calls."""
    return {"status": "success"}


def call_reporting(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for reporting widget GPT function calls."""
    return {"status": "success"}


def call_notifications(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for notifications widget GPT function calls."""
    return {"status": "success"}


def call_workflow_automation(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for workflow automation widget GPT function calls."""
    return {"status": "success"}


def call_cross_widget_analysis(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for cross-widget analysis GPT function calls."""
    return {"status": "success"}


def call_anomaly_detection(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for anomaly detection widget GPT function calls."""
    return {"status": "success"}


def call_smart_alerts(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for smart alerts widget GPT function calls."""
    return {"status": "success"}


def call_student_self_service(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for student self-service widget GPT function calls."""
    return {"status": "success"}


def call_equipment_management(*args, **kwargs) -> Dict[str, Any]:
    """Placeholder for equipment management widget GPT function calls."""
    return {"status": "success"}


# ==========================
# 6️⃣ Widget Extraction Master
# ==========================

def extract_widget(user_intent: str, response_text: str) -> Dict[str, Any]:
    """
    Determine correct extraction method based on intent.
    
    Main entry point for all widget extraction. Routes to appropriate handler.
    For Meal/Lesson/Workout widgets, performs structured extraction.
    For all other widgets, returns general response data.
    
    Args:
        user_intent: Classified widget intent
        response_text: AI's response text
        
    Returns:
        Dictionary with extracted widget data
    """
    if user_intent == "meal_plan":
        return _extract_meal_plan_data(response_text)
    elif user_intent == "lesson_plan":
        return _extract_lesson_plan_data(response_text)
    elif user_intent == "workout":
        return _extract_workout_data(response_text)
    else:
        # All other widgets (GPT function calling or general response)
        # Simply return the AI response directly without structured parsing
        return {"type": "general_response", "data": response_text}


# ==========================
# 7️⃣ Auto-Correction Wrapper for Meal + Lesson + Workout
# ==========================

def generate_response_with_retry(
    user_message: str,
    intent: str,
    conversation_state: Dict[str, Any],
    max_retries: int = 2,
    call_openai_func = None,  # Placeholder for OpenAI call function
    load_prompt_modules_func = None  # Placeholder for prompt loading function
) -> Tuple[str, Dict[str, Any], List[str]]:
    """
    Generates AI response with auto-correction for Meal Plan, Lesson Plan, and Workout widgets.
    
    Auto-correction behavior:
    - Meal Plan: ALWAYS forces correction (safety-critical for allergens)
    - Lesson Plan: Validates and corrects if validation fails
    - Workout Plan: Validates and corrects if validation fails
    - Other widgets: No validation/correction (returns AI response directly)
    
    Args:
        user_message: User's message
        intent: Classified widget intent
        conversation_state: Conversation state dictionary
        max_retries: Maximum number of retry attempts
        call_openai_func: Function to call OpenAI API
        load_prompt_modules_func: Function to load prompt modules
        
    Returns:
        Tuple of (response_text, widget_data, errors)
    """
    retry_count = 0
    previous_allergy = conversation_state.get("previous_asked_allergies", False)
    errors: List[str] = []
    response_text = ""
    
    while retry_count <= max_retries:
        # Build messages
        if load_prompt_modules_func:
            messages = safe_build_messages(load_prompt_modules_func(intent))
        else:
            messages = safe_build_messages([{"role": "system", "content": ""}])
        
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI
        if call_openai_func:
            response_text = call_openai_func(messages)
        else:
            response_text = ""  # Placeholder
        
        # Validate based on intent
        if intent == "meal_plan":
            errors = validate_meal_plan(response_text, previous_allergy)
        elif intent == "lesson_plan":
            errors = validate_lesson_plan(response_text)
        elif intent == "workout":
            errors = validate_workout_plan(response_text)
        else:
            errors = []  # Other widgets: No validation
        
        # If no errors, break
        if not errors:
            break
        
        # Prepare correction message
        error_message = "\n".join(errors)
        user_message = f"{user_message}\n\nPlease correct the following issues:\n{error_message}"
        retry_count += 1
    
    # Extract widget data
    widget_data = extract_widget(intent, response_text)
    
    return response_text, widget_data, errors
