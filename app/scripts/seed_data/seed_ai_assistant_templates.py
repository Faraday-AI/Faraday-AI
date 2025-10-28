#!/usr/bin/env python3
"""
Seed AI Assistant Templates for Beta Teacher System
"""

import os
import sys
sys.path.append('/app')

from sqlalchemy import create_engine, text
from app.core.database import DATABASE_URL

def seed_ai_assistant_templates(session=None):
    """Seed the AI assistant templates with explicit IDs."""
    print("🤖 Seeding AI assistant templates...")
    
    if session:
        # Use the provided session
        conn = session.connection()
        use_session = True
    else:
        # Create our own connection
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        use_session = False
    
    try:
        # Insert AI assistant templates with explicit IDs
        templates = [
            ('00000000-0000-0000-0000-000000000001', 'Lesson Plan Generator', 'Generate comprehensive lesson plans for PE classes', 'lesson_planning', 
             'Create a detailed lesson plan for {subject} at {grade_level} level. Include:\n- Learning objectives\n- Materials needed\n- Warm-up activities\n- Main activities\n- Cool-down\n- Assessment methods\n- Safety considerations\n\nDuration: {duration_minutes} minutes\nFocus: {focus_area}', 
             '{"subject": "string", "grade_level": "string", "duration_minutes": "integer", "focus_area": "string"}', True, True),
            
            ('00000000-0000-0000-0000-000000000002', 'Assessment Creator', 'Generate assessments and rubrics for PE activities', 'assessment_creation',
             'Create an assessment for {activity_name} at {grade_level} level. Include:\n- Assessment objectives\n- Performance criteria\n- Scoring rubric\n- Assessment methods\n- Safety considerations\n\nDuration: {duration_minutes} minutes\nFocus: {skill_focus}', 
             '{"activity_name": "string", "grade_level": "string", "duration_minutes": "integer", "skill_focus": "string"}', True, True),
            
            ('00000000-0000-0000-0000-000000000003', 'Resource Generator', 'Generate educational resources and materials', 'resource_generation',
             'Create educational resources for {topic} at {grade_level} level. Include:\n- Resource description\n- Learning objectives\n- Materials needed\n- Instructions\n- Safety considerations\n- Assessment suggestions\n\nFormat: {resource_format}\nDuration: {duration_minutes} minutes', 
             '{"topic": "string", "grade_level": "string", "resource_format": "string", "duration_minutes": "integer"}', True, True),
            
            ('00000000-0000-0000-0000-000000000004', 'Content Analyzer', 'Analyze and provide feedback on educational content', 'content_analysis',
             'Analyze the following educational content and provide feedback:\n- Content quality\n- Age appropriateness\n- Learning objectives alignment\n- Safety considerations\n- Improvement suggestions\n\nContent: {content_to_analyze}\nGrade Level: {grade_level}\nSubject: {subject}', 
             '{"content_to_analyze": "text", "grade_level": "string", "subject": "string"}', True, True),
            
            ('00000000-0000-0000-0000-000000000005', 'General Assistant', 'General purpose AI assistant for teachers', 'general_assistant',
             'I am your AI teaching assistant. I can help you with:\n- Lesson planning\n- Assessment creation\n- Resource generation\n- Content analysis\n- Teaching strategies\n- Curriculum development\n\nHow can I assist you today?', 
             '{}', True, True)
        ]
        
        for template in templates:
            conn.execute(text("""
                INSERT INTO ai_assistant_templates (
                    id, template_name, template_description, template_type, 
                    template_content, template_variables, is_system_template, is_active, usage_count
                ) VALUES (
                    :id, :template_name, :template_description, :template_type,
                    :template_content, :template_variables, :is_system_template, :is_active, :usage_count
                ) ON CONFLICT (id) DO NOTHING
            """), {
                'id': template[0],
                'template_name': template[1],
                'template_description': template[2],
                'template_type': template[3],
                'template_content': template[4],
                'template_variables': template[5],
                'is_system_template': template[6],
                'is_active': template[7],
                'usage_count': 0  # Default usage count
            })
        
        if use_session:
            # Session will be committed by the caller
            pass
        else:
            conn.commit()
        print(f"   ✅ Seeded {len(templates)} AI assistant templates")
    
    finally:
        if not use_session:
            conn.close()

if __name__ == "__main__":
    seed_ai_assistant_templates()
