"""
Specialized Lesson Plan Service
Handles all lesson plan creation with focused prompt and optimized model.
"""

from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from openai import OpenAI
import logging
import os
import re
import json

from app.services.pe.base_widget_service import BaseWidgetService
from app.services.pe.specialized_services.base_specialized_service import BaseSpecializedService

logger = logging.getLogger(__name__)


# ==========================
# Helper Functions for Lesson Plan Extraction
# ==========================

def _clean_text(text: str, remove_numbering: bool = True, remove_bullets: bool = True, 
                remove_headers: bool = False) -> str:
    """Clean text by removing numbering, bullets, and/or headers."""
    if not text:
        return ""
    cleaned = text.strip()
    if remove_numbering:
        cleaned = re.sub(r'^\d+[\.\)]\s*', '', cleaned)
    if remove_bullets:
        cleaned = re.sub(r'^[-•]\s*', '', cleaned)
    if remove_headers:
        cleaned = re.sub(r'###\s*[^#\n]+###', '', cleaned)
        cleaned = re.sub(r'^###\s+[^\n]+$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'Costa\'?s\s+Levels?\s+of\s+Questioning', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'Worksheets?\s+with\s+Answer\s+Keys?', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


def _remove_rubric_markers(text: str) -> str:
    """Remove rubric markers and content from text."""
    if not text:
        return text
    patterns = [
        r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*',
        r'###\s*Grading\s+Rubrics?',
        r'📋\s*Grading\s+Rubric',
        r'Grading\s+Rubric[:\s]*',
    ]
    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern + r'.*?(?=\n\n|\n###|$)', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'\n+\s*(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*\s*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    cleaned = re.sub(r'\n+\s*📋\s*Grading\s+Rubric[:\s]*\s*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    # Remove "### Grading Rubrics" standalone lines
    cleaned = re.sub(r'^###\s*Grading\s+Rubrics?\s*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    return cleaned.strip()


def _is_question_line(line: str) -> bool:
    """Check if a line is likely a question."""
    if not line or '?' not in line or not line.endswith('?'):
        return False
    if len(line) < 10 or len(line) > 200:
        return False
    # Skip section headers, assessment headers, and other non-question text
    if re.search(r'###|Costa|Level\s+\d+|Worksheets?|Answer\s+Key|Assessment\s+[Qq]uestions?|[Qq]uestions?/Tasks?', line, re.IGNORECASE):
        return False
    if re.match(r'^(?:Begin|Engage|Explain|Introduce|Highlight|Discuss|iscussing|\*\*)', line, re.IGNORECASE):
        return False
    # Skip lines that are clearly headers or instructions, not actual questions
    if re.match(r'^\*\*.*\*\*$', line):  # Bold text only (likely headers)
        return False
    has_question_word = bool(re.search(r'(?:what|which|how|when|where|why|who|name|list|describe|explain|should|will|does|do|is|are|can|would|could)', line, re.IGNORECASE))
    is_numbered = bool(re.match(r'^\d+[\.\)]', line))
    is_short = len(line) < 150
    return has_question_word or is_numbered or is_short


def _count_questions_in_text(text: str) -> int:
    """Count questions in text using multiple patterns."""
    if not text or not isinstance(text, str):
        return 0
    pattern1 = r'(?:what|which|how|when|where|why|who|name|list|describe|explain|can\s+you)[^?]+\?'
    pattern2 = r'\d+[\.\)]\s+[^?]+\?'
    count1 = len(re.findall(pattern1, text, re.IGNORECASE))
    count2 = len(re.findall(pattern2, text, re.IGNORECASE))
    return max(count1, count2)


def _extract_questions_from_text(text: str) -> List[str]:
    """Extract all questions from text, filtering out non-question content and avoiding duplicates."""
    if not text:
        return []
    
    # Remove section headers and markers
    text = _clean_text(text, remove_headers=True)
    
    # Track questions we've seen to avoid duplicates
    seen = set()
    unique_questions = []
    
    # Process lines
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Skip MC options and answer keys
        if re.match(r'^[-\s]*[A-D]\)\s+', line, re.IGNORECASE) or \
           re.search(r'(?:correct\s+)?answer[:\s]*[A-D]', line, re.IGNORECASE):
            continue
        
        # Check if it's a question
        if _is_question_line(line):
            cleaned_q = _clean_text(line)
            # Skip if it's clearly not a question (introduction text, assessment headers, etc.)
            skip_patterns = [
                r'^(?:Begin|Engage|Explain|Introduce|Highlight|Discuss|iscussing|The|This|Students)',
                r'^\*\*.*[Qq]uestions?.*\*\*',  # **Assessment Questions**
                r'^Assessment\s+[Qq]uestions?',  # Assessment Questions
                r'^[Qq]uestions?/Tasks?',  # Questions/Tasks
                r'^\d+\.\s*\*\*',  # Numbered bold text (likely headers)
            ]
            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, cleaned_q, re.IGNORECASE):
                    should_skip = True
                    break
            if should_skip:
                continue
            
            # Check for duplicates
            q_key = cleaned_q.lower()
            if q_key not in seen:
                unique_questions.append(cleaned_q)
                seen.add(q_key)
    
    return unique_questions


def _extract_answer_keys_from_text(text: str) -> List[str]:
    """Extract answer keys from text."""
    if not text:
        return []
    patterns = [
        # Pattern for "Correct Answer: A - description" format
        r'(?:correct\s+)?answer[:\s]*[A-D]\s*-\s*[^\n]+',
        # Pattern for "Correct Answer: A) description" format
        r'(?:correct\s+)?answer[:\s]*[A-D]\)\s*[^\n]+',
        # Pattern for numbered "1. Correct Answer: A - description"
        r'\d+\.\s*(?:correct\s+)?answer[:\s]*[A-D]\s*-\s*[^\n]+',
        # Pattern for "Answer: A" or "Answer: A - description"
        r'(?:correct\s+)?answer[:\s]*[A-D](?:\s*-\s*[^\n]+)?',
        # Pattern for "Answer: A) description"
        r'(?:correct\s+)?answer[:\s]*[A-D]\)\s*[^\n]+',
    ]
    all_keys = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        all_keys.extend(matches)
    
    # Also check line by line for answer keys
    for line in text.split('\n'):
        line = line.strip()
        if line and re.search(r'(?:correct\s+)?answer[:\s]*[A-D]', line, re.IGNORECASE):
            # Extract the full answer key line
            if line not in all_keys:
                all_keys.append(line)
    
    seen = set()
    unique_keys = []
    for key in all_keys:
        key_clean = key.strip().lower()
        if key_clean and key_clean not in seen and len(key.strip()) > 5:
            unique_keys.append(key.strip())
            seen.add(key_clean)
    return unique_keys


def _extract_mc_options_from_text(text: str) -> List[str]:
    """Extract multiple choice options from text, ensuring complete options."""
    if not text:
        return []
    
    matches = []
    
    # First, check line by line for standalone MC options (more reliable)
    for line in text.split('\n'):
        line = line.strip()
        # Match lines that start with A), B), C), D) OR A., B., C., D. (with optional dashes/bullets)
        # Pattern: A), A., A) or A. followed by space and text
        if re.match(r'^[-•\s]*[A-D][\.\)]\s+', line, re.IGNORECASE):
            # Clean up the option - remove leading dashes/bullets/spaces
            opt = re.sub(r'^[-•\s]*', '', line)
            # Normalize format: convert "A. " to "A) " for consistency
            opt = re.sub(r'^([A-D])\.\s+', r'\1) ', opt, flags=re.IGNORECASE)
            # Ensure it has the format "A) text"
            if opt and re.match(r'^[A-D]\)\s+', opt, re.IGNORECASE):
                # Normalize to "A) text" format
                opt_match = re.match(r'^([A-D])\)\s+(.+)', opt, re.IGNORECASE)
                if opt_match:
                    letter = opt_match.group(1).upper()
                    text_part = opt_match.group(2).strip()
                    # Skip if option is incomplete, is a materials list, or is a section header
                    is_materials = bool(re.search(r'^\d+\s+(floor\s+hockey|basketball|ball|puck|cone|hoop|whistle|stopwatch)', text_part, re.IGNORECASE))
                    is_section_header = bool(re.match(r'^###?\s+', text_part) or re.match(r'^[-=]+\s*$', text_part))
                    is_invalid = (not text_part or len(text_part) < 3 or 
                                 re.match(r'^[\d\s\-#]+$', text_part) or
                                 is_materials or is_section_header)
                    if not is_invalid:
                        opt_normalized = f"{letter}) {text_part}"
                        # Better duplicate detection: check by letter and content (first 50 chars, case-insensitive)
                        content_key = text_part[:50].lower().strip()
                        is_duplicate = False
                        for existing in matches:
                            existing_match = re.match(r'^([A-D])\)\s+(.+)', existing, re.IGNORECASE)
                            if existing_match:
                                existing_letter = existing_match.group(1).upper()
                                existing_content = existing_match.group(2)[:50].lower().strip()
                                # Same letter and similar content = duplicate
                                if existing_letter == letter and existing_content == content_key:
                                    is_duplicate = True
                                    break
                        if not is_duplicate:
                            matches.append(opt_normalized)
    
    # Also try pattern matching for MC options in blocks (fallback)
    # Match both A) and A. formats
    pattern = r'([A-D][\.\)]\s+[^\n]+?)(?=\s*[A-D][\.\)]\s+|$)'
    pattern_matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
    for match in pattern_matches:
        match_clean = match.strip()
        # Normalize format: convert "A. " to "A) "
        match_clean = re.sub(r'^([A-D])\.\s+', r'\1) ', match_clean, flags=re.IGNORECASE)
        # Normalize format
        opt_match = re.match(r'^([A-D])\)\s+(.+)', match_clean, re.IGNORECASE)
        if opt_match:
            letter = opt_match.group(1).upper()
            text_part = opt_match.group(2).strip()
            # Skip if option is incomplete, is a materials list, or is a section header
            is_materials = bool(re.search(r'^\d+\s+(floor\s+hockey|basketball|ball|puck|cone|hoop|whistle|stopwatch)', text_part, re.IGNORECASE))
            is_section_header = bool(re.match(r'^###?\s+', text_part) or re.match(r'^[-=]+\s*$', text_part))
            is_invalid = (not text_part or len(text_part) < 3 or 
                         re.match(r'^[\d\s\-#]+$', text_part) or
                         is_materials or is_section_header)
            if not is_invalid:
                opt_normalized = f"{letter}) {text_part}"
                # Better duplicate detection: check by letter and content (first 50 chars, case-insensitive)
                content_key = text_part[:50].lower().strip()
                is_duplicate = False
                for existing in matches:
                    existing_match = re.match(r'^([A-D])\)\s+(.+)', existing, re.IGNORECASE)
                    if existing_match:
                        existing_letter = existing_match.group(1).upper()
                        existing_content = existing_match.group(2)[:50].lower().strip()
                        # Same letter and similar content = duplicate
                        if existing_letter == letter and existing_content == content_key:
                            is_duplicate = True
                            break
                if not is_duplicate:
                    matches.append(opt_normalized)
    
    # Sort options by letter (A, B, C, D) to ensure proper order
    def get_option_letter(opt):
        match = re.match(r'([A-D])\)', opt, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return 'Z'  # Put unmatched at end
    
    sorted_options = sorted(matches, key=get_option_letter)
    
    return sorted_options


def _extract_question_option_pairs_from_text(text: str) -> List[dict]:
    """Extract questions with their MC options together from text. Returns list of {question, options: []}."""
    if not text:
        return []
    
    pairs = []
    lines = text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip answer keys that might look like questions
        if re.search(r'correct\s+answer', line, re.IGNORECASE):
            i += 1
            continue
        
        # Look for a question (numbered or not, ending with ?)
        question_match = re.match(r'^(\d+)[\.\)]\s*(.+)$', line)
        if question_match:
            question_num = question_match.group(1)
            question_text = question_match.group(2).strip()
            # Skip if it's an answer key (starts with "Correct Answer:")
            if re.search(r'correct\s+answer', question_text, re.IGNORECASE):
                i += 1
                continue
        elif line.endswith('?') and len(line) > 10:
            question_text = line
            question_num = None
        else:
            i += 1
            continue
        
        # Clean question
        question_text = _clean_text(question_text, remove_headers=True)
        if not question_text or len(question_text) < 10:
            i += 1
            continue
        
        # Skip if it's clearly an answer key
        if re.search(r'correct\s+answer|answer[:\s]*[A-D]', question_text, re.IGNORECASE):
            i += 1
            continue
        
        # Skip questions with markers that indicate they're not worksheet questions
        # These are typically from objectives, Costa's questioning, or other sections
        skip_markers = [
            r'\*\*Question:\*\*',  # **Question:**
            r'Question:\s*',  # Question:
            r'Level\s+\d+\s*[\(:]',  # Level 1 (Gathering): or Level 1:
            r'Gathering|Processing|Applying',  # Costa's levels
            r'Costa\'?s\s+Level',  # Costa's Level
            r'Reflection\s+Question',  # Reflection Question
        ]
        for marker in skip_markers:
            if re.search(marker, question_text, re.IGNORECASE):
                i += 1
                continue
        
        # Look ahead for MC options (A, B, C, D) - up to 10 lines ahead
        options = []
        j = i + 1
        found_letters = set()
        while j < min(i + 10, len(lines)) and len(found_letters) < 4:
            opt_line = lines[j].strip()
            opt_match = re.match(r'^[-•\s]*([A-D])[\.\)]\s+(.+)$', opt_line, re.IGNORECASE)
            if opt_match:
                letter = opt_match.group(1).upper()
                opt_text = opt_match.group(2).strip()
                # Filter invalid content
                is_materials = bool(re.search(r'^\d+\s+(floor\s+hockey|basketball|ball|puck|cone|hoop|whistle|stopwatch)', opt_text, re.IGNORECASE))
                is_valid = (opt_text and len(opt_text) > 2 and 
                          not re.match(r'^[\d\s\-#]+$', opt_text) and
                          not is_materials)
                if is_valid and letter not in found_letters:
                    opt_clean = f"{letter}) {opt_text}"
                    options.append(opt_clean)
                    found_letters.add(letter)
            elif opt_line and not opt_line.startswith(('A)', 'B)', 'C)', 'D)', 'A.', 'B.', 'C.', 'D.')):
                # If we hit a non-option line and we have at least 2 options, stop
                if len(options) >= 2:
                    break
            j += 1
        
        # Sort options by letter
        if options:
            def get_opt_letter(opt):
                match = re.match(r'^([A-D])\)', opt, re.IGNORECASE)
                return match.group(1).upper() if match else 'Z'
            options = sorted(options, key=get_opt_letter)
        
        # Only include questions that have at least 3 MC options (worksheets should have 4)
        # This filters out reflection questions, Costa's questions, etc. that typically have 0-2 options
        if question_text and len(options) >= 3:
            pairs.append({
                'question': question_text,
                'options': options,
                'number': question_num
            })
        elif question_text and len(options) < 3:
            # Skip questions with fewer than 3 options - these aren't worksheet questions
            logger.debug(f"🔍 Skipping question with only {len(options)} options: {question_text[:50]}...")
        
        i = j if options else i + 1
    
    return pairs


def _combine_worksheets(existing: str, questions: List[str], mc_options: List[str], answer_keys: List[str]) -> str:
    """Combine worksheet components into formatted worksheet with proper formatting."""
    # FIRST: Try to extract question-option pairs directly from the original text if we have it
    # This is more reliable than trying to match separately extracted questions and options
    question_option_pairs = []
    
    # If we have questions and options, try to extract pairs from a combined text
    # For now, we'll use the existing approach but improve the matching
    
    # Clean and deduplicate questions
    all_questions = []
    seen = set()
    for q in questions:
        # Clean the question
        cleaned_q = _clean_text(q, remove_headers=True)
        # Also remove Level markers
        cleaned_q = re.sub(r'Level\s+\d+[:\s]*', '', cleaned_q, flags=re.IGNORECASE).strip()
        
        # Skip if empty, too short, or doesn't end with ?
        if not cleaned_q or len(cleaned_q) < 10 or not cleaned_q.endswith('?'):
            continue
        
        # Skip if it's clearly not a question
        if re.match(r'^(?:Begin|Engage|Explain|Introduce|Highlight|Discuss|iscussing|The|This|Students)', cleaned_q, re.IGNORECASE):
            continue
        
        # Check for duplicates
        q_key = cleaned_q.lower()
        if q_key not in seen:
            all_questions.append(cleaned_q)
            seen.add(q_key)
    
    # If existing has content but no questions, check if it's just headers
    existing_has_questions = _count_questions_in_text(existing) > 0 if existing else False
    existing_is_header_only = existing and not existing_has_questions and (
        "Student Worksheet:" in existing or "with Answer Keys" in existing
    )
    
    # If existing has questions but we don't have new questions, extract from existing and renumber
    if existing and existing_has_questions and not all_questions:
        existing_q, existing_mc, existing_ak = _extract_worksheets_from_field(existing, "existing_worksheets")
        if existing_q:
            # Add existing questions to all_questions
            for q in existing_q:
                cleaned_q = q.strip()
                cleaned_q = re.sub(r'^\d+[\.\)]\s*', '', cleaned_q)  # Remove existing numbering
                cleaned_q = re.sub(r'^[-•]\s*', '', cleaned_q)
                cleaned_q = cleaned_q.strip()
                if cleaned_q and cleaned_q.endswith('?') and cleaned_q.lower() not in seen:
                    all_questions.append(cleaned_q)
                    seen.add(cleaned_q.lower())
            # Also add existing MC options and answer keys if we don't have new ones
            if not mc_options and existing_mc:
                mc_options = existing_mc
            if not answer_keys and existing_ak:
                answer_keys = existing_ak
    
    # If we have questions (from new extraction or existing), always create a properly numbered worksheet
    if all_questions:
        # Group MC options with their questions
        # MC options typically come in groups of 4 (A, B, C, D) after each question
        question_mc_pairs = []
        question_num = 1  # Counter for numbering questions (only increments for valid questions)
        
        # Track questions we've added to avoid duplicates within this function
        added_questions = set()
        
        logger.info(f"🔍 _combine_worksheets: Processing {len(all_questions)} questions, {len(mc_options) if mc_options else 0} MC options available")
        logger.info(f"🔍 MC options preview: {mc_options[:4] if mc_options and len(mc_options) >= 4 else mc_options}")
        
        # SIMPLIFIED APPROACH: Group every 4 consecutive valid MC options into sets
        # This is much simpler and works even if options have duplicate letters or are out of order
        option_sets = []
        if mc_options:
            valid_options = []
            for opt in mc_options:
                opt_clean = _clean_text(opt, remove_bullets=True)
                letter_match = re.match(r'^([A-D])\)\s+(.+)', opt_clean, re.IGNORECASE)
                if letter_match:
                    letter = letter_match.group(1).upper()
                    text_part = letter_match.group(2).strip()
                    # Filter invalid content
                    is_materials = bool(re.search(r'^\d+\s+(floor\s+hockey|basketball|ball|puck|cone|hoop|whistle|stopwatch)', text_part, re.IGNORECASE))
                    is_section_header = bool(re.match(r'^###?\s+', text_part) or re.match(r'^[-=]+\s*$', text_part))
                    is_valid = (text_part and len(text_part) > 2 and 
                              not re.match(r'^[\d\s\-#]+$', text_part) and
                              not is_materials and not is_section_header)
                    
                    if is_valid:
                        valid_options.append(opt_clean)
            
            # Group every 4 consecutive options into a set
            # Sort each set by letter (A, B, C, D) to ensure proper order
            for i in range(0, len(valid_options), 4):
                group = valid_options[i:i+4]
                if len(group) >= 2:  # At least 2 options to form a set
                    # Sort by letter within the group
                    def get_letter(opt):
                        match = re.match(r'^([A-D])\)', opt, re.IGNORECASE)
                        return match.group(1).upper() if match else 'Z'
                    sorted_group = sorted(group, key=get_letter)
                    option_sets.append(sorted_group)
        
        logger.info(f"🔍 Grouped MC options into {len(option_sets)} sets (total options: {len(mc_options) if mc_options else 0})")
        if option_sets:
            logger.info(f"🔍 Option sets sizes: {[len(s) for s in option_sets[:5]]} (showing first 5)")
        option_set_index = 0
        
        for q in all_questions:
            # Clean and format the question
            q_formatted = _clean_text(q)
            q_formatted = _remove_rubric_markers(q_formatted)
            
            if not q_formatted or not q_formatted.endswith('?'):
                continue
            
            # Check if this question already has MC options embedded
            has_mc_in_question = bool(re.search(r'[A-D]\)\s+', q_formatted, re.IGNORECASE))
            
            # Get MC options for this question - use pre-grouped option sets
            question_mc = []
            if not has_mc_in_question and option_set_index < len(option_sets):
                question_mc = option_sets[option_set_index]
                option_set_index += 1
                logger.debug(f"✅ Assigned {len(question_mc)} MC options to question: {q_formatted[:50]}...")
            
            # When there are no MC options, ALWAYS add all questions (they'll display without options)
            # When MC options exist but are mismatched, still add questions (better than missing questions)
            should_add = True
            total_mc_count = len(mc_options) if mc_options else 0
            
            # Always add questions, even if they don't have MC options
            if not has_mc_in_question:
                if len(question_mc) == 0:
                    logger.debug(f"ℹ️ No MC options available for this question, adding without options: {q_formatted[:50]}...")
                else:
                    logger.debug(f"ℹ️ Adding question with {len(question_mc)} MC options: {q_formatted[:50]}...")
            
            # Always add the question
            should_add = True
            if should_add:
                # Check for duplicates (case-insensitive)
                q_key = q_formatted.lower().strip()
                if q_key in added_questions:
                    logger.debug(f"⚠️ Skipping duplicate question: {q_formatted[:50]}...")
                    continue
                added_questions.add(q_key)
                
                # Format the question with its MC options - ALWAYS number it
                question_text = f"{question_num}. {q_formatted}"
                if question_mc:
                    # Add MC options indented under the question (ensure no leading dashes)
                    formatted_options = []
                    for opt in question_mc:
                        # Remove any leading dashes/bullets and ensure proper format
                        clean_opt = _clean_text(opt, remove_bullets=True)
                        formatted_options.append(f"   {clean_opt}")
                    question_text += "\n" + "\n".join(formatted_options)
                
                question_mc_pairs.append({
                    'number': question_num,
                    'text': question_text,
                    'has_options': len(question_mc) > 0
                })
                question_num += 1  # Increment counter for next question
        
        # Redistribute leftover option sets to questions that don't have any
        if option_set_index < len(option_sets):
            remaining_sets = option_sets[option_set_index:]
            questions_without_options = [q for q in question_mc_pairs if not q['has_options']]
            
            if remaining_sets and questions_without_options:
                logger.info(f"🔍 Redistributing {len(remaining_sets)} leftover option sets to {len(questions_without_options)} questions without options")
                set_idx = 0
                for q_pair in questions_without_options:
                    if set_idx >= len(remaining_sets):
                        break
                    question_options = remaining_sets[set_idx]
                    set_idx += 1
                    
                    if question_options:
                        # Update the question text to include options
                        q_num = q_pair['number']
                        q_text = q_pair['text'].split('\n')[0]  # Get question without options
                        formatted_options = [f"   {_clean_text(opt, remove_bullets=True)}" for opt in question_options]
                        q_pair['text'] = q_text + "\n" + "\n".join(formatted_options)
                        q_pair['has_options'] = True
                        logger.debug(f"✅ Added {len(question_options)} options to question {q_num}")
        
        # Convert back to list of strings
        final_question_texts = [q['text'] for q in question_mc_pairs]
        
        logger.info(f"🔍 _combine_worksheets: Processed {len(all_questions)} questions, added {len(final_question_texts)} to worksheet (MC options available: {len(mc_options) if mc_options else 0})")
        if len(final_question_texts) < len(all_questions):
            skipped = len(all_questions) - len(final_question_texts)
            logger.warning(f"⚠️ Only {len(final_question_texts)} questions added out of {len(all_questions)} total (skipped {skipped})")
            # If we have 10+ questions but only added a few, something is wrong - log details
            if len(all_questions) >= 10 and len(final_question_texts) < 10:
                logger.warning(f"⚠️ CRITICAL: Expected 10+ questions but only added {len(final_question_texts)}. This indicates filtering issues.")
        worksheet = "Student Worksheet:\n\n" + "\n\n".join(final_question_texts)
        
        # Remove any rubric markers that might have been included
        worksheet = _remove_rubric_markers(worksheet)
        # Remove "with Answer Keys" header if present
        worksheet = re.sub(r'^with\s+answer\s+keys?\s*$', '', worksheet, flags=re.IGNORECASE | re.MULTILINE).strip()
        
        # Add answer keys - deduplicate and match to questions
        if answer_keys:
            # Clean and deduplicate answer keys, preserving their original order
            cleaned_keys = []
            seen_keys = set()
            key_index_map = {}  # Map question number to answer key index
            
            for idx, ak in enumerate(answer_keys):
                ak_clean = ak.strip()
                # Extract question number if present (e.g., "1. Correct Answer: A - ...")
                question_num_match = re.match(r'^(\d+)[\.\)]\s*(.+)', ak_clean)
                if question_num_match:
                    q_num = int(question_num_match.group(1))
                    ak_content = question_num_match.group(2).strip()
                else:
                    # No question number - will be assigned by position
                    q_num = None
                    ak_content = ak_clean
                
                # Remove leading dashes/bullets from content
                ak_content = re.sub(r'^[-•]\s*', '', ak_content)
                
                if ak_content and len(ak_content) > 5:
                    # Check for duplicates (case-insensitive, by answer letter and content)
                    # Extract the answer letter (A, B, C, or D) and description
                    key_match = re.search(r'answer[:\s]*([A-D])[\)\s-]+(.+)', ak_content, re.IGNORECASE)
                    if key_match:
                        answer_letter = key_match.group(1).upper()
                        description = key_match.group(2).strip()
                        key_signature = f"{answer_letter}:{description[:50].lower()}"  # First 50 chars for comparison
                        if key_signature not in seen_keys:
                            cleaned_keys.append(ak_content)
                            seen_keys.add(key_signature)
                            # If this key had a question number, map it
                            if q_num:
                                key_index_map[q_num] = len(cleaned_keys) - 1
                    else:
                        # If we can't parse it, just check if the full text is unique
                        content_lower = ak_content.lower()
                        if content_lower not in seen_keys:
                            cleaned_keys.append(ak_content)
                            seen_keys.add(content_lower)
                            if q_num:
                                key_index_map[q_num] = len(cleaned_keys) - 1
            
            if cleaned_keys:
                # Limit to the number of questions actually added to worksheet
                num_questions_added = len(question_mc_pairs)
                
                # Try to match answer keys to questions by number if available
                # Otherwise, use sequential matching
                keys_to_show = []
                logger.info(f"🔍 Matching {len(cleaned_keys)} answer keys to {num_questions_added} questions")
                logger.info(f"🔍 Answer keys with question numbers: {list(key_index_map.keys())}")
                for i in range(1, num_questions_added + 1):
                    if i in key_index_map:
                        # Use the answer key that was numbered for this question
                        key_idx = key_index_map[i]
                        if key_idx < len(cleaned_keys):
                            keys_to_show.append(cleaned_keys[key_idx])
                            logger.debug(f"✅ Matched answer key {i} by number: {cleaned_keys[key_idx][:60]}...")
                    elif len(keys_to_show) < len(cleaned_keys):
                        # Use next available answer key sequentially
                        keys_to_show.append(cleaned_keys[len(keys_to_show)])
                        logger.debug(f"✅ Matched answer key {i} sequentially: {cleaned_keys[len(keys_to_show)-1][:60]}...")
                
                # If we still don't have enough, pad with remaining keys
                while len(keys_to_show) < num_questions_added and len(keys_to_show) < len(cleaned_keys):
                    next_idx = len(keys_to_show)
                    if next_idx < len(cleaned_keys):
                        keys_to_show.append(cleaned_keys[next_idx])
                
                # Limit to number of questions
                keys_to_show = keys_to_show[:num_questions_added]
                
                # Ensure each answer key has "Correct Answer:" prefix if missing and number them
                formatted_keys = []
                for i, ak in enumerate(keys_to_show, start=1):
                    # Check if it already has "Correct Answer:" or "Answer:"
                    if not re.search(r'(?:correct\s+)?answer[:\s]*', ak, re.IGNORECASE):
                        ak = f"Correct Answer: {ak}"
                    formatted_keys.append(f"{i}. {ak}")
                worksheet += "\n\nAnswer Key:\n\n" + "\n\n".join(formatted_keys)
        
        logger.info(f"✅ Combined worksheet: {len(all_questions)} questions, {len(answer_keys)} answer keys (all properly numbered)")
        return worksheet
    
    # If no questions at all, check if we should return existing or empty
    if existing and existing_has_questions:
        # Even if we can't extract questions, try to add numbering to existing if it doesn't have it
        # Check if existing questions are numbered
        lines = existing.split('\n')
        has_numbering = any(re.match(r'^\d+[\.\)]\s+', line.strip()) for line in lines if '?' in line)
        if not has_numbering:
            # Try to add numbering to existing questions
            numbered_lines = []
            question_num = 1
            for line in lines:
                if '?' in line and not line.strip().startswith('Answer'):
                    # Check if it's a question (not an answer key)
                    if re.search(r'(?:what|which|how|when|where|why|who|name|list|describe|explain|should|will|does|do|is|are)', line, re.IGNORECASE) or len(line.strip()) < 200:
                        numbered_lines.append(f"{question_num}. {line.strip()}")
                        question_num += 1
                    else:
                        numbered_lines.append(line)
                else:
                    numbered_lines.append(line)
            return '\n'.join(numbered_lines)
        return existing
    
    # If existing is just headers, return empty (will trigger re-extraction)
    if existing_is_header_only:
        logger.warning(f"⚠️ Existing worksheets field has only headers, no questions. Returning empty to trigger re-extraction.")
        return ""
    
    return existing if existing else ""


def _clean_objectives_of_questions(objectives: List[Any]) -> List[Any]:
    """Remove questions, answer keys, and MC options from objectives."""
    if not objectives or not isinstance(objectives, list):
        return objectives
    
    cleaned = []
    for obj in objectives:
        obj_str = str(obj) if obj else ""
        # More lenient: if it has a question mark, it's likely a question
        is_question = bool(re.search(r'[?]', obj_str) and (
            re.search(r'(?:what|which|how|when|where|why|who|name|list|describe|explain|can\s+you|should|focus)', obj_str, re.IGNORECASE) or
            len(obj_str) < 150  # Short text with ? is likely a question
        ))
        is_answer_key = bool(re.search(r'(?:correct\s+)?answer[:\s]*(?:[A-D]\)\s*)?', obj_str, re.IGNORECASE))
        is_mc_option = bool(re.match(r'^[-\s]*[A-D]\)\s+', obj_str, re.IGNORECASE))
        is_numbered_question = bool(re.match(r'^\d+[\.\)]\s*(?:what|which|how|when|where|why|who)', obj_str, re.IGNORECASE))
        is_standard = bool(re.match(r'^[-\s]*(?:PE|ELA|MATH|SCI|SS)\.\d+', obj_str, re.IGNORECASE))
        is_intro = bool(re.search(r'begin\s+the\s+lesson|discussing\s+the\s+history|engage\s+students\s+by\s+asking', obj_str, re.IGNORECASE))
        
        if not (is_question or is_answer_key or is_mc_option or is_numbered_question):
            if is_standard or is_intro:
                if len(obj_str) < 150 and not re.search(r'favorite\s+baseball\s+teams|prior\s+knowledge', obj_str, re.IGNORECASE):
                    cleaned.append(obj)
            else:
                cleaned.append(obj)
        else:
            logger.info(f"🔍 Removing question/answer key from objectives: {obj_str[:80]}...")
    
    return cleaned if len(cleaned) < len(objectives) else objectives


def _extract_rubric_rows_from_text(text: str) -> List[str]:
    """Extract rubric table rows from text."""
    if not text:
        return []
    
    rows = []
    
    # First, try line-by-line extraction (most reliable)
    for line in text.split('\n'):
        line = line.strip()
        # Look for lines that start with | and have at least 2 pipes (3 columns minimum)
        if line.startswith('|') and line.count('|') >= 2:
            # Skip separator rows (all dashes/colons/spaces)
            if not re.match(r'^\|\s*[-:\s]+\|', line):
                if line not in rows:
                    rows.append(line)
    
    # Also try regex patterns as fallback
    if not rows:
        patterns = [
            r'\|[^\|\n]+\|[^\|\n]+(?:\|[^\|\n]+)*(?:\||$)',
            r'\|[^\|]+\|[^\|]+',
            r'^\s*\|[^\|]+\|[^\|]+',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                match_clean = match.strip()
                if match_clean and match_clean not in rows:
                    rows.append(match_clean)
    
    return list(dict.fromkeys(rows))


def _format_rubric_row(row: str) -> str:
    """Format a rubric row to have 4 performance levels."""
    # Clean the row first - remove extra pipes and whitespace
    row = re.sub(r'\|\s*\|', '|', row)  # Remove empty columns
    row = row.strip()
    if not row.startswith('|'):
        row = '| ' + row
    if not row.endswith('|'):
        row = row + ' |'
    
    cols = [col.strip() for col in row.split('|') if col.strip()]
    
    # Skip if it's a header row or separator
    if len(cols) == 0 or all(re.match(r'^[\s\-:]+$', col) for col in cols):
        return ""
    
    # Ensure we have at least a criteria name
    if len(cols) < 1:
        return ""
    
    criteria = cols[0]
    
    # Default performance level descriptions
    excellent = "Demonstrates excellent technique and understanding"
    proficient = "Shows good form with minor errors"
    developing = "Demonstrates basic technique but lacks consistency"
    beginning = "Struggles with basic technique, needs significant improvement"
    
    # If we have existing columns, use them (but ensure we have 4)
    if len(cols) >= 4:
        # Use existing columns, but ensure they're not empty
        excellent_col = cols[1] if len(cols) > 1 and cols[1] else excellent
        proficient_col = cols[2] if len(cols) > 2 and cols[2] else proficient
        developing_col = cols[3] if len(cols) > 3 and cols[3] else developing
        beginning_col = cols[4] if len(cols) > 4 and cols[4] else beginning
        return f"| {criteria} | {excellent_col} | {proficient_col} | {developing_col} | {beginning_col} |"
    elif len(cols) == 3:
        excellent_col = cols[1] if cols[1] else excellent
        proficient_col = cols[2] if cols[2] else proficient
        return f"| {criteria} | {excellent_col} | {proficient_col} | {developing} | {beginning} |"
    elif len(cols) == 2:
        excellent_col = cols[1] if cols[1] else excellent
        return f"| {criteria} | {excellent_col} | {proficient} | {developing} | {beginning} |"
    else:
        # Only criteria name, fill with defaults
        return f"| {criteria} | {excellent} | {proficient} | {developing} | {beginning} |"


def _extract_worksheets_from_field(field_data: Any, field_name: str) -> Tuple[List[str], List[str], List[str]]:
    """Extract questions, MC options, and answer keys from a field. Groups questions with their MC options."""
    if not field_data:
        return [], [], []
    
    all_questions, all_mc_options, all_answer_keys = [], [], []
    
    if isinstance(field_data, list):
        # For lists, try to extract question+MC blocks together
        text = "\n".join([str(item) for item in field_data if item])
        logger.debug(f"🔍 Processing {field_name} list: {len(field_data)} items, joined text length: {len(text)}")
        
        # First, try to extract question+MC blocks (question followed by A), B), C), D))
        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this line is a question
            if '?' in line and line.endswith('?') and 10 < len(line) < 200:
                # Skip questions with markers that indicate they're not worksheet questions
                skip_markers = [
                    r'\*\*Question:\*\*',  # **Question:**
                    r'Question:\s*',  # Question:
                    r'Level\s+\d+\s*[\(:]',  # Level 1 (Gathering): or Level 1:
                    r'Gathering|Processing|Applying',  # Costa's levels
                    r'Costa\'?s\s+Level',  # Costa's Level
                    r'Reflection\s+Question',  # Reflection Question
                ]
                should_skip = False
                for marker in skip_markers:
                    if re.search(marker, line, re.IGNORECASE):
                        should_skip = True
                        break
                
                if should_skip:
                    i += 1
                    continue
                
                has_question_word = bool(re.search(r'(?:what|which|how|when|where|why|who|name|list|describe|explain|should|will|does|do|is|are|can|would|could)', line, re.IGNORECASE))
                is_numbered = bool(re.match(r'^\d+[\.\)]', line))
                is_short_question = len(line) < 150
                
                if has_question_word or is_numbered or is_short_question:
                    # Clean the question
                    q_clean = _clean_text(line)
                    
                    if q_clean and q_clean.lower() not in [q.lower() for q in all_questions]:
                        all_questions.append(q_clean)
                        
                        # Look for MC options following this question (next 4-6 lines that start with A), B), C), D))
                        question_mc = []
                        j = i + 1
                        expected_letter = 'A'
                        # Look ahead up to 6 lines to find MC options (in case there are blank lines)
                        max_look_ahead = min(j + 6, len(lines))
                        while j < max_look_ahead and len(question_mc) < 4:
                            next_line = lines[j].strip()
                            # Skip blank lines
                            if not next_line:
                                j += 1
                                continue
                            # Check if this line is an MC option (A) or A. format)
                            mc_match = re.match(rf'^[-•\s]*{expected_letter}[\.\)]\s+(.+)', next_line, re.IGNORECASE)
                            if mc_match:
                                opt_text = mc_match.group(1).strip()
                                # Ensure option has actual text, not just a number or dash
                                if opt_text and len(opt_text) > 2 and not re.match(r'^[\d\s\-]+$', opt_text):
                                    question_mc.append(f"{expected_letter}) {opt_text}")  # Normalize to A) format
                                    expected_letter = chr(ord(expected_letter) + 1)
                                j += 1
                            elif re.match(r'^[-•\s]*[A-D][\.\)]\s+', next_line, re.IGNORECASE):
                                # Found an MC option but not the expected letter - might be out of order
                                # Try to extract it anyway (handle both A) and A. formats)
                                letter_match = re.match(r'^[-•\s]*([A-D])[\.\)]\s+(.+)', next_line, re.IGNORECASE)
                                if letter_match:
                                    letter = letter_match.group(1).upper()
                                    opt_text = letter_match.group(2).strip()
                                    if opt_text and len(opt_text) > 2 and not re.match(r'^[\d\s\-]+$', opt_text):
                                        # Check if we already have this letter
                                        if not any(re.match(rf'^{letter}\)', opt, re.IGNORECASE) for opt in question_mc):
                                            question_mc.append(f"{letter}) {opt_text}")  # Normalize to A) format
                                            # Update expected letter to continue sequence
                                            if ord(letter) >= ord(expected_letter):
                                                expected_letter = chr(ord(letter) + 1)
                                j += 1
                            else:
                                # Not an MC option - stop looking if we've found at least one
                                if len(question_mc) > 0:
                                    break
                                j += 1
                        
                        # If we found 4 options, add them to all_mc_options in order
                        if len(question_mc) == 4:
                            # Sort by letter to ensure A, B, C, D order
                            def get_letter(opt):
                                match = re.match(r'^([A-D])\)', opt, re.IGNORECASE)
                                return match.group(1).upper() if match else 'Z'
                            question_mc.sort(key=get_letter)
                            all_mc_options.extend(question_mc)
                            logger.debug(f"🔍 Found question with 4 MC options in {field_name}: {q_clean[:50]}...")
                        i = j  # Skip past the MC options
                        continue
            
            i += 1
        
        # Also extract from joined text (fallback for questions/options not in blocks)
        questions = _extract_questions_from_text(text)
        mc_options = _extract_mc_options_from_text(text)
        answer_keys = _extract_answer_keys_from_text(text)
        
        # Add questions that weren't already found (filter out non-worksheet questions)
        skip_markers = [
            r'\*\*Question:\*\*',  # **Question:**
            r'Question:\s*',  # Question:
            r'Level\s+\d+\s*[\(:]',  # Level 1 (Gathering): or Level 1:
            r'Gathering|Processing|Applying',  # Costa's levels
            r'Costa\'?s\s+Level',  # Costa's Level
            r'Reflection\s+Question',  # Reflection Question
        ]
        for q in questions:
            # Skip questions with markers that indicate they're not worksheet questions
            should_skip = False
            for marker in skip_markers:
                if re.search(marker, q, re.IGNORECASE):
                    should_skip = True
                    break
            if not should_skip and q.lower() not in [existing_q.lower() for existing_q in all_questions]:
                all_questions.append(q)
        
        # Add MC options that weren't already found
        for mc in mc_options:
            if mc not in all_mc_options:
                all_mc_options.append(mc)
        
        all_answer_keys.extend(answer_keys)
        if questions or answer_keys:
            logger.info(f"🔍 Extracted from {field_name}: {len(all_questions)} questions, {len(all_mc_options)} MC options, {len(answer_keys)} answer keys")
        
        # Also check each item individually (catches standalone questions)
        for idx, item in enumerate(field_data):
            if item:
                item_str = str(item).strip()
                # Check if this item is a question
                if '?' in item_str:
                    # Skip questions with markers that indicate they're not worksheet questions
                    skip_markers = [
                        r'\*\*Question:\*\*',  # **Question:**
                        r'Question:\s*',  # Question:
                        r'Level\s+\d+\s*[\(:]',  # Level 1 (Gathering): or Level 1:
                        r'Gathering|Processing|Applying',  # Costa's levels
                        r'Costa\'?s\s+Level',  # Costa's Level
                        r'Reflection\s+Question',  # Reflection Question
                    ]
                    should_skip = False
                    for marker in skip_markers:
                        if re.search(marker, item_str, re.IGNORECASE):
                            should_skip = True
                            break
                    
                    if should_skip:
                        continue
                    
                    clean_item = _clean_text(item_str, remove_bullets=True)
                    # VERY LENIENT: if it ends with ? and is under 300 chars and over 5 chars, it's a question
                    # Also check for question words anywhere in the text
                    ends_with_q = clean_item.endswith('?')
                    has_question_word = bool(re.search(r'(?:what|which|how|when|where|why|who|name|list|describe|explain|should|will|does|do|is|are|can|would|could)', clean_item, re.IGNORECASE))
                    reasonable_length = 5 < len(clean_item) < 300
                    
                    is_question = ends_with_q and reasonable_length
                    # Also accept if it has a question word and ends with ? (even if longer)
                    if not is_question and has_question_word and ends_with_q and len(clean_item) < 500:
                        is_question = True
                    
                    if is_question:
                        # Check if it's already in all_questions (case-insensitive)
                        item_lower = clean_item.lower()
                        already_found = any(q.lower() == item_lower for q in all_questions)
                        if not already_found:
                            all_questions.append(clean_item)
                            logger.info(f"🔍 Found question in {field_name}[{idx}]: {clean_item[:80]}...")
                # Check if this item is an answer key
                if re.search(r'(?:correct\s+)?answer[:\s]*(?:[A-D]\)\s*)?', item_str, re.IGNORECASE):
                    clean_item = _clean_text(item_str, remove_bullets=True)
                    if clean_item not in all_answer_keys:
                        all_answer_keys.append(clean_item)
                        logger.debug(f"🔍 Found answer key in {field_name}[{idx}]: {clean_item[:80]}...")
                # Check if this item is an MC option (A) or A. format)
                if re.match(r'^[-\s]*[A-D][\.\)]\s+', item_str, re.IGNORECASE):
                    # Normalize to A) format
                    normalized = re.sub(r'^([-\s]*)([A-D])\.\s+', r'\1\2) ', item_str, flags=re.IGNORECASE)
                    if normalized not in all_mc_options:
                        all_mc_options.append(normalized)
    else:
        text = str(field_data)
        all_questions = _extract_questions_from_text(text)
        all_mc_options = _extract_mc_options_from_text(text)
        all_answer_keys = _extract_answer_keys_from_text(text)
        
        # Log extraction results for debugging
        if all_questions or all_mc_options or all_answer_keys:
            logger.debug(f"🔍 Extracted from {field_name} (string): {len(all_questions)} questions, {len(all_mc_options)} MC options, {len(all_answer_keys)} answer keys")
    
    return all_questions, all_mc_options, all_answer_keys


def _extract_section_from_text(text: str, section_patterns: List[str], stop_pattern: str = None) -> str:
    """Extract a section from text using patterns, optionally stopping at a pattern."""
    for pattern in section_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            section = match.group(1).strip() if match.groups() else match.group(0).strip()
            if stop_pattern:
                stop_match = re.search(stop_pattern, section, re.IGNORECASE)
                if stop_match:
                    section = section[:stop_match.start()].strip()
            if section and len(section) > 50:
                return section
    return None


def _is_valid_rubric_row(row: str) -> bool:
    """Check if a table row is a valid rubric row (not a header or separator)."""
    if not row or '|' not in row:
        return False
    
    cols = [col.strip() for col in row.split('|') if col.strip()]
    if len(cols) < 2:
        return False
    
    # REJECT header rows - check if first column is "Criteria" and row contains performance level headers
    first_col = cols[0].lower() if cols else ''
    is_header_row = (
        first_col == 'criteria' and 
        any(re.search(r'(excellent|proficient|developing|beginning)\s*\(?\d+\s*pts?\)?', col, re.IGNORECASE) for col in cols)
    )
    if is_header_row:
        return False
    
    # REJECT separator rows (all dashes, colons, or spaces)
    if all(re.match(r'^[\s\-:]+$', col) for col in cols):
        return False
    
    # REJECT rows that are just performance level headers without a criterion
    if len(cols) >= 4 and all(re.search(r'(excellent|proficient|developing|beginning)', col, re.IGNORECASE) for col in cols[:4]):
        return False
    
    # ACCEPT if it has a criterion name (not "Criteria") and performance descriptions
    has_criterion_name = bool(re.search(
        r'(?:technique|accuracy|understanding|skill|performance|grip|follow-through|throwing|catching|running|ability|mechanics|stance|swing|dribbling|passing|shooting|defense|communication|teamwork|form|control)',
        first_col, re.IGNORECASE
    )) and first_col.lower() != 'criteria'
    
    has_performance = bool(re.search(
        r'(?:demonstrates|shows|excellent|proficient|developing|beginning|perfect|good|inconsistent|struggles|thorough|basic|limited|consistently|most\s+of\s+the\s+time|often|frequently|needs\s+improvement|inaccuracies|form|accuracy|power)',
        row, re.IGNORECASE
    ))
    
    # Valid rubric row: has a criterion name AND performance descriptions
    return has_criterion_name and has_performance and len(cols) >= 2


def _build_rubric_table(rows: List[str]) -> str:
    """Build a complete rubric table from rubric rows, deduplicating and formatting."""
    # Filter out invalid rows (headers, separators) before deduplication
    valid_rows = []
    if rows:
        valid_rows = [row for row in rows if _is_valid_rubric_row(row)]
    
    if not valid_rows:
        # No valid criteria rows found - create a default rubric
        logger.warning("⚠️ No valid rubric criteria rows found, creating default rubric")
        default_criteria = [
            "Dribbling Technique",
            "Passing Accuracy",
            "Shooting Form",
            "Defensive Positioning",
            "Teamwork and Communication"
        ]
        formatted_rows = []
        for criteria in default_criteria:
            formatted_rows.append(f"| {criteria} | Demonstrates excellent technique and understanding | Shows good form with minor errors | Demonstrates basic technique but lacks consistency | Struggles with basic technique, needs significant improvement |")
        
        header = "Grading Rubric:\n| Criteria | Excellent (4 pts) | Proficient (3 pts) | Developing (2 pts) | Beginning (1 pt) |\n|----------|-------------------|-------------------|-------------------|------------------|\n"
        return header + "\n".join(formatted_rows)
    
    # Deduplicate rows (case-insensitive, ignoring whitespace)
    seen = set()
    unique_rows = []
    for row in valid_rows:
        if not row or not row.strip():
            continue
        row_clean = re.sub(r'\s+', ' ', row.strip()).lower()
        if row_clean and row_clean not in seen:
            unique_rows.append(row)
            seen.add(row_clean)
    
    if not unique_rows:
        return ""
    
    # Format rows and deduplicate
    formatted_rows = []
    seen_criteria = set()
    seen_content = set()
    
    for row in unique_rows:
        formatted = _format_rubric_row(row)
        if not formatted or not formatted.strip():
            continue
        
        # Extract criteria name
        criteria_match = re.match(r'^\|\s*([^|]+)\s*\|', formatted)
        if criteria_match:
            criteria_name = criteria_match.group(1).strip().lower()
            # Skip duplicate criteria
            if criteria_name in seen_criteria:
                continue
            seen_criteria.add(criteria_name)
        
        # Also check for duplicate content (normalized)
        content_key = re.sub(r'\s+', ' ', formatted.strip()).lower()
        if content_key in seen_content:
            continue
        seen_content.add(content_key)
        
        formatted_rows.append(formatted)
    
    if not formatted_rows:
        return ""
    
    # Add header
    header = "Grading Rubric:\n| Criteria | Excellent (4 pts) | Proficient (3 pts) | Developing (2 pts) | Beginning (1 pt) |\n|----------|-------------------|-------------------|-------------------|------------------|\n"
    return header + "\n".join(formatted_rows)


def _clean_objectives_of_rubrics(objectives: List[Any]) -> List[Any]:
    """Remove rubric rows from objectives."""
    if not objectives or not isinstance(objectives, list):
        return objectives
    
    cleaned = []
    for obj in objectives:
        obj_str = str(obj) if obj else ""
        # Use the same validation logic as _is_valid_rubric_row
        if '|' in obj_str:
            is_rubric = _is_valid_rubric_row(obj_str)
        else:
            is_rubric = False
        
        if not is_rubric:
            cleaned.append(obj)
        else:
            logger.info(f"🔍 Removing rubric row from objectives: {obj_str[:80]}...")
    
    return cleaned if len(cleaned) < len(objectives) else objectives


def _extract_rubrics_from_field(field_data: Any) -> str:
    """Extract rubric content from a field."""
    if not field_data:
        return ""
    
    text = str(field_data) if not isinstance(field_data, list) else "\n".join([str(item) for item in field_data if item])
    
    patterns = [
        r'(?:###\s*)?(?:rubric|grading\s+rubric|assessment\s+rubric)[:\s]*(.+?)(?=###|assessment|formative|summative|accommodation|$)',
        r'use\s+a\s+rubric\s+to\s+evaluate[:\s]*(.+?)(?=assessment|formative|summative|accommodation|$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            if content and len(content) > 20:
                if '|' in content or re.search(r'(criteria|excellent|proficient)', content, re.IGNORECASE):
                    return content
    
    return ""


def _parse_json_from_response(response_text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from markdown code blocks.
    Uses robust brace-counting method (same as workout plan extraction) to handle
    multiline JSON that might be truncated by simple regex patterns.
    """
    # First, try simple regex pattern (works for most cases)
    json_pattern = re.compile(r'```(?:json)?\s*(\{.*?\})\s*```', re.DOTALL | re.IGNORECASE)
    json_match = json_pattern.search(response_text)
    if json_match:
        try:
            json_str = json_match.group(1)
            parsed_data = json.loads(json_str)
            if isinstance(parsed_data, dict):
                logger.info(f"✅ Parsed JSON successfully from markdown code block (simple method), keys: {list(parsed_data.keys())[:10]}")
                return parsed_data
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"⚠️ Failed to parse JSON from markdown code block (simple method): {e}")
            # Fall through to more robust extraction below
            json_match = None
    
    # If simple extraction failed, try the more robust brace-counting approach
    # This handles cases where JSON is multiline or the regex pattern cuts it off too early
    if json_match is None:
        json_marker_pattern = re.compile(r'```(?:json)?', re.IGNORECASE)
        json_marker_match = json_marker_pattern.search(response_text)
        
        if json_marker_match:
            try:
                marker_start = json_marker_match.start()
                marker_end = json_marker_match.end()
                
                # Find the opening brace after the marker
                brace_start = None
                for i in range(marker_end, min(marker_end + 100, len(response_text))):
                    if response_text[i] == '{':
                        brace_start = i
                        break
                
                if brace_start is None:
                    logger.warning(f"⚠️ Found ```json marker at {marker_start} but no opening brace found")
                else:
                    # Count braces to find the complete JSON object
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
                    
                    # If we didn't find a closing brace, try to find the closing ``` marker
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
                            # No closing marker found, use end of response
                            potential_json = response_text[brace_start:].rstrip()
                            last_brace = potential_json.rfind('}')
                            if last_brace > 0:
                                json_str = potential_json[:last_brace + 1]
                                # Check for missing braces/brackets and add them
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
                            else:
                                logger.warning(f"⚠️ Using end of response as fallback, extracted {len(potential_json) if 'potential_json' in locals() else 0} chars")
                                json_str = potential_json if 'potential_json' in locals() else None
                                json_end_pos = len(response_text) if json_str else None
                    
                    # Try to parse the extracted JSON
                    if json_end_pos is not None and json_str is not None:
                        try:
                            parsed_data = json.loads(json_str)
                            if isinstance(parsed_data, dict):
                                logger.info(f"✅ Parsed JSON successfully (robust method), keys: {list(parsed_data.keys())[:10]}")
                                logger.info(f"🔍 Extracted JSON string length: {len(json_str)} chars (start: {brace_start}, end: {json_end_pos})")
                                return parsed_data
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ JSON parsing failed (robust method): {e}")
                            logger.error(f"❌ JSON string (first 500 chars): {json_str[:500]}")
                            logger.error(f"❌ JSON string (last 500 chars): {json_str[-500:] if len(json_str) > 500 else json_str}")
            except Exception as e:
                logger.error(f"❌ Error during JSON extraction: {e}", exc_info=True)
    
    return None


def _extract_title_from_sources(original_message: str, response_lines: List[str]) -> str:
    """Extract lesson plan title from original message or response text."""
    if original_message:
        title_match = re.search(r'lesson\s+plan\s+(?:on|for|about)\s+(.+?)(?:\.|$|please)', original_message, flags=re.IGNORECASE)
        if not title_match:
            title_match = re.search(r'lesson\s+(?:on|for|about)\s+(.+?)(?:\.|$|please)', original_message, flags=re.IGNORECASE)
        if title_match:
            topic = title_match.group(1).strip()
            topic = re.sub(r'^(a|an|the)\s+', '', topic, flags=re.IGNORECASE)
            return topic.title() + " Lesson Plan"
    
    for line in response_lines[:10]:
        line = line.strip()
        if not line:
            continue
        title_match = re.search(r'title[:\s]+(.+)', line, flags=re.IGNORECASE)
        if title_match:
            return re.sub(r'\*\*', '', title_match.group(1)).strip()
        title_match = re.search(r'lesson\s+plan\s+(?:on|for)\s+(.+?)(?:\.|$)', line, flags=re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip().title()
        title_match = re.search(r'(?:lesson\s+plan|create|help)\s+(?:on|for|about)\s+(.+?)(?:\.|$)', line, flags=re.IGNORECASE)
        if title_match:
            topic = title_match.group(1).strip()
            topic = re.sub(r'^(a|an|the)\s+', '', topic, flags=re.IGNORECASE)
            return topic.title()
        elif len(line) < 100 and not re.match(r'^(absolutely|sure|here|i\s+can|i\s+apologize)', line.lower()):
            clean_title = re.sub(r'\*\*', '', line).strip()
            if not re.match(r'^(absolutely|sure|here|i\s+can|i\s+apologize)', clean_title.lower()):
                return clean_title
    
    return ""


def _extract_and_enhance_worksheets(final_data: Dict[str, Any], lesson_data: Dict[str, Any], 
                                     objectives_data: List[Any], response_text: str) -> None:
    """Extract worksheets from multiple sources and ensure minimum 10 questions."""
    logger.info(f"🔍 _extract_and_enhance_worksheets called: objectives_count={len(objectives_data) if objectives_data else 0}, response_text_length={len(response_text) if response_text else 0}")
    worksheets_field = final_data.get("worksheets", "")
    question_count = _count_questions_in_text(worksheets_field)
    
    # ALWAYS extract and recombine to ensure proper matching of MC options to questions
    # This ensures all questions have complete MC options and answer keys match correctly
    logger.info(f"🔍 Worksheets check: count={question_count}, field_length={len(worksheets_field) if worksheets_field else 0}")
    
    # Extract from all sources and deduplicate
    all_questions, all_mc_options, all_answer_keys = [], [], []
    seen_questions = set()
    seen_mc_options = set()  # Deduplicate MC options
    
    fields_to_check = [
        (worksheets_field, "worksheets"),
        (objectives_data, "objectives"),
        (final_data.get("costas_questioning", "") or lesson_data.get("costas_questioning", ""), "costas_questioning"),
        (final_data.get("curriculum_standards", "") or lesson_data.get("curriculum_standards", ""), "curriculum_standards"),
        (response_text, "response_text"),
    ]
    
    for field_data, field_name in fields_to_check:
        if field_data:
            q, mc, ak = _extract_worksheets_from_field(field_data, field_name)
            # Deduplicate questions
            for question in q:
                q_key = question.lower().strip()
                if q_key not in seen_questions:
                    all_questions.append(question)
                    seen_questions.add(q_key)
            # Deduplicate MC options (by first 50 chars to catch similar options)
            for opt in mc:
                opt_key = opt.lower().strip()[:50] if len(opt) > 50 else opt.lower().strip()
                if opt_key not in seen_mc_options:
                    all_mc_options.append(opt)
                    seen_mc_options.add(opt_key)
            all_answer_keys.extend(ak)
            if q or ak:
                logger.info(f"✅ Found {len(q)} questions, {len(mc)} MC options, {len(ak)} answer keys in {field_name}")
    
    logger.info(f"🔍 Total extracted: {len(all_questions)} unique questions, {len(all_mc_options)} unique MC options, {len(all_answer_keys)} answer keys")
    
    # CRITICAL FIX: Extract question-option pairs directly from response_text for accurate matching
    # This is more reliable than trying to match separately extracted questions and options
    question_option_pairs = []
    if response_text:
        pairs = _extract_question_option_pairs_from_text(response_text)
        if pairs:
            logger.info(f"✅ Extracted {len(pairs)} question-option pairs directly from response_text")
            question_option_pairs = pairs
    
    # If we have pairs, use them to build the worksheet (more accurate)
    # Use pairs if we have at least 3 (better than mismatched options)
    if question_option_pairs and len(question_option_pairs) >= 3:
        # Build worksheet from pairs - take exactly 10 questions
        worksheet_parts = []
        num_questions = min(10, len(question_option_pairs))
        
        for idx in range(1, num_questions + 1):
            pair = question_option_pairs[idx - 1]  # Use idx-1 since we're numbering from 1
            question = pair['question']
            options = pair['options']
            
            # Format question with number
            question_text = f"{idx}. {question}"
            
            # Add options if available
            if options:
                formatted_options = [f"   {opt}" for opt in options]
                question_text += "\n" + "\n".join(formatted_options)
            
            worksheet_parts.append(question_text)
        
        # Build answer keys section - match by question number if available
        # Ensure we have exactly num_questions answer keys
        answer_keys_section = ""
        if all_answer_keys:
            answer_keys_section = "\n\nAnswer Key:\n\n"
            # Create a map of answer keys by question number
            answer_key_map = {}
            unnumbered_keys = []
            for ak in all_answer_keys:
                ak_clean = ak.strip()
                # Extract question number from answer key
                num_match = re.match(r'^(\d+)[\.\)]\s*(.+)', ak_clean)
                if num_match:
                    q_num = int(num_match.group(1))
                    answer_key_map[q_num] = ak_clean
                else:
                    unnumbered_keys.append(ak_clean)
            
            # Match answer keys to questions - ensure we get exactly num_questions keys
            for idx in range(1, num_questions + 1):
                if idx in answer_key_map:
                    # Use the answer key that matches this question number
                    ak = answer_key_map[idx]
                elif unnumbered_keys:
                    # Use next unnumbered key
                    ak = unnumbered_keys.pop(0)
                    # Ensure it has "Correct Answer:" prefix and number
                    if not re.match(r'^\d+\.', ak):
                        ak = f"{idx}. {ak}"
                    if not re.search(r'correct\s+answer', ak, re.IGNORECASE):
                        ak = re.sub(r'^(\d+\.\s*)', r'\1Correct Answer: ', ak)
                else:
                    # No more answer keys available - create a placeholder
                    ak = f"{idx}. Correct Answer: [Answer key not found]"
                
                # Ensure format is correct
                if not re.match(r'^\d+\.', ak):
                    ak = f"{idx}. {ak}"
                if not re.search(r'correct\s+answer', ak, re.IGNORECASE):
                    ak = re.sub(r'^(\d+\.\s*)', r'\1Correct Answer: ', ak)
                
                answer_keys_section += ak + "\n"
        
        worksheet = "Student Worksheet:\n\n" + "\n\n".join(worksheet_parts) + answer_keys_section
        final_data["worksheets"] = worksheet
        logger.info(f"✅ Built worksheet: {num_questions} questions, {len(worksheet_parts)} question parts, answer keys: {len(answer_keys_section.split(chr(10))) if answer_keys_section else 0} lines")
        return
    
    curriculum_standards_text = final_data.get("curriculum_standards", "")
    if all_answer_keys and curriculum_standards_text and isinstance(curriculum_standards_text, str):
            # More aggressive cleaning patterns for answer keys
            cleaned = curriculum_standards_text
            # Remove numbered answer keys: "1. Correct Answer: A - description"
            cleaned = re.sub(r'\d+\.\s*(?:correct\s+)?answer[:\s]*[A-D]\s*-\s*[^\n]+', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
            # Remove "Correct Answer: A - description"
            cleaned = re.sub(r'(?:correct\s+)?answer[:\s]*[A-D]\s*-\s*[^\n]+', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
            # Remove "Correct Answer: A) description"
            cleaned = re.sub(r'(?:correct\s+)?answer[:\s]*[A-D]\)\s*[^\n]+', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
            # Remove standalone "Answer: A" lines
            cleaned = re.sub(r'^\s*(?:correct\s+)?answer[:\s]*[A-D]\s*$', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
            cleaned = cleaned.strip()
            if len(cleaned) < len(curriculum_standards_text):
                final_data["curriculum_standards"] = cleaned
                logger.info(f"✅ Cleaned answer keys from curriculum_standards (removed {len(curriculum_standards_text) - len(cleaned)} chars)")
    
    if all_questions:
        logger.info(f"🔍 Combining {len(all_questions)} questions into worksheets...")
        # If worksheets_field is just headers, pass empty string to force new worksheet creation
        worksheets_field_to_use = worksheets_field if _count_questions_in_text(worksheets_field) > 0 else ""
        combined = _combine_worksheets(worksheets_field_to_use, all_questions, all_mc_options, all_answer_keys)
        combined_count = _count_questions_in_text(combined)
        logger.info(f"🔍 Combined result: {combined_count} questions, {len(combined)} chars (original had {question_count} questions)")
        # Always use combined worksheet if it has content (even if count is off due to numbering)
        # Use the actual number of questions added, not the count from _count_questions_in_text
        actual_question_count = len([q for q in all_questions if q and q.strip().endswith('?')])
        if len(combined) > 50:
            # If we have 10+ questions or if it's better than original, use it
            if combined_count >= 10 or combined_count > question_count or actual_question_count >= 10:
                final_data["worksheets"] = combined
                logger.info(f"✅ Combined worksheets: {combined_count} questions counted, {actual_question_count} actual questions (was {question_count})")
            elif len(combined) > 200:  # If worksheet has substantial content, use it even if count is off
                final_data["worksheets"] = combined
                logger.info(f"✅ Combined worksheets: {len(combined)} chars of content (count may be off due to formatting)")
            
            if objectives_data:
                cleaned = _clean_objectives_of_questions(objectives_data)
                if len(cleaned) < len(objectives_data):
                    final_data["objectives"] = cleaned
                    logger.info(f"✅ Cleaned {len(objectives_data) - len(cleaned)} items from objectives")
        else:
            logger.warning(f"⚠️ Combined worksheet has insufficient content: {combined_count} questions, {len(combined)} chars")
    else:
        logger.warning(f"⚠️ No questions found to combine! Checked {len(fields_to_check)} fields")


def _extract_and_enhance_rubrics(final_data: Dict[str, Any], lesson_data: Dict[str, Any], 
                                 objectives_data: List[Any], response_text: str) -> None:
    """Extract rubrics from multiple sources and ensure proper formatting."""
    logger.info(f"🔍 _extract_and_enhance_rubrics called: current_rubrics={final_data.get('rubrics', '')[:50] if final_data.get('rubrics') else 'empty'}..., objectives_count={len(objectives_data) if objectives_data else 0}")
    
    # Check if existing rubric is incomplete (truncated)
    existing_rubrics = final_data.get("rubrics", "")
    is_incomplete = False
    if existing_rubrics and isinstance(existing_rubrics, str) and existing_rubrics.strip():
        existing_rubrics_clean = existing_rubrics.strip()
        # Check for signs of truncation
        if existing_rubrics_clean.endswith('|') or re.search(r'\|\s*[A-Z][a-z]+\s*$', existing_rubrics_clean):
            is_incomplete = True
            logger.warning(f"⚠️ Existing rubric appears truncated, will try to extract full rubric from response_text")
        elif '|' in existing_rubrics_clean and 'criteria' in existing_rubrics_clean.lower():
            # Count data rows
            lines = existing_rubrics_clean.split('\n')
            data_row_count = sum(1 for line in lines if '|' in line and 
                                not re.match(r'^\|[\s\-:]+\|', line) and
                                not line.lower().startswith('| criteria') and
                                line.strip().startswith('|') and len(line.split('|')) >= 3)
            if data_row_count < 3:
                is_incomplete = True
                logger.warning(f"⚠️ Existing rubric appears incomplete ({data_row_count} data rows), will try to extract full rubric")
    
    if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip() or is_incomplete:
        if objectives_data:
            objectives_text = "\n".join([str(obj) for obj in objectives_data if obj])
            rubric_rows = _extract_rubric_rows_from_text(objectives_text)
            valid_rows = [row for row in rubric_rows if _is_valid_rubric_row(row)]
            
            # Also check individual objectives for rubric-like content (incomplete rows)
            for obj in objectives_data:
                obj_str = str(obj) if obj else ""
                # More aggressive: check any item with pipes, even if short
                if '|' in obj_str and len(obj_str) > 15:
                    # Check if it's a valid rubric row
                    if _is_valid_rubric_row(obj_str):
                        # Check if it's not already in valid_rows (by content, not exact match)
                        obj_clean = obj_str.strip()
                        already_found = any(obj_clean in row or row in obj_clean for row in valid_rows)
                        if not already_found:
                            valid_rows.append(obj_str)
                            logger.info(f"🔍 Found additional rubric row in individual objective: {obj_str[:80]}...")
                    # Also check if it looks like a rubric row even if validation is borderline
                    elif len(obj_str.split('|')) >= 3:  # At least 3 columns
                        cols = [col.strip() for col in obj_str.split('|') if col.strip()]
                        if len(cols) >= 2:
                            # Check for rubric indicators
                            has_technique = any(re.search(r'(technique|accuracy|understanding|skill|performance|criteria)', col, re.IGNORECASE) for col in cols)
                            has_performance = any(re.search(r'(demonstrates|shows|excellent|proficient|developing|beginning|good|form)', col, re.IGNORECASE) for col in cols)
                            if has_technique or has_performance:
                                if obj_str not in valid_rows:
                                    valid_rows.append(obj_str)
                                    logger.info(f"🔍 Found borderline rubric row in individual objective (lenient check): {obj_str[:80]}...")
            
            if valid_rows:
                logger.info(f"🔍 Found {len(valid_rows)} rubric rows in objectives")
                rubric_table = _build_rubric_table(valid_rows)
                if rubric_table:
                    # Only set if rubrics is empty (don't overwrite existing)
                    if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
                        final_data["rubrics"] = rubric_table
                        logger.info(f"✅ Extracted rubric from objectives: {len(valid_rows)} rows")
                    else:
                        logger.info(f"⚠️ Rubric already exists, skipping extraction from objectives")
                    
                    cleaned = _clean_objectives_of_rubrics(objectives_data)
                    if len(cleaned) < len(objectives_data):
                        final_data["objectives"] = cleaned
                        logger.info(f"✅ Cleaned {len(objectives_data) - len(cleaned)} rubric rows from objectives")
        
        assessments_text = final_data.get("assessments", "") or lesson_data.get("assessments", "")
        curriculum_standards_text = final_data.get("curriculum_standards", "") or lesson_data.get("curriculum_standards", "")
        
        # Check assessments field for rubric content
        if assessments_text:
            logger.info(f"🔍 Checking assessments field for rubric (length: {len(assessments_text)})")
            # Extract rubric rows from assessments
            rubric_rows_from_assessments = _extract_rubric_rows_from_text(assessments_text)
            valid_rows_from_assessments = [row for row in rubric_rows_from_assessments if _is_valid_rubric_row(row)]
            if valid_rows_from_assessments:
                rubric_table = _build_rubric_table(valid_rows_from_assessments)
                if rubric_table and (not final_data.get("rubrics") or not final_data.get("rubrics", "").strip()):
                    final_data["rubrics"] = rubric_table
                    logger.info(f"✅ Extracted rubric from assessments: {len(valid_rows_from_assessments)} rows")
            else:
                # Try the _extract_rubrics_from_field function
                rubric_content = _extract_rubrics_from_field(assessments_text)
                if rubric_content and (not final_data.get("rubrics") or not final_data.get("rubrics", "").strip()):
                    final_data["rubrics"] = rubric_content
                    logger.info(f"✅ Extracted rubric content from assessments field")
        
        # Also check curriculum_standards if it mentions rubric
        if curriculum_standards_text and 'rubric' in curriculum_standards_text.lower():
            logger.info(f"🔍 Checking curriculum_standards field for rubric (length: {len(curriculum_standards_text)})")
            rubric_content = _extract_rubrics_from_field(curriculum_standards_text)
            if rubric_content and (not final_data.get("rubrics") or not final_data.get("rubrics", "").strip()):
                final_data["rubrics"] = rubric_content
                logger.info(f"✅ Extracted rubric from curriculum_standards")
                
                # Clean rubric from curriculum_standards if it was extracted from there
                if curriculum_standards_text:
                    # Remove rubric table (markdown table format)
                    cleaned = re.sub(r'\|[^\|\n]+\|[^\|\n]+(?:\|[^\|\n]+)*\|', '', curriculum_standards_text, flags=re.MULTILINE)
                    # Remove rubric header
                    cleaned = re.sub(r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*', '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
                    # Remove any remaining rubric-related content
                    cleaned = re.sub(r'\|.*?criteria.*?\|.*?excellent.*?\|', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
                    cleaned = cleaned.strip()
                    if len(cleaned) < len(curriculum_standards_text):
                        final_data["curriculum_standards"] = cleaned
                        logger.info(f"✅ Cleaned rubric from curriculum_standards (removed {len(curriculum_standards_text) - len(cleaned)} chars)")
        
        if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
            if response_text:
                logger.info(f"🔍 Searching response_text for rubric (length: {len(response_text)})")
                # Try multiple patterns to find rubric section - use greedy match to get more content
                rubric_section = _extract_section_from_text(
                    response_text,
                    [
                        # Greedy match to get all rubric content until next major section
                        r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*\n(.+?)(?=\n###|\n##\s+[A-Z]|assessments?|exit\s+ticket|extensions?|safety|homework|worksheets?|$)',
                        # Match table directly
                        r'(\|\s*Criteria\s*\|[^\n]+\n(?:\|[-:\s]+\|.*\n)?(?:\|[^\n]+\|.*\n)+)',
                        # Emoji or header pattern
                        r'(?:📋|##)\s*(?:grading\s+)?rubrics?[:\s]*\n(.+?)(?=\n###|\n##\s+[A-Z]|assessments?|exit|extensions?|safety|homework|worksheets?|$)',
                    ]
                )
                
                if rubric_section:
                    logger.info(f"🔍 Found rubric section: {len(rubric_section)} chars, preview: {rubric_section[:100]}...")
                    # Log the full section for debugging
                    logger.debug(f"🔍 Full rubric section: {rubric_section}")
                    
                    # If section is too short, expand it to get more rows
                    if len(rubric_section) < 500:
                        logger.info(f"🔍 Rubric section too short ({len(rubric_section)} chars), expanding...")
                        # Find where rubric section starts in response_text
                        rubric_match = re.search(r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*', response_text, re.IGNORECASE)
                        if rubric_match:
                            # Extract a larger chunk starting from rubric (up to 3000 chars or until next major section)
                            start_pos = rubric_match.end()
                            # Look for next major section or end of text
                            next_section = re.search(r'(?:\n###|\n##\s+[A-Z]|assessments?|exit\s+ticket|extensions?|safety|homework|worksheets?)', response_text[start_pos:], re.IGNORECASE)
                            end_pos = start_pos + (next_section.start() if next_section else min(3000, len(response_text) - start_pos))
                            expanded_section = response_text[start_pos:end_pos].strip()
                            if len(expanded_section) > len(rubric_section):
                                rubric_section = expanded_section
                                logger.info(f"🔍 Expanded rubric section to {len(rubric_section)} chars")
                
                # ALWAYS search full response_text for rubric rows to ensure we get all of them
                # The section might be incomplete, so search everywhere
                logger.info(f"🔍 Searching full response_text for ALL rubric rows...")
                rubric_rows = _extract_rubric_rows_from_text(response_text)
                logger.info(f"🔍 Extracted {len(rubric_rows)} potential rubric rows from full response_text")
                if rubric_rows:
                    logger.debug(f"🔍 Sample rubric rows: {rubric_rows[:3]}")
                
                # Also try the rubric section if we have one
                if rubric_section and '|' in rubric_section:
                    section_rows = _extract_rubric_rows_from_text(rubric_section)
                    if section_rows:
                        # Add any rows from section that aren't already in rubric_rows
                        for row in section_rows:
                            if row not in rubric_rows:
                                rubric_rows.append(row)
                        logger.info(f"🔍 Added {len(section_rows)} rows from rubric section, total: {len(rubric_rows)} rows")
                
                # Use lenient validation - accept rows with at least 2 columns that look like rubric data
                valid_rows = []
                for row in rubric_rows:
                    if _is_valid_rubric_row(row):
                        valid_rows.append(row)
                    else:
                        # Lenient check: if it has 2+ columns and doesn't look like a header, accept it
                        cols = [col.strip() for col in row.split('|') if col.strip()]
                        if len(cols) >= 2:
                            first_col = cols[0].lower()
                            # Skip if it's clearly a header row
                            is_header = (
                                first_col == 'criteria' and 
                                any(re.search(r'(excellent|proficient|developing|beginning)\s*\(?\d+\s*pts?\)?', col, re.IGNORECASE) for col in cols)
                            )
                            if not is_header and first_col not in ['excellent', 'proficient', 'developing', 'beginning']:
                                # Accept if it has a criteria name (not just performance levels)
                                has_criteria_name = bool(re.search(
                                    r'(technique|skill|performance|ability|understanding|accuracy|form|control|dribbling|passing|shooting|defense|teamwork|communication|stance|grip|follow-through)',
                                    first_col, re.IGNORECASE
                                ))
                                if has_criteria_name:
                                    valid_rows.append(row)
                                    logger.info(f"🔍 Accepted rubric row (lenient, {len(cols)} cols): {row[:80]}...")
                
                logger.info(f"🔍 Validated {len(valid_rows)} rubric rows (including lenient matches)")
                
                if valid_rows:
                    # If we only found 1-2 rows, supplement with default criteria to make it comprehensive
                    if len(valid_rows) < 3:
                        logger.info(f"🔍 Only {len(valid_rows)} criteria found, supplementing with default criteria...")
                        # Extract criteria names we already have (both full name and keywords)
                        existing_criteria_names = set()
                        existing_criteria_keywords = set()
                        for row in valid_rows:
                            cols = [col.strip() for col in row.split('|') if col.strip()]
                            if cols:
                                criteria_name = cols[0].lower()
                                existing_criteria_names.add(criteria_name)
                                # Also extract keywords from the criteria name
                                if 'dribbling' in criteria_name:
                                    existing_criteria_keywords.add('dribbling')
                                if 'passing' in criteria_name:
                                    existing_criteria_keywords.add('passing')
                                if 'shooting' in criteria_name:
                                    existing_criteria_keywords.add('shooting')
                                if 'defense' in criteria_name or 'defensive' in criteria_name:
                                    existing_criteria_keywords.add('defense')
                                if 'teamwork' in criteria_name or 'communication' in criteria_name:
                                    existing_criteria_keywords.add('teamwork')
                        
                        # Add default criteria that aren't already present
                        # Use a set to track which criteria names we've added to prevent duplicates
                        added_criteria_names = set()
                        default_criteria_list = [
                            ('dribbling', 'Dribbling Technique'),
                            ('passing', 'Passing Accuracy'),
                            ('shooting', 'Shooting Form'),
                            ('defense', 'Defensive Positioning'),
                            ('teamwork', 'Teamwork and Communication')
                        ]
                        
                        # Check what we have and add missing ones
                        for keyword, criteria_name in default_criteria_list:
                            criteria_name_lower = criteria_name.lower()
                            # Skip if we already have this exact criteria name
                            if criteria_name_lower in existing_criteria_names:
                                continue
                            # Skip if we already added this criteria name
                            if criteria_name_lower in added_criteria_names:
                                continue
                            # Skip if we have a keyword match in existing criteria
                            if keyword in existing_criteria_keywords:
                                continue
                            
                            # Create a default row for this criteria
                            default_row = f"| {criteria_name} | Demonstrates excellent technique and understanding | Shows good form with minor errors | Demonstrates basic technique but lacks consistency | Struggles with basic technique, needs significant improvement |"
                            valid_rows.append(default_row)
                            added_criteria_names.add(criteria_name_lower)
                            logger.info(f"🔍 Added default criteria: {criteria_name}")
                        
                        logger.info(f"🔍 Expanded rubric to {len(valid_rows)} criteria rows")
                    
                    rubric_table = _build_rubric_table(valid_rows)
                    if rubric_table:
                        # Only set if rubrics is empty (don't overwrite existing)
                        if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
                            final_data["rubrics"] = rubric_table
                            logger.info(f"✅ Extracted rubric from raw text: {len(valid_rows)} criteria rows")
                        else:
                            logger.info(f"⚠️ Rubric already exists, skipping extraction from raw text")
                elif rubric_section:
                    # Parse the rubric section and format each row properly
                    logger.info(f"🔍 Formatting rubric section directly (validation failed but section exists, {len(rubric_section)} chars)")
                    
                    # If section is too short, try extracting from full response_text around the rubric area
                    if len(rubric_section) < 200:
                        logger.info(f"🔍 Rubric section too short ({len(rubric_section)} chars), searching full response_text for rubric table...")
                        # Find where rubric section starts in response_text
                        rubric_match = re.search(r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*', response_text, re.IGNORECASE)
                        if rubric_match:
                            # Extract a larger chunk starting from rubric (up to 2000 chars or until next major section)
                            start_pos = rubric_match.end()
                            # Look for next major section or end of text
                            next_section = re.search(r'(?:\n###|assessments?|exit|extensions?|safety|homework|worksheets?)', response_text[start_pos:], re.IGNORECASE)
                            end_pos = start_pos + (next_section.start() if next_section else min(2000, len(response_text) - start_pos))
                            expanded_section = response_text[start_pos:end_pos].strip()
                            if len(expanded_section) > len(rubric_section):
                                rubric_section = expanded_section
                                logger.info(f"🔍 Expanded rubric section to {len(rubric_section)} chars")
                    
                    # Extract all rows from the section - try multiple methods
                    section_rows = _extract_rubric_rows_from_text(rubric_section)
                    
                    # If still no rows, try splitting by lines and looking for table-like content
                    if not section_rows:
                        logger.info(f"🔍 No rows found with standard extraction, trying line-by-line parsing...")
                        for line in rubric_section.split('\n'):
                            line = line.strip()
                            # Accept any line with pipes that looks like a table row
                            if '|' in line and line.count('|') >= 2:
                                # Skip separator lines
                                if not re.match(r'^\|\s*[-:\s]+\|', line):
                                    section_rows.append(line)
                        logger.info(f"🔍 Found {len(section_rows)} rows via line-by-line parsing")
                    
                    if section_rows:
                        # Filter out header rows and separator rows before formatting
                        data_rows = []
                        for row in section_rows:
                            cols = [col.strip() for col in row.split('|') if col.strip()]
                            if not cols:
                                continue
                            first_col = cols[0].lower()
                            # Skip header rows
                            is_header = (
                                first_col == 'criteria' and 
                                any(re.search(r'(excellent|proficient|developing|beginning)\s*\(?\d+\s*pts?\)?', col, re.IGNORECASE) for col in cols)
                            )
                            # Skip separator rows
                            is_separator = all(re.match(r'^[\s\-:]+$', col) for col in cols)
                            if not is_header and not is_separator and len(cols) >= 2:
                                data_rows.append(row)
                        
                        logger.info(f"🔍 Filtered to {len(data_rows)} data rows (excluding headers/separators)")
                        
                        # Format each row to ensure all 4 performance levels
                        formatted_rows = []
                        for row in data_rows:
                            formatted = _format_rubric_row(row)
                            if formatted and formatted.strip():
                                # Double-check it's not a header
                                criteria_match = re.match(r'^\|\s*([^|]+)\s*\|', formatted)
                                if criteria_match:
                                    criteria_name = criteria_match.group(1).strip().lower()
                                    if criteria_name != 'criteria':
                                        formatted_rows.append(formatted)
                        
                        if formatted_rows:
                            # Build proper rubric table with header (only once)
                            header = "Grading Rubric:\n| Criteria | Excellent (4 pts) | Proficient (3 pts) | Developing (2 pts) | Beginning (1 pt) |\n|----------|-------------------|-------------------|-------------------|------------------|\n"
                            rubric_table = header + "\n".join(formatted_rows)
                            # Only set if rubrics is empty (don't overwrite existing)
                            if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
                                final_data["rubrics"] = rubric_table
                                logger.info(f"✅ Formatted and saved rubric from section: {len(formatted_rows)} criteria rows")
                            else:
                                logger.info(f"⚠️ Rubric already exists, skipping formatted rubric section")
                        else:
                            # Fallback: use section as-is but ensure it has proper header
                            if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
                                # Check if it already has a header
                                if not re.search(r'criteria.*excellent.*proficient', rubric_section, re.IGNORECASE):
                                    header = "Grading Rubric:\n| Criteria | Excellent (4 pts) | Proficient (3 pts) | Developing (2 pts) | Beginning (1 pt) |\n|----------|-------------------|-------------------|-------------------|------------------|\n"
                                    final_data["rubrics"] = header + rubric_section
                                else:
                                    final_data["rubrics"] = "Grading Rubric:\n" + rubric_section
                                logger.info(f"✅ Using rubric section directly from raw text (with header)")
                    else:
                        # No rows found in section, use as-is
                        if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
                            final_data["rubrics"] = "Grading Rubric:\n" + rubric_section
                            logger.info(f"✅ Using rubric section directly from raw text")
                else:
                    logger.warning(f"⚠️ No rubric found in response_text (searched {len(response_text) if response_text else 0} chars)")
                    # Create default rubric if none found
                    default_rubric = _build_rubric_table([])  # Empty list triggers default creation
                    if default_rubric:
                        final_data["rubrics"] = default_rubric
                        logger.info(f"✅ Created default rubric (no rubric found in response)")
            
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
                            if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
                                final_data["rubrics"] = rubric_table
                                logger.info(f"✅ Found rubric in field '{field_name}': {len(valid_rows)} rows")
                                break
    
    # If still no rubric found, create default
    if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
        logger.info(f"🔍 No rubric found after all extraction attempts, creating default rubric...")
        default_rubric = _build_rubric_table([])  # Empty list triggers default creation
        if default_rubric:
            final_data["rubrics"] = default_rubric
            logger.info(f"✅ Created default rubric (no rubric found in any source): {len(default_rubric)} chars")
        else:
            logger.error(f"❌ Failed to create default rubric - _build_rubric_table returned empty")


def _separate_rubric_from_worksheets(final_data: Dict[str, Any]) -> None:
    """Check if rubric is embedded in worksheets field and separate them. More aggressive cleaning."""
    worksheets_field = final_data.get("worksheets", "")
    if not worksheets_field or not isinstance(worksheets_field, str) or len(worksheets_field) < 50:
        return
    
    # More aggressive patterns to find rubric markers
    rubric_marker_patterns = [
        r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*',
        r'###\s*Grading\s+Rubrics?',
        r'📋\s*Grading\s+Rubric',
        r'Grading\s+Rubric[:\s]*',
    ]
    rubric_table_pattern = r'\|[^\|]*\s*(?:criteria|technique|ability|mechanics|accuracy|understanding)[^\|]*\|\s*(?:excellent|proficient|developing|beginning|4\s*pts?|3\s*pts?|2\s*pts?|1\s*pt)[^\|]*\|'
    
    rubric_start = None
    rubric_marker_match = None
    
    # Try each rubric marker pattern
    for pattern in rubric_marker_patterns:
        rubric_marker_match = re.search(pattern, worksheets_field, re.IGNORECASE)
        if rubric_marker_match:
            rubric_start = rubric_marker_match.start()
            logger.info(f"🔍 Found rubric marker in worksheets field at position {rubric_start} (pattern: {pattern[:30]}...)")
            break
    
    # If no marker found, try to find rubric table
    if rubric_start is None:
        rubric_table_match = re.search(rubric_table_pattern, worksheets_field, re.IGNORECASE)
        if rubric_table_match:
            rubric_start = rubric_table_match.start()
            # Look backwards for a header
            before_table = worksheets_field[max(0, rubric_start-150):rubric_start]
            for pattern in rubric_marker_patterns:
                header_match = re.search(pattern + r'\s*$', before_table, re.IGNORECASE | re.MULTILINE)
                if header_match:
                    rubric_start = rubric_start - 150 + header_match.start()
                    break
            logger.info(f"🔍 Found rubric table in worksheets field at position {rubric_start}")
    
    if rubric_start is not None:
        # Extract everything from rubric_start to end (or next section)
        rubric_content_from_worksheets = worksheets_field[rubric_start:].strip()
        
        # Try to find where rubric ends (next section or end of text)
        rubric_end_match = re.search(r'\n(?:###|assessments?|worksheets?|answer\s+key|$)', rubric_content_from_worksheets, re.IGNORECASE | re.MULTILINE)
        if rubric_end_match:
            rubric_content_from_worksheets = rubric_content_from_worksheets[:rubric_end_match.start()].strip()
        else:
            # Limit to reasonable size
            rubric_content_from_worksheets = rubric_content_from_worksheets[:3000].strip()
        
        # Check if it's actually a rubric (has table structure and rubric keywords)
        is_rubric = False
        if '|' in rubric_content_from_worksheets:
            has_criteria = re.search(r'(criteria|technique|ability|mechanics|accuracy|understanding|teamwork|communication|safety|effort|performance|skill)', rubric_content_from_worksheets, re.IGNORECASE)
            has_levels = re.search(r'(excellent|proficient|developing|beginning|4\s*pts?|3\s*pts?|2\s*pts?|1\s*pt|perfect|good|inconsistent|struggles|demonstrates|shows)', rubric_content_from_worksheets, re.IGNORECASE)
            if has_criteria and has_levels:
                is_rubric = True
        
        if is_rubric:
            logger.info(f"✅ Found rubric embedded in worksheets field. Extracting separately. Length: {len(rubric_content_from_worksheets)} chars")
            # Only set rubrics if it's empty (don't overwrite existing)
            if not final_data.get("rubrics") or not final_data.get("rubrics", "").strip():
                final_data["rubrics"] = rubric_content_from_worksheets
            
            # Remove rubric from worksheets (everything from rubric_start onwards)
            worksheets_cleaned = worksheets_field[:rubric_start].strip()
            worksheets_cleaned = _remove_rubric_markers(worksheets_cleaned)
            worksheets_cleaned = re.sub(r'^with\s+answer\s+keys?\s*$', '', worksheets_cleaned, flags=re.IGNORECASE | re.MULTILINE).strip()
            final_data["worksheets"] = worksheets_cleaned
            logger.info(f"✅ Cleaned worksheets field, removed rubric. New length: {len(worksheets_cleaned)} chars (was {len(worksheets_field)} chars)")
        else:
            # Even if not a full rubric, remove rubric markers to prevent them from appearing
            worksheets_cleaned = _remove_rubric_markers(worksheets_field)
            if len(worksheets_cleaned) < len(worksheets_field):
                final_data["worksheets"] = worksheets_cleaned
                logger.info(f"✅ Removed rubric markers from worksheets field. New length: {len(worksheets_cleaned)} chars")
    
    # Final cleanup: remove any remaining rubric markers
    worksheets_final = final_data.get("worksheets", "")
    if worksheets_final:
        cleaned = _remove_rubric_markers(worksheets_final)
        # Remove any table-like content that might be rubric remnants
        if '|' in cleaned and re.search(r'criteria|excellent|proficient', cleaned, re.IGNORECASE):
            # Check if there's a table that looks like a rubric
            lines = cleaned.split('\n')
            cleaned_lines = []
            in_rubric_table = False
            for line in lines:
                if re.search(r'(?:###\s*)?(?:grading\s+)?rubrics?|criteria.*excellent', line, re.IGNORECASE):
                    in_rubric_table = True
                    continue
                if in_rubric_table and line.strip().startswith('|') and 'criteria' in line.lower():
                    in_rubric_table = True
                    continue
                if in_rubric_table and line.strip().startswith('|'):
                    continue  # Skip rubric table rows
                if in_rubric_table and not line.strip().startswith('|'):
                    in_rubric_table = False
                if not in_rubric_table:
                    cleaned_lines.append(line)
            cleaned = '\n'.join(cleaned_lines)
        
        if len(cleaned) < len(worksheets_final):
            final_data["worksheets"] = cleaned.strip()
            logger.info(f"✅ Final cleanup: removed rubric content from worksheets. New length: {len(cleaned)} chars")


def extract_lesson_plan_data(response_text: str, original_message: str = "") -> Dict[str, Any]:
    """
    Extract structured lesson plan data from AI response text.
    Returns a dict with lesson plan information if found.
    Comprehensive extraction handling multiple formats and edge cases.
    
    Args:
        response_text: The AI's response text
        original_message: The original user message (used for title extraction)
        
    Returns:
        Dictionary with structured lesson plan data
    """
    logger.info(f"🔍 extract_lesson_plan_data called: response_text length={len(response_text) if response_text else 0}, original_message={original_message[:50] if original_message else ''}...")
    if not response_text:
        logger.warning("⚠️ extract_lesson_plan_data: Empty response_text")
        return {}
    
    # Step 1: Try to extract JSON from markdown code blocks
    parsed_json_data = _parse_json_from_response(response_text)
    logger.info(f"🔍 JSON parsing result: {type(parsed_json_data).__name__}, has_data={bool(parsed_json_data)}")
    if parsed_json_data:
        logger.info(f"🔍 JSON keys: {list(parsed_json_data.keys())[:10] if isinstance(parsed_json_data, dict) else 'N/A'}")
    
    lesson_data = {
        "title": "",
        "description": "",
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
        
        if not line:
            if skip_next_empty:
                current_section = None
            skip_next_empty = True
            continue
        skip_next_empty = False
        
        numbered_section_match = None
        if current_section and len(line) < 100 and re.match(r'^\d+\.\s+[a-z]', line):
            pass
        else:
            numbered_section_match = re.match(r'^(\d+)\.\s*\*\*([^*]+)\*\*\s*[-:]?\s*(.*)', line)
        if numbered_section_match:
            section_num = numbered_section_match.group(1)
            section_header = numbered_section_match.group(2).strip()
            section_content = numbered_section_match.group(3).strip()
            section_header_lower = section_header.lower()
            
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
        
        if "title:" in line_lower and i < 5:
            title_match = re.search(r'title[:\s]+(.+)', line, flags=re.IGNORECASE)
            if title_match:
                lesson_data["title"] = re.sub(r'\*\*', '', title_match.group(1)).strip()
            continue
        
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
        
        elif re.match(r'^(introduction|intro)(\s+to\s+[^:]+)?\s*\(?\d+\s*minutes?\)?\s*[:\-]?', line_lower) or \
             (re.search(r'^(introduction|intro)(\s+to\s+[^:]+)?[:\-]', line_lower) and i < 20):
            current_section = "introduction"
            intro_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            intro_text = re.sub(r'\*\*?', '', intro_text)
            intro_text = re.sub(r'(introduction|intro)(\s+to\s+[^-]+)?\s*\(?\d+\s*minutes?\)?\s*[:\-]?\s*', '', intro_text, flags=re.IGNORECASE)
            intro_text = re.sub(r'(introduction|intro)[:\s]+', '', intro_text, flags=re.IGNORECASE).strip()
            if intro_text and len(intro_text) > 10:
                lesson_data["introduction"] = intro_text
        
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
        
        elif re.search(r'step\s+\d+[:\-]', line_lower):
            current_section = "activities"
            step_text = re.sub(r'^[-•*]\s*', '', line, flags=re.IGNORECASE)
            step_text = re.sub(r'\*\*?step\s+\d+[:\-]\s*\*\*?', '', step_text, flags=re.IGNORECASE)
            step_text = re.sub(r'step\s+\d+[:\-]\s*', '', step_text, flags=re.IGNORECASE)
            step_text = re.sub(r'\*\*?', '', step_text).strip()
            if step_text and len(step_text) > 10:
                lesson_data["activities"].append(step_text)
            continue
        
        elif re.match(r'^\d+\.', line) and current_section is None:
            if re.search(r'(minutes?|hours?|discussion|demonstration|simulation|exercise|review|practice|assignment|assessment)', line_lower):
                current_section = "activities"
        elif re.match(r'^\d+\.', line) and current_section in ["danielson_framework", "costas_questioning", "curriculum_standards", "description"]:
            continue
        
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
        
        elif re.search(r'(assessment|evaluation|homework|assignment)', line_lower):
            current_section = "assessment"
            assessment_text = re.sub(r'^\d+\.?\s*\*\*?', '', line, flags=re.IGNORECASE)
            assessment_text = re.sub(r'\*\*?', '', assessment_text)
            assessment_text = re.sub(r'(assessment|evaluation|homework|assignment)[:\s]+', '', assessment_text, flags=re.IGNORECASE).strip()
            if assessment_text and len(assessment_text) > 10:
                lesson_data["assessment"] = assessment_text
            continue
        
        elif "grade" in line_lower and ("level" in line_lower or "class" in line_lower or "suitable" in line_lower):
            grade_match = re.search(r'grade[s]?\s+(?:level[s]?[:\s]+)?([\w-]+)', line_lower)
            if grade_match:
                lesson_data["grade_level"] = grade_match.group(1).upper()
            continue
        
        elif "subject" in line_lower:
            subject_match = re.search(r'subject[:\s]+(.+)', line_lower)
            if subject_match:
                lesson_data["subject"] = subject_match.group(1).strip()
            continue
        
        elif "duration" in line_lower:
            duration_match = re.search(r'duration[:\s]+(.+)', line_lower)
            if duration_match:
                lesson_data["duration"] = duration_match.group(1).strip()
            continue
        
        elif re.match(r'^\d*\.?\s*(body|content|main)', line_lower):
            current_section = None
            continue
        
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
                line_lower = clean_line.lower()
                
                if re.search(r'(?:^###\s*)?(?:worksheets?|student\s+worksheet|worksheet\s+with\s+answer)', line_lower):
                    current_section = "worksheets"
                    worksheet_text = re.sub(r'^\d+\.?\s*\*\*?', '', clean_line, flags=re.IGNORECASE)
                    worksheet_text = re.sub(r'\*\*?', '', worksheet_text)
                    worksheet_text = re.sub(r'(?:###\s*)?(?:worksheets?|student\s+worksheet|worksheet\s+with\s+answer\s+keys?)[:\s]*', '', worksheet_text, flags=re.IGNORECASE).strip()
                    if worksheet_text and len(worksheet_text) > 5:
                        if lesson_data["worksheets"]:
                            lesson_data["worksheets"] += "\n\n" + worksheet_text
                        else:
                            lesson_data["worksheets"] = worksheet_text
                    if lesson_data["costas_questioning"]:
                        lesson_data["costas_questioning"] += " " + clean_line
                    else:
                        lesson_data["costas_questioning"] = clean_line
                elif re.search(r'(?:^###\s*)?(?:grading\s+rubric|rubric|assessment\s+rubric|scoring\s+rubric)', line_lower):
                    current_section = "rubrics"
                    rubric_text = re.sub(r'^\d+\.?\s*\*\*?', '', clean_line, flags=re.IGNORECASE)
                    rubric_text = re.sub(r'\*\*?', '', rubric_text)
                    rubric_text = re.sub(r'(?:###\s*)?(?:grading\s+rubric|rubric|assessment\s+rubric|scoring\s+rubric)[:\s]*', '', rubric_text, flags=re.IGNORECASE).strip()
                    if rubric_text and len(rubric_text) > 5:
                        if lesson_data["rubrics"]:
                            lesson_data["rubrics"] += "\n\n" + rubric_text
                        else:
                            lesson_data["rubrics"] = rubric_text
                    if lesson_data["costas_questioning"]:
                        lesson_data["costas_questioning"] += " " + clean_line
                    else:
                        lesson_data["costas_questioning"] = clean_line
                elif re.search(r'answer\s+key[:\s]*', line_lower) and not lesson_data.get("worksheets"):
                    current_section = "worksheets"
                    answer_key_text = re.sub(r'answer\s+key[:\s]*', '', clean_line, flags=re.IGNORECASE).strip()
                    if answer_key_text and len(answer_key_text) > 5:
                        lesson_data["worksheets"] = "Answer Key:\n" + answer_key_text
                    if lesson_data["costas_questioning"]:
                        lesson_data["costas_questioning"] += " " + clean_line
                    else:
                        lesson_data["costas_questioning"] = clean_line
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
                            if re.match(r'^[A-Z]\)\s+', clean_line) or re.match(r'^\d+[\.\)]\s+[A-Z]', clean_line):
                                if not lesson_data.get("worksheets"):
                                    lesson_data["worksheets"] = clean_line
                                else:
                                    lesson_data["worksheets"] += "\n" + clean_line
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
    
    # Step 2: Extract title from original message or response text
    if not lesson_data["title"]:
        lesson_data["title"] = _extract_title_from_sources(original_message, lines)
    
    lesson_data["objectives"] = [
        re.sub(r'^objective[:\s]+', '', obj, flags=re.IGNORECASE).strip()
        for obj in lesson_data["objectives"]
        if obj and len(obj) > 10
    ]
    
    has_activities = len(lesson_data["activities"]) > 0
    has_objectives = len(lesson_data["objectives"]) > 0
    has_introduction = bool(lesson_data["introduction"])
    has_title = bool(lesson_data["title"])
    
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
    
    if parsed_json_data and isinstance(parsed_json_data, dict):
        logger.info(f"🔍 Processing JSON data path - has JSON, proceeding with enhancement")
        final_data = parsed_json_data.copy()
        
        json_worksheets = final_data.get("worksheets", "")
        json_rubrics = final_data.get("rubrics", "")
        json_assessments = final_data.get("assessments", "")
        
        logger.info(f"🔍 JSON worksheets/rubrics check - worksheets: {len(json_worksheets) if json_worksheets else 0} chars, rubrics: {len(json_rubrics) if json_rubrics else 0} chars")
        logger.info(f"🔍 Regex extracted - worksheets: {len(lesson_data.get('worksheets', '')) if lesson_data.get('worksheets') else 0} chars, rubrics: {len(lesson_data.get('rubrics', '')) if lesson_data.get('rubrics') else 0} chars")
        
        if lesson_data.get("worksheets") and (not json_worksheets or (isinstance(json_worksheets, str) and not json_worksheets.strip())):
            logger.info(f"✅ Using regex-extracted worksheets ({len(lesson_data['worksheets'])} chars)")
            final_data["worksheets"] = lesson_data["worksheets"]
        # Check if JSON rubric is incomplete (truncated)
        json_rubrics_incomplete = False
        if json_rubrics and isinstance(json_rubrics, str) and json_rubrics.strip():
            # Check for signs of truncation: ends with incomplete row, has header but few/no data rows
            json_rubrics_clean = json_rubrics.strip()
            # Check if it ends with an incomplete table row (starts with | but doesn't have enough cells)
            if json_rubrics_clean.endswith('|') or re.search(r'\|\s*[A-Z][a-z]+\s*$', json_rubrics_clean):
                # Ends with incomplete row
                json_rubrics_incomplete = True
                logger.warning(f"⚠️ JSON rubric appears truncated (ends with incomplete row): {json_rubrics_clean[-50:]}")
            # Check if it has header but very few data rows (less than 3 criteria rows)
            elif '|' in json_rubrics_clean and 'criteria' in json_rubrics_clean.lower():
                # Count data rows (rows with | that aren't headers or separators)
                lines = json_rubrics_clean.split('\n')
                data_row_count = sum(1 for line in lines if '|' in line and 
                                    not re.match(r'^\|[\s\-:]+\|', line) and
                                    not line.lower().startswith('| criteria') and
                                    line.strip().startswith('|') and len(line.split('|')) >= 3)
                if data_row_count < 3:
                    json_rubrics_incomplete = True
                    logger.warning(f"⚠️ JSON rubric appears incomplete (only {data_row_count} data rows found)")
        
        if lesson_data.get("rubrics") and (not json_rubrics or (isinstance(json_rubrics, str) and not json_rubrics.strip()) or json_rubrics_incomplete):
            logger.info(f"✅ Using regex-extracted rubrics ({len(lesson_data['rubrics'])} chars) - JSON rubric was {'empty' if not json_rubrics or not json_rubrics.strip() else 'incomplete'}")
            final_data["rubrics"] = lesson_data["rubrics"]
        if lesson_data.get("assessments") and (not json_assessments or (isinstance(json_assessments, str) and not json_assessments.strip())):
            final_data["assessments"] = lesson_data["assessments"]
        
        # Step 3: Separate rubric from JSON worksheets if embedded (before enhancement)
        json_worksheets_final = final_data.get("worksheets", "")
        json_question_count = _count_questions_in_text(json_worksheets_final)
        has_good_worksheets = json_question_count >= 10 and len(json_worksheets_final.strip()) > 100
        
        if json_worksheets_final and isinstance(json_worksheets_final, str) and len(json_worksheets_final) > 50:
            rubric_marker_pattern = r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*'
            rubric_table_pattern = r'\|[^\|]*\s*(?:criteria|technique|ability|mechanics|accuracy|understanding)[^\|]*\|\s*(?:excellent|proficient|developing|beginning|4\s*pts?|3\s*pts?|2\s*pts?|1\s*pt)[^\|]*\|'
            
            rubric_marker_match = re.search(rubric_marker_pattern, json_worksheets_final, re.IGNORECASE)
            rubric_table_match = re.search(rubric_table_pattern, json_worksheets_final, re.IGNORECASE)
            
            rubric_start = None
            if rubric_marker_match:
                rubric_start = rubric_marker_match.start()
                logger.info(f"🔍 Found rubric marker in JSON worksheets field at position {rubric_start}")
            elif rubric_table_match:
                rubric_start = rubric_table_match.start()
                before_table = json_worksheets_final[max(0, rubric_start-100):rubric_start]
                header_match = re.search(r'(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*\s*$', before_table, re.IGNORECASE | re.MULTILINE)
                if header_match:
                    rubric_start = rubric_start - 100 + header_match.start()
                logger.info(f"🔍 Found rubric table in JSON worksheets field at position {rubric_start}")
            
            if rubric_start is not None and has_good_worksheets and (not final_data.get("rubrics") or not final_data.get("rubrics", "").strip()):
                rubric_content_from_json_worksheets = json_worksheets_final[rubric_start:].strip()
                
                rubric_end_match = re.search(r'\n(?:###|assessments?|$)', rubric_content_from_json_worksheets, re.IGNORECASE | re.MULTILINE)
                if rubric_end_match:
                    rubric_content_from_json_worksheets = rubric_content_from_json_worksheets[:rubric_end_match.start()].strip()
                else:
                    rubric_content_from_json_worksheets = rubric_content_from_json_worksheets[:3000].strip()
                
                is_rubric = False
                if '|' in rubric_content_from_json_worksheets:
                    has_criteria = re.search(r'(criteria|technique|ability|mechanics|accuracy|understanding|teamwork|communication|safety|effort|performance|skill)', rubric_content_from_json_worksheets, re.IGNORECASE)
                    has_levels = re.search(r'(excellent|proficient|developing|beginning|4\s*pts?|3\s*pts?|2\s*pts?|1\s*pt|perfect|good|inconsistent|struggles|demonstrates|shows)', rubric_content_from_json_worksheets, re.IGNORECASE)
                    if has_criteria and has_levels:
                        is_rubric = True
                
                if is_rubric:
                    logger.info(f"✅ Found rubric embedded in JSON worksheets field. Extracting separately. Length: {len(rubric_content_from_json_worksheets)} chars")
                    final_data["rubrics"] = rubric_content_from_json_worksheets
                    
                    worksheets_cleaned = json_worksheets_final[:rubric_start].strip()
                    worksheets_cleaned = re.sub(r'\n+\s*(?:###\s*)?(?:grading\s+)?rubrics?[:\s]*\s*$', '', worksheets_cleaned, flags=re.IGNORECASE | re.MULTILINE)
                    if _count_questions_in_text(worksheets_cleaned) >= 10:
                        final_data["worksheets"] = worksheets_cleaned
                        logger.info(f"✅ Cleaned JSON worksheets field, removed rubric. New length: {len(worksheets_cleaned)} chars, questions: {_count_questions_in_text(worksheets_cleaned)}")
                    else:
                        logger.warning(f"⚠️ Removing rubric would leave worksheets incomplete, preserving original")
                else:
                    logger.warning(f"⚠️ Found rubric marker/table in JSON worksheets but content doesn't match rubric pattern")
        
        # Step 4: Extract and enhance worksheets (ensure minimum 10 questions)
        # Combine objectives from both JSON and regex extraction to ensure we catch everything
        json_objectives = final_data.get("objectives", []) or final_data.get("learning_objectives", [])
        regex_objectives = lesson_data.get("objectives", [])
        # Combine both sources, prioritizing JSON but including regex if different
        objectives_data = list(json_objectives) if json_objectives else []
        if regex_objectives:
            # Add regex objectives that aren't already in JSON objectives
            for obj in regex_objectives:
                obj_str = str(obj) if obj else ""
                if obj_str and obj_str not in [str(o) for o in objectives_data]:
                    objectives_data.append(obj)
        
        logger.info(f"🔍 Combined objectives for extraction: {len(objectives_data)} items (JSON: {len(json_objectives) if json_objectives else 0}, Regex: {len(regex_objectives) if regex_objectives else 0})")
        _extract_and_enhance_worksheets(final_data, lesson_data, objectives_data, response_text)
        
        # Step 5: Separate rubric from worksheets if embedded
        _separate_rubric_from_worksheets(final_data)
        
        # Step 6: Extract and enhance rubrics from multiple sources (use same combined objectives_data)
        _extract_and_enhance_rubrics(final_data, lesson_data, objectives_data, response_text)
        
        for key in ["title", "description", "introduction", "exit_ticket", "homework"]:
            if lesson_data.get(key) and not final_data.get(key):
                final_data[key] = lesson_data[key]
        
        if lesson_data.get("objectives") and not final_data.get("learning_objectives") and not final_data.get("objectives"):
            final_data["learning_objectives"] = lesson_data["objectives"]
        if lesson_data.get("activities") and not final_data.get("activities"):
            final_data["activities"] = lesson_data["activities"]
        if lesson_data.get("materials") and not final_data.get("materials_list") and not final_data.get("materials"):
            final_data["materials_list"] = lesson_data["materials"]
        
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
    
    # If no JSON, still try to enhance lesson_data (extract worksheets/rubrics from objectives, etc.)
    logger.info(f"🔍 No JSON found, but enhancing lesson_data directly - has_activities={has_activities}, has_objectives={has_objectives}")
    if has_activities or has_objectives or has_introduction or has_title:
        # Still run enhancement on lesson_data to extract worksheets/rubrics from objectives
        objectives_data = lesson_data.get("objectives", [])
        logger.info(f"🔍 Running enhancement on lesson_data with {len(objectives_data)} objectives")
        
        # Preserve existing rubrics if they exist
        existing_rubrics = lesson_data.get("rubrics", "")
        
        _extract_and_enhance_worksheets(lesson_data, lesson_data, objectives_data, response_text)
        _extract_and_enhance_rubrics(lesson_data, lesson_data, objectives_data, response_text)
        
        # If we had rubrics before but lost them, restore them
        if existing_rubrics and existing_rubrics.strip() and (not lesson_data.get("rubrics") or not lesson_data.get("rubrics", "").strip()):
            lesson_data["rubrics"] = existing_rubrics
            logger.info(f"✅ Restored existing rubrics ({len(existing_rubrics)} chars)")
        
        return lesson_data
    
    return {}


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
        return extract_lesson_plan_data(response_text, original_message)
    
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

