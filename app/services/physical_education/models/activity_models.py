"""
Activity Models

This module contains models for physical education activities.
"""

class Activity:
    """Model for physical education activities."""
    
    def __init__(self):
        self.activity_id = None
        self.name = None
        self.description = None
        self.activity_type = None
        self.difficulty_level = None
        self.equipment_required = []
        self.duration_minutes = 0
        self.max_participants = 0
        self.category = None
        self.safety_considerations = []
        self.learning_objectives = []
        self.skill_levels = []
        self.created_at = None
        self.updated_at = None 