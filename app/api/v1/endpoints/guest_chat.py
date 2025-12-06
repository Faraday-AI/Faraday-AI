"""
Guest-friendly chat endpoint for dashboard.
Allows users to chat with AI assistant without requiring authentication.
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
import re
from openai import OpenAI
from app.core.config import get_settings
from app.services.integration.twilio_service import get_twilio_service
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)

router = APIRouter()

def _extract_workout_data(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Extract structured workout data from AI response text.
    Returns a dict with workout plan information if found.
    Handles multiple formats: numbered lists, bullet points, bold text, plain text.
    """
    if not response_text:
        return None
    
    workout_data = {
        "exercises": [],
        "plan_name": "Workout Plan",
        "description": ""
    }
    
    # Try to extract exercises from numbered lists or bullet points
    lines = response_text.split('\n')
    current_exercise = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Pattern 1: Numbered list with bold (e.g., "1. **Push-ups**: 3 sets of 10")
        numbered_bold_match = re.match(r'^\d+\.\s*\*\*(.*?)\*\*', line)
        if numbered_bold_match:
            exercise_name = numbered_bold_match.group(1).strip()
            if current_exercise:
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
                if current_exercise:
                    workout_data["exercises"].append(current_exercise)
                current_exercise = {
                    "name": exercise_name,
                    "sets": None,
                    "reps": None,
                    "description": ""
                }
                line = re.sub(r'^\d+\.\s+.*?:?\s*', '', line)
        
        # Pattern 3: Bold text (without numbers) (e.g., "**Push-ups**: 3 sets of 10")
        elif '**' in line and not current_exercise:
            bold_text = re.findall(r'\*\*(.*?)\*\*', line)
            if bold_text:
                exercise_name = bold_text[0].strip()
                if current_exercise:
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
            
            # Add description if it's not an exercise name and contains useful info
            if not re.match(r'^\d+\.\s*\*\*', line) and not '**' in line and not sets_reps_match and not reps_sets_match:
                # Skip lines that are just dashes, bullets, or common workout section headers
                skip_patterns = ['warm', 'cool', 'rest', 'notes', 'tips', 'instructions', '---', '===']
                if line and not line.startswith('-') and not line.startswith('•') and not any(pattern in line.lower() for pattern in skip_patterns):
                    if current_exercise["description"]:
                        current_exercise["description"] += " " + line
                    else:
                        current_exercise["description"] = line
    
    # Add last exercise if exists
    if current_exercise:
        workout_data["exercises"].append(current_exercise)
    
    # If we found exercises, return the data
    if workout_data["exercises"]:
        return workout_data
    
    return None

