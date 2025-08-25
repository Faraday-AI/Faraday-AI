from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, text

def seed_adapted_activities(session: Session) -> Dict[str, int]:
    """Seed adapted activities and special needs data for comprehensive district coverage."""
    print("Seeding adapted activities and special needs data...")
    
    total_records = {}
    
    # Get existing data for relationships
    students = session.execute(select(text("id")).select_from(text("students")).limit(300)).fetchall()
    activities = session.execute(select(text("id")).select_from(text("activities")).limit(150)).fetchall()
    users = session.execute(select(text("id")).select_from(text("users")).limit(30)).fetchall()
    
    if not students or not activities:
        print("  No students or activities found, skipping adapted activities seeding")
        return {"total": 0}
    
    student_ids = [row[0] for row in students]
    activity_ids = [row[0] for row in activities]
    user_ids = [row[0] for row in users] if users else []
    
    # 1. Seed Adapted Activities (should be 300+)
    try:
        from app.models.activity_adaptation.activity.activity import AdaptedActivity
        
        # Clear existing data
        session.execute(AdaptedActivity.__table__.delete())
        
        adapted_activities_created = 0
        adaptation_reasons = ["ACCESSIBILITY", "SKILL_LEVEL", "EQUIPMENT", "SAFETY", "PHYSICAL_LIMITATION", "COGNITIVE_NEEDS"]
        difficulty_adjustments = ["EASIER", "SAME", "HARDER", "CUSTOM"]
        
        for i in range(350):  # Create 350 adapted activities
            adapted = AdaptedActivity(
                name=f"Adapted Activity {i+1}",
                activity_id=random.choice(activity_ids),
                type=random.choice(["CARDIO", "STRENGTH_TRAINING", "FLEXIBILITY", "BALANCE", "COORDINATION"]),
                difficulty_level=random.choice(["BEGINNER", "INTERMEDIATE", "ADVANCED"]),
                equipment_requirements=random.choice(["none", "minimal", "standard", "specialized", "extensive"]),
                duration_minutes=random.randint(15, 60),
                instructions={
                    "description": f"Adapted instructions for comprehensive record {i+1}",
                    "modifications": random.choice([
                        "Modified for students with mobility challenges.",
                        "Simplified for beginners and special needs students.",
                        "Enhanced with additional support and guidance.",
                        "Specialized for specific physical limitations.",
                        "Customized for individual student requirements.",
                        "Adapted for wheelchair accessibility.",
                        "Modified for students with balance issues.",
                        "Enhanced with visual and auditory cues."
                    ])
                },
                adaptations={
                    "equipment_modifications": random.choice([
                        "No equipment needed",
                        "Modified equipment provided",
                        "Assistive devices available",
                        "Alternative equipment options",
                        "Equipment adapted for accessibility"
                    ]),
                    "safety_considerations": random.choice([
                        "Enhanced supervision required",
                        "Modified safety protocols",
                        "Additional safety equipment",
                        "Reduced intensity for safety",
                        "Special safety considerations noted"
                    ])
                },
                activity_metadata={
                    "created_for": "comprehensive_district_seeding",
                    "adaptation_reason": random.choice(adaptation_reasons),
                    "difficulty_adjustment": random.choice(difficulty_adjustments)
                },
                status="ACTIVE",
                created_at=datetime.now() - timedelta(days=random.randint(1, 365)),
                updated_at=datetime.now() - timedelta(days=random.randint(1, 180))
            )
            session.add(adapted)
            adapted_activities_created += 1
            
            if adapted_activities_created % 100 == 0:
                session.flush()
                print(f"      Created {adapted_activities_created} adapted activities...")
        
        session.commit()
        total_records["adapted_activities"] = adapted_activities_created
        print(f"    Created {adapted_activities_created} adapted activities")
        
    except Exception as e:
        print(f"    Could not seed adapted activities: {e}")
        total_records["adapted_activities"] = 0
    
    # 2. Seed Student Activity Adaptations (skipping - model not found)
    total_records["student_activity_adaptations"] = 0
    print("    Skipping student activity adaptations - model not found")
    
    # 3. Seed Activity Assessments (should be 500+)
    try:
        from app.models.physical_education.activity.models import ActivityAssessment
        from app.models.physical_education.pe_enums.pe_types import PerformanceLevel
        
        # Get users (teachers) for assessors
        try:
            users = session.execute(text("SELECT id FROM users LIMIT 50")).fetchall()
            user_ids = [u[0] for u in users] if users else [1]
        except:
            user_ids = [1]  # Default fallback
        
        # Don't clear existing data - append to it instead
        # session.execute(ActivityAssessment.__table__.delete())  # REMOVED: Don't clear existing data
        
        activity_assessments_created = 0
        assessment_types = ["SKILL_EVALUATION", "SAFETY_ASSESSMENT", "PERFORMANCE_REVIEW", "PROGRESS_CHECK"]
        
        for i in range(600):  # Create 600 additional activity assessments
            # Get random performance level and convert to uppercase string for database compatibility
            performance_level_enum = random.choice([PerformanceLevel.EXCELLENT, PerformanceLevel.GOOD, PerformanceLevel.SATISFACTORY, PerformanceLevel.NEEDS_IMPROVEMENT, PerformanceLevel.POOR])
            performance_level_str = performance_level_enum.value.upper()
            
            assessment = ActivityAssessment(
                activity_id=random.choice(activity_ids),
                assessment_type=random.choice(assessment_types),
                assessment_date=datetime.now() - timedelta(days=random.randint(1, 180)),
                assessor_id=random.choice(user_ids),
                performance_level=performance_level_str,  # Use the correct field name
                feedback=f"Additional comprehensive activity assessment {i+1}. " +
                               random.choice([
                                   "Student demonstrated excellent form and technique.",
                                   "Good performance with room for improvement.",
                                   "Satisfactory completion of activity requirements.",
                                   "Needs additional practice and guidance.",
                                   "Excellent progress shown in skill development."
                               ]),
                recommendations=random.choice([
                    "Continue with current progression",
                    "Focus on form improvement",
                    "Increase difficulty gradually",
                    "Provide additional support",
                    "Maintain current level"
                ])
            )
            session.add(assessment)
            activity_assessments_created += 1
            
            if activity_assessments_created % 150 == 0:
                session.flush()
                print(f"      Created {activity_assessments_created} additional activity assessments...")
        
        session.commit()
        total_records["activity_assessments"] = activity_assessments_created
        print(f"    Created {activity_assessments_created} additional activity assessments (appended to existing data)")
        
    except Exception as e:
        print(f"    Could not seed activity assessments: {e}")
        total_records["activity_assessments"] = 0
    
    # 4. Seed Activity Preferences (should be 1,000+)
    try:
        from app.models.physical_education.student.student import ActivityPreference
        
        # Don't clear existing data - append to it instead
        # session.execute(ActivityPreference.__table__.delete())  # REMOVED: Don't clear existing data
        
        activity_preferences_created = 0
        preference_levels = ["STRONGLY_DISLIKE", "DISLIKE", "NEUTRAL", "LIKE", "STRONGLY_LIKE"]
        preference_reasons = ["ENJOYMENT", "SKILL_LEVEL", "CHALLENGE", "SOCIAL", "INDIVIDUAL", "TEAM"]
        
        for i in range(1200):  # Create 1,200 additional activity preferences
            preference = ActivityPreference(
                student_id=random.choice(student_ids),
                activity_id=random.choice(activity_ids),
                preference_level=random.choice(preference_levels),
                preference_reason=random.choice(preference_reasons),
                notes=f"Additional student preference record {i+1}. " +
                      random.choice([
                          "Student enjoys this type of activity.",
                          "Activity matches student's skill level well.",
                          "Provides appropriate challenge for student.",
                          "Student prefers individual activities.",
                          "Student enjoys team-based activities."
                      ]),
                created_at=datetime.now() - timedelta(days=random.randint(1, 365)),
                updated_at=datetime.now() - timedelta(days=random.randint(1, 180))
            )
            session.add(preference)
            activity_preferences_created += 1
            
            if activity_preferences_created % 200 == 0:
                session.flush()
                print(f"      Created {activity_preferences_created} additional activity preferences...")
        
        session.commit()
        total_records["activity_preferences"] = activity_preferences_created
        print(f"    Created {activity_preferences_created} additional activity preferences (appended to existing data)")
        
    except Exception as e:
        print(f"    Could not seed activity preferences: {e}")
        total_records["activity_preferences"] = 0
    
    # 5. Seed Activity Progression History (skipping - model not found)
    total_records["activity_progression_history"] = 0
    print("    Skipping progression history - model not found")
    
    # Calculate total records
    total_records["total"] = sum(total_records.values())
    
    print(f"✅ Adapted activities seeding complete! Created {total_records['total']} total records")
    return total_records 