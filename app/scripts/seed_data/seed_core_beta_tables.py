"""
Seed Core Beta Teacher System Tables

This script seeds the core tables that are created by SQLAlchemy models:
- lesson_plan_templates
- lesson_plan_activities  
- lesson_plan_categories
- assessment_templates
- assessment_criteria
- assessment_rubrics
- assessment_categories
- resource_categories
- educational_resources
- ai_assistant_configs
- ai_assistant_templates
"""

import os
import sys
import json
sys.path.append('/app')

from sqlalchemy import create_engine, text
from app.core.database import DATABASE_URL

def seed_lesson_plan_categories():
    """Seed lesson plan categories with default values."""
    print("  📚 Seeding lesson plan categories...")
    
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        categories = [
            ('00000000-0000-0000-0000-000000000001', 'Warm-up Activities', 'Activities to prepare students for physical activity', 'PE', 'K-12', 'warmup', '#ff6b6b'),
            ('00000000-0000-0000-0000-000000000002', 'Cardiovascular Fitness', 'Activities that improve heart and lung health', 'PE', 'K-12', 'heart', '#ff4757'),
            ('00000000-0000-0000-0000-000000000003', 'Strength Training', 'Activities that build muscular strength and endurance', 'PE', '6-12', 'dumbbell', '#ffa502'),
            ('00000000-0000-0000-0000-000000000004', 'Flexibility & Stretching', 'Activities that improve range of motion and flexibility', 'PE', 'K-12', 'stretch', '#2ed573'),
            ('00000000-0000-0000-0000-000000000005', 'Team Sports', 'Organized sports activities requiring teamwork', 'PE', '3-12', 'soccer', '#1e90ff'),
            ('00000000-0000-0000-0000-000000000006', 'Individual Sports', 'Sports activities that can be done individually', 'PE', 'K-12', 'running', '#ff6348'),
            ('00000000-0000-0000-0000-000000000007', 'Cooldown Activities', 'Activities to gradually reduce heart rate and cool down', 'PE', 'K-12', 'cooldown', '#70a1ff'),
            ('00000000-0000-0000-0000-000000000008', 'Assessment Activities', 'Activities designed to evaluate student performance', 'PE', 'K-12', 'assessment', '#ff9ff3'),
            ('00000000-0000-0000-0000-000000000009', 'Health Education', 'Activities focused on health knowledge and wellness', 'Health', 'K-12', 'health', '#26de81'),
            ('00000000-0000-0000-0000-000000000010', 'Safety Education', 'Activities teaching safety awareness and practices', 'Health', 'K-12', 'safety', '#ff3838'),
            ('00000000-0000-0000-0000-000000000011', 'Nutrition Education', 'Activities about healthy eating and nutrition', 'Health', 'K-12', 'nutrition', '#ff9f43'),
            ('00000000-0000-0000-0000-000000000012', 'Mental & Emotional Health', 'Activities promoting mental well-being and emotional regulation', 'Health', '6-12', 'mind', '#a29bfe'),
            ('00000000-0000-0000-0000-000000000013', 'Substance Abuse Prevention', 'Education on the risks and prevention of substance abuse', 'Health', '6-12', 'no-drugs', '#eb4d4b'),
            ('00000000-0000-0000-0000-000000000014', 'Human Anatomy & Physiology', 'Study of the human body systems and functions', 'Health', '9-12', 'anatomy', '#686de0'),
            ('00000000-0000-0000-0000-000000000015', 'First Aid & CPR', 'Training in emergency first aid and cardiopulmonary resuscitation', 'Health', '9-12', 'first-aid', '#badc58'),
            ('00000000-0000-0000-0000-000000000016', 'Drivers Education', 'Curriculum related to safe driving practices and road rules', 'Drivers Ed', '9-12', 'car', '#fdcb6e')
        ]
        
        for category in categories:
            conn.execute(text("""
                INSERT INTO lesson_plan_categories (
                    id, name, description, subject, grade_level_range, icon_name, color_code
                ) VALUES (
                    :id, :name, :description, :subject, :grade_level_range, :icon_name, :color_code
                ) ON CONFLICT (id) DO NOTHING
            """), {
                'id': category[0],
                'name': category[1],
                'description': category[2],
                'subject': category[3],
                'grade_level_range': category[4],
                'icon_name': category[5],
                'color_code': category[6]
            })
        conn.commit()
        print(f"    ✅ Seeded {len(categories)} lesson plan categories")

