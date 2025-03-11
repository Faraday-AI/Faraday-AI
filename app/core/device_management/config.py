"""
Configuration settings for device management and educational progression in Faraday AI.
"""

# Device-specific configurations
DEVICE_CONFIGS = {
    "laptop": {
        "offline_sync_interval": 300,  # 5 minutes
        "local_storage_limit": 500_000_000,  # 500MB for offline content
        "auto_save_interval": 60,  # 1 minute
        "keyboard_shortcuts_enabled": True,
        "default_ui_scale": 1.0
    },
    "mobile": {
        "offline_sync_interval": 600,  # 10 minutes
        "local_storage_limit": 100_000_000,  # 100MB for offline content
        "auto_save_interval": 120,  # 2 minutes
        "touch_optimization": True,
        "default_ui_scale": 1.2
    },
    "tablet": {
        "offline_sync_interval": 450,  # 7.5 minutes
        "local_storage_limit": 250_000_000,  # 250MB for offline content
        "auto_save_interval": 90,  # 1.5 minutes
        "touch_optimization": True,
        "default_ui_scale": 1.1
    }
}

# Grade-level specific configurations
GRADE_CONFIGS = {
    "elementary": {  # K-5
        "max_session_duration": 30,  # 30 minutes
        "break_reminder_interval": 15,  # 15 minutes
        "parent_oversight_required": True,
        "gamification_level": "high",
        "content_reading_level": "basic",
        "ui_theme": "elementary",
        "accessibility_features": {
            "text_to_speech": True,
            "large_buttons": True,
            "simplified_navigation": True,
            "high_contrast": False
        }
    },
    "middle": {  # 6-8
        "max_session_duration": 45,  # 45 minutes
        "break_reminder_interval": 25,  # 25 minutes
        "parent_oversight_required": False,
        "gamification_level": "medium",
        "content_reading_level": "intermediate",
        "ui_theme": "middle_school",
        "accessibility_features": {
            "text_to_speech": False,
            "large_buttons": False,
            "simplified_navigation": False,
            "high_contrast": False
        }
    },
    "high": {  # 9-12
        "max_session_duration": 60,  # 60 minutes
        "break_reminder_interval": 30,  # 30 minutes
        "parent_oversight_required": False,
        "gamification_level": "low",
        "content_reading_level": "advanced",
        "ui_theme": "high_school",
        "accessibility_features": {
            "text_to_speech": False,
            "large_buttons": False,
            "simplified_navigation": False,
            "high_contrast": False
        }
    }
}

# Learning progression thresholds
PROGRESSION_THRESHOLDS = {
    "elementary_to_middle": {
        "min_reading_level": 5.0,  # 5th grade reading level
        "min_math_level": 5.0,
        "required_milestones": [
            "basic_typing_proficiency",
            "independent_learning_readiness",
            "basic_research_skills"
        ]
    },
    "middle_to_high": {
        "min_reading_level": 8.0,  # 8th grade reading level
        "min_math_level": 8.0,
        "required_milestones": [
            "advanced_typing_proficiency",
            "research_methodology",
            "critical_thinking_basics"
        ]
    }
}

# Offline learning configurations
OFFLINE_CONFIGS = {
    "max_offline_duration": 72,  # hours
    "sync_retry_interval": 300,  # 5 minutes
    "min_storage_required": 50_000_000,  # 50MB
    "max_pending_syncs": 100,
    "conflict_resolution": "latest_wins"
}

# Parent oversight configurations
PARENT_OVERSIGHT = {
    "elementary": {
        "approval_required": True,
        "daily_summary": True,
        "real_time_alerts": True,
        "content_restrictions": "strict"
    },
    "middle": {
        "approval_required": False,
        "daily_summary": True,
        "real_time_alerts": True,
        "content_restrictions": "moderate"
    },
    "high": {
        "approval_required": False,
        "daily_summary": False,
        "real_time_alerts": False,
        "content_restrictions": "minimal"
    }
}

# AI tutoring adaptations
AI_TUTORING = {
    "elementary": {
        "interaction_style": "friendly_mentor",
        "vocabulary_level": "basic",
        "explanation_depth": "simplified",
        "use_animations": True,
        "gamification_elements": True
    },
    "middle": {
        "interaction_style": "supportive_guide",
        "vocabulary_level": "intermediate",
        "explanation_depth": "moderate",
        "use_animations": True,
        "gamification_elements": True
    },
    "high": {
        "interaction_style": "academic_advisor",
        "vocabulary_level": "advanced",
        "explanation_depth": "detailed",
        "use_animations": False,
        "gamification_elements": False
    }
} 