def _extract_lesson_plan_data(response_text: str, original_message: str = "") -> Optional[Dict[str, Any]]:
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
        # Pattern matches: "1. **Header** - content" or "1. **Header**: content"
        # BUT: Skip if we're already in a section and this looks like a sub-item (short line, starts with lowercase article)
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
            # Categorize the section based on its header
            # IMPORTANT: Don't continue here - let subsequent lines be processed as content for this section
            if any(keyword in section_header_lower for keyword in ['introduction', 'intro', 'overview']):
                current_section = "introduction"
                # Start with section content if present, subsequent lines will be appended
                if section_content and len(section_content) > 5:
                    # Remove leading dash if present
                    section_content = re.sub(r'^-\s*', '', section_content).strip()
                    lesson_data["introduction"] = section_content
                # Don't continue - let subsequent lines be added to introduction
            elif any(keyword in section_header_lower for keyword in ['objective', 'goal', 'learning outcome']):
                current_section = "objectives"
                if section_content and len(section_content) > 10:
                    section_content = re.sub(r'^-\s*', '', section_content).strip()
                    lesson_data["objectives"].append(section_content)
                # Don't continue - let subsequent lines be added to objectives
            elif any(keyword in section_header_lower for keyword in ['material', 'supply', 'resource', 'equipment']):
                current_section = "materials"
                if section_content:
                    for material in section_content.split(','):
                        material = material.strip()
                        material = re.sub(r'^-\s*', '', material).strip()
                        if material and len(material) > 2:
                            lesson_data["materials"].append(material)
                # Don't continue - let subsequent lines be added to materials
            elif any(keyword in section_header_lower for keyword in ['warm-up', 'warmup', 'warm', 'practice', 'drill', 'skill', 'demonstration', 'demo', 'activity', 'procedure', 'step', 'pathway', 'flow', 'structure', 'vessel', 'heartbeat', 'sound', 'importance', 'conclusion', 'wrap', 'cool-down', 'cooldown', 'cool', 'recap', 'homework']):
                current_section = "activities"
                # Build activity text with header and content
                activity_text = section_header
                if section_content:
                    # Remove leading dash if present
                    section_content = re.sub(r'^-\s*', '', section_content).strip()
                    activity_text += ": " + section_content
                if activity_text and len(activity_text) > 10:
                    lesson_data["activities"].append(activity_text)
                # Don't continue - let subsequent lines be added to activities
            elif any(keyword in section_header_lower for keyword in ['assessment', 'evaluation', 'homework', 'assignment']):
                current_section = "assessment"
                if section_content and len(section_content) > 10:
                    section_content = re.sub(r'^-\s*', '', section_content).strip()
                    lesson_data["assessment"] = section_content
                # Don't continue - let subsequent lines be added to assessment
            else:
                # Unknown section - default to activities if it has content
                current_section = "activities"
                activity_text = section_header
                if section_content:
                    section_content = re.sub(r'^-\s*', '', section_content).strip()
                    activity_text += ": " + section_content
                if activity_text and len(activity_text) > 10:
                    lesson_data["activities"].append(activity_text)
                # Don't continue - let subsequent lines be added to activities
        
        # Detect section headers - check for common patterns
        # Title detection
        if "title:" in line_lower and i < 5:
            title_match = re.search(r'title[:\s]+(.+)', line, flags=re.IGNORECASE)
            if title_match:
                lesson_data["title"] = re.sub(r'\*\*', '', title_match.group(1)).strip()
            continue
        
        # Lesson Description detection - must come early, before objectives
        # Look for "Description:", "Lesson Description:", "Overview:", etc. near the beginning
        # Also check for lines that start with "**Description:" or "**Lesson Description:"
        if (re.search(r'(lesson\s+description|description|overview|lesson\s+overview|what\s+is\s+this\s+lesson)', line_lower) and i < 30) or \
           (re.search(r'\*\*.*?(lesson\s+description|description)[:\s]', line_lower, flags=re.IGNORECASE) and i < 30):
            current_section = "description"
            # Extract description text from this line
            desc_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            desc_text = re.sub(r'\*\*?', '', desc_text)
            desc_text = re.sub(r'(lesson\s+description|description|overview|lesson\s+overview|what\s+is\s+this\s+lesson)[:\s]+', '', desc_text, flags=re.IGNORECASE).strip()
            if desc_text and len(desc_text) > 20:
                if lesson_data["description"]:
                    lesson_data["description"] += " " + desc_text
                else:
                    lesson_data["description"] = desc_text
            # Don't continue - let subsequent lines be added to description
            continue
        
        # Objective detection - handle variations like "Objective of the Lesson", "Objectives:", etc.
        if re.search(r'(objective|objectives|learning\s+objective)', line_lower):
            current_section = "objectives"
            # Skip header lines like "Detailed (Using Bloom's Taxonomy):" or "Learning Objectives:"
            if re.search(r'(detailed|using|bloom|taxonomy|learning\s+objectives?)[:\s]*$', line_lower):
                continue  # Skip this line, but keep current_section = "objectives" for next lines
            
            # Extract objective text from this line - handle "Objective of the Lesson:" format
            objective_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)  # Remove leading number and bold
            objective_text = re.sub(r'\*\*?', '', objective_text)  # Remove all bold markers
            objective_text = re.sub(r'(objective|objectives|learning\s+objective)(\s+of\s+the\s+lesson)?[:\s]+', '', objective_text, flags=re.IGNORECASE).strip()
            
            # Skip if it's just a header or marker (like "- Remember:", "- Understand:")
            if re.match(r'^[-•]\s*(remember|understand|apply|analyze|evaluate|create)[:\s]*$', objective_text.lower()):
                continue  # Skip this line, but keep current_section for next lines
            
            # Remove leading dashes/bullets and clean up
            objective_text = re.sub(r'^[-•]\s*', '', objective_text).strip()
            
            # Only add if it's a complete objective (not just a category header)
            if objective_text and len(objective_text) > 10 and not re.match(r'^(detailed|using|bloom|taxonomy)', objective_text.lower()):
                # Check if it's a complete sentence (has a verb and object)
                if re.search(r'(will|can|should|students?\s+will|students?\s+can|students?\s+should|recall|explain|perform|demonstrate|identify|analyze|create|evaluate)', objective_text.lower()):
                    lesson_data["objectives"].append(objective_text)
            continue
        
        # Materials detection - handle "Materials Needed:", "Materials:", etc.
        elif re.search(r'(material|materials|supplies|resources|equipment)(\s+needed)?', line_lower):
            current_section = "materials"
            # Extract materials from this line if present
            materials_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            materials_text = re.sub(r'\*\*?', '', materials_text)
            materials_text = re.sub(r'(material|materials|supplies|resources|equipment)(\s+needed)?[:\s]+', '', materials_text, flags=re.IGNORECASE).strip()
            if materials_text and len(materials_text) > 5:
                # Split by comma and add each material
                for material in materials_text.split(','):
                    material = material.strip()
                    if material and len(material) > 2:
                        lesson_data["materials"].append(material)
            continue
        
        # Introduction detection - handle "Introduction (15 minutes):" or "Introduction to Topic - 10 minutes" format
        elif re.match(r'^(introduction|intro)(\s+to\s+[^:]+)?\s*\(?\d+\s*minutes?\)?\s*[:\-]?', line_lower) or \
             (re.search(r'^(introduction|intro)(\s+to\s+[^:]+)?[:\-]', line_lower) and i < 20):
            current_section = "introduction"
            # Extract intro text from this line if it has content
            intro_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            intro_text = re.sub(r'\*\*?', '', intro_text)
            # Remove "Introduction (X minutes):" or "Introduction to Topic - X minutes" pattern
            intro_text = re.sub(r'(introduction|intro)(\s+to\s+[^-]+)?\s*\(?\d+\s*minutes?\)?\s*[:\-]?\s*', '', intro_text, flags=re.IGNORECASE)
            intro_text = re.sub(r'(introduction|intro)[:\s]+', '', intro_text, flags=re.IGNORECASE).strip()
            if intro_text and len(intro_text) > 10:
                lesson_data["introduction"] = intro_text
            # Don't continue - let subsequent numbered items be added to introduction
        
        # Activity/Activities detection (explicit section headers)
        # Handle "Activity 1:", "Activity 2:", "Activity 1: Introduction to CPR", etc.
        elif re.search(r'activity\s+\d+[:\-]', line_lower):
            current_section = "activities"
            # Extract activity header and content - handle formats like:
            # "Activity 1: Demonstrating CPR (30 minutes)"
            # "**Activity 1:** Demonstrating CPR (30 minutes)"
            # "- Activity 1: Demonstrating CPR (30 minutes)"
            activity_match = re.search(r'activity\s+\d+[:\-]\s*(.+)', line, flags=re.IGNORECASE)
            if activity_match:
                activity_content = activity_match.group(1).strip()
                activity_content = re.sub(r'\*\*?', '', activity_content).strip()
                # Remove leading dashes/bullets
                activity_content = re.sub(r'^[-•]\s*', '', activity_content).strip()
                if activity_content and len(activity_content) > 5:
                    lesson_data["activities"].append(activity_content)
            # Don't continue - let subsequent lines be added to activities
        # Also handle "Activities" section header
        elif re.match(r'^activities?[:\-]?\s*$', line_lower) or (re.match(r'^activities?[:\-]', line_lower) and i > 5):
            current_section = "activities"
            # Extract content after "Activities:" if present
            activities_match = re.match(r'^activities?[:\-]\s*(.+)', line, flags=re.IGNORECASE)
            if activities_match and activities_match.group(1).strip():
                activity_content = activities_match.group(1).strip()
                activity_content = re.sub(r'\*\*?', '', activity_content).strip()
                if activity_content and len(activity_content) > 5:
                    lesson_data["activities"].append(activity_content)
            # Don't continue - let subsequent lines be added to activities
        # Handle "Warmup:", "Cool Down:", etc. as activity headers
        elif re.match(r'^(warmup|warm-up|warm\s+up|cool\s+down|cooldown|cool-down|homework)[:\-]', line_lower):
            current_section = "activities"
            # Extract content after the header
            header_match = re.match(r'^(warmup|warm-up|warm\s+up|cool\s+down|cooldown|cool-down|homework)[:\-]\s*(.+)', line, flags=re.IGNORECASE)
            if header_match:
                header_name = header_match.group(1).strip()
                header_content = header_match.group(2).strip() if header_match.lastindex >= 2 else ""
                header_content = re.sub(r'\*\*?', '', header_content).strip()
                if header_content and len(header_content) > 5:
                    lesson_data["activities"].append(f"{header_name.title()}: {header_content}")
            # Don't continue - let subsequent lines be added to activities
        elif re.match(r'^\d*\.?\s*(activity|activities|procedure|lesson\s+procedure)', line_lower):
            # "Lesson Procedure" is a section header, not an activity
            if "procedure" in line_lower and "lesson" in line_lower:
                current_section = None  # Reset - procedure is a container section
            else:
                current_section = "activities"
            continue
        
        # Step-by-step format detection (e.g., "Step 1:", "Step 2:", "- **Step 1**:")
        elif re.search(r'step\s+\d+[:\-]', line_lower):
            current_section = "activities"
            # Extract step content - handle formats like "- **Step 1**: content" or "Step 1: content"
            step_text = re.sub(r'^[-•*]\s*', '', line, flags=re.IGNORECASE)  # Remove leading dash/bullet
            step_text = re.sub(r'\*\*?step\s+\d+[:\-]\s*\*\*?', '', step_text, flags=re.IGNORECASE)  # Remove "**Step 1:**"
            step_text = re.sub(r'step\s+\d+[:\-]\s*', '', step_text, flags=re.IGNORECASE)  # Remove "Step 1:"
            step_text = re.sub(r'\*\*?', '', step_text).strip()  # Remove any remaining bold markers
            if step_text and len(step_text) > 10:
                lesson_data["activities"].append(step_text)
            continue
        
        # Numbered items that are likely activities (after we've seen objectives/materials)
        # BUT: Skip if we're already in a special section (danielson, costas, standards, etc.)
        elif re.match(r'^\d+\.', line) and current_section is None:
            # If we've already processed objectives and materials, numbered items are likely activities
            # Check if this looks like an activity (has time, or activity keywords)
            if re.search(r'(minutes?|hours?|discussion|demonstration|simulation|exercise|review|practice|assignment|assessment)', line_lower):
                current_section = "activities"
        # If we're in danielson_framework or costas_questioning, numbered items should go there, not activities or materials
        # This check must come BEFORE materials detection to prevent misclassification
        elif re.match(r'^\d+\.', line) and current_section in ["danielson_framework", "costas_questioning", "curriculum_standards", "description"]:
            # These numbered items belong to the current section, not activities or materials
            # Skip the rest of the detection logic for this line - content processing will handle it
            continue
        
        # Section headers with time markers (e.g., "Instructional Content (45 minutes):", "Student Practice (45 minutes):")
        elif re.match(r'^[A-Z][a-z]+\s+(Content|Practice|Review|Assessment|Evaluation|Discussion|Demonstration|Instruction|Activity)\s*\(?\d+\s*minutes?\)?\s*[:\-]?', line, re.IGNORECASE):
            current_section = "activities"
            # Extract section name and content
            section_match = re.match(r'^([A-Z][a-z]+\s+(?:Content|Practice|Review|Assessment|Evaluation|Discussion|Demonstration|Instruction|Activity))\s*\(?\d+\s*minutes?\)?\s*[:\-]?\s*(.*)', line, re.IGNORECASE)
            if section_match:
                section_name = section_match.group(1).strip()
                section_content = section_match.group(2).strip() if section_match.lastindex >= 2 else ""
                if section_content and len(section_content) > 5:
                    lesson_data["activities"].append(f"{section_name}: {section_content}")
            # Don't continue - let subsequent numbered items be added to activities
        # Discussion detection (often part of activities) - handle "Discussion - 15 minutes" format
        elif re.search(r'^(discussion|demonstration|simulation|exercise|review|q&a|qa)\s*\(?\d+\s*minutes?\)?\s*[:\-]', line_lower):
            current_section = "activities"
            # Extract activity text from this line
            activity_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            activity_text = re.sub(r'\*\*?', '', activity_text)
            # Remove time patterns like "- 15 minutes" or "(15 minutes)"
            activity_text = re.sub(r'\s*\(?\d+\s*minutes?\)?\s*[:\-]?\s*', '', activity_text, flags=re.IGNORECASE)
            activity_text = re.sub(r'(discussion|demonstration|simulation|exercise|review|q&a|qa)[:\s]+', '', activity_text, flags=re.IGNORECASE).strip()
            if activity_text and len(activity_text) > 10:
                lesson_data["activities"].append(activity_text)
            # Don't continue - let subsequent numbered items be added to activities
        
        # Lesson Description detection - look for "Description:", "Overview:", "Lesson Description:", etc.
        elif re.search(r'(lesson\s+description|description|overview|lesson\s+overview|what\s+is\s+this\s+lesson)', line_lower) and i < 30:
            current_section = "description"
            # Extract description text from this line
            desc_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            desc_text = re.sub(r'\*\*?', '', desc_text)
            desc_text = re.sub(r'(lesson\s+description|description|overview|lesson\s+overview|what\s+is\s+this\s+lesson)[:\s]+', '', desc_text, flags=re.IGNORECASE).strip()
            if desc_text and len(desc_text) > 20:
                if lesson_data["description"]:
                    lesson_data["description"] += " " + desc_text
                else:
                    lesson_data["description"] = desc_text
            # Don't continue - let subsequent lines be added to description
        
        # Danielson Framework detection
        elif re.search(r'danielson\s+framework|domain\s+[1234]|framework\s+alignment', line_lower):
            current_section = "danielson_framework"
            # Extract framework text from this line (if any content after the header)
            framework_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            framework_text = re.sub(r'\*\*?', '', framework_text)
            framework_text = re.sub(r'(danielson\s+framework|framework\s+alignment)[:\s]+', '', framework_text, flags=re.IGNORECASE).strip()
            if framework_text and len(framework_text) > 10:
                if lesson_data["danielson_framework"]:
                    lesson_data["danielson_framework"] += "\n\n" + framework_text
                else:
                    lesson_data["danielson_framework"] = framework_text
            # Don't continue - let subsequent numbered items be added to framework
            # The next lines should be numbered items like "1. Planning and Preparation:"
        
        # Costa's Levels of Questioning detection
        elif re.search(r"costa'?s\s+level|level\s+[123]\s+question|questioning\s+level", line_lower):
            current_section = "costas_questioning"
            # Extract questioning text from this line
            questioning_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            questioning_text = re.sub(r'\*\*?', '', questioning_text)
            questioning_text = re.sub(r"(costa'?s\s+level|questioning\s+level)[:\s]+", '', questioning_text, flags=re.IGNORECASE).strip()
            if questioning_text and len(questioning_text) > 10:
                if lesson_data["costas_questioning"]:
                    lesson_data["costas_questioning"] += " " + questioning_text
                else:
                    lesson_data["costas_questioning"] = questioning_text
            # Don't continue - let subsequent lines be added to questioning
        
        # Curriculum Standards detection - improved to catch more variations
        elif re.search(r'(curriculum\s+standard|core\s+curriculum\s+standard|common\s+core|ngss|standard\s+[a-z0-9\.]+|state\s+standard|standards\s+alignment|aligned\s+with\s+standard)', line_lower):
            current_section = "curriculum_standards"
            # Extract standards text from this line
            standards_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            standards_text = re.sub(r'\*\*?', '', standards_text)
            standards_text = re.sub(r'(curriculum\s+standard|core\s+curriculum\s+standard|common\s+core|ngss|state\s+standard|standards\s+alignment|aligned\s+with\s+standard)[:\s]+', '', standards_text, flags=re.IGNORECASE).strip()
            if standards_text and len(standards_text) > 10:
                if lesson_data["curriculum_standards"]:
                    lesson_data["curriculum_standards"] += "\n\n" + standards_text
                else:
                    lesson_data["curriculum_standards"] = standards_text
            # Don't continue - let subsequent lines be added to standards
        
        # Exit Ticket detection
        elif re.search(r'exit\s+ticket|exit\s+slip|formative\s+assessment\s+\(exit', line_lower):
            current_section = "exit_ticket"
            # Extract exit ticket text from this line
            exit_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            exit_text = re.sub(r'\*\*?', '', exit_text)
            exit_text = re.sub(r'(exit\s+ticket|exit\s+slip|formative\s+assessment)[:\s]+', '', exit_text, flags=re.IGNORECASE).strip()
            if exit_text and len(exit_text) > 10:
                if lesson_data["exit_ticket"]:
                    lesson_data["exit_ticket"] += " " + exit_text
                else:
                    lesson_data["exit_ticket"] = exit_text
            # Don't continue - let subsequent lines be added to exit ticket
        
        # Worksheets detection - look for worksheet headers and content
        # CRITICAL: Only detect if it's clearly a worksheet section, not just "handout" in materials
        # Also detect if it starts with actual questions (numbered or lettered)
        elif (re.search(r'^\s*(worksheet|worksheets|activity\s+sheet|student\s+worksheet|worksheet\s+title|worksheet\s+instructions)', line_lower) and not re.search(r'(material|supply|equipment|resource)', line_lower)) or \
             (re.match(r'^\s*\d+[\.\)]\s+', line) and current_section == "worksheets"):
            # If we're already in worksheets section and see a numbered question, keep it
            if current_section != "worksheets":
                current_section = "worksheets"
                # Extract worksheet text from this line
                worksheet_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
                worksheet_text = re.sub(r'\*\*?', '', worksheet_text)
                worksheet_text = re.sub(r'(worksheet|worksheets|activity\s+sheet|student\s+worksheet|worksheet\s+title|worksheet\s+instructions)[:\s]+', '', worksheet_text, flags=re.IGNORECASE).strip()
                if worksheet_text and len(worksheet_text) > 5:
                    if lesson_data["worksheets"]:
                        lesson_data["worksheets"] += "\n\n" + worksheet_text
                    else:
                        lesson_data["worksheets"] = worksheet_text
            # Don't continue - let subsequent lines be added to worksheets
        
        # Rubrics detection - look for rubric headers and content
        elif re.search(r'^\s*(rubric|rubrics|assessment\s+rubric|scoring\s+rubric|evaluation\s+rubric)', line_lower):
            current_section = "rubrics"
            # Extract rubric text from this line
            rubric_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            rubric_text = re.sub(r'\*\*?', '', rubric_text)
            rubric_text = re.sub(r'(rubric|rubrics|assessment\s+rubric|scoring\s+rubric|evaluation\s+rubric)[:\s]+', '', rubric_text, flags=re.IGNORECASE).strip()
            if rubric_text and len(rubric_text) > 5:
                if lesson_data["rubrics"]:
                    lesson_data["rubrics"] += "\n\n" + rubric_text
                else:
                    lesson_data["rubrics"] = rubric_text
            # Don't continue - let subsequent lines be added to rubrics
        
        # Assessments detection (separate from general assessment section and rubrics)
        elif re.search(r'(summative\s+assessment|formative\s+assessment|assessment\s+criteria|assessment\s+questions)', line_lower) and current_section != "rubrics":
            current_section = "assessments"
            # Extract assessment text from this line
            assessment_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            assessment_text = re.sub(r'\*\*?', '', assessment_text)
            assessment_text = re.sub(r'(summative\s+assessment|formative\s+assessment|assessment\s+criteria|assessment\s+questions)[:\s]+', '', assessment_text, flags=re.IGNORECASE).strip()
            if assessment_text and len(assessment_text) > 10:
                if lesson_data["assessments"]:
                    lesson_data["assessments"] += " " + assessment_text
                else:
                    lesson_data["assessments"] = assessment_text
            # Don't continue - let subsequent lines be added to assessments
        
        # Assessment detection - handle "Assessment:" or "Assignment:" format
        elif re.search(r'(assessment|evaluation|homework|assignment)', line_lower):
            current_section = "assessment"
            # Extract assessment text from this line
            assessment_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            assessment_text = re.sub(r'\*\*?', '', assessment_text)
            assessment_text = re.sub(r'(assessment|evaluation|homework|assignment)[:\s]+', '', assessment_text, flags=re.IGNORECASE).strip()
            if assessment_text and len(assessment_text) > 10:
                lesson_data["assessment"] = assessment_text
            continue
        
        # Conclusion detection (can be part of activities or separate)
        elif re.match(r'^\d*\.?\s*(conclusion|wrap\s+up|summary)', line_lower):
            current_section = "activities"
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
        
        # Body/Content section - this is usually a container, reset section
        elif re.match(r'^\d*\.?\s*(body|content|main)', line_lower):
            current_section = None
            continue
        
        # Add content to current section
        if current_section:
            # Skip if this is a numbered section header (already processed above)
            if re.match(r'^\d+\.\s*\*\*[^*]+\*\*', line):
                # This was already handled by numbered_section_match above
                continue
            
            # For numbered items with bold headers, extract content after the colon
            # Pattern: "4. **Video Demonstration - 15 minutes**: Show students..."
            if re.match(r'^\d+\.\s*\*\*', line):
                # Extract content after the colon
                colon_match = re.search(r':\s*(.+)', line)
                if colon_match:
                    clean_line = colon_match.group(1).strip()
                    clean_line = re.sub(r'\*\*?', '', clean_line)  # Remove any remaining bold
                    # Remove time patterns like "- 15 minutes"
                    clean_line = re.sub(r'\s*-\s*\d+\s*minutes?[:\s]*', '', clean_line, flags=re.IGNORECASE).strip()
                else:
                    # No colon, extract after bold header
                    clean_line = re.sub(r'^\d+\.\s*\*\*[^*]+\*\*[:\s]*', '', line)
                    clean_line = re.sub(r'\*\*?', '', clean_line).strip()
            else:
                # Regular line processing
                # Handle "Step 1:", "Step 2:" format - these are activities
                if re.match(r'^step\s+\d+[:\-]', line_lower):
                    step_text = re.sub(r'^step\s+\d+[:\-]\s*', '', line, flags=re.IGNORECASE)
                    step_text = re.sub(r'\*\*?', '', step_text).strip()
                    clean_line = step_text
                else:
                    # Regular line - remove leading markers
                    clean_line = re.sub(r'^\d+\.?\s*\*\*?', '', line)  # Remove leading number and bold
                    clean_line = re.sub(r'\*\*?', '', clean_line)  # Remove all bold markers
                    clean_line = re.sub(r'^\d+\.?\s*[-•*]?\s*', '', clean_line)  # Remove any remaining list markers
                    clean_line = clean_line.strip()
            
            if not clean_line or len(clean_line) < 3:
                continue
            
            # Skip lines that are just section headers (unless they have content after)
            if re.match(r'^(introduction|objective|material|activity|assessment|discussion|conclusion|procedure|video|simulation|review|assignment|demonstration|exercise|q&a|qa)[:\s]*$', clean_line.lower()):
                continue
            
            if current_section == "description":
                # Handle description content - append lines to build comprehensive description
                if clean_line and len(clean_line) > 10:
                    # Skip if it's just a header or section marker
                    if not re.match(r'^(description|overview|lesson|introduction|objective|material|activity|assessment)[:\s]*$', clean_line.lower()):
                        if lesson_data["description"]:
                            lesson_data["description"] += " " + clean_line
                        else:
                            lesson_data["description"] = clean_line
            elif current_section == "introduction":
                # Handle numbered items within introduction (e.g., "1. Introduction to the importance...")
                if re.match(r'^\d+\.\s+', clean_line):
                    # This is a numbered sub-item - append to introduction
                    numbered_item = re.sub(r'^\d+\.\s+', '', clean_line).strip()
                    if lesson_data["introduction"]:
                        lesson_data["introduction"] += " " + numbered_item
                    else:
                        lesson_data["introduction"] = numbered_item
                else:
                    # Regular content - append to introduction
                    if lesson_data["introduction"]:
                        lesson_data["introduction"] += " " + clean_line
                    else:
                        lesson_data["introduction"] = clean_line
            elif current_section == "objectives":
                # Clean up "Objective:" prefix if present
                clean_line = re.sub(r'^objective[:\s]+', '', clean_line, flags=re.IGNORECASE)
                
                # Skip header lines like "Detailed (Using Bloom's Taxonomy):"
                if re.match(r'^(detailed|using|bloom|taxonomy)[:\s]*$', clean_line.lower()):
                    continue
                
                # Skip category markers like "- Remember:", "- Understand:", etc.
                if re.match(r'^[-•]\s*(remember|understand|apply|analyze|evaluate|create)[:\s]*$', clean_line.lower()):
                    continue
                
                # Only add if it's a complete learning objective (has action verb)
                if clean_line and len(clean_line) > 10:
                    # Check if it's a complete objective (has action verb)
                    if re.search(r'(will|can|should|students?\s+will|students?\s+can|students?\s+should|recall|explain|perform|demonstrate|identify|analyze|create|evaluate|understand|apply|remember)', clean_line.lower()):
                        lesson_data["objectives"].append(clean_line)
            elif current_section == "activities":
                if clean_line and len(clean_line) > 5:
                    # Skip lines that are just time markers like "(10 minutes)" or "(5 minutes)"
                    if re.match(r'^\(?\d+\s*(minutes?|mins?|hours?|hrs?)\)?\s*$', clean_line, re.IGNORECASE):
                        # This is just a time marker - skip it or append to previous activity if it exists
                        if lesson_data["activities"]:
                            # Add time to previous activity if it doesn't already have time info
                            last_activity = lesson_data["activities"][-1]
                            if not re.search(r'\(\d+\s*(minutes?|mins?|hours?|hrs?)\)', last_activity, re.IGNORECASE):
                                lesson_data["activities"][-1] = last_activity + " " + clean_line
                        continue
                    
                    # Skip lines that are just headers like "Cool Down:" without content
                    if re.match(r'^(warmup|warm-up|warm\s+up|cool\s+down|cooldown|cool-down|homework|assessment|activity|introduction|demonstration|practice|drill)[:\-]?\s*$', clean_line, re.IGNORECASE):
                        # Just a header, skip it - content should be on next line
                        continue
                    
                    # Handle numbered items within activities (e.g., "1. Demonstrate the steps...", "2. AED Introduction...")
                    if re.match(r'^\d+\.\s+', clean_line):
                        # This is a numbered sub-item - check if we should append to last activity or create new
                        numbered_item = re.sub(r'^\d+\.\s+', '', clean_line).strip()
                        # Remove leading dashes/bullets if present
                        numbered_item = re.sub(r'^[-•]\s*', '', numbered_item).strip()
                        
                        if lesson_data["activities"]:
                            # Check if last activity is a section header (like "Instructional Content (45 minutes):")
                            last_activity = lesson_data["activities"][-1]
                            if re.search(r'\(?\d+\s*minutes?\)?[:\-]?$', last_activity):
                                # Last activity is a section header - append numbered item to it
                                lesson_data["activities"][-1] = last_activity + " " + numbered_item
                            elif len(last_activity) < 100:
                                # Last activity is short - might be a header, append to it
                                lesson_data["activities"][-1] = last_activity + " " + numbered_item
                            else:
                                # Last activity is substantial - create new activity
                                lesson_data["activities"].append(numbered_item)
                        else:
                            # No activities yet - create new one
                            lesson_data["activities"].append(numbered_item)
                    else:
                        # Check if this is an incomplete sentence that should be merged with previous
                        # Incomplete sentences often start with lowercase, are short, or start with articles
                        is_incomplete = (
                            clean_line.startswith('-') or
                            clean_line.startswith('•') or
                            (len(clean_line) < 60 and lesson_data["activities"] and (
                                not re.match(r'^[A-Z]', clean_line) or  # Doesn't start with capital
                                re.match(r'^(A|An|The|And|Of|To|In|On|At|For|With|By)\s+', clean_line, re.IGNORECASE)  # Starts with article/preposition
                            ))
                        )
                        
                        if is_incomplete and lesson_data["activities"]:
                            # Append to last activity - this is a continuation
                            last_activity = lesson_data["activities"][-1]
                            # Remove leading dash/bullet and add as continuation
                            continuation = re.sub(r'^[-•]\s*', '', clean_line).strip()
                            lesson_data["activities"][-1] = last_activity + " " + continuation
                        else:
                            # New activity - but check if it's a partial line that should be merged
                            # If it's very short (< 30 chars) and previous activity exists, merge it
                            if len(clean_line) < 30 and lesson_data["activities"]:
                                last_activity = lesson_data["activities"][-1]
                                lesson_data["activities"][-1] = last_activity + " " + clean_line
                            else:
                                # New activity
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
                # CRITICAL: Stop worksheet extraction if we hit materials, activities, or other sections
                # Also stop if we see description language like "A worksheet with..." or "Students should..."
                if re.match(r'^(materials|activities|instruction|procedure|introduction|body|activity|discussion|conclusion|assessment|homework|danielson|costas|exit\s+ticket|assessments|begin\s+with|present\s+the|show\s+a|discuss|pair\s+students|circulate|i\s+hope|let\s+me\s+know)', clean_line.lower()):
                    current_section = None
                # Skip description lines (e.g., "A worksheet with...", "Students should write...")
                elif re.match(r'^(a\s+worksheet|students\s+should|the\s+worksheet|this\s+worksheet)', clean_line.lower()):
                    # This is a description, not actual worksheet content - skip it
                    continue
                elif clean_line and len(clean_line) > 3:
                    # Skip lines that are just section headers or closing text
                    if not re.match(r'^(lesson|procedure|introduction|body|activity|discussion|conclusion|assessment|homework|this\s+is|always\s+remember|feel\s+free)', clean_line.lower()):
                        # Skip if it looks like materials (e.g., "- CPR mannequins", "- Safety gloves")
                        if not re.match(r'^[-•]\s+(cpr|safety|step-by-step|instructional)', clean_line.lower()):
                            # Check if it's a description vs actual content
                            # Descriptions usually start with "A worksheet", "Students should", "The key should"
                            if not re.match(r'^(a\s+worksheet|students\s+should|the\s+key\s+should|the\s+worksheet)', clean_line.lower()):
                                if lesson_data["worksheets"]:
                                    # Add newline for better formatting, especially for numbered items
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
                # Handle numbered items (e.g., "1. Planning and Preparation:: content")
                if re.match(r'^\d+\.', clean_line):
                    # Remove the number prefix
                    content = re.sub(r'^\d+\.\s*', '', clean_line).strip()
                    # Remove double colons if present
                    content = re.sub(r'::\s*', ': ', content)
                    # Remove bold markers
                    content = re.sub(r'\*\*?', '', content).strip()
                    if content and len(content) > 5:
                        if lesson_data["danielson_framework"]:
                            lesson_data["danielson_framework"] += "\n\n" + content
                        else:
                            lesson_data["danielson_framework"] = content
                else:
                    # Regular content line
                    if clean_line and len(clean_line) > 3:
                        if lesson_data["danielson_framework"]:
                            lesson_data["danielson_framework"] += " " + clean_line
                        else:
                            lesson_data["danielson_framework"] = clean_line
            elif current_section == "costas_questioning":
                # Handle numbered items (e.g., "1. Gathering:: content")
                if re.match(r'^\d+\.', clean_line):
                    # Remove the number prefix
                    content = re.sub(r'^\d+\.\s*', '', clean_line).strip()
                    # Remove double colons if present
                    content = re.sub(r'::\s*', ': ', content)
                    # Remove bold markers
                    content = re.sub(r'\*\*?', '', content).strip()
                    if content and len(content) > 5:
                        if lesson_data["costas_questioning"]:
                            lesson_data["costas_questioning"] += "\n\n" + content
                        else:
                            lesson_data["costas_questioning"] = content
                else:
                    # Regular content line
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
                # Skip lines that are section headers, numbered headers, or homework/closing text
                if not re.match(r'^(\d+\.?\s+)?(lesson|procedure|introduction|body|activity|discussion|conclusion|assessment|homework|materials|this\s+is|always\s+remember)', clean_line.lower()):
                    # Skip if it's just a number or section header
                    if clean_line and not re.match(r'^\d+\.?\s*$', clean_line) and len(clean_line) > 3:
                        lesson_data["materials"].append(clean_line)
    
    # Extract title from original message or response
    if not lesson_data["title"]:
        # First, try to extract from original message
        if original_message:
            # Try "lesson plan on [topic]"
            title_match = re.search(r'lesson\s+plan\s+(?:on|for|about)\s+(.+?)(?:\.|$|please)', original_message, flags=re.IGNORECASE)
            if not title_match:
                # Try "lesson on [topic]"
                title_match = re.search(r'lesson\s+(?:on|for|about)\s+(.+?)(?:\.|$|please)', original_message, flags=re.IGNORECASE)
            if title_match:
                topic = title_match.group(1).strip()
                # Clean up common prefixes
                topic = re.sub(r'^(a|an|the)\s+', '', topic, flags=re.IGNORECASE)
                lesson_data["title"] = topic.title() + " Lesson Plan"
        
        # If still no title, check response text
        if not lesson_data["title"]:
            for line in lines[:10]:  # Check first 10 lines
                line = line.strip()
                if not line:
                    continue
                # Look for "Title:" pattern
                title_match = re.search(r'title[:\s]+(.+)', line, flags=re.IGNORECASE)
                if title_match:
                    lesson_data["title"] = re.sub(r'\*\*', '', title_match.group(1)).strip()
                    break
                # Look for "lesson plan on [topic]" pattern
                title_match = re.search(r'lesson\s+plan\s+(?:on|for)\s+(.+?)(?:\.|$)', line, flags=re.IGNORECASE)
                if title_match:
                    lesson_data["title"] = title_match.group(1).strip().title()
                    break
                # Look for "Defensive Driving" or similar topic in first line
                # Pattern: "I can help you create a lesson plan on [topic]"
                title_match = re.search(r'(?:lesson\s+plan|create|help)\s+(?:on|for|about)\s+(.+?)(?:\.|$)', line, flags=re.IGNORECASE)
                if title_match:
                    topic = title_match.group(1).strip()
                    # Clean up common prefixes
                    topic = re.sub(r'^(a|an|the)\s+', '', topic, flags=re.IGNORECASE)
                    lesson_data["title"] = topic.title()
                    break
                # Or use first substantial line as title (skip greetings)
                elif len(line) < 100 and not re.match(r'^(absolutely|sure|here|i\s+can|i\s+apologize)', line.lower()):
                    clean_title = re.sub(r'\*\*', '', line).strip()
                    # Skip if it's just a greeting
                    if not re.match(r'^(absolutely|sure|here|i\s+can|i\s+apologize)', clean_title.lower()):
                        lesson_data["title"] = clean_title
                        break
    
    # Clean up objectives - remove "Objective:" prefix
    lesson_data["objectives"] = [
        re.sub(r'^objective[:\s]+', '', obj, flags=re.IGNORECASE).strip()
        for obj in lesson_data["objectives"]
        if obj and len(obj) > 10
    ]
    
    # If we found meaningful data, return it
    # Also check if we have activities (step-by-step format) even without other structured data
    has_activities = len(lesson_data["activities"]) > 0
    has_objectives = len(lesson_data["objectives"]) > 0
    has_introduction = bool(lesson_data["introduction"])
    has_title = bool(lesson_data["title"])
    
    # If we have activities (like step-by-step), create a basic lesson plan
    if has_activities and not (has_objectives or has_introduction or has_title):
        # Extract title from original message if we have activities
        if original_message:
            title_match = re.search(r'lesson\s+(?:plan\s+)?(?:on|for|about)\s+(.+?)(?:\.|$|please)', original_message, flags=re.IGNORECASE)
            if title_match:
                topic = title_match.group(1).strip()
                topic = re.sub(r'^(a|an|the)\s+', '', topic, flags=re.IGNORECASE)
                lesson_data["title"] = topic.title() + " Lesson Plan"
            else:
                # Use first activity as title hint
                lesson_data["title"] = "Lesson Plan"
        
        # Create a simple objective from the activities
        if not lesson_data["objectives"]:
            lesson_data["objectives"].append("Understand the key concepts and steps presented in this lesson.")
        
        # Use first activity as introduction if no intro
        if not lesson_data["introduction"] and lesson_data["activities"]:
            first_activity = lesson_data["activities"][0]
            lesson_data["introduction"] = first_activity[:200] + "..." if len(first_activity) > 200 else first_activity
    
    if has_activities or has_objectives or has_introduction or has_title:
        return lesson_data
    
    return None

