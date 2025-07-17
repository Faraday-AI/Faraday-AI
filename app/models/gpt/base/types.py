"""
GPT Types

This module defines all GPT-related enumerations and types.
"""

import enum

class GPTCategory(str, enum.Enum):
    """Enumeration of GPT categories."""
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"
    PARENT = "parent"
    ADDITIONAL = "additional"

class GPTType(str, enum.Enum):
    """Enumeration of GPT types within categories."""
    # Teacher GPTs
    MATH_TEACHER = "math_teacher"
    SCIENCE_TEACHER = "science_teacher"
    LANGUAGE_ARTS_TEACHER = "language_arts_teacher"
    HISTORY_TEACHER = "history_teacher"
    PHYSICAL_ED_TEACHER = "physical_ed_teacher"
    ADMIN_ASSISTANT = "admin_assistant"
    
    # Student GPTs
    MATH_TUTOR = "math_tutor"
    SCIENCE_TUTOR = "science_tutor"
    LANGUAGE_ARTS_TUTOR = "language_arts_tutor"
    HISTORY_TUTOR = "history_tutor"
    STUDY_SKILLS_COACH = "study_skills_coach"
    WRITING_ASSISTANT = "writing_assistant"
    
    # Additional Service GPTs
    LEARNING_ANALYTICS = "learning_analytics"
    CONTENT_GENERATION = "content_generation"
    ADAPTIVE_LEARNING = "adaptive_learning"
    ASSESSMENT_GRADING = "assessment_grading"
    MEMORY_CONTEXT = "memory_context"
    LMS_INTEGRATION = "lms_integration"
    COLLABORATION = "collaboration"
    RESOURCE_RECOMMENDATION = "resource_recommendation"
    MULTIMEDIA_PROCESSING = "multimedia_processing"
    TRANSLATION_LOCALIZATION = "translation_localization"
    CALENDAR_SCHEDULING = "calendar_scheduling"
    FILE_PROCESSING = "file_processing"
    COMMUNICATION = "communication"
    EMOTION_FEEDBACK = "emotion_feedback"
    
    # Parent GPTs
    PARENT_COMMUNICATION = "parent_communication"
    PROGRESS_TRACKING = "progress_tracking" 