def seed_assessment_categories():
    """Seed assessment categories with default values."""
    print("  📊 Seeding assessment categories...")
    
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        categories = [
            ('00000000-0000-0000-0000-000000000001', 'Physical Skills', 'Assessment of physical abilities and motor skills', 'PE', 'K-12', 'fitness', '#ff6b6b'),
            ('00000000-0000-0000-0000-000000000002', 'Knowledge & Understanding', 'Assessment of theoretical knowledge and concepts', 'General', 'K-12', 'brain', '#2ed573'),
            ('00000000-0000-0000-0000-000000000003', 'Participation & Effort', 'Assessment of student engagement and effort', 'PE', 'K-12', 'participation', '#1e90ff'),
            ('00000000-0000-0000-0000-000000000004', 'Safety & Rules', 'Assessment of safety awareness and rule following', 'PE', 'K-12', 'safety', '#ffa502'),
            ('00000000-0000-0000-0000-000000000005', 'Teamwork & Cooperation', 'Assessment of collaborative skills and sportsmanship', 'PE', '3-12', 'teamwork', '#ff6348'),
            ('00000000-0000-0000-0000-000000000006', 'Health Knowledge', 'Assessment of health-related knowledge and concepts', 'Health', 'K-12', 'health', '#a29bfe'),
            ('00000000-0000-0000-0000-000000000007', 'Written Assessment', 'Traditional written tests and quizzes', 'General', '6-12', 'test', '#badc58'),
            ('00000000-0000-0000-0000-000000000008', 'Practical Assessment', 'Hands-on demonstrations and practical tests', 'PE', 'K-12', 'practical', '#ff9ff3'),
            ('00000000-0000-0000-0000-000000000009', 'Portfolio Assessment', 'Collection of student work and progress over time', 'General', 'K-12', 'portfolio', '#26de81'),
            ('00000000-0000-0000-0000-000000000010', 'Self-Assessment', 'Student self-evaluation and reflection', 'General', '6-12', 'self', '#ff3838')
        ]
        
        for category in categories:
            conn.execute(text("""
                INSERT INTO assessment_categories (
                    id, name, description, subject, grade_level_range, icon_name, color_code
                ) VALUES (
                    :id, :name, :description, :subject, :grade_level_range, :icon_name, :color_code
                ) ON CONFLICT (id) DO NOTHING
            """), {
                'id': category[0],
                'name': category[1],
                'description': category[2],
                'subject': category[3],
                'grade_level_range': category[4],
                'icon_name': category[5],
                'color_code': category[6]
            })
        conn.commit()
        print(f"    ✅ Seeded {len(categories)} assessment categories")

def seed_resource_categories():
    """Seed resource categories with default values."""
    print("  📁 Seeding resource categories...")
    
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        categories = [
            ('00000000-0000-0000-0000-000000000001', 'Lesson Plans', 'Complete lesson plans and instructional materials', 'PE', 'K-12', 'lesson', '#ff6b6b'),
            ('00000000-0000-0000-0000-000000000002', 'Worksheets', 'Printable exercises and activity sheets', 'General', 'K-12', 'worksheet', '#2ed573'),
            ('00000000-0000-0000-0000-000000000003', 'Videos', 'Educational video content', 'General', 'K-12', 'video', '#1e90ff'),
            ('00000000-0000-0000-0000-000000000004', 'Games', 'Interactive educational games', 'PE', 'K-8', 'game', '#ffa502'),
            ('00000000-0000-0000-0000-000000000005', 'Assessments', 'Evaluation tools and rubrics', 'General', 'K-12', 'assessment', '#ff6348'),
            ('00000000-0000-0000-0000-000000000006', 'Presentations', 'Slides and visual aids for teaching', 'General', '6-12', 'presentation', '#a29bfe'),
            ('00000000-0000-0000-0000-000000000007', 'Infographics', 'Visual summaries of information', 'General', '6-12', 'infographic', '#badc58'),
            ('00000000-0000-0000-0000-000000000008', 'Activity Ideas', 'Quick and easy activity suggestions', 'PE', 'K-12', 'idea', '#ff9ff3'),
            ('00000000-0000-0000-0000-000000000009', 'Curriculum Guides', 'Comprehensive guides for curriculum planning', 'General', 'K-12', 'guide', '#26de81'),
            ('00000000-0000-0000-0000-000000000010', 'Safety Protocols', 'Guidelines and procedures for safety', 'Health', 'K-12', 'safety', '#ff3838'),
            ('00000000-0000-0000-0000-000000000011', 'Health Education Materials', 'Resources specific to health topics', 'Health', 'K-12', 'health', '#ff9f43'),
            ('00000000-0000-0000-0000-000000000012', 'Drivers Ed Materials', 'Resources specific to drivers education', 'Drivers Ed', '9-12', 'car', '#fdcb6e'),
            ('00000000-0000-0000-0000-000000000013', 'Fitness Routines', 'Structured exercise routines', 'PE', '6-12', 'fitness', '#70a1ff'),
            ('00000000-0000-0000-0000-000000000014', 'Mindfulness Exercises', 'Activities for mental well-being', 'Health', 'K-12', 'mindfulness', '#5f27cd'),
            ('00000000-0000-0000-0000-000000000015', 'Equipment Guides', 'Guides for using and maintaining PE equipment', 'PE', 'K-12', 'equipment', '#c8d6e5'),
            ('00000000-0000-0000-0000-000000000016', 'Other', 'Miscellaneous educational resources', 'General', 'K-12', 'other', '#8395a7')
        ]
        
        for category in categories:
            conn.execute(text("""
                INSERT INTO resource_categories (
                    id, name, description, subject, grade_level_range, icon_name, color_code
                ) VALUES (
                    :id, :name, :description, :subject, :grade_level_range, :icon_name, :color_code
                ) ON CONFLICT (id) DO NOTHING
            """), {
                'id': category[0],
                'name': category[1],
                'description': category[2],
                'subject': category[3],
                'grade_level_range': category[4],
                'icon_name': category[5],
                'color_code': category[6]
            })
        conn.commit()
        print(f"    ✅ Seeded {len(categories)} resource categories")

