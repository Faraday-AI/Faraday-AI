from datetime import datetime, timedelta
import random
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, text

from app.models.routine import Routine, RoutineActivity
from app.models.physical_education.class_ import PhysicalEducationClass
from app.models.physical_education.exercise.models import Exercise
from app.models.physical_education.activity.models import Activity

def seed_routines(session: Session) -> Tuple[int, int]:
    """Seed routine data with comprehensive district coverage."""
    print("Seeding performance tracking system...")
    
    # Get existing classes, activities, and users
    classes = session.execute(select(PhysicalEducationClass.id, PhysicalEducationClass.name, PhysicalEducationClass.grade_level)).fetchall()
    activities = session.execute(select(Activity.id, Activity.name, Activity.type)).fetchall()
    exercises = session.execute(select(Exercise.id, Exercise.name, Exercise.exercise_type)).fetchall()
    users = session.execute(select(text("id")).select_from(text("users")).limit(50)).fetchall()
    
    if not classes or not activities:
        print("No classes or activities found, skipping routine creation")
        return 0, 0
    
    print(f"Found {len(classes)} classes and {len(activities)} activities for routine creation")
    
    # Clear existing routines first
    session.execute(RoutineActivity.__table__.delete())
    session.execute(Routine.__table__.delete())
    session.commit()
    
    routine_count = 0
    routine_activity_count = 0
    
    # Create comprehensive district-wide routines
    routine_templates = [
        # Elementary School Routines (K-5)
        {"name": "Kindergarten Movement Foundation", "description": "Basic movement skills for kindergarten students", "grade_levels": ["KINDERGARTEN"], "duration": 20, "type": "WARM_UP"},
        {"name": "Grade 1-2 Coordination Builder", "description": "Coordination and balance development", "grade_levels": ["FIRST", "SECOND"], "duration": 25, "type": "SKILL_DEVELOPMENT"},
        {"name": "Grade 3-5 Strength Introduction", "description": "Introduction to basic strength training", "grade_levels": ["THIRD", "FOURTH", "FIFTH"], "duration": 30, "type": "STRENGTH_TRAINING"},
        
        # Middle School Routines (6-8)
        {"name": "Grade 6-8 Cardio Foundation", "description": "Cardiovascular fitness building", "grade_levels": ["SIXTH", "SEVENTH", "EIGHTH"], "duration": 35, "type": "CARDIO"},
        {"name": "Middle School Team Sports", "description": "Team sports skills and coordination", "grade_levels": ["SIXTH", "SEVENTH", "EIGHTH"], "duration": 40, "type": "TEAM_SPORTS"},
        {"name": "Grade 6-8 Flexibility Program", "description": "Flexibility and mobility development", "grade_levels": ["SIXTH", "SEVENTH", "EIGHTH"], "duration": 25, "type": "FLEXIBILITY"},
        
        # High School Routines (9-12)
        {"name": "Grade 9-12 Advanced Fitness", "description": "Advanced fitness training program", "grade_levels": ["NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 45, "type": "ADVANCED_FITNESS"},
        {"name": "High School Athletic Training", "description": "Athletic performance enhancement", "grade_levels": ["NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 50, "type": "ATHLETIC_TRAINING"},
        {"name": "Grade 9-12 HIIT Program", "description": "High-intensity interval training", "grade_levels": ["NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 40, "type": "HIIT"},
        
        # Specialized Programs
        {"name": "Adaptive PE Foundation", "description": "Adaptive physical education for special needs", "grade_levels": ["KINDERGARTEN", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH"], "duration": 25, "type": "ADAPTIVE"},
        {"name": "Recreational Fitness", "description": "Recreational fitness activities", "grade_levels": ["NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 35, "type": "RECREATIONAL"},
        {"name": "Competitive Sports Prep", "description": "Preparation for competitive sports", "grade_levels": ["NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 45, "type": "COMPETITIVE"},
        
        # Seasonal Routines
        {"name": "Fall Fitness Program", "description": "Fall season fitness activities", "grade_levels": ["SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 40, "type": "SEASONAL"},
        {"name": "Winter Indoor Activities", "description": "Indoor activities for winter months", "grade_levels": ["KINDERGARTEN", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH"], "duration": 30, "type": "INDOOR"},
        {"name": "Spring Outdoor Program", "description": "Outdoor activities for spring", "grade_levels": ["KINDERGARTEN", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH"], "duration": 35, "type": "OUTDOOR"},
        
        # Skill-Specific Routines
        {"name": "Basketball Skills Development", "description": "Basketball fundamentals and skills", "grade_levels": ["FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 40, "type": "BASKETBALL"},
        {"name": "Soccer Technique Training", "description": "Soccer skills and technique", "grade_levels": ["FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 40, "type": "SOCCER"},
        {"name": "Track and Field Basics", "description": "Track and field fundamentals", "grade_levels": ["FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 35, "type": "TRACK_FIELD"},
        
        # Fitness Level Routines
        {"name": "Beginner Fitness", "description": "Basic fitness for beginners", "grade_levels": ["KINDERGARTEN", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH"], "duration": 25, "type": "BEGINNER"},
        {"name": "Intermediate Fitness", "description": "Intermediate fitness training", "grade_levels": ["FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH"], "duration": 35, "type": "INTERMEDIATE"},
        {"name": "Advanced Fitness", "description": "Advanced fitness challenges", "grade_levels": ["NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 45, "type": "ADVANCED"},
        
        # Wellness Routines
        {"name": "Mindfulness and Movement", "description": "Mindfulness combined with gentle movement", "grade_levels": ["KINDERGARTEN", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH"], "duration": 20, "type": "WELLNESS"},
        {"name": "Yoga for Teens", "description": "Yoga practice for teenage students", "grade_levels": ["NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 30, "type": "YOGA"},
        {"name": "Dance and Expression", "description": "Creative dance and movement expression", "grade_levels": ["SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 35, "type": "DANCE"},
        
        # Equipment-Based Routines
        {"name": "Equipment-Free Fitness", "description": "Fitness using body weight only", "grade_levels": ["KINDERGARTEN", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH"], "duration": 30, "type": "BODYWEIGHT"},
        {"name": "Resistance Band Training", "description": "Fitness using resistance bands", "grade_levels": ["FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 35, "type": "RESISTANCE"},
        {"name": "Medicine Ball Workout", "description": "Medicine ball strength training", "grade_levels": ["SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 30, "type": "STRENGTH_TRAINING"},
        
        # Recovery and Cool-Down
        {"name": "Active Recovery", "description": "Active recovery and cool-down", "grade_levels": ["KINDERGARTEN", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 15, "type": "COOL_DOWN"},
        {"name": "Stretching and Flexibility", "description": "Comprehensive stretching routine", "grade_levels": ["KINDERGARTEN", "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 20, "type": "FLEXIBILITY"},
        {"name": "Mobility and Movement", "description": "Mobility and movement preparation", "grade_levels": ["SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"], "duration": 25, "type": "MOBILITY"}
    ]
    
    # Debug: Show available grade levels
    available_grades = set(c[2] for c in classes)
    print(f"Available grade levels in database: {sorted(available_grades)}")
    
    # Debug: Show template grade levels
    template_grades = set()
    for template in routine_templates:
        template_grades.update(template["grade_levels"])
    print(f"Template grade levels: {sorted(template_grades)}")
    
    # Check for mismatches
    missing_grades = template_grades - available_grades
    if missing_grades:
        print(f"⚠️  Warning: Template references grades not in database: {sorted(missing_grades)}")
    
    print(f"Starting routine creation with {len(routine_templates)} templates...")
    
    # Create routines for each template with variations
    for template_idx, template in enumerate(routine_templates):
        print(f"  Processing template {template_idx + 1}/{len(routine_templates)}: {template['name']}")
        for grade_level in template["grade_levels"]:
            # Get valid class IDs for this grade level
            # Convert enum values to strings for comparison
            valid_classes = [c[0] for c in classes if str(c[2]).split('.')[-1] == grade_level]
            print(f"    Grade {grade_level}: Found {len(valid_classes)} valid classes")
            
            if not valid_classes:
                print(f"      Skipping {grade_level} - no classes found")
                continue  # Skip if no classes for this grade level
            
            # Create multiple variations of each routine
            for variation in range(3):  # 3 variations per template
                routine_name = f"{template['name']} - Variation {variation + 1}"
                if variation > 0:
                    routine_name = f"{template['name']} - Advanced {variation + 1}"
                
                try:
                    routine = Routine(
                        name=routine_name,
                        description=f"{template['description']} - {grade_level} level variation {variation + 1}",
                        duration=template["duration"] + (variation * 5),  # Increase duration for variations
                        difficulty="INTERMEDIATE" if variation == 0 else "ADVANCED" if variation == 1 else "EXPERT",
                        instructions=f"Follow the routine sequence for {routine_name}. Each activity should be performed for the specified duration.",
                        equipment_needed={"equipment": ["None required"]},
                        target_skills=["coordination", "strength", "endurance"],
                        created_by=random.choice([u[0] for u in users]) if users else 1,  # Use valid user ID
                        class_id=random.choice(valid_classes),  # Use valid class ID for this grade
                        created_at=datetime.now() - timedelta(days=random.randint(1, 365)),
                        updated_at=datetime.now()
                    )
                    
                    session.add(routine)
                    session.flush()  # Get the ID
                    print(f"      Created routine: {routine_name} (ID: {routine.id})")
                    
                except Exception as e:
                    print(f"      ERROR creating routine {routine_name}: {e}")
                    continue
                
                # Add 3-6 activities to each routine
                num_activities = random.randint(3, 6)
                selected_activities = random.sample(activities, min(num_activities, len(activities)))
                
                for i, activity in enumerate(selected_activities):
                    routine_activity = RoutineActivity(
                        routine_id=routine.id,
                        activity_id=activity[0],
                        sequence_order=i + 1,
                        duration_minutes=template["duration"] // num_activities,
                        notes=f"Activity {i + 1} in {routine_name}"
                    )
                    session.add(routine_activity)
                    routine_activity_count += 1
                
                routine_count += 1
                
                # Commit every 10 routines to avoid memory issues
                if routine_count % 10 == 0:
                    session.commit()
                    print(f"  Created {routine_count} routines...")
    
    session.commit()
    print(f"✅ Routines seeded successfully! Created {routine_count} routines with {routine_activity_count} routine activities")
    print(f"📊 Summary: {len(routine_templates)} templates processed, {routine_count} routines created")
    
    if routine_count == 0:
        print("⚠️  WARNING: No routines were created! This may indicate a grade level mismatch.")
        print("   Check the grade level comparison above for any mismatches.")
    
    return routine_count, routine_activity_count