class ChatMessageRequest(BaseModel):
    message: str
    context: Optional[List[Dict[str, str]]] = None

class ChatMessageResponse(BaseModel):
    response: str
    widgets: Optional[Dict[str, Any]] = None
    widget_data: Optional[Dict[str, Any]] = None

@router.post("/chat/message", response_model=ChatMessageResponse)
async def guest_chat_message(
    request: ChatMessageRequest,
    authorization: Optional[str] = Header(None),
    x_guest_name: Optional[str] = Header(None, alias="X-Guest-Name")
) -> JSONResponse:
    """
    Send a message to the AI assistant (guest-friendly, no authentication required).
    This endpoint allows users to chat with the AI assistant without logging in.
    """
    try:
        settings = get_settings()
        
        if not settings.OPENAI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured"
            )
        
        # Initialize OpenAI client
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Prepare messages for OpenAI
        messages = []
        
        # Use condensed system prompt to save tokens (full opening prompt remains in HTML for TTS)
        # Condensed version maintains all critical requirements while reducing token usage by ~40-50%
        from app.core.ai_system_prompts import CONDENSED_SYSTEM_PROMPT
        system_prompt = CONDENSED_SYSTEM_PROMPT
        
        # Try to get user's first name from token if available, or from guest name header
        user_first_name = None
        
        # First, check if guest provided their name via header (stored in sessionStorage)
        if x_guest_name:
            user_first_name = x_guest_name.strip()
            logger.info(f"Using guest name from header: {user_first_name}")
        
        # If not from header, try to extract from token (for authenticated users)
        if not user_first_name and authorization:
            try:
                from jose import jwt
                
                # Extract token from "Bearer <token>"
                if authorization.startswith("Bearer "):
                    token = authorization.split(" ")[1]
                    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
                    
                    # Try to get first name from token payload
                    user_first_name = payload.get("first_name") or payload.get("firstName")
                    
                    # If not in token, try to get from database (check both User and TeacherRegistration)
                    if not user_first_name:
                        from app.core.database import SessionLocal
                        from app.models.core.user import User
                        db = SessionLocal()
                        try:
                            email = payload.get("email") or payload.get("sub")
                            if email:
                                # Try User model first
                                user = db.query(User).filter(User.email == email).first()
                                if user and user.first_name:
                                    user_first_name = user.first_name
                                else:
                                    # Try TeacherRegistration model
                                    from app.models.teacher_registration import TeacherRegistration
                                    teacher = db.query(TeacherRegistration).filter(TeacherRegistration.email == email).first()
                                    if teacher:
                                        # Try to get first name from teacher
                                        user_first_name = getattr(teacher, 'first_name', None) or getattr(teacher, 'name', None)
                                        # If name is full name, extract first name
                                        if not user_first_name and hasattr(teacher, 'name') and teacher.name:
                                            name_parts = teacher.name.split()
                                            if name_parts:
                                                user_first_name = name_parts[0]
                        except Exception as e:
                            logger.warning(f"Could not get user name from database: {e}")
                        finally:
                            db.close()
            except Exception as e:
                logger.debug(f"Could not extract user name from token: {e}")
        
        # Personalize system prompt with user's first name if available
        # We'll check the user message after adding system prompt to see if it's just a name
        if user_first_name:
            logger.info(f"Personalizing chat with user's first name: {user_first_name}")
            system_prompt = f"{system_prompt}\n\nCRITICAL: The user's first name is {user_first_name}. You MUST always refer to them by their first name ({user_first_name}) in EVERY response to make the conversation personal and friendly. Use their name naturally in your greetings and throughout the conversation. For example: 'Hello {user_first_name}!', 'Sure, {user_first_name}, I can help with that.', '{user_first_name}, here's what I recommend...'"
        else:
            logger.debug("No user first name found, proceeding without personalization")
            # Even without a name in header, check if name might be in conversation context
            # Add instruction to use name if user provides it
            system_prompt = f"{system_prompt}\n\nIMPORTANT: If the user provides their name in the conversation (e.g., 'my name is X', 'I'm X', or just 'X'), you MUST remember it and use it in all subsequent responses. Always refer to users by their name when you know it to make conversations more personal and friendly."
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Define available functions for OpenAI
        functions = [
            {
                "type": "function",
                "function": {
                    "name": "send_sms",
                    "description": "Send an SMS/text message to a phone number using Twilio",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to_number": {
                                "type": "string",
                                "description": "The recipient's phone number in E.164 format (e.g., +1234567890). Must include country code."
                            },
                            "message": {
                                "type": "string",
                                "description": "The message content to send"
                            }
                        },
                        "required": ["to_number", "message"]
                    }
                }
            }
        ]
        
        # Check if this is a lesson plan request early (needed for context limiting)
        message_lower = request.message.lower()
        # Check for health/nutrition requests first to avoid false matches
        health_keywords = ["meal plan", "meal planning", "nutrition", "diet", "diet plan", "calorie", "calories", "protein", "carb", "macros", "meal prep", "eating plan", "food plan", "nutrition plan", "wrestler", "weight loss", "weight gain", "cutting", "bulking", "meal", "breakfast", "lunch", "dinner", "snack", "nutritional"]
        is_health_request_early = any(keyword in message_lower for keyword in health_keywords)
        
        # Lesson plan keywords - make more specific to avoid matching "meal plan"
        lesson_keywords = ["lesson plan", "lesson planning", "curriculum", "teaching", "class", "student", "grade", "learning objective", "education", "pedagogy", "instruction", "teaching plan"]
        # Exclude health requests to avoid false matches
        is_lesson_request = any(keyword in message_lower for keyword in lesson_keywords) and not is_health_request_early
        
        # Add conversation context if provided (limit to prevent token overflow)
        # CRITICAL: For lesson plans, system prompt is very long (~4500 tokens), so limit context even more
        # Truncate long messages to keep within token limits
        # Get system prompt size for context limiting (defined earlier in function)
        system_prompt_size = len(system_prompt)
        
        if request.context:
            # For lesson plans, limit to 1 context message; for others, allow 2
            # But if system prompt is long, reduce context even more
            context_limit = 1 if is_lesson_request else 2
            
            # If system prompt is very long, reduce context limit
            if system_prompt_size > 15000:  # Very long system prompt (~4500 tokens)
                context_limit = 1  # Only allow 1 context message
                logger.info(f"System prompt is very long ({system_prompt_size} chars), reducing context limit to 1")
            
            for ctx in request.context[:context_limit]:
                if isinstance(ctx, dict) and 'role' in ctx and 'content' in ctx:
                    content = ctx['content']
                    # Truncate very long messages to prevent token overflow
                    # For lesson plans or long system prompts, truncate more aggressively
                    max_length = 200 if (is_lesson_request or system_prompt_size > 15000) else 400
                    if len(content) > max_length:
                        content = content[:max_length] + "..."
                        logger.debug(f"Truncated context message from {len(ctx['content'])} to {len(content)} characters")
                    messages.append({
                        "role": ctx['role'],
                        "content": content
                    })
        
        # Add current user message (truncate if very long to prevent token overflow)
        user_message = request.message
        
        # Check if the message is just a name (user providing their name)
        # This handles cases where user just types their name like "antoinette" or "bob"
        if not user_first_name:  # Only check if we don't already have a name
            trimmed_message = user_message.strip()
            logger.debug(f"Checking if message is a name: '{trimmed_message}' (length: {len(trimmed_message)})")
            # Check if message is just a name (2-20 letters, no spaces, no special chars, no numbers)
            if len(trimmed_message) >= 2 and len(trimmed_message) <= 20 and re.match(r'^[a-zA-Z]+$', trimmed_message):
                # This looks like a name - extract and use it
                extracted_name = trimmed_message.capitalize()
                user_first_name = extracted_name
                logger.info(f"✅ Detected name in user message: '{extracted_name}' (from '{trimmed_message}'), updating system prompt")
                # Update system prompt to include the name
                updated_system_prompt = f"{system_prompt}\n\nCRITICAL: The user's first name is {extracted_name}. You MUST always refer to them by their first name ({extracted_name}) in EVERY response to make the conversation personal and friendly. Use their name naturally in your greetings and throughout the conversation. For example: 'Hello {extracted_name}!', 'Sure, {extracted_name}, I can help with that.', '{extracted_name}, here's what I recommend...'"
                # Update the system message in messages array
                messages[-1]["content"] = updated_system_prompt  # Update the last message (system prompt)
                # Modify user message to be more explicit about providing name
                user_message = f"My name is {extracted_name}."
                logger.info(f"✅ Updated user message from '{request.message}' to '{user_message}' and system prompt updated with name")
            else:
                logger.debug(f"Message '{trimmed_message}' does not match name pattern (length: {len(trimmed_message)}, regex match: {bool(re.match(r'^[a-zA-Z]+$', trimmed_message))})")
        
        if len(user_message) > 1000:  # Truncate very long user messages
            user_message = user_message[:1000] + "..."
            logger.warning(f"Truncated user message from {len(request.message)} to {len(user_message)} characters")
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        logger.info(f"Guest chat request: {len(messages)} messages in context, is_lesson_request={is_lesson_request}")
        
        # Estimate token count (more accurate: 1 token ≈ 3.5 characters for English text)
        # Count total characters in all messages, including system prompt
        total_chars = sum(len(str(msg.get('content', ''))) for msg in messages)
        # For lesson plans, use slightly more optimistic estimation (3.6 chars/token) 
        # since system prompts are mostly English and compress better
        # For other requests, use 3.5 chars/token
        chars_per_token = 3.6 if is_lesson_request else 3.5
        estimated_tokens = int(total_chars / chars_per_token)
        logger.info(f"Estimated token count: ~{estimated_tokens} tokens (from {total_chars} characters, using {chars_per_token} chars/token)")
        
        # Call OpenAI API with function calling (with timeout)
        import asyncio
        try:
            logger.info(f"Calling OpenAI API with {len(messages)} messages, {len(functions)} functions")
            response_lower = ""  # Will be set after first response if needed
            
            # Use longer timeout and more tokens for lesson plans to allow comprehensive responses
            # CRITICAL: Keep max_tokens lower to avoid exceeding model's 8192 token limit
            # System prompt is ~4500 tokens, so we need to limit max_tokens to ~3000-3500
            # Increase timeout for all requests - meal plans and complex requests can take longer
            timeout_seconds = 60.0 if is_lesson_request else 45.0  # Increased from 30 to 45 seconds
            
            # Dynamically adjust max_tokens based on estimated context length
            # For lesson plans, we use gpt-4-turbo (128k context) so we have much more room
            # For regular requests, we use gpt-4 (8k context) so we need to be more careful
            if is_lesson_request:
                # Turbo model: 128k context limit, but max 4096 completion tokens
                # So we can use the full 4096 tokens for complete lesson plans
                base_max_tokens = 4096  # Turbo's maximum completion tokens (hard limit)
                safety_margin = 50  # Small margin
                functions_overhead = 100  # Functions overhead
                # With 128k context, we have plenty of room for input, but output is capped at 4096
                available_tokens = 100000  # Turbo has 128k context, so input space is not a concern
                min_tokens = 3500  # Ensure at least 3500 tokens for complete responses
                # Cap at 4096 (turbo's hard limit) even if we calculated higher
                max_tokens_value = min(4096, max(min_tokens, min(base_max_tokens, available_tokens)))
            else:
                # Regular gpt-4: 8k context limit, need to be careful
                base_max_tokens = 2000
                safety_margin = 200
                functions_overhead = 150
                available_tokens = 8192 - estimated_tokens - functions_overhead - safety_margin
                min_tokens = 500
                max_tokens_value = max(min_tokens, min(base_max_tokens, available_tokens))
            
            # If we're still constrained for lesson plans, log a warning
            if is_lesson_request and max_tokens_value < 3500:
                logger.warning(f"⚠️ Lesson plan max_tokens ({max_tokens_value}) may be insufficient for complete responses. Estimated context: {estimated_tokens} tokens")
            
            if max_tokens_value < base_max_tokens:
                logger.warning(f"Reduced max_tokens from {base_max_tokens} to {max_tokens_value} due to long context (estimated {estimated_tokens} tokens, available: {available_tokens})")
            else:
                logger.info(f"Using full max_tokens={max_tokens_value} for {'lesson plan' if is_lesson_request else 'regular'} request")
            
            logger.info(f"Using max_tokens={max_tokens_value} (estimated context: {estimated_tokens} tokens, available: {available_tokens})")
            
            # For lesson plans, use gpt-4-turbo which has 128k context window (vs 8k for gpt-4)
            # This allows for much longer, complete lesson plan responses
            # For other requests, use gpt-4 to save costs
            model_name = "gpt-4-turbo-preview" if is_lesson_request else "gpt-4"
            logger.info(f"Using model: {model_name} for {'lesson plan' if is_lesson_request else 'regular'} request")
            
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.chat.completions.create,
                    model=model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=max_tokens_value,
                    tools=[{"type": "function", "function": func["function"]} for func in functions],
                    tool_choice="auto"
                ),
                timeout=timeout_seconds
            )
            logger.info(f"OpenAI API call successful, response received")
        except asyncio.TimeoutError:
            logger.error("OpenAI API call timed out after 30 seconds")
            raise HTTPException(
                status_code=504,
                detail="Request timeout - AI response took too long. Please try again with a shorter message."
            )
        except Exception as api_error:
            error_type = type(api_error).__name__
            error_msg = str(api_error) if str(api_error) else repr(api_error)
            logger.error(f"OpenAI API call failed: {error_type}: {error_msg}")
            logger.exception("OpenAI API error traceback:")
            
            # Check for specific error types and provide user-friendly messages
            if error_type == "RateLimitError" or "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
                raise HTTPException(
                    status_code=503,  # Service Unavailable
                    detail="AI service is currently unavailable due to quota limits. Please check your OpenAI account billing or try again later."
                )
            elif error_type == "AuthenticationError" or "invalid_api_key" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail="AI service authentication error. Please contact support."
                )
            elif error_type == "BadRequestError" and ("context_length_exceeded" in error_msg.lower() or "maximum context length" in error_msg.lower()):
                # Context length exceeded - provide helpful error message
                logger.warning(f"Context length exceeded: {error_msg}")
                raise HTTPException(
                    status_code=400,
                    detail="Your message or conversation history is too long. Please try a shorter message or start a new conversation."
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"AI service error: {error_type}. Please try again later."
                )
        
        message = response.choices[0].message
        ai_response = message.content
        
        # Check if response was cut off due to token limit
        finish_reason = response.choices[0].finish_reason if response.choices else None
        if finish_reason == "length":
            logger.warning(f"⚠️ Response was cut off due to token limit (finish_reason=length). Response length: {len(ai_response) if ai_response else 0} chars, max_tokens was: {max_tokens_value}")
            # For lesson plans, this is a problem - we need more tokens
            if is_lesson_request:
                logger.error(f"❌ Lesson plan response incomplete due to token limit! Consider increasing max_tokens further.")
        
        # Initialize extracted content for function results
        extracted_content = {
            "images": [],
            "file_content": None,
            "filename": None,
            "web_url": None,
            "file_id": None,
            "widget_data": None
        }
        
        # Handle function calls
        if message.tool_calls:
            logger.info(f"AI requested {len(message.tool_calls)} function calls")
            
            # Add assistant message with tool calls to conversation
            messages.append({
                "role": "assistant",
                "content": ai_response,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })
            
            # Store function results to include in response (for images, documents, etc.)
            function_results = []
            
            # Execute function calls
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                result = None
                
                if function_name == "send_sms":
                    twilio_service = get_twilio_service()
                    result = await twilio_service.send_sms(
                        to_number=function_args["to_number"],
                        message=function_args["message"]
                    )
                    
                    if result.get("status") in ["success", "pending"]:
                        logger.info(f"SMS sent successfully: {result.get('message_sid', 'unknown')}, Twilio status: {result.get('twilio_status', 'unknown')}")
                    else:
                        logger.warning(f"SMS send failed: {result.get('error', 'unknown error')}")
                elif function_name in ["generate_image", "create_powerpoint_presentation", "create_word_document", 
                                       "create_pdf_document", "create_excel_spreadsheet"]:
                    # Handle content generation functions using GPTFunctionService
                    try:
                        from app.dashboard.services.gpt_function_service import GPTFunctionService
                        from app.core.database import SessionLocal
                        
                        db = SessionLocal()
                        try:
                            # Get user_id from token if available, otherwise use None for guest
                            user_id = None
                            if authorization and authorization.startswith("Bearer "):
                                token = authorization[7:]
                                # Try to extract user_id from token (simplified - in production, decode JWT)
                                # For now, use a placeholder
                                user_id = "guest"
                            
                            gpt_function_service = GPTFunctionService(db=db, user_id=user_id)
                            result = await gpt_function_service._execute_function_call(
                                function_name=function_name,
                                arguments=function_args,
                                user_id=user_id or "guest"
                            )
                            
                            # Store result for response and extract content
                            if result:
                                function_results.append(result)
                                
                                # Extract images, file_content, web_url, etc. for frontend display
                                if result.get("images"):
                                    extracted_content["images"] = result.get("images", [])
                                if result.get("file_content"):
                                    extracted_content["file_content"] = result.get("file_content")
                                    extracted_content["filename"] = result.get("filename")
                                if result.get("web_url"):
                                    extracted_content["web_url"] = result.get("web_url")
                                    extracted_content["file_id"] = result.get("file_id")
                                    extracted_content["filename"] = result.get("filename")
                                if result.get("widget_data"):
                                    extracted_content["widget_data"] = result.get("widget_data")
                                
                                logger.info(f"Function {function_name} executed successfully")
                        finally:
                            db.close()
                    except Exception as func_error:
                        logger.error(f"Error executing function {function_name}: {str(func_error)}")
                        result = {"status": "error", "error": str(func_error)}
                    
                    # Add function result to conversation (result is always a dict)
                if result:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
            
            # Get final response from AI after function execution (with timeout)
            try:
                final_response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.chat.completions.create,
                        model="gpt-4",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=2000,
                        tools=[{"type": "function", "function": func["function"]} for func in functions],
                        tool_choice="auto"
                    ),
                    timeout=30.0  # 30 second timeout
                )
                final_message = final_response.choices[0].message
                ai_response = final_message.content
                
                # If AI wants to call another function, handle it (up to 2 iterations to avoid loops)
                if final_message.tool_calls:
                    logger.info("AI requested additional function calls after SMS attempt")
                    # For now, just use the content if available, or provide a helpful message
                    if not ai_response:
                        ai_response = "I attempted to send the message, but encountered an issue. Please check the error details above."
            except asyncio.TimeoutError:
                # If timeout on final response, return what we have
                logger.warning("Timeout on final AI response, returning partial response")
                if not ai_response:
                    ai_response = "I've processed your request, but the response is taking longer than expected. Please try again."
            except Exception as final_error:
                error_type = type(final_error).__name__
                error_msg = str(final_error) if str(final_error) else repr(final_error)
                logger.error(f"OpenAI API final response call failed: {error_type}: {error_msg}")
                logger.exception("Final response error traceback:")
                if not ai_response:
                    ai_response = f"I encountered an error while processing your request. Please try again."
        
        logger.info(f"Guest chat response: {len(ai_response) if ai_response else 0} characters")
        
        # Detect widget type and extract structured data
        # GUEST USERS: Limited functionality - basic chat only, no advanced lesson plan generation
        # Advanced features (worksheets, rubrics, 3-step generation) are ONLY for authenticated/paying users
        widget_data = None
        message_lower = request.message.lower()
        response_lower = (ai_response or "").lower()
        
        # GUEST USERS: Widget detection - check in priority order
        # 1. Health/Nutrition/Meal Plan requests (BEFORE lesson plans to avoid false matches)
        # 2. Lesson plan requests
        # 3. Fitness/workout requests
        
        # Health/Nutrition keywords - check FIRST to avoid "meal plan" being misclassified as "lesson plan"
        health_keywords = ["meal plan", "meal planning", "nutrition plan", "nutrition planning", "nutrition", "diet", "diet plan", "calorie", "calories", "protein", "carb", "macros", "meal prep", "eating plan", "food plan", "wrestler", "weight loss plan", "weight loss", "weight gain plan", "weight gain", "cutting plan", "cutting", "bulking plan", "bulking", "meal", "breakfast", "lunch", "dinner", "snack", "nutritional"]
        is_health_request = any(keyword in message_lower for keyword in health_keywords) or any(keyword in response_lower for keyword in ["meal", "nutrition", "diet", "calorie", "protein", "carb", "macro", "breakfast", "lunch", "dinner"])
        
        # Lesson plan keywords - make more specific to avoid matching "meal plan"
        lesson_keywords = ["lesson plan", "lesson planning", "curriculum", "teaching", "class", "student", "grade", "learning objective", "education", "pedagogy", "instruction", "teaching plan"]
        # Exclude "plan" alone to avoid matching "meal plan", "diet plan", etc.
        is_lesson_request = (any(keyword in message_lower for keyword in lesson_keywords) or 
                            any(keyword in response_lower for keyword in ["lesson plan", "learning objective", "students will", "grade level", "curriculum"])) and not is_health_request
        
        if is_health_request:
            # GUEST USERS: Create preview/teaser widget for health/nutrition
            logger.info(f"Guest user requested health/nutrition/meal plan - creating preview widget (teaser)")
            
            # Extract basic info from message
            meal_title = ""
            if request.message:
                # Try to extract topic from message
                title_match = re.search(r'meal\s+plan\s+(?:for|on|about)\s+(.+?)(?:\.|$|please|in|that)', request.message, flags=re.IGNORECASE)
                if not title_match:
                    title_match = re.search(r'(?:make|create|generate|give)\s+(?:me\s+)?(?:a\s+)?(?:meal\s+plan|diet\s+plan|nutrition\s+plan)\s+(?:for|on|about)?\s*(.+?)(?:\.|$|please|in|that)', request.message, flags=re.IGNORECASE)
                if title_match:
                    topic = title_match.group(1).strip()
                    meal_title = topic.title() + " Meal Plan"
            
            if not meal_title:
                meal_title = "Meal Plan Preview"
            
            # Create preview widget data
            preview_data = {
                "title": meal_title,
                "description": "[Detailed meal plan description would appear here - Premium Feature]",
                "daily_calories": "[Daily calorie target would appear here - Premium Feature]",
                "macros": {
                    "protein": "[Protein target would appear here]",
                    "carbs": "[Carb target would appear here]",
                    "fat": "[Fat target would appear here]"
                },
                "meals": [
                    {"meal": "Breakfast", "foods": "[Breakfast foods would appear here - Premium Feature]"},
                    {"meal": "Lunch", "foods": "[Lunch foods would appear here - Premium Feature]"},
                    {"meal": "Dinner", "foods": "[Dinner foods would appear here - Premium Feature]"},
                    {"meal": "Snacks", "foods": "[Snacks would appear here - Premium Feature]"}
                ],
                "is_preview": True,
                "preview_message": "This is a preview of what a complete meal plan would include. Sign up for a premium account to generate full, personalized meal plans with detailed nutrition information, recipes, and meal prep guides."
            }
            
            widget_data = {
                "type": "health",
                "data": preview_data
            }
            logger.info(f"✅ Created preview health/nutrition widget for guest user")
        elif is_lesson_request:
            # GUEST USERS: Create preview/teaser widget showing lesson plan structure
            # This shows what a full lesson plan would include, but with placeholder text
            logger.info(f"Guest user requested lesson plan - creating preview widget (teaser)")
            
            # Extract basic lesson info from AI response for preview
            lesson_title = ""
            original_message = request.message  # Store for title extraction
            
            # Try to extract topic from original message
            if original_message:
                title_match = re.search(r'lesson\s+plan\s+(?:on|for|about)\s+(.+?)(?:\.|$|please)', original_message, flags=re.IGNORECASE)
                if not title_match:
                    title_match = re.search(r'lesson\s+(?:on|for|about)\s+(.+?)(?:\.|$|please)', original_message, flags=re.IGNORECASE)
                if title_match:
                    topic = title_match.group(1).strip()
                    topic = re.sub(r'^(a|an|the)\s+', '', topic, flags=re.IGNORECASE)
                    lesson_title = topic.title() + " Lesson Plan"
            
            # If no title from message, try to extract from AI response
            if not lesson_title and ai_response:
                lines = ai_response.split('\n')[:10]
                for line in lines:
                    line = line.strip()
                    if "title:" in line.lower():
                        title_match = re.search(r'title[:\s]+(.+)', line, flags=re.IGNORECASE)
                        if title_match:
                            lesson_title = re.sub(r'\*\*', '', title_match.group(1)).strip()
                            break
                    elif len(line) < 100 and not re.match(r'^(absolutely|sure|here|i\s+can|i\s+apologize)', line.lower()):
                        clean_title = re.sub(r'\*\*', '', line).strip()
                        if not re.match(r'^(absolutely|sure|here|i\s+can|i\s+apologize)', clean_title.lower()):
                            lesson_title = clean_title
                            break
            
            # Create preview widget data with placeholder structure
            preview_data = {
                "title": lesson_title or "Lesson Plan Preview",
                "description": "[Detailed description of the lesson would appear here - Premium Feature]",
                "objectives": ["[Learning objectives would appear here - Premium Feature]"],
                "grade_level": "[Grade level would appear here]",
                "subject": "[Subject would appear here]",
                "duration": "[Duration would appear here]",
                "materials": ["[Materials list would appear here - Premium Feature]"],
                "activities": ["[Step-by-step activities would appear here - Premium Feature]"],
                "assessment": "[Assessment criteria would appear here - Premium Feature]",
                "introduction": "[Introduction would appear here - Premium Feature]",
                "danielson_framework": "[Danielson Framework alignment would appear here - Premium Feature]",
                "costas_questioning": "[Costa's Levels of Questioning would appear here - Premium Feature]",
                "curriculum_standards": "[Core Curriculum Standards would appear here - Premium Feature]",
                "exit_ticket": "[Exit ticket would appear here - Premium Feature]",
                "worksheets": "[Complete worksheets with 10+ questions and answer keys would appear here - Premium Feature]",
                "assessments": "[Comprehensive assessments would appear here - Premium Feature]",
                "rubrics": "[Detailed rubrics with criteria and performance levels would appear here - Premium Feature]",
                "is_preview": True,  # Flag to indicate this is a preview/teaser
                "preview_message": "This is a preview of what a complete lesson plan would include. Sign up for a premium account to generate full, professional-grade lesson plans with worksheets, rubrics, and all components."
            }
            
            widget_data = {
                "type": "lesson-planning",
                "data": preview_data
            }
            logger.info(f"✅ Created preview lesson plan widget for guest user")
        else:
            # Check if this is a workout/fitness related request (more specific keywords, excluding "plan" alone)
            fitness_keywords = ["workout", "exercise", "fitness", "chest", "training", "routine", "muscle", "strength", "cardio", "gym", "weight", "lifting", "squat", "bench", "deadlift"]
            is_fitness_request = any(keyword in message_lower for keyword in fitness_keywords) or any(keyword in response_lower for keyword in ["exercise", "workout", "sets", "reps", "push", "pull", "squat", "bench", "deadlift"])
            
            if is_fitness_request:
                logger.info(f"Detected workout/fitness request (message: '{request.message[:50]}...'), extracting data from response")
                logger.info(f"Response preview: {ai_response[:200] if ai_response else 'None'}...")
                # Try to extract workout plan data from the response
                workout_data = _extract_workout_data(ai_response or "")
                logger.info(f"Extracted workout data: {workout_data}")
                if workout_data and workout_data.get("exercises") and len(workout_data["exercises"]) > 0:
                    # GUEST USERS: Mark as preview widget
                    workout_data["is_preview"] = True
                    workout_data["preview_message"] = "This is a preview of what a complete workout plan would include. Sign up for a premium account to generate full, detailed workout plans with advanced features and customization."
                    widget_data = {
                        "type": "fitness",
                        "data": workout_data
                    }
                    logger.info(f"✅ Created preview fitness widget for guest user with {len(workout_data['exercises'])} exercises: {widget_data}")
                else:
                    logger.warning(f"⚠️ Failed to extract workout data - workout_data: {workout_data}, exercises: {workout_data.get('exercises') if workout_data else None}")
            else:
                logger.info(f"Not a fitness or lesson plan request - message: '{request.message[:50]}...'")
        
        logger.info(f"Returning response with widget_data: {widget_data is not None}")
        
        # Merge extracted content with widget_data if available
        if extracted_content.get("widget_data") and not widget_data:
            widget_data = extracted_content.get("widget_data")
        
        # Also extract file_content and filename from widget_data.data if present (for generated documents)
        # This ensures chat display works even if they're nested in widget_data
        if widget_data and isinstance(widget_data, dict) and widget_data.get("data"):
            widget_data_content = widget_data.get("data", {})
            if isinstance(widget_data_content, dict):
                # Extract file_content and filename from widget_data.data if not already extracted
                if widget_data_content.get("file_content") and not extracted_content.get("file_content"):
                    extracted_content["file_content"] = widget_data_content.get("file_content")
                    logger.info("📄 Extracted file_content from widget_data.data for chat display (guest)")
                if widget_data_content.get("filename") and not extracted_content.get("filename"):
                    extracted_content["filename"] = widget_data_content.get("filename")
                    logger.info("📄 Extracted filename from widget_data.data for chat display (guest)")
                # Also extract web_url if present
                if widget_data_content.get("web_url") and not extracted_content.get("web_url"):
                    extracted_content["web_url"] = widget_data_content.get("web_url")
                    logger.info("☁️ Extracted web_url from widget_data.data for chat display (guest)")
        
        try:
            response_data = {
                "response": ai_response or "I've processed your request.",
                "widgets": None,
                "widget_data": widget_data
            }
            
            # Include extracted content for frontend display
            if extracted_content.get("images") and len(extracted_content["images"]) > 0:
                response_data["images"] = extracted_content["images"]
            if extracted_content.get("file_content"):
                response_data["file_content"] = extracted_content["file_content"]
                response_data["filename"] = extracted_content["filename"]
            if extracted_content.get("web_url"):
                response_data["web_url"] = extracted_content["web_url"]
                response_data["file_id"] = extracted_content["file_id"]
                if extracted_content.get("filename"):
                    response_data["filename"] = extracted_content["filename"]
            
            return JSONResponse(response_data)
        except Exception as response_error:
            # If there's an error sending the response (e.g., connection lost), log it but don't crash
            error_type = type(response_error).__name__
            error_msg = str(response_error) if response_error else repr(response_error)
            logger.error(f"Error sending response: {error_type}: {error_msg}")
            
            # Check if it's a connection/protocol error (client disconnected)
            if "LocalProtocolError" in error_type or "Can't send data" in error_msg or "connection" in error_msg.lower():
                logger.warning(f"Client connection lost before response could be sent. This is usually due to network timeout or client disconnection.")
                # Re-raise to let FastAPI handle it (it will log but not crash the server)
                raise
            
            # Try to return a simple response for other errors
            try:
                response_data = {
                    "response": ai_response or "I've processed your request.",
                    "widgets": None,
                    "widget_data": widget_data
                }
                # Include extracted content if available
                if extracted_content.get("images") and len(extracted_content["images"]) > 0:
                    response_data["images"] = extracted_content["images"]
                if extracted_content.get("file_content"):
                    response_data["file_content"] = extracted_content["file_content"]
                    response_data["filename"] = extracted_content["filename"]
                if extracted_content.get("web_url"):
                    response_data["web_url"] = extracted_content["web_url"]
                    response_data["file_id"] = extracted_content["file_id"]
                
                return JSONResponse(response_data, status_code=200)
            except:
                # If that also fails, raise the original error
                raise response_error
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is (they already have proper error messages)
        raise
    except Exception as e:
        error_msg = str(e) if str(e) else repr(e)
        error_type = type(e).__name__
        
        # Check if it's a connection/protocol error (client disconnected)
        if "LocalProtocolError" in error_type or "Can't send data" in error_msg:
            # This happens when the client disconnects before we can send the response
            # It's not really an error on our side - just log it and let it pass
            logger.warning(f"Client connection lost during response: {error_type}. This is usually due to network timeout or client disconnection.")
            # Return a simple error response that won't try to send data
            from fastapi import Response
            return Response(
                content='{"error": "Connection lost during processing. Please try again."}',
                status_code=200,
                media_type="application/json"
            )
        
        logger.error(f"Error in guest chat: {error_type}: {error_msg}")
        logger.exception("Full traceback:")
        # Provide more detailed error message
        detail_msg = f"Error processing chat message: {error_type}"
        if error_msg:
            detail_msg += f" - {error_msg}"
        raise HTTPException(
            status_code=500,
            detail=detail_msg
        )