def seed_ai_assistant_templates():
    """Seed AI assistant templates with default values."""
    print("  🤖 Seeding AI assistant templates...")
    
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        templates = [
            ('00000000-0000-0000-0000-000000000001', 'Lesson Plan Generator', 'Generate comprehensive lesson plans for PE classes', 'lesson_planning', 
             'Create a detailed lesson plan for {subject} at {grade_level} level. Include:\n- Learning objectives\n- Materials needed\n- Warm-up activities\n- Main activities\n- Cool-down\n- Assessment methods\n- Safety considerations\n\nDuration: {duration_minutes} minutes\nFocus: {focus_area}', 
             '{"subject": "string", "grade_level": "string", "duration_minutes": "integer", "focus_area": "string"}', True, True, 0),
            ('00000000-0000-0000-0000-000000000002', 'Assessment Creator', 'Generate assessments and rubrics for PE activities', 'assessment_creation',
             'Create an assessment for {activity_name} at {grade_level} level. Include:\n- Assessment objectives\n- Performance criteria\n- Scoring rubric\n- Assessment methods\n- Safety considerations\n\nDuration: {duration_minutes} minutes\nFocus: {skill_focus}',
             '{"activity_name": "string", "grade_level": "string", "duration_minutes": "integer", "skill_focus": "string"}', True, True, 0),
            ('00000000-0000-0000-0000-000000000003', 'Resource Generator', 'Generate educational resources and materials', 'resource_generation',
             'Create educational resources for {topic} at {grade_level} level. Include:\n- Resource description\n- Learning objectives\n- Materials needed\n- Instructions\n- Safety considerations\n- Assessment suggestions\n\nFormat: {resource_format}\nDuration: {duration_minutes} minutes',
             '{"topic": "string", "grade_level": "string", "resource_format": "string", "duration_minutes": "integer"}', True, True, 0),
            ('00000000-0000-0000-0000-000000000004', 'Content Analyzer', 'Analyze and provide feedback on educational content', 'content_analysis',
             'Analyze the following educational content and provide feedback:\n- Content quality\n- Age appropriateness\n- Learning objectives alignment\n- Safety considerations\n- Improvement suggestions\n\nContent: {content_to_analyze}\nGrade Level: {grade_level}\nSubject: {subject}',
             '{"content_to_analyze": "string", "grade_level": "string", "subject": "string"}', True, True, 0),
            ('00000000-0000-0000-0000-000000000005', 'General Assistant', 'General purpose AI assistant for teachers', 'general_assistant',
             'I am your AI teaching assistant. I can help you with:\n- Lesson planning\n- Assessment creation\n- Resource generation\n- Content analysis\n- Teaching strategies\n- Curriculum development\n\nHow can I assist you today?', 
             '{}', True, True, 0)
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
                'usage_count': template[8]
            })
        conn.commit()
        print(f"    ✅ Seeded {len(templates)} AI assistant templates")

def seed_lesson_plan_templates():
    """Seed lesson plan templates with sample data."""
    print("  📚 Seeding lesson plan templates...")
    
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check if already seeded
        result = conn.execute(text("SELECT COUNT(*) FROM lesson_plan_templates"))
        if result.scalar() > 0:
            print("    ✅ lesson_plan_templates already has data, skipping...")
            return
        
        # Get a teacher_id to use for the templates
        teacher_result = conn.execute(text("SELECT id FROM teacher_registrations LIMIT 1"))
        teacher_row = teacher_result.fetchone()
        if not teacher_row:
            print("    ⚠️  No teachers found, skipping lesson plan templates")
            return
        
        teacher_id = teacher_row[0]
        
        # Insert sample lesson plan templates
        templates_data = [
            {
                'teacher_id': teacher_id,
                'title': 'Elementary PE Warm-up',
                'template_type': 'warm_up',
                'subject': 'Physical Education',
                'grade_level': 'K-5',
                'duration_minutes': 15,
                'difficulty_level': 'beginner',
                'description': 'A fun warm-up routine for elementary students',
                'learning_objectives': ['Get students moving and ready for PE class', 'Improve coordination and balance'],
                'materials_needed': ['Cones', 'Music player'],
                'safety_considerations': ['Ensure adequate space between students', 'Check for obstacles'],
                'assessment_methods': ['Observation', 'Participation checklist'],
                'is_public': True,
                'ai_generated': True
            },
            {
                'teacher_id': teacher_id,
                'title': 'Middle School Basketball Skills',
                'template_type': 'skill_development',
                'subject': 'Physical Education',
                'grade_level': '6-8',
                'duration_minutes': 45,
                'difficulty_level': 'intermediate',
                'description': 'Basketball fundamentals for middle school',
                'learning_objectives': ['Develop dribbling skills', 'Improve shooting technique', 'Practice passing accuracy'],
                'materials_needed': ['Basketballs', 'Hoop', 'Cones'],
                'safety_considerations': ['Check equipment condition before use', 'Ensure proper spacing'],
                'assessment_methods': ['Skill demonstration', 'Peer evaluation'],
                'is_public': True,
                'ai_generated': True
            },
            {
                'teacher_id': teacher_id,
                'title': 'High School Fitness Assessment',
                'template_type': 'assessment',
                'subject': 'Physical Education',
                'grade_level': '9-12',
                'duration_minutes': 60,
                'difficulty_level': 'advanced',
                'description': 'Comprehensive fitness assessment for high school',
                'learning_objectives': ['Evaluate cardiovascular fitness', 'Assess strength levels', 'Measure flexibility'],
                'materials_needed': ['Stopwatch', 'Measuring tape', 'Mats'],
                'safety_considerations': ['Ensure proper form', 'Adequate rest periods', 'Medical clearance if needed'],
                'assessment_methods': ['Standardized tests', 'Performance tracking', 'Self-assessment'],
                'is_public': True,
                'ai_generated': True
            }
        ]
        
        for template in templates_data:
            conn.execute(text("""
                INSERT INTO lesson_plan_templates (
                    id, teacher_id, title, template_type, subject, grade_level, duration_minutes,
                    difficulty_level, description, learning_objectives, materials_needed, 
                    safety_considerations, assessment_methods, is_public, ai_generated,
                    created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :teacher_id, :title, :template_type, :subject, :grade_level, :duration_minutes,
                    :difficulty_level, :description, :learning_objectives, :materials_needed,
                    :safety_considerations, :assessment_methods, :is_public, :ai_generated,
                    NOW(), NOW()
                )
            """), template)
        
        conn.commit()
        print(f"    ✅ Created {len(templates_data)} lesson plan templates")

def seed_assessment_templates():
    """Seed assessment templates with sample data."""
    print("  📊 Seeding assessment templates...")
    
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check if already seeded
        result = conn.execute(text("SELECT COUNT(*) FROM assessment_templates"))
        if result.scalar() > 0:
            print("    ✅ assessment_templates already has data, skipping...")
            return
        
        # Get a teacher_id to use for the templates
        teacher_result = conn.execute(text("SELECT id FROM teacher_registrations LIMIT 1"))
        teacher_row = teacher_result.fetchone()
        if not teacher_row:
            print("    ⚠️  No teachers found, skipping assessment templates")
            return
        
        teacher_id = teacher_row[0]
        
        # Insert sample assessment templates
        templates_data = [
            {
                'teacher_id': teacher_id,
                'title': 'PE Skills Rubric',
                'assessment_type': 'rubric',
                'subject': 'Physical Education',
                'grade_level': 'K-12',
                'description': 'Comprehensive rubric for PE skill assessment',
                'instructions': 'Rate each skill on a scale of 1-4 based on performance criteria',
                'duration_minutes': 30,
                'total_points': 100,
                'materials_needed': ['Rubric sheet', 'Pencil'],
                'safety_considerations': ['Ensure safe environment', 'Monitor student safety'],
                'ai_generated': True,
                'difficulty_level': 'intermediate'
            },
            {
                'teacher_id': teacher_id,
                'title': 'Fitness Test Checklist',
                'assessment_type': 'checklist',
                'subject': 'Physical Education',
                'grade_level': '6-12',
                'description': 'Checklist for fitness test administration',
                'instructions': 'Mark each item as completed during testing and record scores',
                'duration_minutes': 45,
                'total_points': 50,
                'materials_needed': ['Stopwatch', 'Measuring tape', 'Checklist form'],
                'safety_considerations': ['Proper warm-up required', 'Monitor for fatigue'],
                'ai_generated': True,
                'difficulty_level': 'beginner'
            }
        ]
        
        for template in templates_data:
            conn.execute(text("""
                INSERT INTO assessment_templates (
                    id, teacher_id, title, assessment_type, subject, grade_level, description,
                    instructions, duration_minutes, total_points, materials_needed,
                    safety_considerations, ai_generated, difficulty_level, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :teacher_id, :title, :assessment_type, :subject, :grade_level, :description,
                    :instructions, :duration_minutes, :total_points, :materials_needed,
                    :safety_considerations, :ai_generated, :difficulty_level, NOW(), NOW()
                )
            """), template)
        
        conn.commit()
        print(f"    ✅ Created {len(templates_data)} assessment templates")

def seed_educational_resources():
    """Seed educational resources with sample data."""
    print("  📁 Seeding educational resources...")
    
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check if already seeded
        result = conn.execute(text("SELECT COUNT(*) FROM educational_resources"))
        if result.scalar() > 0:
            print("    ✅ educational_resources already has data, skipping...")
            return
        
        # Get a teacher_id to use for the resources
        teacher_result = conn.execute(text("SELECT id FROM teacher_registrations LIMIT 1"))
        teacher_row = teacher_result.fetchone()
        if not teacher_row:
            print("    ⚠️  No teachers found, skipping educational resources")
            return
        
        teacher_id = teacher_row[0]
        
        # Insert sample educational resources
        resources_data = [
            {
                'teacher_id': teacher_id,
                'title': 'PE Activity Cards',
                'resource_type': 'activity_cards',
                'description': 'Printable cards with PE activities for different age groups',
                'file_path': '/resources/pe-activity-cards.pdf',
                'file_name': 'pe-activity-cards.pdf',
                'file_size_bytes': 2048000,
                'mime_type': 'application/pdf',
                'subject': 'Physical Education',
                'grade_level': 'K-5',
                'tags': ['activities', 'elementary', 'printable'],
                'keywords': ['PE', 'activities', 'cards'],
                'difficulty_level': 'beginner',
                'duration_minutes': 30
            },
            {
                'teacher_id': teacher_id,
                'title': 'Fitness Assessment Guide',
                'resource_type': 'assessment_guide',
                'description': 'Step-by-step guide for conducting fitness assessments',
                'file_path': '/resources/fitness-assessment-guide.pdf',
                'file_name': 'fitness-assessment-guide.pdf',
                'file_size_bytes': 1536000,
                'mime_type': 'application/pdf',
                'subject': 'Physical Education',
                'grade_level': '6-12',
                'tags': ['assessment', 'fitness', 'guide'],
                'keywords': ['fitness', 'assessment', 'testing'],
                'difficulty_level': 'intermediate',
                'duration_minutes': 60
            }
        ]
        
        for resource in resources_data:
            conn.execute(text("""
                INSERT INTO educational_resources (
                    id, teacher_id, title, resource_type, description, file_path, file_name,
                    file_size_bytes, mime_type, subject, grade_level, tags, keywords,
                    difficulty_level, duration_minutes, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :teacher_id, :title, :resource_type, :description, :file_path, :file_name,
                    :file_size_bytes, :mime_type, :subject, :grade_level, :tags, :keywords,
                    :difficulty_level, :duration_minutes, NOW(), NOW()
                )
            """), resource)
        
        conn.commit()
        print(f"    ✅ Created {len(resources_data)} educational resources")

def seed_ai_assistant_configs():
    """Seed AI assistant configurations with sample data."""
    print("  🤖 Seeding AI assistant configurations...")
    
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check if already seeded
        result = conn.execute(text("SELECT COUNT(*) FROM ai_assistant_configs"))
        if result.scalar() > 0:
            print("    ✅ ai_assistant_configs already has data, skipping...")
            return
        
        # Get a teacher_id to use for the configs
        teacher_result = conn.execute(text("SELECT id FROM teacher_registrations LIMIT 1"))
        teacher_row = teacher_result.fetchone()
        if not teacher_row:
            print("    ⚠️  No teachers found, skipping AI assistant configs")
            return
        
        teacher_id = teacher_row[0]
        
        # Insert sample AI assistant configs
        configs_data = [
            {
                'teacher_id': teacher_id,
                'config_name': 'PE Lesson Planner',
                'config_description': 'AI assistant for creating PE lesson plans',
                'assistant_type': 'lesson_planning',
                'is_active': True,
                'config_data': json.dumps({
                    'system_prompt': 'You are a helpful PE teacher assistant specializing in creating engaging lesson plans.',
                    'temperature': 0.7,
                    'max_tokens': 1000,
                    'model': 'gpt-4'
                })
            },
            {
                'teacher_id': teacher_id,
                'config_name': 'Assessment Helper',
                'config_description': 'AI assistant for creating assessments and rubrics',
                'assistant_type': 'assessment_creation',
                'is_active': True,
                'config_data': json.dumps({
                    'system_prompt': 'You are a helpful assessment assistant specializing in creating rubrics and evaluation tools.',
                    'temperature': 0.5,
                    'max_tokens': 800,
                    'model': 'gpt-4'
                })
            }
        ]
        
        for config in configs_data:
            conn.execute(text("""
                INSERT INTO ai_assistant_configs (
                    id, teacher_id, config_name, config_description, assistant_type,
                    is_active, config_data, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :teacher_id, :config_name, :config_description, :assistant_type,
                    :is_active, :config_data, NOW(), NOW()
                )
            """), config)
        
        conn.commit()
        print(f"    ✅ Created {len(configs_data)} AI assistant configurations")

def seed_beta_testing_programs():
    """Seed beta testing programs with sample data."""
    print("  🧪 Seeding beta testing programs...")
    
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check if already seeded
        result = conn.execute(text("SELECT COUNT(*) FROM beta_testing_programs"))
        if result.scalar() > 0:
            print("    ✅ beta_testing_programs already has data, skipping...")
            return
        
        # Insert sample beta testing programs
        programs_data = [
            {
                'name': 'PE AI Assistant Beta',
                'description': 'Beta testing program for the PE AI Assistant',
                'version': '1.0.0',
                'status': 'active',
                'start_date': '2024-01-01',
                'end_date': '2024-12-31',
                'max_participants': 100,
                'requirements': json.dumps({
                    'min_experience_years': 2,
                    'required_subjects': ['Physical Education'],
                    'device_requirements': ['Computer', 'Internet connection']
                })
            }
        ]
        
        for program in programs_data:
            conn.execute(text("""
                INSERT INTO beta_testing_programs (
                    id, name, description, version, status, start_date, end_date,
                    max_participants, requirements, created_at, updated_at
                ) VALUES (
                    gen_random_uuid(), :name, :description, :version, :status, :start_date, :end_date,
                    :max_participants, :requirements, NOW(), NOW()
                )
            """), program)
        
        conn.commit()
        print(f"    ✅ Created {len(programs_data)} beta testing programs")

def seed_core_beta_tables():
    """Seed all core beta teacher system tables."""
    print("🌱 Seeding core beta teacher system tables...")
    
    # Seed category/lookup tables
    seed_lesson_plan_categories()
    seed_assessment_categories()
    seed_resource_categories()
    seed_ai_assistant_templates()
    
    # Seed main data tables
    seed_lesson_plan_templates()
    seed_assessment_templates()
    seed_educational_resources()
    seed_ai_assistant_configs()
    seed_beta_testing_programs()
    
    print("✅ Core beta teacher system tables seeded successfully!")

if __name__ == "__main__":
    seed_core_beta_tables()
