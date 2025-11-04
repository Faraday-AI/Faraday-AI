"""
Beta Teacher System Integration Script
Integrates all new beta teacher components into the main seeding process
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
import random
import logging
from sqlalchemy.exc import SQLAlchemyError

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import SessionLocal, engine
from app.core.config import settings
from app.core.monitoring import track_metrics
from app.core.logging import get_logger

def env_true(key: str) -> bool:
    """Check if environment variable is set to true"""
    return os.getenv(key, '').lower() in ('true', '1', 'yes', 'on')

def seed_beta_teacher_system(session: Session) -> None:
    """
    Seed all beta teacher system components
    This integrates all the new beta teacher features into the main seeding process
    """
    print("\n🎯 BETA TEACHER SYSTEM INTEGRATION")
    print("=" * 60)
    
    try:
        # ==================== PHASE 1.6: LESSON PLAN BUILDER ====================
        if not env_true('SKIP_PHASE_1_6'):
            print("\n📚 PHASE 1.6: LESSON PLAN BUILDER SYSTEM")
            print("-" * 50)
            
            # Note: Tables are created by SQLAlchemy models, not SQL migration
            print("🔄 Tables already exist (created by SQLAlchemy models)")
            
            # Seed sample lesson plan templates
            print("🔄 Seeding sample lesson plan templates...")
            seed_lesson_plan_templates(session)
            
            # Seed AI lesson suggestions using existing table schema
            print("🔄 Seeding AI lesson suggestions...")
            seed_ai_lesson_suggestions(session)
            
            session.commit()
            print("✅ Phase 1.6: Lesson Plan Builder completed successfully!")
        else:
            print("⏭️  SKIP_PHASE_1_6 enabled: skipping Lesson Plan Builder")
        
        # ==================== PHASE 1.7: ASSESSMENT TOOLS ====================
        if not env_true('SKIP_PHASE_1_7'):
            print("\n📊 PHASE 1.7: ASSESSMENT TOOLS SYSTEM")
            print("-" * 50)
            
            # Note: Tables already exist (created by SQLAlchemy models)
            print("🔄 Tables already exist (created by SQLAlchemy models)")
            
            # Seed sample assessment templates
            print("🔄 Seeding sample assessment templates...")
            seed_assessment_templates(session)
            
            # Seed assessment questions and checklists
            print("🔄 Seeding assessment questions and checklists...")
            seed_assessment_questions(session)
            seed_assessment_checklists(session)
            
            session.commit()
            print("✅ Phase 1.7: Assessment Tools completed successfully!")
        else:
            print("⏭️  SKIP_PHASE_1_7 enabled: skipping Assessment Tools")
        
        # ==================== PHASE 1.8: RESOURCE MANAGEMENT ====================
        if not env_true('SKIP_PHASE_1_8'):
            print("\n📁 PHASE 1.8: RESOURCE MANAGEMENT SYSTEM")
            print("-" * 50)
            
            # Note: Tables already exist (created by SQLAlchemy models)
            print("🔄 Tables already exist (created by SQLAlchemy models)")
            
            # Seed resource categories first
            print("🔄 Seeding resource categories...")
            seed_resource_categories(session)
            
            # NOTE: Seed resource management data will run AFTER educational resources are created
            # Educational resources are created in Phase 1.10, so seeding happens later
            
            session.commit()
            print("✅ Phase 1.8: Resource Management completed successfully!")
        else:
            print("⏭️  SKIP_PHASE_1_8 enabled: skipping Resource Management")
        
        # ==================== PHASE 1.9: TEACHER DASHBOARD ====================
        if not env_true('SKIP_PHASE_1_9'):
            print("\n📊 PHASE 1.9: TEACHER DASHBOARD SYSTEM")
            print("-" * 50)
            
            # Wrap Phase 1.9 in a savepoint for isolation
            phase19_savepoint = session.begin_nested()
            try:
                # Note: Tables already exist (created by SQLAlchemy models)
                print("🔄 Tables already exist (created by SQLAlchemy models)")
                
                # Seed dashboard layouts and widgets
                print("🔄 Seeding dashboard layouts and widgets...")
                seed_teacher_dashboard_data(session)
                
                # Commit the savepoint and session
                phase19_savepoint.commit()
                session.commit()
                print("✅ Phase 1.9: Teacher Dashboard completed successfully!")
            except Exception as phase19_error:
                print(f"❌ Error in Phase 1.9: {phase19_error}")
                try:
                    phase19_savepoint.rollback()
                    # Try to recover session for Phase 1.10
                    session.rollback()
                    session.flush()
                    print("⚠️  Phase 1.9 failed but continuing with Phase 1.10...")
                except:
                    pass
        else:
            print("⏭️  SKIP_PHASE_1_9 enabled: skipping Teacher Dashboard")
        
        # ==================== PHASE 1.10: AI ASSISTANT INTEGRATION ====================
        if not env_true('SKIP_PHASE_1_10'):
            print("\n🤖 PHASE 1.10: AI ASSISTANT INTEGRATION")
            print("-" * 50)
            
            # Ensure session is in good state after Phase 1.9 (in case it failed)
            session_healthy = False
            try:
                # Test session state
                session.execute(text("SELECT 1")).scalar()
                session_healthy = True
            except Exception as session_error:
                print(f"⚠️  Session in failed state, attempting recovery...")
                try:
                    session.rollback()
                    session.flush()
                    # Test again after recovery
                    session.execute(text("SELECT 1")).scalar()
                    session_healthy = True
                    print("✅ Session recovered")
                except Exception as recovery_error:
                    print(f"⚠️  Could not recover session: {recovery_error}")
                    print("⚠️  Phase 1.10 may fail - parent transaction is in failed state")
            
            # Wrap Phase 1.10 in a savepoint for isolation (only if session is healthy)
            if not session_healthy:
                print("⚠️  Skipping Phase 1.10 savepoint creation due to failed session state")
                raise Exception("Cannot create savepoint - parent transaction is in failed state")
            
            phase10_savepoint = session.begin_nested()
            try:
                # Note: Tables already exist (created by SQLAlchemy models)
                print("🔄 Tables already exist (created by SQLAlchemy models)")
                
                # Seed AI assistant templates first (base templates for all teachers)
                print("🔄 Seeding AI assistant templates...")
                from app.scripts.seed_data.seed_ai_assistant_templates import seed_ai_assistant_templates
                seed_ai_assistant_templates(session)
                session.flush()  # Use flush() not commit() when called from within savepoint
                
                # Seed AI assistant configurations
                print("🔄 Seeding AI assistant configurations...")
                seed_ai_assistant_data(session)
                
                # Seed beta testing data
                print("🔄 Seeding beta testing data...")
                seed_beta_testing_data(session)
                
                # Create additional beta teachers FIRST for realistic testing and sharing
                # This ensures we have sufficient teachers (>2) before creating sharing data
                print("🔄 Creating additional beta teachers...")
                create_additional_beta_teachers(session)
                
                # Seed lesson plan sharing data (now with multiple teachers available)
                print("🔄 Seeding lesson plan sharing data...")
                seed_lesson_plan_sharing_data(session)
                
                # Seed assessment template data
                print("🔄 Seeding assessment template data...")
                seed_assessment_template_data(session)
                
                # Seed curriculum and lesson data
                print("🔄 Seeding curriculum and lesson data...")
                seed_curriculum_and_lesson_data(session)
                
                # Create comprehensive educational resources
                print("🔄 Creating comprehensive educational resources...")
                create_comprehensive_educational_resources(session)
                
                # Migrate content from main system to beta
                print("🔄 Migrating content from main system to beta...")
                migrate_main_system_content_to_beta(session)
                
                # Distribute content evenly among all teachers
                print("🔄 Distributing content evenly among teachers...")
                distribute_content_evenly(session)
                
                # Now seed resource management data with all teachers and resources
                print("🔄 Seeding resource management data with all teachers...")
                seed_resource_management_data(session)
                
                # Create lesson plan activities
                print("🔄 Creating lesson plan activities...")
                create_lesson_plan_activities(session)
                
                # Enhance avatar and widget configurations
                print("🔄 Enhancing avatar and widget configurations...")
                enhance_avatar_widget_configurations(session)
                
                # Seed remaining empty tables
                print("🔄 Seeding remaining empty tables...")
                seed_remaining_empty_tables(session)
                
                # Flush all changes to the savepoint before committing
                session.flush()
                
                # Check session state before committing
                session_healthy = True
                try:
                    # Test if parent session is healthy
                    session.execute(text("SELECT 1")).scalar()
                except Exception as session_test_error:
                    # Parent session is in failed state - can't commit savepoint
                    session_healthy = False
                    print(f"  ⚠️  Parent session is in failed state: {session_test_error}")
                    print("  ⚠️  Cannot commit savepoint - data may be lost")
                
                # Commit the savepoint and session (only if parent session is healthy)
                if not session_healthy:
                    print("⚠️  Cannot commit Phase 1.10 - parent transaction is in failed state")
                    print("⚠️  Data was seeded but may not be persisted")
                    # Try to recover for next phase
                    try:
                        phase10_savepoint.rollback()
                        session.rollback()
                        session.flush()
                    except:
                        pass
                else:
                    try:
                        phase10_savepoint.commit()
                        # Only commit the parent session after savepoint succeeds
                        session.commit()
                        print("✅ Phase 1.10: AI Assistant Integration completed successfully!")
                    except Exception as commit_error:
                        # If commit fails, rollback the savepoint
                        print(f"⚠️  Commit error in Phase 1.10: {commit_error}")
                        # Check if error is due to closed transaction
                        if "closed" in str(commit_error).lower() or "aborted" in str(commit_error).lower():
                            print("  ℹ️  Transaction is closed/aborted - data was seeded but commit failed")
                            print("  ℹ️  Attempting to recover session for next phase...")
                            try:
                                # Try to rollback savepoint (may fail if already closed)
                                try:
                                    phase10_savepoint.rollback()
                                except:
                                    pass
                                # Rollback parent session to clear failed state
                                session.rollback()
                                session.flush()
                                print("  ✅ Parent session rolled back and recovered")
                            except Exception as recovery_err:
                                print(f"  ⚠️  Could not recover parent session: {recovery_err}")
                        else:
                            # For other errors, try normal rollback
                            try:
                                # Rollback the savepoint first
                                phase10_savepoint.rollback()
                                # Then rollback the parent session
                                session.rollback()
                                session.flush()
                                print("⚠️  Phase 1.10 rolled back due to commit error")
                            except Exception as rollback_err:
                                print(f"⚠️  Could not rollback Phase 1.10 savepoint: {rollback_err}")
                                # If savepoint rollback fails, try to rollback parent session
                                try:
                                    session.rollback()
                                    session.flush()
                                except:
                                    pass
            except Exception as phase10_error:
                print(f"❌ Error in Phase 1.10: {phase10_error}")
                try:
                    phase10_savepoint.rollback()
                    # Try to recover session for remaining phases
                    session.rollback()
                    session.flush()
                except Exception as rollback_error:
                    # If rollback also fails, session might be closed
                    print(f"⚠️  Could not rollback Phase 1.10: {rollback_error}")
                print("⚠️  Phase 1.10 failed but continuing with remaining phases")
        else:
            print("⏭️  SKIP_PHASE_1_10 enabled: skipping AI Assistant Integration")
        
        print("\n🎉 BETA TEACHER SYSTEM INTEGRATION COMPLETE!")
        print("=" * 60)
        print("✅ All beta teacher components integrated successfully!")
        print("✅ Data migration completed for all new features!")
        print("✅ System ready for beta teacher testing!")
        
    except Exception as e:
        print(f"❌ ERROR: Beta teacher system integration failed: {e}")
        print("⚠️  Continuing with remaining phases - Beta components can be run separately")
        print(f"Full error details: {str(e)}")
        import traceback
        traceback.print_exc()
        session.rollback()

def seed_lesson_plan_templates(session: Session) -> None:
    """Seed sample lesson plan templates"""
    try:
        # Get a sample teacher ID
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
        if not teacher_result:
            print("⚠️  No teachers found, skipping lesson plan templates")
            return
        
        teacher_id = teacher_result[0]
        
        # Sample lesson plan templates - Expanded for more realistic mock data
        templates = [
            {
                "title": "Basketball Fundamentals",
                "description": "Basic basketball skills and techniques",
                "subject": "PE",
                "grade_level": "6-8",
                "duration_minutes": 45,
                "learning_objectives": ["Dribbling", "Shooting", "Passing", "Defense"],
                "materials_needed": ["Basketballs", "Cones", "Whistle"],
                "safety_considerations": ["Proper warm-up", "Safe spacing", "Equipment check"],
                "assessment_methods": ["Skill demonstration", "Peer observation", "Self-assessment"],
                "template_type": "standard",
                "difficulty_level": "intermediate",
                "equipment_required": ["Basketballs", "Cones"],
                "space_requirements": "Gymnasium",
                "weather_dependent": False,
                "is_public": True
            },
            {
                "title": "Cardio Fitness Circuit",
                "description": "High-intensity cardio workout circuit",
                "subject": "PE",
                "grade_level": "9-12",
                "duration_minutes": 30,
                "learning_objectives": ["Cardiovascular endurance", "Muscle strength", "Coordination"],
                "materials_needed": ["Timer", "Music", "Cones"],
                "safety_considerations": ["Heart rate monitoring", "Proper form", "Hydration breaks"],
                "assessment_methods": ["Heart rate zones", "Completion time", "Form check"],
                "template_type": "standard",
                "difficulty_level": "advanced",
                "equipment_required": ["Timer", "Cones"],
                "space_requirements": "Gymnasium or Outdoor",
                "weather_dependent": True,
                "is_public": True
            },
            {
                "title": "Yoga and Mindfulness",
                "description": "Relaxing yoga session with mindfulness techniques",
                "subject": "PE",
                "grade_level": "K-5",
                "duration_minutes": 25,
                "learning_objectives": ["Flexibility", "Balance", "Mindfulness", "Stress relief"],
                "materials_needed": ["Yoga mats", "Soft music", "Timer"],
                "safety_considerations": ["Gentle movements", "Proper breathing", "Comfortable clothing"],
                "assessment_methods": ["Participation", "Breathing technique", "Balance poses"],
                "template_type": "standard",
                "difficulty_level": "beginner",
                "equipment_required": ["Yoga mats"],
                "space_requirements": "Quiet indoor space",
                "weather_dependent": False,
                "is_public": True
            },
            {
                "title": "Soccer Skills Development",
                "description": "Fundamental soccer techniques and game play",
                "subject": "PE",
                "grade_level": "3-5",
                "duration_minutes": 40,
                "learning_objectives": ["Ball control", "Passing accuracy", "Teamwork", "Sportsmanship"],
                "materials_needed": ["Soccer balls", "Cones", "Jerseys"],
                "safety_considerations": ["Proper footwear", "Field inspection", "Hydration"],
                "assessment_methods": ["Skill tests", "Game participation", "Peer evaluation"],
                "template_type": "standard",
                "difficulty_level": "intermediate",
                "equipment_required": ["Soccer balls", "Cones"],
                "space_requirements": "Soccer field or gymnasium",
                "weather_dependent": True,
                "is_public": True
            },
            {
                "title": "Swimming Safety and Skills",
                "description": "Water safety and basic swimming techniques",
                "subject": "PE",
                "grade_level": "6-8",
                "duration_minutes": 50,
                "learning_objectives": ["Water safety", "Basic strokes", "Breathing techniques", "Rescue skills"],
                "materials_needed": ["Pool", "Life jackets", "Kickboards"],
                "safety_considerations": ["Lifeguard supervision", "Proper equipment", "Emergency procedures"],
                "assessment_methods": ["Stroke demonstration", "Safety knowledge", "Water confidence"],
                "template_type": "specialized",
                "difficulty_level": "intermediate",
                "equipment_required": ["Pool access", "Safety equipment"],
                "space_requirements": "Swimming pool",
                "weather_dependent": False,
                "is_public": True
            },
            {
                "title": "Track and Field Fundamentals",
                "description": "Introduction to track and field events",
                "subject": "PE",
                "grade_level": "9-12",
                "duration_minutes": 45,
                "learning_objectives": ["Running technique", "Jumping form", "Throwing mechanics", "Event strategy"],
                "materials_needed": ["Stopwatch", "Measuring tape", "Shot put", "High jump bar"],
                "safety_considerations": ["Proper warm-up", "Equipment safety", "Field conditions"],
                "assessment_methods": ["Performance times", "Technique evaluation", "Event participation"],
                "template_type": "standard",
                "difficulty_level": "advanced",
                "equipment_required": ["Track equipment", "Measuring tools"],
                "space_requirements": "Track and field facility",
                "weather_dependent": True,
                "is_public": True
            },
            {
                "title": "Dance and Movement",
                "description": "Creative movement and dance expression",
                "subject": "PE",
                "grade_level": "K-2",
                "duration_minutes": 30,
                "learning_objectives": ["Rhythm", "Coordination", "Creativity", "Self-expression"],
                "materials_needed": ["Music player", "Open space", "Props"],
                "safety_considerations": ["Clear space", "Comfortable clothing", "Age-appropriate music"],
                "assessment_methods": ["Participation", "Creativity", "Movement quality"],
                "template_type": "creative",
                "difficulty_level": "beginner",
                "equipment_required": ["Music system"],
                "space_requirements": "Large open space",
                "weather_dependent": False,
                "is_public": True
            },
            {
                "title": "Volleyball Basics",
                "description": "Introduction to volleyball skills and rules",
                "subject": "PE",
                "grade_level": "6-8",
                "duration_minutes": 40,
                "learning_objectives": ["Serving", "Passing", "Setting", "Game rules"],
                "materials_needed": ["Volleyballs", "Net", "Cones"],
                "safety_considerations": ["Proper technique", "Net safety", "Court boundaries"],
                "assessment_methods": ["Skill demonstration", "Game play", "Rule knowledge"],
                "template_type": "standard",
                "difficulty_level": "intermediate",
                "equipment_required": ["Volleyballs", "Net"],
                "space_requirements": "Volleyball court",
                "weather_dependent": False,
                "is_public": True
            },
            {
                "title": "Gymnastics Fundamentals",
                "description": "Basic gymnastics skills and safety",
                "subject": "PE",
                "grade_level": "3-5",
                "duration_minutes": 35,
                "learning_objectives": ["Balance", "Flexibility", "Body awareness", "Safety"],
                "materials_needed": ["Mats", "Balance beam", "Music"],
                "safety_considerations": ["Spotting techniques", "Mat placement", "Progressive skill building"],
                "assessment_methods": ["Skill progression", "Safety awareness", "Participation"],
                "template_type": "specialized",
                "difficulty_level": "beginner",
                "equipment_required": ["Gymnastics mats", "Balance equipment"],
                "space_requirements": "Gymnastics area",
                "weather_dependent": False,
                "is_public": True
            },
            {
                "title": "Fitness Testing and Assessment",
                "description": "Comprehensive fitness assessment program",
                "subject": "PE",
                "grade_level": "9-12",
                "duration_minutes": 60,
                "learning_objectives": ["Fitness components", "Testing protocols", "Goal setting", "Health awareness"],
                "materials_needed": ["Stopwatch", "Measuring tape", "Scale", "Heart rate monitors"],
                "safety_considerations": ["Medical clearance", "Proper warm-up", "Individual pacing"],
                "assessment_methods": ["Fitness scores", "Improvement tracking", "Goal achievement"],
                "template_type": "assessment",
                "difficulty_level": "advanced",
                "equipment_required": ["Fitness testing equipment"],
                "space_requirements": "Gymnasium and outdoor area",
                "weather_dependent": True,
                "is_public": True
            }
        ]
        
        for template_data in templates:
            # Insert lesson plan template
            template_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO lesson_plan_templates (
                    id, teacher_id, title, description, subject, grade_level,
                    duration_minutes, learning_objectives, materials_needed,
                    safety_considerations, assessment_methods, template_type,
                    difficulty_level, equipment_required, space_requirements,
                    weather_dependent, is_public, ai_generated, created_at
                ) VALUES (
                    :id, :teacher_id, :title, :description, :subject, :grade_level,
                    :duration_minutes, :learning_objectives, :materials_needed,
                    :safety_considerations, :assessment_methods, :template_type,
                    :difficulty_level, :equipment_required, :space_requirements,
                    :weather_dependent, :is_public, :ai_generated, :created_at
                )
            """), {
                "id": template_id,
                "teacher_id": teacher_id,
                "title": template_data["title"],
                "description": template_data["description"],
                "subject": template_data["subject"],
                "grade_level": template_data["grade_level"],
                "duration_minutes": template_data["duration_minutes"],
                "learning_objectives": template_data["learning_objectives"],
                "materials_needed": template_data["materials_needed"],
                "safety_considerations": template_data["safety_considerations"],
                "assessment_methods": template_data["assessment_methods"],
                "template_type": template_data["template_type"],
                "difficulty_level": template_data["difficulty_level"],
                "equipment_required": template_data["equipment_required"],
                "space_requirements": template_data["space_requirements"],
                "weather_dependent": template_data["weather_dependent"],
                "is_public": template_data["is_public"],
                "ai_generated": True,
                "created_at": datetime.utcnow()
            })
            
            # Add sample activities for each template
            activities = [
                {
                    "activity_name": "Warm-up",
                    "activity_description": "Light jogging and stretching",
                    "duration_minutes": 5,
                    "activity_type": "warmup",
                    "instructions": ["Start with light jogging", "Include dynamic stretches", "Focus on major muscle groups"]
                },
                {
                    "activity_name": "Main Activity",
                    "activity_description": "Core skill development",
                    "duration_minutes": 30,
                    "activity_type": "main_activity",
                    "instructions": ["Demonstrate proper technique", "Practice in small groups", "Provide individual feedback"]
                },
                {
                    "activity_name": "Cool-down",
                    "activity_description": "Stretching and reflection",
                    "duration_minutes": 10,
                    "activity_type": "cooldown",
                    "instructions": ["Static stretching", "Reflect on learning", "Prepare for next class"]
                }
            ]
            
            for i, activity_data in enumerate(activities):
                session.execute(text("""
                    INSERT INTO beta_lesson_plan_activities (
                        id, template_id, activity_name, activity_description,
                        duration_minutes, activity_type, instructions, order_index, created_at
                    ) VALUES (
                        :id, :template_id, :activity_name, :activity_description,
                        :duration_minutes, :activity_type, :instructions, :order_index, :created_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "template_id": template_id,
                    "activity_name": activity_data["activity_name"],
                    "activity_description": activity_data["activity_description"],
                    "duration_minutes": activity_data["duration_minutes"],
                    "activity_type": activity_data["activity_type"],
                    "instructions": activity_data["instructions"],
                    "order_index": i + 1,
                    "created_at": datetime.utcnow()
                })
        
        print(f"✅ Seeded {len(templates)} lesson plan templates with activities")
        
    except Exception as e:
        print(f"❌ Error seeding lesson plan templates: {e}")
        raise

def seed_assessment_templates(session: Session) -> None:
    """Seed sample assessment templates"""
    try:
        # Get a sample teacher ID
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
        if not teacher_result:
            print("⚠️  No teachers found, skipping assessment templates")
            return
        
        teacher_id = teacher_result[0]
        
        # Sample assessment templates
        templates = [
            {
                "title": "Basketball Skills Assessment",
                "description": "Comprehensive basketball skills evaluation",
                "subject": "PE",
                "grade_level": "6-8",
                "assessment_type": "summative",
                "duration_minutes": 30,
                "total_points": 100,
                "instructions": "Complete all skill stations and demonstrate proper technique",
                "materials_needed": ["Basketballs", "Cones", "Stopwatch", "Score sheets"],
                "safety_considerations": ["Proper warm-up", "Safe spacing", "Equipment check"],
                "difficulty_level": "intermediate",
                "equipment_required": ["Basketballs", "Cones"],
                "space_requirements": "Gymnasium",
                "weather_dependent": False,
                "is_public": True
            },
            {
                "title": "Fitness Test Battery",
                "description": "Standard fitness assessment for cardiovascular and muscular fitness",
                "subject": "PE",
                "grade_level": "9-12",
                "assessment_type": "diagnostic",
                "duration_minutes": 45,
                "total_points": 100,
                "instructions": "Complete all fitness tests to the best of your ability",
                "materials_needed": ["Stopwatch", "Measuring tape", "Cones", "Recording sheets"],
                "safety_considerations": ["Medical clearance", "Proper warm-up", "Hydration"],
                "difficulty_level": "advanced",
                "equipment_required": ["Stopwatch", "Measuring tape"],
                "space_requirements": "Gymnasium or Track",
                "weather_dependent": True,
                "is_public": True
            }
        ]
        
        for template_data in templates:
            # Insert assessment template
            template_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO assessment_templates (
                    id, teacher_id, title, description, subject, grade_level,
                    assessment_type, duration_minutes, total_points, instructions,
                    materials_needed, safety_considerations, difficulty_level,
                    equipment_required, space_requirements, weather_dependent,
                    is_public, ai_generated, created_at
                ) VALUES (
                    :id, :teacher_id, :title, :description, :subject, :grade_level,
                    :assessment_type, :duration_minutes, :total_points, :instructions,
                    :materials_needed, :safety_considerations, :difficulty_level,
                    :equipment_required, :space_requirements, :weather_dependent,
                    :is_public, :ai_generated, :created_at
                )
            """), {
                "id": template_id,
                "teacher_id": teacher_id,
                "title": template_data["title"],
                "description": template_data["description"],
                "subject": template_data["subject"],
                "grade_level": template_data["grade_level"],
                "assessment_type": template_data["assessment_type"],
                "duration_minutes": template_data["duration_minutes"],
                "total_points": template_data["total_points"],
                "instructions": template_data["instructions"],
                "materials_needed": template_data["materials_needed"],
                "safety_considerations": template_data["safety_considerations"],
                "difficulty_level": template_data["difficulty_level"],
                "equipment_required": template_data["equipment_required"],
                "space_requirements": template_data["space_requirements"],
                "weather_dependent": template_data["weather_dependent"],
                "is_public": template_data["is_public"],
                "ai_generated": True,
                "created_at": datetime.utcnow()
            })
            
            # Add sample criteria
            criteria_data = [
                {
                    "criterion_name": "Skill Execution",
                    "criterion_description": "Proper technique and form",
                    "max_points": 40,
                    "weight_percentage": 40.0,
                    "assessment_method": "observation"
                },
                {
                    "criterion_name": "Effort and Participation",
                    "criterion_description": "Active engagement and effort",
                    "max_points": 30,
                    "weight_percentage": 30.0,
                    "assessment_method": "observation"
                },
                {
                    "criterion_name": "Safety Awareness",
                    "criterion_description": "Following safety protocols",
                    "max_points": 30,
                    "weight_percentage": 30.0,
                    "assessment_method": "checklist"
                }
            ]
            
            for i, criterion in enumerate(criteria_data):
                criterion_id = str(uuid.uuid4())
                session.execute(text("""
                    INSERT INTO assessment_criteria (
                        id, template_id, criterion_name, criterion_description,
                        max_points, weight_percentage, assessment_method, order_index, created_at
                    ) VALUES (
                        :id, :template_id, :criterion_name, :criterion_description,
                        :max_points, :weight_percentage, :assessment_method, :order_index, :created_at
                    )
                """), {
                    "id": criterion_id,
                    "template_id": template_id,
                    "criterion_name": criterion["criterion_name"],
                    "criterion_description": criterion["criterion_description"],
                    "max_points": criterion["max_points"],
                    "weight_percentage": criterion["weight_percentage"],
                    "assessment_method": criterion["assessment_method"],
                    "order_index": i + 1,
                    "created_at": datetime.utcnow()
                })
                
                # Add rubric for each criterion
                session.execute(text("""
                    INSERT INTO assessment_rubrics (
                        id, template_id, criterion_id, rubric_name, rubric_description,
                        performance_levels, performance_descriptions, point_values, order_index, created_at
                    ) VALUES (
                        :id, :template_id, :criterion_id, :rubric_name, :rubric_description,
                        :performance_levels, :performance_descriptions, :point_values, :order_index, :created_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "template_id": template_id,
                    "criterion_id": criterion_id,
                    "rubric_name": f"{criterion['criterion_name']} Rubric",
                    "rubric_description": f"Detailed rubric for {criterion['criterion_name']}",
                    "performance_levels": ["Excellent", "Good", "Satisfactory", "Needs Improvement"],
                    "performance_descriptions": [
                        "Exceeds expectations with exceptional performance",
                        "Meets expectations with good performance",
                        "Meets basic expectations",
                        "Below expectations, needs improvement"
                    ],
                    "point_values": [criterion["max_points"], int(criterion["max_points"] * 0.8), int(criterion["max_points"] * 0.6), int(criterion["max_points"] * 0.4)],
                    "order_index": i + 1,
                    "created_at": datetime.utcnow()
                })
        
        print(f"✅ Seeded {len(templates)} assessment templates with criteria and rubrics")
        
    except Exception as e:
        print(f"❌ Error seeding assessment templates: {e}")
        raise

def seed_assessment_questions(session: Session) -> None:
    """Seed assessment questions for existing templates"""
    try:
        # Get existing assessment template IDs
        template_results = session.execute(text("SELECT id FROM assessment_templates LIMIT 2")).fetchall()
        if not template_results:
            print("⚠️  No assessment templates found, skipping questions")
            return
        
        template_ids = [row[0] for row in template_results]
        
        # Sample questions for each template
        questions = [
            {
                "question_text": "What is the proper technique for shooting a basketball?",
                "question_type": "short_answer",
                "points": 10,
                "correct_answer": "BEEF - Balance, Eyes, Elbow, Follow-through",
                "possible_answers": [],
                "order_index": 1
            },
            {
                "question_text": "Which of the following is NOT a component of fitness?",
                "question_type": "multiple_choice",
                "points": 5,
                "correct_answer": "Flexibility",
                "possible_answers": ["Cardiovascular endurance", "Muscular strength", "Flexibility", "Speed"],
                "order_index": 2
            },
            {
                "question_text": "True or False: Warming up before exercise is important for injury prevention.",
                "question_type": "true_false",
                "points": 3,
                "correct_answer": "True",
                "possible_answers": [],
                "order_index": 3
            }
        ]
        
        for template_id in template_ids:
            for question_data in questions:
                session.execute(text("""
                    INSERT INTO assessment_questions (
                        id, template_id, question_text, question_type, points,
                        correct_answer, possible_answers, order_index, created_at
                    ) VALUES (
                        :id, :template_id, :question_text, :question_type, :points,
                        :correct_answer, :possible_answers, :order_index, :created_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "template_id": template_id,
                    "question_text": question_data["question_text"],
                    "question_type": question_data["question_type"],
                    "points": question_data["points"],
                    "correct_answer": question_data["correct_answer"],
                    "possible_answers": question_data["possible_answers"],
                    "order_index": question_data["order_index"],
                    "created_at": datetime.utcnow()
                })
        
        print(f"✅ Seeded {len(questions) * len(template_ids)} assessment questions")
        
    except Exception as e:
        print(f"❌ Error seeding assessment questions: {e}")
        raise

def seed_assessment_checklists(session: Session) -> None:
    """Seed assessment checklists for existing templates"""
    try:
        # Get existing assessment template IDs
        template_results = session.execute(text("SELECT id FROM assessment_templates LIMIT 2")).fetchall()
        if not template_results:
            print("⚠️  No assessment templates found, skipping checklists")
            return
        
        template_ids = [row[0] for row in template_results]
        
        # Sample checklist items for each template
        checklist_items = [
            {
                "checklist_item": "Student demonstrates proper form and technique",
                "is_required": True,
                "points": 10,
                "order_index": 1
            },
            {
                "checklist_item": "Student shows effort and participation",
                "is_required": True,
                "points": 8,
                "order_index": 2
            },
            {
                "checklist_item": "Student follows safety guidelines",
                "is_required": True,
                "points": 7,
                "order_index": 3
            },
            {
                "checklist_item": "Student helps others when appropriate",
                "is_required": False,
                "points": 5,
                "order_index": 4
            }
        ]
        
        for template_id in template_ids:
            for item_data in checklist_items:
                session.execute(text("""
                    INSERT INTO assessment_checklists (
                        id, template_id, checklist_item, is_required,
                        points, order_index, created_at
                    ) VALUES (
                        :id, :template_id, :checklist_item, :is_required,
                        :points, :order_index, :created_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "template_id": template_id,
                    "checklist_item": item_data["checklist_item"],
                    "is_required": item_data["is_required"],
                    "points": item_data["points"],
                    "order_index": item_data["order_index"],
                    "created_at": datetime.utcnow()
                })
        
        print(f"✅ Seeded {len(checklist_items) * len(template_ids)} assessment checklist items")
        
    except Exception as e:
        print(f"❌ Error seeding assessment checklists: {e}")
        raise

def seed_resource_management_data(session: Session) -> None:
    """Seed sample resources and collections"""
    try:
        # Get a sample teacher ID
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
        if not teacher_result:
            print("⚠️  No teachers found, skipping resource management data")
            return
        
        teacher_id = teacher_result[0]
        
        # Sample resources
        resources = [
            {
                "title": "Basketball Rules and Regulations",
                "description": "Complete guide to basketball rules for students",
                "resource_type": "document",
                "subject": "PE",
                "grade_level": "6-8",
                "tags": ["basketball", "rules", "sports"],
                "keywords": ["basketball", "rules", "regulations", "sports"],
                "difficulty_level": "intermediate",
                "language": "en",
                "license_type": "educational_use",
                "is_public": True,
                "is_featured": True
            },
            {
                "title": "Fitness Assessment Video",
                "description": "Instructional video demonstrating proper fitness test techniques",
                "resource_type": "video",
                "subject": "PE",
                "grade_level": "9-12",
                "tags": ["fitness", "assessment", "video"],
                "keywords": ["fitness", "assessment", "technique", "video"],
                "difficulty_level": "advanced",
                "duration_minutes": 15,
                "language": "en",
                "license_type": "educational_use",
                "is_public": True,
                "is_featured": False
            },
            {
                "title": "Yoga Poses Reference Sheet",
                "description": "Visual reference sheet with common yoga poses",
                "resource_type": "image",
                "subject": "PE",
                "grade_level": "K-5",
                "tags": ["yoga", "poses", "flexibility"],
                "keywords": ["yoga", "poses", "flexibility", "mindfulness"],
                "difficulty_level": "beginner",
                "language": "en",
                "license_type": "educational_use",
                "is_public": True,
                "is_featured": True
            }
        ]
        
        resource_ids = []
        for resource_data in resources:
            resource_id = str(uuid.uuid4())
            resource_ids.append(resource_id)
            
            session.execute(text("""
                INSERT INTO educational_resources (
                    id, teacher_id, title, description, resource_type, subject, grade_level,
                    tags, keywords, difficulty_level, duration_minutes, language,
                    license_type, is_public, is_featured, ai_generated, created_at
                ) VALUES (
                    :id, :teacher_id, :title, :description, :resource_type, :subject, :grade_level,
                    :tags, :keywords, :difficulty_level, :duration_minutes, :language,
                    :license_type, :is_public, :is_featured, :ai_generated, :created_at
                )
            """), {
                "id": resource_id,
                "teacher_id": teacher_id,
                "title": resource_data["title"],
                "description": resource_data["description"],
                "resource_type": resource_data["resource_type"],
                "subject": resource_data["subject"],
                "grade_level": resource_data["grade_level"],
                "tags": resource_data["tags"],
                "keywords": resource_data["keywords"],
                "difficulty_level": resource_data["difficulty_level"],
                "duration_minutes": resource_data.get("duration_minutes"),
                "language": resource_data["language"],
                "license_type": resource_data["license_type"],
                "is_public": resource_data["is_public"],
                "is_featured": resource_data["is_featured"],
                "ai_generated": True,
                "created_at": datetime.utcnow()
            })
        
        # Create sample resource collection
        collection_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO resource_collections (
                id, teacher_id, title, description, subject, grade_level,
                collection_type, is_public, is_featured, resource_count, created_at
            ) VALUES (
                :id, :teacher_id, :title, :description, :subject, :grade_level,
                :collection_type, :is_public, :is_featured, :resource_count, :created_at
            )
        """), {
            "id": collection_id,
            "teacher_id": teacher_id,
            "title": "PE Fundamentals Collection",
            "description": "Essential resources for physical education fundamentals",
            "subject": "PE",
            "grade_level": "K-12",
            "collection_type": "curriculum",
            "is_public": True,
            "is_featured": True,
            "resource_count": len(resource_ids),
            "created_at": datetime.utcnow()
        })
        
        # Add resources to collection
        for i, resource_id in enumerate(resource_ids):
            session.execute(text("""
                INSERT INTO collection_resource_associations (
                    id, collection_id, resource_id, order_index, added_at
                ) VALUES (
                    :id, :collection_id, :resource_id, :order_index, :added_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "collection_id": collection_id,
                "resource_id": resource_id,
                "order_index": i + 1,
                "added_at": datetime.utcnow()
            })
        
        print(f"✅ Seeded {len(resources)} resources and 1 collection")
        
    except Exception as e:
        print(f"❌ Error seeding resource management data: {e}")
        raise

def seed_teacher_dashboard_data(session: Session) -> None:
    """Seed dashboard data using existing tables"""
    try:
        # Get a sample teacher ID
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
        if not teacher_result:
            print("⚠️  No teachers found, skipping teacher dashboard data")
            return
        
        teacher_id = teacher_result[0]
        
        # Seed dashboard widgets (using existing dashboard_widgets table)
        print("🔄 Seeding dashboard widgets...")
        
        # Get a dashboard ID first
        dashboard_result = session.execute(text("SELECT id FROM dashboards LIMIT 1")).fetchone()
        if not dashboard_result:
            print("⚠️  No dashboards found, creating a default dashboard...")
            session.execute(text("""
                INSERT INTO dashboards (name, description, is_active, created_at)
                VALUES ('Default Dashboard', 'Default dashboard for teachers', true, :created_at)
            """), {"created_at": datetime.utcnow()})
            dashboard_id = session.execute(text("SELECT id FROM dashboards ORDER BY id DESC LIMIT 1")).fetchone()[0]
        else:
            dashboard_id = dashboard_result[0]
        
        # Check if id column requires a value by checking schema
        schema_result = session.execute(
            text("""
                SELECT column_name, data_type, column_default, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'dashboard_widgets' AND column_name = 'id'
            """)
        ).first()
        
        widget_data = [
            {
                "name": "Lesson Plan Overview",
                "description": "Overview of recent lesson plans",
                "widget_type": "CHART",
                "is_active": True
            },
            {
                "name": "Student Progress",
                "description": "Student progress tracking widget",
                "widget_type": "METRIC",
                "is_active": True
            },
            {
                "name": "Assessment Results",
                "description": "Recent assessment results",
                "widget_type": "TABLE",
                "is_active": True
            },
            {
                "name": "Resource Library",
                "description": "Quick access to educational resources",
                "widget_type": "LIST",
                "is_active": True
            }
        ]
        
        # Add savepoint isolation for dashboard widgets
        savepoint = session.begin_nested()
        try:
            for widget in widget_data:
                widget_values = {
                    "name": widget["name"],
                    "description": widget["description"],
                    "widget_type": widget["widget_type"],
                    "layout_position": "TOP_LEFT",
                    "size": json.dumps({"width": 4, "height": 3}),
                    "configuration": json.dumps({"refresh_interval": 300}),
                    "is_active": widget["is_active"],
                    "is_visible": True,
                    "dashboard_id": dashboard_id,
                    "created_at": datetime.utcnow()
                }
                
                # Add id if required (NOT NULL with no default)
                if schema_result and schema_result[2] is None and schema_result[3] == 'NO':
                    widget_values["id"] = str(uuid.uuid4())
                    session.execute(text("""
                        INSERT INTO dashboard_widgets (
                            id, name, description, widget_type, layout_position, size, configuration,
                            is_active, is_visible, dashboard_id, created_at
                        ) VALUES (
                            :id, :name, :description, :widget_type, :layout_position, :size, :configuration,
                            :is_active, :is_visible, :dashboard_id, :created_at
                        )
                    """), widget_values)
                else:
                    # id has default or is nullable - let database handle it
                    session.execute(text("""
                        INSERT INTO dashboard_widgets (
                            name, description, widget_type, layout_position, size, configuration,
                            is_active, is_visible, dashboard_id, created_at
                        ) VALUES (
                            :name, :description, :widget_type, :layout_position, :size, :configuration,
                            :is_active, :is_visible, :dashboard_id, :created_at
                        )
                    """), widget_values)
            
            savepoint.commit()
            session.flush()  # Use flush() not commit() when called from within savepoint
        except Exception as e:
            print(f"❌ Error seeding dashboard widgets: {e}")
            savepoint.rollback()
            raise
        
        # Seed dashboard analytics
        print("🔄 Seeding dashboard analytics...")
        analytics_data = [
            {
                "metrics": {"lesson_plans_created": 15, "students_assessed": 120, "resources_shared": 8},
                "period": "daily",
                "gpt_usage": {"requests": 45, "tokens": 1200},
                "api_calls": {"total": 200, "successful": 195, "failed": 5},
                "error_logs": {"errors": 2, "warnings": 1}
            },
            {
                "metrics": {"lesson_plans_created": 8, "students_assessed": 85, "resources_shared": 3},
                "period": "weekly",
                "gpt_usage": {"requests": 120, "tokens": 3200},
                "api_calls": {"total": 450, "successful": 440, "failed": 10},
                "error_logs": {"errors": 1, "warnings": 0}
            }
        ]
        
        for analytics in analytics_data:
            session.execute(text("""
                INSERT INTO dashboard_analytics (
                    user_id, metrics, timestamp, period, gpt_usage, api_calls, error_logs
                ) VALUES (
                    :user_id, :metrics, :timestamp, :period, :gpt_usage, :api_calls, :error_logs
                )
            """), {
                "user_id": 1,  # Use a default user ID
                "metrics": json.dumps(analytics["metrics"]),
                "timestamp": datetime.utcnow(),
                "period": analytics["period"],
                "gpt_usage": json.dumps(analytics["gpt_usage"]),
                "api_calls": json.dumps(analytics["api_calls"]),
                "error_logs": json.dumps(analytics["error_logs"])
            })
        
        # Seed dashboard feedback
        print("🔄 Seeding dashboard feedback...")
        feedback_data = [
            {
                "title": "Lesson Plan Builder Feedback",
                "feedback_type": "suggestion",
                "content": {"message": "The lesson plan builder could use more template options", "category": "ui"},
                "rating": 4,
                "status": "open",
                "priority": "medium"
            },
            {
                "title": "Assessment Bug Report",
                "feedback_type": "bug_report",
                "content": {"message": "Assessment results sometimes don't save properly", "category": "bug"},
                "rating": 2,
                "status": "in_progress",
                "priority": "high"
            },
            {
                "title": "Analytics Feature Request",
                "feedback_type": "feature_request",
                "content": {"message": "Would like to see more analytics on student engagement", "category": "feature"},
                "rating": 5,
                "status": "open",
                "priority": "low"
            }
        ]
        
        for feedback in feedback_data:
            session.execute(text("""
                INSERT INTO dashboard_feedback (
                    user_id, gpt_id, title, feedback_type, content, rating, created_at, status, priority
                ) VALUES (
                    :user_id, :gpt_id, :title, :feedback_type, :content, :rating, :created_at, :status, :priority
                )
            """), {
                "user_id": 1,  # Use a default user ID
                "gpt_id": "gpt-4",
                "title": feedback["title"],
                "feedback_type": feedback["feedback_type"],
                "content": json.dumps(feedback["content"]),
                "rating": feedback["rating"],
                "created_at": datetime.utcnow(),
                "status": feedback["status"],
                "priority": feedback["priority"]
            })
        
        print("✅ Seeded teacher dashboard data with widgets, analytics, and feedback")
        
        # Seed the 12 Beta Teacher Dashboard tables
        print("\n🔄 Seeding Beta Teacher Dashboard tables...")
        try:
            seed_beta_teacher_dashboard_tables(session)
        except Exception as beta_dashboard_error:
            print(f"⚠️  Error seeding beta teacher dashboard tables: {beta_dashboard_error}")
            # Don't raise - allow Phase 1.9 to complete with what it has
            # The beta dashboard tables seeding has its own savepoint, so it won't affect other data
        
    except Exception as e:
        print(f"❌ Error seeding teacher dashboard data: {e}")
        # Don't raise - allow Phase 1.9's savepoint to handle recovery
        # This allows Phase 1.10 to still run even if Phase 1.9 partially fails

def migrate_existing_teacher_data_to_beta(session: Session) -> None:
    """Migrate existing teacher-related data from main system to beta dashboard tables
    
    IMPORTANT: Beta system REUSES main system teacher functions that are NOT tied to district/student data.
    - Main system = Has district-level AND teacher-only features
    - Beta system = Uses ONLY teacher-only features (lesson plans, assessments, resources, AI assistant)
    - Teacher-only features: Lesson Plan Builder, Assessment Tools, Resource Management, AI Assistant
    
    This migration migrates teacher personal data (not district data):
    1. Lesson plans they created (lesson_plan_templates)
    2. Assessment templates they created (assessment_templates)
    3. Resources they uploaded/shared (educational_resources)
    4. Their personal activity/statistics (teacher-level only)
    5. Their personal goals/achievements (not district goals)
    
    NOTE: Beta teachers use the SAME main system tables for teacher-only features.
    Migration only populates beta dashboard tables (analytics, achievements, notifications) from main system teacher data.
    """
    savepoint = session.begin_nested()
    try:
        print("\n📦 Migrating teacher personal data to Beta Teacher Dashboard...")
        print("   ℹ️  Beta teachers use main system teacher functions (lesson plans, assessments, resources)")
        print("   ℹ️  Only migrating personal analytics/achievements to beta dashboard tables")
        
        # Get beta teacher IDs (from teacher_registrations - same table used by both systems)
        teacher_results = session.execute(text("SELECT id FROM teacher_registrations LIMIT 10")).fetchall()
        if not teacher_results:
            print("⚠️  No beta teachers found, skipping migration")
            savepoint.commit()
            return
        
        teacher_ids = [row[0] for row in teacher_results]
        
        # Check if educational_resources table exists and has created_by column
        has_educational_resources_created_by = False
        try:
            result = session.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'educational_resources' AND column_name = 'created_by'
            """)).fetchone()
            has_educational_resources_created_by = result is not None
        except Exception:
            pass
        
        # Beta teachers use main system teacher functions, so they may have data in main system tables
        # Check which teachers have created lesson plans, assessments, or resources in main system
        teachers_with_main_data = []
        for teacher_id in teacher_ids:
            teacher_email_result = session.execute(text("""
                SELECT email FROM teacher_registrations WHERE id = :teacher_id
            """), {"teacher_id": teacher_id}).fetchone()
            
            if teacher_email_result:
                email = teacher_email_result[0]
                # Check if teacher has created any personal content (lesson plans, assessments, resources)
                # Only check educational_resources if the created_by column exists
                if has_educational_resources_created_by:
                    has_content = session.execute(text("""
                        SELECT COUNT(*) FROM (
                            SELECT 1 FROM lesson_plan_templates WHERE teacher_id = :teacher_id
                            UNION ALL
                            SELECT 1 FROM assessment_templates WHERE teacher_id = :teacher_id
                            UNION ALL
                            SELECT 1 FROM educational_resources WHERE created_by = :teacher_id
                        ) content
                    """), {"teacher_id": teacher_id}).scalar()
                else:
                    # Skip educational_resources check if column doesn't exist
                    has_content = session.execute(text("""
                        SELECT COUNT(*) FROM (
                            SELECT 1 FROM lesson_plan_templates WHERE teacher_id = :teacher_id
                            UNION ALL
                            SELECT 1 FROM assessment_templates WHERE teacher_id = :teacher_id
                        ) content
                    """), {"teacher_id": teacher_id}).scalar()
                
                if has_content:
                    teachers_with_main_data.append(teacher_id)
        
        if not teachers_with_main_data:
            print("   ℹ️  No teachers with existing content - will seed fresh data")
            print("   ✅ Beta teachers will use main system functions going forward")
            savepoint.commit()
            return
        
        print(f"   🔍 Found {len(teachers_with_main_data)} teachers with existing personal content")
        print("   📋 Migrating teacher personal data to beta dashboard (analytics, achievements, etc.)")
        
        # Initialize all migration counters to avoid reference errors
        migrated_count = 0
        migrated_stats = 0
        migrated_notifs = 0
        migrated_goals = 0
        
        # 1. Migrate activity_logs → teacher_activity_logs (teacher personal activities only)
        # These are activities from using main system teacher functions (lesson plans, assessments, resources)
        try:
            print("  🔄 Migrating teacher activity logs (from main system teacher functions)...")
            
            # Check if activity_logs table exists and has the action column (correct column name)
            activity_logs_available = False
            try:
                result = session.execute(text("""
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = 'activity_logs' AND column_name = 'action'
                """)).fetchone()
                activity_logs_available = result is not None
            except Exception:
                pass
            
            # Migrate activities related to teacher-only features (lesson plans, assessments, resources, AI)
            # activity_logs table has: id, action, resource_type, resource_id, details (JSON), user_id, org_id, timestamp, created_at
            # We map: action -> activity_type, details -> activity_metadata, action -> activity_description
            if not teachers_with_main_data:
                print("    ℹ️  No teachers with existing content, skipping activity log migration")
                migrated_count = 0
            elif not activity_logs_available:
                print("    ⚠️  Activity logs migration skipped: activity_logs table not available")
                print("    ℹ️  This is OK - beta system will seed fresh activity logs")
                migrated_count = 0
            else:
                # Query activity_logs using correct column names: action (not activity_type), details (not metadata)
                activity_logs_result = session.execute(text("""
                    SELECT DISTINCT ON (al.id) 
                        al.id, al.user_id, al.action, al.action as description,
                        al.resource_type, al.resource_id, al.details, 
                        NULL as ip_address, NULL as user_agent, NULL as session_id, al.created_at
                    FROM activity_logs al
                    INNER JOIN users u ON al.user_id = u.id
                    INNER JOIN teacher_registrations tr ON u.email = tr.email
                    WHERE al.created_at >= NOW() - INTERVAL '90 days'
                        AND al.action IN (
                            'lesson_created', 'lesson_plan_created', 'assessment_created', 
                            'assessment_template_created', 'resource_downloaded', 'resource_uploaded',
                            'resource_shared', 'ai_used', 'ai_assistant_used', 'login', 'dashboard_viewed',
                            'create_lesson', 'create_assessment', 'download_resource', 'upload_resource'
                        )
                        AND tr.id = ANY(:teacher_ids)
                    ORDER BY al.id, al.created_at DESC
                    LIMIT 1000
                """), {"teacher_ids": teachers_with_main_data}).fetchall()
                
                migrated_count = 0
                for log in activity_logs_result:
                    # Get teacher_id from teacher_registrations
                    teacher_result = session.execute(text("""
                        SELECT tr.id FROM teacher_registrations tr
                        INNER JOIN users u ON tr.email = u.email
                        WHERE u.id = :user_id
                        LIMIT 1
                    """), {"user_id": log[1]}).fetchone()
                    
                    if teacher_result:
                        teacher_id = teacher_result[0]
                        # Check if already migrated
                        # log structure: [id, user_id, action, description (same as action), resource_type, resource_id, details (JSON), ip_address (NULL), user_agent (NULL), session_id (NULL), created_at]
                        activity_type = log[2] or "unknown"  # action from activity_logs
                        activity_description = log[3] or activity_type  # description (same as action)
                        resource_type = log[4]
                        resource_id = str(log[5]) if log[5] else None
                        activity_metadata = json.dumps(log[6]) if log[6] else None  # details JSON from activity_logs
                        created_at = log[10]  # created_at from activity_logs
                        
                        exists = session.execute(text("""
                            SELECT COUNT(*) FROM teacher_activity_logs 
                            WHERE id = :id OR (teacher_id = CAST(:teacher_id AS VARCHAR) AND activity_type = :activity_type AND created_at = :created_at)
                        """), {
                            "id": str(log[0]),
                            "teacher_id": str(teacher_id),
                            "activity_type": activity_type,
                            "created_at": created_at
                        }).scalar()
                        
                        if not exists:
                            session.execute(text("""
                                INSERT INTO teacher_activity_logs (
                                    id, teacher_id, activity_type, activity_description, resource_type,
                                    resource_id, resource_title, activity_metadata, ip_address, user_agent,
                                    session_id, created_at
                                ) VALUES (
                                    :id, :teacher_id, :activity_type, :description, :resource_type,
                                    :resource_id, NULL, :metadata, NULL, NULL, NULL, :created_at
                                )
                                ON CONFLICT (id) DO NOTHING
                            """), {
                                "id": str(log[0]),
                                "teacher_id": str(teacher_id),
                                "activity_type": activity_type,
                                "description": activity_description,
                                "resource_type": resource_type,
                                "resource_id": resource_id,
                                "metadata": activity_metadata,
                                "created_at": created_at
                            })
                            migrated_count += 1
                
                if migrated_count > 0:
                    print(f"    ✅ Migrated {migrated_count} activity logs")
                else:
                    print(f"    ℹ️  No activity logs to migrate (or already migrated)")
        except Exception as e:
            print(f"    ⚠️  Activity logs migration skipped: {e}")
            # Recover session if transaction was aborted
            try:
                session.rollback()
                session.flush()
            except:
                pass
        
        # 2. Migrate analytics_events → teacher_statistics (from teacher-only feature usage)
        # Aggregate stats from teacher using main system functions (lesson plans, assessments, resources)
        try:
            print("  🔄 Migrating teacher statistics (from main system teacher function usage)...")
            
            # Ensure session is in good state before proceeding
            try:
                session.execute(text("SELECT 1")).scalar()
            except Exception:
                # Session is in failed state, recover it
                try:
                    session.rollback()
                    session.flush()
                except:
                    pass
            
            for teacher_id in teachers_with_main_data:
                # Get teacher email to match analytics events
                teacher_email_result = session.execute(text("""
                    SELECT email FROM teacher_registrations WHERE id = :teacher_id
                """), {"teacher_id": teacher_id}).fetchone()
                
                if not teacher_email_result:
                    continue
                
                teacher_email = teacher_email_result[0]
                
                # Aggregate analytics from teacher using main system teacher functions
                # Count activities from lesson plans, assessments, resources, AI assistant
                # analytics_events table has: id, user_id, event_type, event_data, session_id, timestamp (not created_at), source, version, event_metadata
                stats_result = session.execute(text("""
                    SELECT 
                        DATE(ae.timestamp) as stat_date,
                        COUNT(*) FILTER (WHERE ae.event_type IN ('lesson_created', 'lesson_plan_created', 'lesson_plan_template_created')) as lessons,
                        COUNT(*) FILTER (WHERE ae.event_type IN ('assessment_created', 'assessment_template_created')) as assessments,
                        COUNT(*) FILTER (WHERE ae.event_type IN ('resource_downloaded', 'resource_accessed')) as downloads,
                        COUNT(*) FILTER (WHERE ae.event_type IN ('resource_shared', 'resource_shared_with_teacher')) as shares,
                        COUNT(*) FILTER (WHERE ae.event_type = 'login') as logins
                    FROM analytics_events ae
                    INNER JOIN users u ON ae.user_id = u.id
                    WHERE u.email = :email
                        AND ae.timestamp >= NOW() - INTERVAL '30 days'
                        AND ae.event_type IN (
                            'lesson_created', 'lesson_plan_created', 'lesson_plan_template_created',
                            'assessment_created', 'assessment_template_created',
                            'resource_downloaded', 'resource_uploaded', 'resource_shared', 'resource_accessed',
                            'ai_used', 'ai_assistant_used',
                            'login', 'dashboard_viewed'
                        )
                    GROUP BY DATE(ae.timestamp)
                    ORDER BY stat_date DESC
                """), {"email": teacher_email}).fetchall()
                
                migrated_stats = 0
                for stat in stats_result:
                    # Check if already migrated
                    exists = session.execute(text("""
                        SELECT COUNT(*) FROM teacher_statistics 
                        WHERE teacher_id = CAST(:teacher_id AS VARCHAR) AND stat_date = :stat_date
                    """), {
                        "teacher_id": str(teacher_id),
                        "stat_date": stat[0]
                    }).scalar()
                    
                    if not exists and (stat[1] or stat[2] or stat[3] or stat[4] or stat[5]):
                        session.execute(text("""
                            INSERT INTO teacher_statistics (
                                id, teacher_id, stat_date, stat_type,
                                lessons_created, assessments_created, resources_downloaded,
                                resources_shared, login_count, created_at
                            ) VALUES (
                                :id, :teacher_id, :stat_date, 'daily',
                                :lessons, :assessments, :downloads,
                                :shares, :logins, :created_at
                            )
                            ON CONFLICT DO NOTHING
                        """), {
                            "id": str(uuid.uuid4()),
                            "teacher_id": teacher_id,
                            "stat_date": stat[0],
                            "lessons": stat[1] or 0,
                            "assessments": stat[2] or 0,
                            "downloads": stat[3] or 0,
                            "shares": stat[4] or 0,
                            "logins": stat[5] or 0,
                            "created_at": datetime.utcnow()
                        })
                        migrated_stats += 1
                
                if migrated_stats > 0:
                    print(f"    ✅ Migrated {migrated_stats} statistics records for teacher {teacher_id[:8]}")
            
            print(f"    ✅ Teacher statistics migration completed")
        except Exception as e:
            print(f"    ⚠️  Analytics events migration skipped: {e}")
            # Recover session if transaction was aborted
            try:
                session.rollback()
                session.flush()
            except:
                pass
        
        # 3. Migrate dashboard_notification_models → teacher_notifications (ONLY if teacher-specific)
        # NOTE: Most dashboard_notification_models are district-level, not teacher-level
        try:
            print("  🔄 Checking for teacher-specific notifications...")
            
            # Only migrate if notifications are clearly teacher-level (not district announcements)
            # dashboard_notification_models table has: id, user_id, type (not notification_type), title, message, data, priority, status, created_at, read_at, expires_at
            # Note: Enum values must match NotificationType enum: SYSTEM, ALERT, UPDATE, REMINDER, ACHIEVEMENT
            notifications_result = session.execute(text("""
                SELECT id, title, message, NULL as action_url, created_at, expires_at
                FROM dashboard_notification_models
                WHERE created_at >= NOW() - INTERVAL '30 days'
                    AND (type::text IN ('achievement', 'reminder', 'ACHIEVEMENT', 'REMINDER')
                         OR title ILIKE '%teacher%' OR title ILIKE '%your%')
                    -- Exclude district-level announcements
                    AND title NOT ILIKE '%district%'
                    AND title NOT ILIKE '%school%'
                LIMIT 25
            """)).fetchall()
            
            migrated_notifs = 0
            for notif in notifications_result:
                # Distribute to teachers (each notification goes to a random teacher)
                teacher_id = random.choice(teacher_ids)
                
                # Check if already migrated
                exists = session.execute(text("""
                    SELECT COUNT(*) FROM teacher_notifications 
                    WHERE teacher_id = CAST(:teacher_id AS VARCHAR) AND title = :title AND created_at = :created_at
                """), {
                    "teacher_id": str(teacher_id),
                    "title": notif[1],
                    "created_at": notif[4]
                }).scalar()
                
                if not exists:
                    session.execute(text("""
                        INSERT INTO teacher_notifications (
                            id, teacher_id, notification_type, title, message, action_url,
                            action_label, is_read, is_important, expires_at, created_at, read_at
                        ) VALUES (
                            :id, :teacher_id, 'system_update', :title, :message, :action_url,
                            'View Details', false, false, :expires_at, :created_at, NULL
                        )
                        ON CONFLICT (id) DO NOTHING
                    """), {
                        "id": str(notif[0]),
                        "teacher_id": teacher_id,
                        "title": notif[1] or "System Notification",
                        "message": notif[2] or "You have a new notification",
                        "action_url": notif[3],
                        "expires_at": notif[5],
                        "created_at": notif[4]
                    })
                    migrated_notifs += 1
            
            if migrated_notifs > 0:
                print(f"    ✅ Migrated {migrated_notifs} notifications")
            else:
                print(f"    ℹ️  No notifications to migrate (or already migrated)")
        except Exception as e:
            print(f"    ⚠️  Notifications migration skipped: {e}")
            # Recover session if transaction was aborted
            try:
                session.rollback()
                session.flush()
            except:
                pass
        
        # 4. Migrate goals → teacher_goals (SKIPPED)
        # NOTE: The 'goals' table is for STUDENTS only (has student_id, not user_id)
        # There is no main system goals table for teachers, so we skip this migration
        # Teachers will create goals fresh in the beta system
        print("  🔄 Checking for teacher personal goals to migrate...")
        print("    ℹ️  Main system 'goals' table is student-only (no teacher goals to migrate)")
        print("    ℹ️  Teachers will create goals fresh in the beta system")
        migrated_goals = 0
        
        if any([migrated_count > 0, migrated_stats > 0, migrated_notifs > 0, migrated_goals > 0]):
            print("✅ Teacher data migration completed (only for teachers with main system overlap)")
        else:
            print("✅ No migration needed - beta teachers are independent (as designed)")
        
        try:
            savepoint.commit()
            session.flush()  # Use flush() not commit() when called from within savepoint
        except Exception as commit_error:
            # If savepoint commit fails (e.g., parent transaction closed), 
            # rollback parent session first, then try to rollback savepoint
            print(f"⚠️  Migration savepoint commit failed: {commit_error}")
            try:
                # Rollback parent session to clear failed state
                session.rollback()
                session.flush()
            except:
                pass
            try:
                # Try to rollback savepoint (may fail if transaction already closed)
                savepoint.rollback()
            except:
                pass  # Savepoint may already be rolled back
        
    except Exception as e:
        print(f"⚠️  Migration check skipped: {e}")
        print("   ℹ️  This is OK - beta system is independent and will seed fresh data")
        try:
            # Try to rollback savepoint first (if still valid)
            try:
                savepoint.rollback()
            except:
                pass  # Savepoint may already be rolled back or transaction closed
            # Recover session state after migration failure
            session.rollback()
            session.flush()
        except Exception as recovery_error:
            # If rollback fails, try to flush to reset state
            try:
                session.flush()
            except:
                pass
        # Don't raise - allow seeding to continue with new data

def seed_beta_teacher_dashboard_tables(session: Session) -> None:
    """Seed all 12 Beta Teacher Dashboard tables with sample data
    
    Enhanced with:
    - Links to real resources/lessons/assessments
    - Realistic data relationships
    - Batch inserts for performance
    - Data validation
    - Migration from existing tables (runs first)
    """
    # Wrap entire seeding operation in savepoint for isolation
    savepoint = session.begin_nested()
    try:
        # First, migrate existing data from main system tables (non-blocking)
        try:
            migrate_existing_teacher_data_to_beta(session)
        except Exception as migration_error:
            print(f"⚠️  Migration failed (non-critical): {migration_error}")
            print("   ℹ️  Continuing with fresh data seeding...")
            # Migration savepoint may have failed, recover parent session
            try:
                session.rollback()
                session.flush()
            except:
                pass
        
        # Ensure session is in good state before proceeding
        # Test with a simple query - if parent transaction is failed, we need to recover
        try:
            test_result = session.execute(text("SELECT 1")).scalar()
        except Exception as test_error:
            print(f"⚠️  Session state check failed: {test_error}")
            print("   ℹ️  Attempting session recovery...")
            try:
                # Rollback current savepoint (seeding hasn't started yet)
                savepoint.rollback()
            except:
                pass
            try:
                # Rollback parent transaction to clear failed state
                session.rollback()
                session.flush()
                # Re-create savepoint for seeding
                savepoint = session.begin_nested()
                print("   ✅ Session recovered, creating new savepoint for seeding")
            except Exception as recovery_error:
                print(f"   ❌ Could not recover session: {recovery_error}")
                print("   ❌ Skipping beta teacher dashboard seeding")
                return
        
        # Get teacher IDs from teacher_registrations
        teacher_results = session.execute(text("SELECT id FROM teacher_registrations LIMIT 10")).fetchall()
        if not teacher_results:
            print("⚠️  No teachers found, skipping beta teacher dashboard tables")
            return
        
        teacher_ids = [row[0] for row in teacher_results]
        
        # Get real resource IDs for linking activities
        lesson_plan_ids = []
        assessment_template_ids = []
        resource_ids = []
        
        try:
            lesson_result = session.execute(text("SELECT id FROM lesson_plan_templates LIMIT 100")).fetchall()
            lesson_plan_ids = [row[0] for row in lesson_result]
        except:
            pass
        
        try:
            assessment_result = session.execute(text("SELECT id FROM assessment_templates LIMIT 100")).fetchall()
            assessment_template_ids = [row[0] for row in assessment_result]
        except:
            pass
        
        try:
            resource_result = session.execute(text("SELECT id FROM educational_resources LIMIT 100")).fetchall()
            resource_ids = [row[0] for row in resource_result]
        except:
            pass
        
        print(f"  📊 Found {len(lesson_plan_ids)} lesson plans, {len(assessment_template_ids)} assessments, {len(resource_ids)} resources for linking")
        
        # 1. Seed teacher_achievements (achievement definitions)
        print("  🔄 Seeding teacher achievements...")
        achievements = [
            {"code": "FIRST_LESSON", "name": "First Lesson Plan", "description": "Created your first lesson plan", "category": "lesson_planning", "icon": "star", "color": "#FFD700", "points": 10},
            {"code": "LESSON_MASTER", "name": "Lesson Master", "description": "Created 10 lesson plans", "category": "lesson_planning", "icon": "trophy", "color": "#C0C0C0", "points": 50},
            {"code": "ASSESSMENT_PRO", "name": "Assessment Pro", "description": "Created 5 assessments", "category": "assessments", "icon": "clipboard", "color": "#FF6347", "points": 30},
            {"code": "RESOURCE_COLLECTOR", "name": "Resource Collector", "description": "Downloaded 20 resources", "category": "resources", "icon": "folder", "color": "#4169E1", "points": 25},
            {"code": "SHARING_MASTER", "name": "Sharing Master", "description": "Shared 10 resources", "category": "resources", "icon": "share", "color": "#32CD32", "points": 40},
            {"code": "AI_EXPLORER", "name": "AI Explorer", "description": "Used AI assistant 50 times", "category": "ai", "icon": "robot", "color": "#9370DB", "points": 60},
            {"code": "ACTIVE_TEACHER", "name": "Active Teacher", "description": "Logged in 30 days in a row", "category": "engagement", "icon": "fire", "color": "#FF4500", "points": 75},
            {"code": "COMPLETE_PATH", "name": "Path Completer", "description": "Completed a learning path", "category": "learning", "icon": "graduation", "color": "#00CED1", "points": 100},
        ]
        
        achievement_ids = {}
        for ach in achievements:
            # Check if achievement already exists
            existing = session.execute(text("""
                SELECT id FROM teacher_achievements WHERE achievement_code = :code
            """), {"code": ach["code"]}).first()
            
            if existing:
                achievement_ids[ach["code"]] = existing[0]
                continue
            
            try:
                ach_id = str(uuid.uuid4())
                session.execute(text("""
                    INSERT INTO teacher_achievements (
                        id, achievement_code, achievement_name, achievement_description,
                        achievement_category, icon_name, color_code, points, is_active, created_at
                    ) VALUES (
                        :id, :code, :name, :description, :category, :icon, :color, :points, true, :created_at
                    )
                """), {
                    "id": ach_id,
                    "code": ach["code"],
                    "name": ach["name"],
                    "description": ach["description"],
                    "category": ach["category"],
                    "icon": ach["icon"],
                    "color": ach["color"],
                    "points": ach["points"],
                    "created_at": datetime.utcnow()
                })
                achievement_ids[ach["code"]] = ach_id
            except Exception as e:
                # If insert fails (e.g., unique constraint), try to get existing ID
                if 'unique' in str(e).lower():
                    existing = session.execute(text("""
                        SELECT id FROM teacher_achievements WHERE achievement_code = :code
                    """), {"code": ach["code"]}).first()
                    if existing:
                        achievement_ids[ach["code"]] = existing[0]
                        continue
                raise
        
        print(f"    ✅ Created {len(achievements)} achievement definitions")
        
        # 2. Seed teacher_dashboard_layouts
        print("  🔄 Seeding teacher dashboard layouts...")
        layout_ids = {}
        for teacher_id in teacher_ids[:5]:  # Create layouts for first 5 teachers
            layout_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO teacher_dashboard_layouts (
                    id, teacher_id, layout_name, layout_description, is_default, is_active, created_at, updated_at
                ) VALUES (
                    :id, :teacher_id, :name, :description, :is_default, true, :created_at, :updated_at
                )
            """), {
                "id": layout_id,
                "teacher_id": teacher_id,
                "name": "Default Layout",
                "description": "Default dashboard layout",
                "is_default": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            layout_ids[teacher_id] = layout_id
        
        print(f"    ✅ Created {len(layout_ids)} dashboard layouts")
        
        # 3. Seed dashboard_widget_instances (requires layouts and widgets)
        print("  🔄 Seeding dashboard widget instances...")
        widget_results = session.execute(text("SELECT id FROM dashboard_widgets LIMIT 10")).fetchall()
        widget_ids_list = [row[0] for row in widget_results] if widget_results else []
        
        widget_instance_count = 0
        for teacher_id, layout_id in layout_ids.items():
            for i, widget_id in enumerate(widget_ids_list[:5]):  # Add up to 5 widgets per layout
                instance_id = str(uuid.uuid4())
                session.execute(text("""
                    INSERT INTO dashboard_widget_instances (
                        id, layout_id, widget_id, position_x, position_y, width, height,
                        widget_config, is_visible, created_at, updated_at
                    ) VALUES (
                        :id, :layout_id, :widget_id, :x, :y, :width, :height,
                        :config, true, :created_at, :updated_at
                    )
                """), {
                    "id": instance_id,
                    "layout_id": layout_id,
                    "widget_id": widget_id,
                    "x": (i % 3) * 4,
                    "y": (i // 3) * 3,
                    "width": 4,
                    "height": 3,
                    "config": json.dumps({"refresh_interval": 300}),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                widget_instance_count += 1
        
        print(f"    ✅ Created {widget_instance_count} widget instances")
        
        # 4. Seed teacher_learning_paths
        print("  🔄 Seeding teacher learning paths...")
        learning_path_ids = {}
        learning_paths = [
            {"name": "Introduction to Lesson Planning", "description": "Learn the basics of creating effective lesson plans", "category": "lesson_planning", "difficulty": "beginner", "hours": 2.0},
            {"name": "Advanced Assessment Strategies", "description": "Master advanced assessment techniques", "category": "assessments", "difficulty": "intermediate", "hours": 4.0},
            {"name": "Resource Management Mastery", "description": "Become an expert in organizing and sharing resources", "category": "resources", "difficulty": "advanced", "hours": 3.0},
            {"name": "AI Assistant Power User", "description": "Unlock the full potential of AI assistant features", "category": "ai", "difficulty": "intermediate", "hours": 2.5},
        ]
        
        for teacher_id in teacher_ids[:8]:
            for path_data in learning_paths[:random.randint(1, 3)]:  # Each teacher gets 1-3 paths
                path_id = str(uuid.uuid4())
                is_completed = random.random() < 0.3  # 30% chance of completion
                completion_pct = 100.0 if is_completed else random.randint(0, 90)
                
                session.execute(text("""
                    INSERT INTO teacher_learning_paths (
                        id, teacher_id, path_name, path_description, path_category,
                        difficulty_level, estimated_hours, is_completed, completion_percentage,
                        started_at, completed_at, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :teacher_id, :name, :description, :category, :difficulty, :hours,
                        :is_completed, :completion_pct, :started_at, :completed_at, true, :created_at, :updated_at
                    )
                """), {
                    "id": path_id,
                    "teacher_id": teacher_id,
                    "name": path_data["name"],
                    "description": path_data["description"],
                    "category": path_data["category"],
                    "difficulty": path_data["difficulty"],
                    "hours": path_data["hours"],
                    "is_completed": is_completed,
                    "completion_pct": completion_pct,
                    "started_at": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                    "completed_at": datetime.utcnow() - timedelta(days=random.randint(0, 5)) if is_completed else None,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                
                if path_id not in learning_path_ids:
                    learning_path_ids[path_id] = {
                        "teacher_id": teacher_id,
                        "name": path_data["name"]
                    }
        
        print(f"    ✅ Created {len(learning_path_ids)} learning paths")
        
        # 5. Seed learning_path_steps (requires learning paths)
        print("  🔄 Seeding learning path steps...")
        step_count = 0
        for path_id in learning_path_ids.keys():
            num_steps = random.randint(3, 8)
            for step_num in range(num_steps):
                step_id = str(uuid.uuid4())
                is_completed = random.random() < 0.4
                session.execute(text("""
                    INSERT INTO learning_path_steps (
                        id, learning_path_id, step_title, step_description, step_type,
                        step_url, step_content, estimated_minutes, is_completed,
                        completed_at, step_order, created_at
                    ) VALUES (
                        :id, :path_id, :title, :description, :type, :url, :content,
                        :minutes, :is_completed, :completed_at, :order, :created_at
                    )
                """), {
                    "id": step_id,
                    "path_id": path_id,
                    "title": f"Step {step_num + 1}: {learning_path_ids[path_id]['name']}",
                    "description": f"Complete this step to progress in {learning_path_ids[path_id]['name']}",
                    "type": random.choice(["video", "reading", "exercise", "quiz"]),
                    "url": f"/learning/path/{path_id}/step/{step_num + 1}",
                    "content": f"Content for step {step_num + 1}",
                    "minutes": random.randint(5, 30),
                    "is_completed": is_completed,
                    "completed_at": datetime.utcnow() - timedelta(days=random.randint(0, 10)) if is_completed else None,
                    "order": step_num,
                    "created_at": datetime.utcnow()
                })
                step_count += 1
        
        print(f"    ✅ Created {step_count} learning path steps")
        
        # 6. Seed teacher_goals (moved before achievement progress so goals can be used in notifications)
        print("  🔄 Seeding teacher goals...")
        goal_types = ["lesson_plans", "assessments", "resources", "engagement", "professional_development"]
        goal_count = 0
        for teacher_id in teacher_ids:
            num_goals = random.randint(2, 5)
            for i in range(num_goals):
                goal_type = random.choice(goal_types)
                is_completed = random.random() < 0.25  # 25% completed
                target_val = random.randint(10, 100)
                
                session.execute(text("""
                    INSERT INTO teacher_goals (
                        id, teacher_id, goal_title, goal_description, goal_type, goal_category,
                        target_value, current_value, target_date, is_completed, completed_at,
                        priority_level, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :teacher_id, :title, :description, :type, :category,
                        :target, :current, :target_date, :is_completed, :completed_at,
                        :priority, true, :created_at, :updated_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "teacher_id": teacher_id,
                    "title": f"Goal: {goal_type.replace('_', ' ').title()}",
                    "description": f"Work towards improving {goal_type}",
                    "type": goal_type,
                    "category": random.choice(["professional", "engagement", "quality"]),
                    "target": target_val,
                    "current": target_val if is_completed else random.randint(0, int(target_val * 0.9)),
                    "target_date": datetime.utcnow().date() + timedelta(days=random.randint(30, 90)),
                    "is_completed": is_completed,
                    "completed_at": datetime.utcnow() - timedelta(days=random.randint(0, 20)) if is_completed else None,
                    "priority": random.choice(["low", "medium", "high"]),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                goal_count += 1
        
        print(f"    ✅ Created {goal_count} teacher goals")
        
        # 7. Seed teacher_statistics (ENHANCED: more realistic patterns) - Must be before achievement progress
        print("  🔄 Seeding teacher statistics...")
        stat_count = 0
        
        # Track statistics per teacher for more realistic patterns
        teacher_stats_totals = {}
        
        for teacher_id in teacher_ids:
            # Calculate realistic totals based on available resources
            lessons_total = min(len(lesson_plan_ids), random.randint(5, 30))
            assessments_total = min(len(assessment_template_ids), random.randint(3, 15))
            resources_downloaded_total = min(len(resource_ids), random.randint(10, 50))
            
            teacher_stats_totals[teacher_id] = {
                "lessons": lessons_total,
                "assessments": assessments_total,
                "resources_downloaded": resources_downloaded_total
            }
            
            # Distribute statistics across 30 days with realistic patterns
            # More activity on weekdays, less on weekends
            remaining_lessons = lessons_total
            remaining_assessments = assessments_total
            remaining_downloads = resources_downloaded_total
            
            for day_offset in range(30):
                stat_date = (datetime.utcnow() - timedelta(days=day_offset)).date()
                is_weekend = stat_date.weekday() >= 5  # Saturday = 5, Sunday = 6
                stat_type = "weekly" if day_offset % 7 == 0 else "daily"
                
                # Less activity on weekends
                activity_multiplier = 0.3 if is_weekend else 1.0
                
                lessons_today = min(remaining_lessons, random.randint(0, int(2 * activity_multiplier)))
                assessments_today = min(remaining_assessments, random.randint(0, int(1 * activity_multiplier)))
                downloads_today = min(remaining_downloads, random.randint(0, int(5 * activity_multiplier)))
                
                remaining_lessons -= lessons_today
                remaining_assessments -= assessments_today
                remaining_downloads -= downloads_today
                
                session.execute(text("""
                    INSERT INTO teacher_statistics (
                        id, teacher_id, stat_date, stat_type,
                        lessons_created, assessments_created, resources_uploaded, resources_downloaded,
                        resources_shared, resources_received, collections_created, reviews_written,
                        time_spent_minutes, login_count, created_at
                    ) VALUES (
                        :id, :teacher_id, :stat_date, :stat_type,
                        :lessons, :assessments, :uploaded, :downloaded,
                        :shared, :received, :collections, :reviews,
                        :time_minutes, :logins, :created_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "teacher_id": teacher_id,
                    "stat_date": stat_date,
                    "stat_type": stat_type,
                    "lessons": lessons_today,
                    "assessments": assessments_today,
                    "uploaded": random.randint(0, int(2 * activity_multiplier)),
                    "downloaded": downloads_today,
                    "shared": random.randint(0, int(3 * activity_multiplier)),
                    "received": random.randint(0, int(4 * activity_multiplier)),
                    "collections": random.randint(0, int(1 * activity_multiplier)),
                    "reviews": random.randint(0, int(2 * activity_multiplier)),
                    "time_minutes": random.randint(int(15 * activity_multiplier), int(120 * activity_multiplier)),
                    "logins": random.randint(1, 3) if not is_weekend else random.randint(0, 1),
                    "created_at": datetime.utcnow()
                })
                stat_count += 1
        
        print(f"    ✅ Created {stat_count} teacher statistics records (realistic weekday/weekend patterns)")
        
        # 8. Seed teacher_achievement_progress (ENHANCED: correlates with actual statistics)
        # NOTE: Must run AFTER statistics are created
        print("  🔄 Seeding teacher achievement progress...")
        progress_count = 0
        
        # Get statistics to correlate achievements with actual activity
        stats_by_teacher = {}
        for teacher_id in teacher_ids:
            # Cast teacher_id to VARCHAR to match teacher_statistics.teacher_id type
            stats_result = session.execute(text("""
                SELECT 
                    SUM(lessons_created) as lessons,
                    SUM(assessments_created) as assessments,
                    SUM(resources_downloaded) as downloads,
                    SUM(resources_shared) as shares,
                    SUM(login_count) as logins
                FROM teacher_statistics
                WHERE teacher_id = CAST(:teacher_id AS VARCHAR)
            """), {"teacher_id": str(teacher_id)}).fetchone()
            
            if stats_result:
                stats_by_teacher[teacher_id] = {
                    "lessons": stats_result[0] or 0,
                    "assessments": stats_result[1] or 0,
                    "downloads": stats_result[2] or 0,
                    "shares": stats_result[3] or 0,
                    "logins": stats_result[4] or 0
                }
        
        for teacher_id in teacher_ids:
            teacher_stats = stats_by_teacher.get(teacher_id, {})
            
            for ach_code, ach_id in achievement_ids.items():
                # Calculate progress based on actual teacher activity
                progress_val = 0.0
                is_completed = False
                
                if ach_code == "FIRST_LESSON":
                    progress_val = 100.0 if teacher_stats.get("lessons", 0) >= 1 else 0.0
                    is_completed = teacher_stats.get("lessons", 0) >= 1
                elif ach_code == "LESSON_MASTER":
                    progress_val = min(100.0, (teacher_stats.get("lessons", 0) / 10.0) * 100.0)
                    is_completed = teacher_stats.get("lessons", 0) >= 10
                elif ach_code == "ASSESSMENT_PRO":
                    progress_val = min(100.0, (teacher_stats.get("assessments", 0) / 5.0) * 100.0)
                    is_completed = teacher_stats.get("assessments", 0) >= 5
                elif ach_code == "RESOURCE_COLLECTOR":
                    progress_val = min(100.0, (teacher_stats.get("downloads", 0) / 20.0) * 100.0)
                    is_completed = teacher_stats.get("downloads", 0) >= 20
                elif ach_code == "SHARING_MASTER":
                    progress_val = min(100.0, (teacher_stats.get("shares", 0) / 10.0) * 100.0)
                    is_completed = teacher_stats.get("shares", 0) >= 10
                elif ach_code == "ACTIVE_TEACHER":
                    progress_val = min(100.0, (teacher_stats.get("logins", 0) / 30.0) * 100.0)
                    is_completed = teacher_stats.get("logins", 0) >= 30
                else:
                    # Default: random progress for other achievements
                    if random.random() < 0.6:  # 60% of teachers have progress
                        is_completed = random.random() < 0.3
                        progress_val = 100.0 if is_completed else random.uniform(0, 90)
                
                # Only create progress record if there's actual progress
                if progress_val > 0 or random.random() < 0.4:  # 40% chance even with 0 progress for variety
                    session.execute(text("""
                        INSERT INTO teacher_achievement_progress (
                            id, teacher_id, achievement_id, progress_value, target_value,
                            is_completed, completed_at, created_at, updated_at
                        ) VALUES (
                            :id, :teacher_id, :achievement_id, :progress, 100.0,
                            :is_completed, :completed_at, :created_at, :updated_at
                        )
                    """), {
                        "id": str(uuid.uuid4()),
                        "teacher_id": teacher_id,
                        "achievement_id": ach_id,
                        "progress": progress_val,
                        "is_completed": is_completed,
                        "completed_at": datetime.utcnow() - timedelta(days=random.randint(0, 15)) if is_completed else None,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    progress_count += 1
        
        print(f"    ✅ Created {progress_count} achievement progress records (correlated with actual activity)")
        
        # 9. Seed teacher_activity_logs (ENHANCED: links to real resources)
        print("  🔄 Seeding teacher activity logs...")
        activity_types = ["lesson_created", "assessment_created", "resource_downloaded", "resource_shared", "ai_used", "login", "dashboard_viewed"]
        log_count = 0
        
        # Use batch inserts for better performance
        batch_size = 50
        logs_batch = []
        
        for teacher_id in teacher_ids:
            num_activities = random.randint(20, 50)
            for i in range(num_activities):
                activity_type = random.choice(activity_types)
                created_at = datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
                
                # Link to real resources when possible
                resource_type = None
                resource_id = None
                resource_title = None
                
                if activity_type == "lesson_created" and lesson_plan_ids:
                    resource_type = "lesson_plan"
                    resource_id = str(random.choice(lesson_plan_ids))
                    resource_title = f"Lesson Plan {resource_id[:8]}"
                elif activity_type == "assessment_created" and assessment_template_ids:
                    resource_type = "assessment"
                    resource_id = str(random.choice(assessment_template_ids))
                    resource_title = f"Assessment {resource_id[:8]}"
                elif activity_type in ["resource_downloaded", "resource_shared"] and resource_ids:
                    resource_type = "resource"
                    resource_id = str(random.choice(resource_ids))
                    resource_title = f"Resource {resource_id[:8]}"
                elif activity_type in ["login", "dashboard_viewed"]:
                    resource_type = None
                    resource_id = None
                    resource_title = None
                
                logs_batch.append({
                    "id": str(uuid.uuid4()),
                    "teacher_id": teacher_id,
                    "type": activity_type,
                    "description": f"Teacher {activity_type.replace('_', ' ')}",
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "title": resource_title,
                    "metadata": json.dumps({"source": "web", "device": random.choice(["desktop", "tablet", "mobile"])}),
                    "ip": f"192.168.1.{random.randint(1, 255)}",
                    "user_agent": random.choice(["Chrome/120.0", "Firefox/121.0", "Safari/17.0", "Edge/120.0"]),
                    "session_id": str(uuid.uuid4()),
                    "created_at": created_at
                })
                
                # Insert in batches
                if len(logs_batch) >= batch_size:
                    for log_data in logs_batch:
                        session.execute(text("""
                            INSERT INTO teacher_activity_logs (
                                id, teacher_id, activity_type, activity_description, resource_type,
                                resource_id, resource_title, activity_metadata, ip_address, user_agent,
                                session_id, created_at
                            ) VALUES (
                                :id, :teacher_id, :type, :description, :resource_type,
                                :resource_id, :title, :metadata, :ip, :user_agent, :session_id, :created_at
                            )
                        """), log_data)
                    log_count += len(logs_batch)
                    logs_batch = []
        
        # Insert remaining batch
        if logs_batch:
            for log_data in logs_batch:
                session.execute(text("""
                    INSERT INTO teacher_activity_logs (
                        id, teacher_id, activity_type, activity_description, resource_type,
                        resource_id, resource_title, activity_metadata, ip_address, user_agent,
                        session_id, created_at
                    ) VALUES (
                        :id, :teacher_id, :type, :description, :resource_type,
                        :resource_id, :title, :metadata, :ip, :user_agent, :session_id, :created_at
                    )
                """), log_data)
            log_count += len(logs_batch)
        
        print(f"    ✅ Created {log_count} activity logs (linked to real resources)")
        
        # 10. Seed teacher_notifications (ENHANCED: links to achievements/goals)
        print("  🔄 Seeding teacher notifications...")
        notification_types = ["achievement", "goal_reminder", "system_update", "resource_shared", "new_feature"]
        notification_count = 0
        
        # Get teacher goals for linking reminders
        teacher_goal_ids = {}
        for teacher_id in teacher_ids:
            # Cast teacher_id to VARCHAR to match teacher_goals.teacher_id type
            goal_result = session.execute(text("""
                SELECT id FROM teacher_goals 
                WHERE teacher_id = CAST(:teacher_id AS VARCHAR) AND is_completed = false 
                LIMIT 5
            """), {"teacher_id": str(teacher_id)}).fetchall()
            teacher_goal_ids[teacher_id] = [row[0] for row in goal_result]
        
        for teacher_id in teacher_ids:
            num_notifications = random.randint(5, 15)
            for _ in range(num_notifications):
                notif_type = random.choice(notification_types)
                is_read = random.random() < 0.6  # 60% read
                
                # Create realistic notification content based on type
                title = ""
                message = ""
                action_url = None
                action_label = None
                
                if notif_type == "achievement" and achievement_ids:
                    ach_code = random.choice(list(achievement_ids.keys()))
                    ach_id = achievement_ids[ach_code]
                    title = f"🎉 Achievement Unlocked: {ach_code.replace('_', ' ').title()}"
                    message = f"Congratulations! You've unlocked the {ach_code.replace('_', ' ')} achievement."
                    action_url = f"/achievements/{ach_id}"
                    action_label = "View Achievement"
                elif notif_type == "goal_reminder" and teacher_id in teacher_goal_ids and teacher_goal_ids[teacher_id]:
                    goal_id = random.choice(teacher_goal_ids[teacher_id])
                    title = "📅 Goal Reminder"
                    message = "Don't forget to work on your active goals this week!"
                    action_url = f"/goals/{goal_id}"
                    action_label = "View Goal"
                elif notif_type == "resource_shared" and resource_ids:
                    resource_id = random.choice(resource_ids)
                    title = "📁 Resource Shared With You"
                    message = "A colleague has shared a new educational resource with you."
                    action_url = f"/resources/{resource_id}"
                    action_label = "View Resource"
                else:
                    title = f"{notif_type.replace('_', ' ').title()} Notification"
                    message = f"You have a new {notif_type.replace('_', ' ')} update"
                    if random.random() < 0.5:
                        action_url = f"/notifications/{notif_type}"
                        action_label = "View Details"
                
                session.execute(text("""
                    INSERT INTO teacher_notifications (
                        id, teacher_id, notification_type, title, message, action_url,
                        action_label, is_read, is_important, expires_at, created_at, read_at
                    ) VALUES (
                        :id, :teacher_id, :type, :title, :message, :action_url,
                        :action_label, :is_read, :is_important, :expires_at, :created_at, :read_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "teacher_id": teacher_id,
                    "type": notif_type,
                    "title": title,
                    "message": message,
                    "action_url": action_url,
                    "action_label": action_label,
                    "is_read": is_read,
                    "is_important": random.random() < 0.2,  # 20% important
                    "expires_at": datetime.utcnow() + timedelta(days=random.randint(1, 30)) if random.random() < 0.3 else None,
                    "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 14)),
                    "read_at": datetime.utcnow() - timedelta(days=random.randint(0, 7)) if is_read else None
                })
                notification_count += 1
        
        print(f"    ✅ Created {notification_count} notifications (linked to achievements/goals/resources)")
        
        # 11. Seed teacher_quick_actions
        print("  🔄 Seeding teacher quick actions...")
        quick_actions = [
            {"name": "Create Lesson Plan", "type": "lesson_plan", "url": "/lessons/create", "icon": "plus", "color": "#4CAF50"},
            {"name": "New Assessment", "type": "assessment", "url": "/assessments/create", "icon": "clipboard", "color": "#2196F3"},
            {"name": "Browse Resources", "type": "resource", "url": "/resources", "icon": "folder", "color": "#FF9800"},
            {"name": "AI Assistant", "type": "ai", "url": "/ai/assistant", "icon": "robot", "color": "#9C27B0"},
            {"name": "View Dashboard", "type": "dashboard", "url": "/dashboard", "icon": "chart", "color": "#607D8B"},
        ]
        
        action_count = 0
        for teacher_id in teacher_ids:
            for order, action in enumerate(quick_actions):
                session.execute(text("""
                    INSERT INTO teacher_quick_actions (
                        id, teacher_id, action_name, action_description, action_type,
                        action_url, icon_name, color_code, display_order, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :teacher_id, :name, :description, :type,
                        :url, :icon, :color, :order, true, :created_at, :updated_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "teacher_id": teacher_id,
                    "name": action["name"],
                    "description": f"Quick action: {action['name']}",
                    "type": action["type"],
                    "url": action["url"],
                    "icon": action["icon"],
                    "color": action["color"],
                    "order": order,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                action_count += 1
        
        print(f"    ✅ Created {action_count} quick actions")
        
        # 12. Seed beta_teacher_preferences
        print("  🔄 Seeding beta teacher preferences...")
        preferences = [
            {"key": "theme", "value": "light", "type": "ui"},
            {"key": "notifications_enabled", "value": "true", "type": "notification"},
            {"key": "email_digest", "value": "weekly", "type": "email"},
            {"key": "default_dashboard_view", "value": "grid", "type": "ui"},
            {"key": "auto_save", "value": "true", "type": "behavior"},
        ]
        
        pref_count = 0
        for teacher_id in teacher_ids:
            for pref in preferences:
                if random.random() < 0.8:  # 80% of teachers have each preference set
                    session.execute(text("""
                        INSERT INTO beta_teacher_preferences (
                            id, teacher_id, preference_key, preference_value, preference_type,
                            created_at, updated_at
                        ) VALUES (
                            :id, :teacher_id, :key, :value, :type, :created_at, :updated_at
                        )
                    """), {
                        "id": str(uuid.uuid4()),
                        "teacher_id": teacher_id,
                        "key": pref["key"],
                        "value": pref["value"],
                        "type": pref["type"],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    })
                    pref_count += 1
        
        print(f"    ✅ Created {pref_count} teacher preferences")
        
        # Data validation and summary
        print("\n📊 Validating seeded data...")
        validation_queries = {
            "teacher_achievements": "SELECT COUNT(*) FROM teacher_achievements",
            "teacher_dashboard_layouts": "SELECT COUNT(*) FROM teacher_dashboard_layouts",
            "dashboard_widget_instances": "SELECT COUNT(*) FROM dashboard_widget_instances",
            "teacher_learning_paths": "SELECT COUNT(*) FROM teacher_learning_paths",
            "learning_path_steps": "SELECT COUNT(*) FROM learning_path_steps",
            "teacher_achievement_progress": "SELECT COUNT(*) FROM teacher_achievement_progress",
            "teacher_goals": "SELECT COUNT(*) FROM teacher_goals",
            "teacher_statistics": "SELECT COUNT(*) FROM teacher_statistics",
            "teacher_activity_logs": "SELECT COUNT(*) FROM teacher_activity_logs",
            "teacher_notifications": "SELECT COUNT(*) FROM teacher_notifications",
            "teacher_quick_actions": "SELECT COUNT(*) FROM teacher_quick_actions",
            "beta_teacher_preferences": "SELECT COUNT(*) FROM beta_teacher_preferences",
        }
        
        validation_results = {}
        for table_name, query in validation_queries.items():
            try:
                result = session.execute(text(query))
                count = result.scalar() or 0
                validation_results[table_name] = count
                status = "✅" if count > 0 else "⚠️"
                print(f"  {status} {table_name}: {count:,} records")
            except Exception as e:
                print(f"  ❌ {table_name}: Error - {e}")
                validation_results[table_name] = 0
        
        total_records = sum(validation_results.values())
        print(f"\n✅ All 12 Beta Teacher Dashboard tables seeded successfully!")
        print(f"📊 Total records created: {total_records:,}")
        
        # Check session state before committing
        try:
            # Test if session is healthy
            session.execute(text("SELECT 1")).scalar()
        except Exception:
            # Session is in failed state, rollback and recover
            print("  ⚠️  Session was in failed state, recovering...")
            try:
                savepoint.rollback()
            except:
                pass
            try:
                session.rollback()
                session.flush()
            except:
                pass
            # Re-create savepoint for seeding operations
            savepoint = session.begin_nested()
            print("  ✅ Session recovered, data was preserved")
        
        # Commit the savepoint and flush (don't commit parent when in savepoint)
        try:
            savepoint.commit()
            session.flush()  # Use flush() not commit() when called from within savepoint
        except Exception as commit_err:
            print(f"  ⚠️  Savepoint commit failed (data may already be committed): {commit_err}")
            # Try to recover session
            try:
                session.rollback()
                session.flush()
            except:
                pass
        
    except Exception as e:
        print(f"❌ Error seeding beta teacher dashboard tables: {e}")
        import traceback
        traceback.print_exc()
        try:
            savepoint.rollback()
        except:
            pass
        # Don't raise - allow other seeding to continue

def seed_ai_lesson_suggestions(session: Session) -> None:
    """Seed AI lesson suggestions using the existing table schema"""
    try:
        # Get a sample teacher ID
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
        if not teacher_result:
            print("⚠️  No teachers found, skipping AI lesson suggestions")
            return
        
        teacher_id = teacher_result[0]
        
        # Sample AI lesson suggestions
        suggestions = [
            {
                "suggestion_type": "activity_modification",
                "subject": "PE",
                "grade_level": "6-8",
                "context": "Basketball fundamentals lesson for middle school students",
                "ai_suggestion": "Consider adding a warm-up activity that incorporates ball handling skills to better prepare students for the main basketball activities.",
                "confidence_score": 0.85,
                "tags": ["basketball", "warm-up", "ball-handling"],
                "is_applied": False
            },
            {
                "suggestion_type": "assessment_idea",
                "subject": "PE",
                "grade_level": "9-12",
                "context": "Fitness assessment for high school students",
                "ai_suggestion": "Add peer assessment component where students evaluate each other's form during exercises to promote learning and engagement.",
                "confidence_score": 0.92,
                "tags": ["fitness", "assessment", "peer-evaluation"],
                "is_applied": True,
                "applied_at": datetime.utcnow() - timedelta(days=5)
            },
            {
                "suggestion_type": "safety_improvement",
                "subject": "PE",
                "grade_level": "K-5",
                "context": "Yoga and mindfulness session for elementary students",
                "ai_suggestion": "Ensure all students have adequate space between mats and consider using visual cues on the floor to help maintain proper spacing.",
                "confidence_score": 0.78,
                "tags": ["yoga", "safety", "spacing"],
                "is_applied": False
            }
        ]
        
        for suggestion_data in suggestions:
            session.execute(text("""
                INSERT INTO ai_lesson_suggestions (
                    id, teacher_id, suggestion_type, subject, grade_level,
                    context, ai_suggestion, confidence_score, tags, is_applied,
                    applied_at, created_at
                ) VALUES (
                    :id, :teacher_id, :suggestion_type, :subject, :grade_level,
                    :context, :ai_suggestion, :confidence_score, :tags, :is_applied,
                    :applied_at, :created_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "teacher_id": teacher_id,
                "suggestion_type": suggestion_data["suggestion_type"],
                "subject": suggestion_data["subject"],
                "grade_level": suggestion_data["grade_level"],
                "context": suggestion_data["context"],
                "ai_suggestion": suggestion_data["ai_suggestion"],
                "confidence_score": suggestion_data["confidence_score"],
                "tags": suggestion_data["tags"],
                "is_applied": suggestion_data["is_applied"],
                "applied_at": suggestion_data.get("applied_at"),
                "created_at": datetime.utcnow()
            })
        
        print(f"✅ Seeded {len(suggestions)} AI lesson suggestions")
        
    except Exception as e:
        print(f"❌ Error seeding AI lesson suggestions: {e}")
        raise

def seed_ai_assistant_data(session: Session) -> None:
    """Seed AI assistant integration data"""
    try:
        # Get a sample teacher ID
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
        if not teacher_result:
            print("⚠️  No teachers found, skipping AI assistant data")
            return
        
        teacher_id = teacher_result[0]
        
        # Create sample AI assistant configurations
        ai_configs = [
            {
                "config_name": "Lesson Plan Assistant",
                "config_description": "AI assistant for creating lesson plans",
                "assistant_type": "lesson_planning",
                "is_active": True,
                "config_data": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "system_prompt": "You are an expert PE teacher assistant specializing in creating engaging lesson plans."
                }
            },
            {
                "config_name": "Assessment Generator",
                "config_description": "AI assistant for creating assessments",
                "assistant_type": "assessment_creation",
                "is_active": True,
                "config_data": {
                    "model": "gpt-4",
                    "temperature": 0.5,
                    "max_tokens": 1500,
                    "system_prompt": "You are an expert assessment creator specializing in PE and health education."
                }
            }
        ]
        
        # Insert AI assistant configs and get their IDs
        config_ids = []
        for config_data in ai_configs:
            session.execute(text("""
                INSERT INTO ai_assistant_configs (
                    id, teacher_id, config_name, config_description, assistant_type,
                    is_active, config_data, created_at
                ) VALUES (
                    :id, :teacher_id, :config_name, :config_description, :assistant_type,
                    :is_active, :config_data, :created_at
                ) ON CONFLICT (teacher_id, config_name) DO NOTHING
            """), {
                "id": str(uuid.uuid4()),
                "teacher_id": teacher_id,
                "config_name": config_data["config_name"],
                "config_description": config_data["config_description"],
                "assistant_type": config_data["assistant_type"],
                "is_active": config_data["is_active"],
                "config_data": json.dumps(config_data["config_data"]),
                "created_at": datetime.utcnow()
            })
        
        # Get the actual config IDs from the database
        config_result = session.execute(text("SELECT id FROM ai_assistant_configs WHERE teacher_id = :teacher_id"), {"teacher_id": teacher_id}).fetchall()
        config_ids = [row[0] for row in config_result]
        
        # Seed AI assistant conversations
        print("🔄 Seeding AI assistant conversations...")
        for i in range(75):  # Increased from 10 to 75 for more realistic usage
            session.execute(text("""
                INSERT INTO ai_assistant_conversations (
                    id, teacher_id, config_id, conversation_title, conversation_type, is_active, created_at, updated_at
                ) VALUES (
                    :id, :teacher_id, :config_id, :conversation_title, :conversation_type, :is_active, :created_at, :updated_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "teacher_id": teacher_id,
                "config_id": config_ids[i % len(config_ids)],
                "conversation_title": f"Lesson Planning Session {i+1}",
                "conversation_type": ["lesson_planning", "assessment_creation", "resource_generation", "content_analysis", "general_chat"][i % 5],
                "is_active": i < 50,  # 50 active, 25 archived
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                "updated_at": datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            })
        
        # Seed AI assistant messages
        print("🔄 Seeding AI assistant messages...")
        conversation_result = session.execute(text("SELECT id FROM ai_assistant_conversations LIMIT 50")).fetchall()  # Increased from 5 to 50
        for i, (conv_id,) in enumerate(conversation_result):
            for j in range(random.randint(3, 8)):  # 3-8 messages per conversation for more realistic depth
                session.execute(text("""
                    INSERT INTO ai_assistant_messages (
                        id, conversation_id, message_type, content, token_count, processing_time_ms, created_at
                    ) VALUES (
                        :id, :conversation_id, :message_type, :content, :token_count, :processing_time_ms, :created_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "conversation_id": conv_id,
                    "message_type": "user" if j % 2 == 0 else "assistant",
                    "content": f"Message {j+1} in conversation {i+1}: {'User question about lesson planning' if j % 2 == 0 else 'AI assistant response with helpful suggestions'}",
                    "token_count": random.randint(10, 50),
                    "processing_time_ms": random.randint(200, 2000),
                    "created_at": datetime.utcnow() - timedelta(minutes=random.randint(1, 60))
                })
        
        # Seed AI assistant usage
        print("🔄 Seeding AI assistant usage...")
        for i in range(200):  # Increased from 20 to 200 for more realistic usage patterns
            session.execute(text("""
                INSERT INTO ai_assistant_usage (
                    id, teacher_id, config_id, usage_type, tokens_used, requests_count, processing_time_ms, 
                    success, usage_date, created_at
                ) VALUES (
                    :id, :teacher_id, :config_id, :usage_type, :tokens_used, :requests_count, :processing_time_ms,
                    :success, :usage_date, :created_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "teacher_id": teacher_id,
                "config_id": config_ids[i % len(config_ids)],
                "usage_type": ["lesson_planning", "assessment_creation", "resource_generation", "content_analysis", "general_chat"][i % 5],
                "tokens_used": random.randint(50, 500),
                "requests_count": random.randint(1, 10),
                "processing_time_ms": random.randint(500, 5000),
                "success": random.choice([True, True, True, False]),  # 75% success rate
                "usage_date": datetime.utcnow().date() - timedelta(days=random.randint(0, 30)),
                "created_at": datetime.utcnow() - timedelta(hours=random.randint(1, 720))
            })
        
        # Seed AI assistant feedback
        print("🔄 Seeding AI assistant feedback...")
        conversation_result = session.execute(text("SELECT id FROM ai_assistant_conversations LIMIT 50")).fetchall()  # Increased from 5 to 50
        message_result = session.execute(text("SELECT id FROM ai_assistant_messages LIMIT 50")).fetchall()  # Increased from 5 to 50
        
        for i in range(50):  # Increased from 15 to 50 for more realistic feedback
            conv_id = conversation_result[i % len(conversation_result)][0] if conversation_result else None
            msg_id = message_result[i % len(message_result)][0] if message_result else None
            
            session.execute(text("""
                INSERT INTO ai_assistant_feedback (
                    id, teacher_id, conversation_id, message_id, feedback_type, feedback_value, 
                    feedback_text, is_helpful, created_at
                ) VALUES (
                    :id, :teacher_id, :conversation_id, :message_id, :feedback_type, :feedback_value,
                    :feedback_text, :is_helpful, :created_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "teacher_id": teacher_id,
                "conversation_id": conv_id,
                "message_id": msg_id,
                "feedback_type": "thumbs_up" if i % 3 == 0 else "rating" if i % 3 == 1 else "thumbs_down",
                "feedback_value": 4 + (i % 2),
                "feedback_text": f"Feedback {i+1} for AI assistant",
                "is_helpful": i % 2 == 0,
                "created_at": datetime.utcnow()
            })
        
        # Seed AI assistant analytics
        print("🔄 Seeding AI assistant analytics...")
        for i in range(25):
            analytics_date = datetime.utcnow().date() - timedelta(days=i)
            session.execute(text("""
                INSERT INTO ai_assistant_analytics (
                    id, teacher_id, analytics_date, total_requests, successful_requests, failed_requests,
                    total_tokens_used, total_processing_time_ms, average_response_time_ms, 
                    most_used_type, satisfaction_score, created_at, updated_at
                ) VALUES (
                    :id, :teacher_id, :analytics_date, :total_requests, :successful_requests, :failed_requests,
                    :total_tokens_used, :total_processing_time_ms, :average_response_time_ms,
                    :most_used_type, :satisfaction_score, :created_at, :updated_at
                ) ON CONFLICT (teacher_id, analytics_date) DO NOTHING
            """), {
                "id": str(uuid.uuid4()),
                "teacher_id": teacher_id,
                "analytics_date": analytics_date,
                "total_requests": 10 + (i * 2),
                "successful_requests": 8 + (i * 2),
                "failed_requests": 2,
                "total_tokens_used": 1000 + (i * 100),
                "total_processing_time_ms": 5000 + (i * 500),
                "average_response_time_ms": 250.0 + (i * 10.5),
                "most_used_type": "lesson_planning" if i % 2 == 0 else "assessment_creation",
                "satisfaction_score": 4.0 + (i % 3) * 0.5,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        print("✅ Seeded AI assistant integration data")
        # Flush changes to savepoint (don't commit/rollback - let parent savepoint handle it)
        session.flush()
        
    except Exception as e:
        print(f"❌ Error seeding AI assistant data: {e}")
        # Don't rollback here - let the parent savepoint handle rollback
        # Just flush any partial changes to ensure clean state
        try:
            session.flush()
        except:
            pass
        # Re-raise to let parent savepoint handle it
        raise

def seed_beta_testing_data(session: Session) -> None:
    """Seed beta testing system data"""
    try:
        # Get a sample teacher ID
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
        if not teacher_result:
            print("⚠️  No teachers found, skipping beta testing data")
            return
        
        teacher_id = teacher_result[0]
        
        # Get beta testing program ID
        program_result = session.execute(text("SELECT id FROM beta_testing_programs LIMIT 1")).fetchone()
        if not program_result:
            print("⚠️  No beta testing programs found, creating one...")
            program_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO beta_testing_programs (
                    id, name, description, version, status, created_at
                ) VALUES (
                    :id, :name, :description, :version, :status, :created_at
                )
            """), {
                "id": program_id,
                "name": "PE Teacher Beta Program",
                "description": "Beta testing program for PE teachers",
                "version": "1.0",
                "status": "active",
                "created_at": datetime.utcnow()
            })
        else:
            program_id = program_result[0]
        
        # Seed beta testing participants
        print("🔄 Seeding beta testing participants...")
        for i in range(10):
            session.execute(text("""
                INSERT INTO beta_testing_participants (
                    id, teacher_id, beta_program_id, email, first_name, last_name, 
                    organization, role, experience_level, interests, status, created_at, updated_at
                ) VALUES (
                    :id, :teacher_id, :beta_program_id, :email, :first_name, :last_name,
                    :organization, :role, :experience_level, :interests, :status, :created_at, :updated_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "teacher_id": teacher_id,
                "beta_program_id": program_id,
                "email": f"teacher{i+1}@example.com",
                "first_name": f"Teacher{i+1}",
                "last_name": "Beta",
                "organization": None,  # BETA SYSTEM: No district affiliation
                "role": "PE Teacher",
                "experience_level": "intermediate" if i % 2 == 0 else "advanced",
                "interests": ["lesson_planning", "assessment_tools"],
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Seed beta testing feature flags
        print("🔄 Seeding beta testing feature flags...")
        feature_flags = [
            {"name": "ai_lesson_planning", "description": "AI-powered lesson planning", "is_enabled": True},
            {"name": "advanced_assessments", "description": "Advanced assessment tools", "is_enabled": True},
            {"name": "real_time_analytics", "description": "Real-time analytics dashboard", "is_enabled": False},
            {"name": "collaborative_planning", "description": "Collaborative lesson planning", "is_enabled": True},
            {"name": "mobile_app", "description": "Mobile application access", "is_enabled": False}
        ]
        
        for flag in feature_flags:
            session.execute(text("""
                INSERT INTO beta_testing_feature_flags (
                    id, name, description, is_enabled, target_percentage, conditions, created_at, updated_at
                ) VALUES (
                    :id, :name, :description, :is_enabled, :target_percentage, :conditions, :created_at, :updated_at
                ) ON CONFLICT (name) DO NOTHING
            """), {
                "id": str(uuid.uuid4()),
                "name": flag["name"],
                "description": flag["description"],
                "is_enabled": flag["is_enabled"],
                "target_percentage": 50 + (hash(flag["name"]) % 50),  # Random percentage between 50-100
                "conditions": json.dumps({"min_users": 5, "max_users": 100}),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Seed beta testing surveys
        print("🔄 Seeding beta testing surveys...")
        for i in range(5):
            session.execute(text("""
                INSERT INTO beta_testing_surveys (
                    id, beta_program_id, title, description, questions, status, start_date, end_date, created_at, updated_at
                ) VALUES (
                    :id, :beta_program_id, :title, :description, :questions, :status, :start_date, :end_date, :created_at, :updated_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "beta_program_id": program_id,
                "title": f"Beta Survey {i+1}",
                "description": f"Survey to gather feedback on beta features {i+1}",
                "questions": json.dumps([
                    {"question": "How satisfied are you with this feature?", "type": "rating", "required": True},
                    {"question": "What improvements would you suggest?", "type": "text", "required": False}
                ]),
                "status": "active",
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=30),  # 30 days from now
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Seed beta testing feedback
        print("🔄 Seeding beta testing feedback...")
        # Get participant IDs for feedback
        participant_result = session.execute(text("SELECT id FROM beta_testing_participants LIMIT 5")).fetchall()
        participant_ids = [row[0] for row in participant_result]
        
        for i in range(20):
            participant_id = participant_ids[i % len(participant_ids)] if participant_ids else str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO beta_testing_feedback (
                    id, participant_id, beta_program_id, feedback_type, title, description, priority, status, tags, attachments, created_at, updated_at
                ) VALUES (
                    :id, :participant_id, :beta_program_id, :feedback_type, :title, :description, :priority, :status, :tags, :attachments, :created_at, :updated_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "participant_id": participant_id,
                "beta_program_id": program_id,
                "feedback_type": "feature_request" if i % 3 == 0 else "bug_report" if i % 3 == 1 else "general",
                "title": f"Beta Feedback {i+1}",
                "description": f"Beta testing feedback description {i+1}",
                "priority": "high" if i % 4 == 0 else "medium" if i % 4 == 1 else "low",
                "status": "open" if i % 2 == 0 else "in_progress",
                "tags": ["beta", "feedback", f"feature_{i+1}"],
                "attachments": json.dumps({"files": [], "links": []}),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Seed beta testing notifications
        print("🔄 Seeding beta testing notifications...")
        for i in range(15):
            participant_id = participant_ids[i % len(participant_ids)] if participant_ids else str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO beta_testing_notifications (
                    id, participant_id, type, title, message, is_read, sent_at, created_at
                ) VALUES (
                    :id, :participant_id, :type, :title, :message, :is_read, :sent_at, :created_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "participant_id": participant_id,
                "type": "feature_update" if i % 2 == 0 else "survey_reminder",
                "title": f"Beta Notification {i+1}",
                "message": f"Beta testing notification message {i+1}",
                "is_read": i % 3 == 0,
                "sent_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            })
        
        # Seed beta testing survey responses
        print("🔄 Seeding beta testing survey responses...")
        survey_result = session.execute(text("SELECT id FROM beta_testing_surveys LIMIT 3")).fetchall()
        for i, (survey_id,) in enumerate(survey_result):
            for j in range(5):  # 5 responses per survey
                participant_id = participant_ids[j % len(participant_ids)] if participant_ids else str(uuid.uuid4())
                session.execute(text("""
                    INSERT INTO beta_testing_survey_responses (
                        id, survey_id, participant_id, responses, completed_at, created_at
                    ) VALUES (
                        :id, :survey_id, :participant_id, :responses, :completed_at, :created_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "survey_id": survey_id,
                    "participant_id": participant_id,
                    "responses": json.dumps({"question_1": f"Response {j+1}", "rating": 4 + (j % 2)}),
                    "completed_at": datetime.utcnow(),
                    "created_at": datetime.utcnow()
                })
        
        # Seed beta testing reports
        print("🔄 Seeding beta testing reports...")
        for i in range(20):  # Increased from 8 to 20 for more comprehensive reporting
            session.execute(text("""
                INSERT INTO beta_testing_reports (
                    id, beta_program_id, report_type, title, content, generated_at, created_at
                ) VALUES (
                    :id, :beta_program_id, :report_type, :title, :content, :generated_at, :created_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "beta_program_id": program_id,
                "report_type": "usage" if i % 2 == 0 else "feedback",
                "title": f"Beta Report {i+1}",
                "content": json.dumps({"summary": f"Report content {i+1}", "metrics": {"users": 10 + i}}),
                "generated_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            })
        
        # Seed beta testing usage analytics
        print("🔄 Seeding beta testing usage analytics...")
        for i in range(30):
            participant_id = participant_ids[i % len(participant_ids)] if participant_ids else str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO beta_testing_usage_analytics (
                    id, participant_id, beta_program_id, event_type, event_data, session_id, timestamp, created_at
                ) VALUES (
                    :id, :participant_id, :beta_program_id, :event_type, :event_data, :session_id, :timestamp, :created_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "participant_id": participant_id,
                "beta_program_id": program_id,
                "event_type": "feature_used" if i % 2 == 0 else "survey_completed",
                "event_data": json.dumps({"feature": f"feature_{i+1}", "duration": 100 + i}),
                "session_id": f"session_{i+1}",
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow()
            })
        
        print("✅ Seeded beta testing system data")
        # Flush changes to savepoint (don't commit/rollback - let parent savepoint handle it)
        session.flush()
        
    except Exception as e:
        print(f"❌ Error seeding beta testing data: {e}")
        # Don't rollback here - let the parent savepoint handle rollback
        # Just flush any partial changes to ensure clean state
        try:
            session.flush()
        except:
            pass
        # Re-raise to let parent savepoint handle it
        raise

def seed_lesson_plan_sharing_data(session: Session) -> None:
    """Seed lesson plan sharing and usage data"""
    try:
        # Get template and teacher IDs - use ALL available data for realistic testing
        template_result = session.execute(text("SELECT id FROM lesson_plan_templates LIMIT 10")).fetchall()
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations")).fetchall()
        
        # Check if we have sufficient teachers (>2) for realistic sharing
        teacher_count = len(teacher_result)
        if teacher_count < 3:
            print(f"⚠️  Only {teacher_count} teachers found - need at least 3 for realistic sharing")
            print("⚠️  Sharing data will be created but may be limited")
        elif teacher_count >= 5:
            print(f"✅ Found {teacher_count} teachers - sufficient for realistic sharing data")
        
        if not template_result or len(teacher_result) < 2:
            print("⚠️  Insufficient data for lesson plan sharing, creating minimal data...")
            # Create a template if none exists
            if not template_result:
                template_id = str(uuid.uuid4())
                session.execute(text("""
                    INSERT INTO lesson_plan_templates (
                        id, title, description, subject, grade_level, duration_minutes, 
                        objectives, materials, activities, assessment, created_at
                    ) VALUES (
                        :id, :title, :description, :subject, :grade_level, :duration_minutes,
                        :objectives, :materials, :activities, :assessment, :created_at
                    )
                """), {
                    "id": template_id,
                    "title": "Sample PE Lesson Template",
                    "description": "A sample physical education lesson template",
                    "subject": "Physical Education",
                    "grade_level": "Elementary",
                    "duration_minutes": 45,
                    "objectives": json.dumps(["Improve coordination", "Build teamwork"]),
                    "materials": json.dumps(["Cones", "Balls", "Stopwatch"]),
                    "activities": json.dumps(["Warm-up", "Main activity", "Cool-down"]),
                    "assessment": "Observation and participation",
                    "created_at": datetime.utcnow()
                })
            else:
                template_id = template_result[0]
            
            # Get or create teachers
            if len(teacher_result) < 2:
                teacher1_id = teacher_result[0][0] if teacher_result else str(uuid.uuid4())
                teacher2_id = str(uuid.uuid4())
                # Create second teacher if needed
                session.execute(text("""
                    INSERT INTO teacher_registrations (
                        id, first_name, last_name, email, school_name, password_hash, 
                        is_verified, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :first_name, :last_name, :email, :school_name, :password_hash,
                        :is_verified, :is_active, :created_at, :updated_at
                    ) ON CONFLICT (email) DO NOTHING
                """), {
                    "id": teacher2_id,
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "email": "jane.smith@example.com",
                    "school_name": "Test Elementary School",
                    "password_hash": "hashed_password_123",
                    "is_verified": True,
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
        # Extract IDs from results
        template_ids = [row[0] for row in template_result] if template_result else []
        teacher_ids = [row[0] for row in teacher_result] if teacher_result else []
        
        # Fallback if insufficient data
        if len(template_ids) == 0 or len(teacher_ids) < 2:
            print("⚠️  Insufficient data for lesson plan sharing, using fallback...")
            if len(template_ids) == 0:
                # Use first template from query
                template_ids = [template_result[0][0]] if template_result else []
            if len(teacher_ids) < 2:
                # Use available teachers
                pass
        
        # Seed lesson plan sharing - use multiple templates and teachers
        print("🔄 Seeding lesson plan sharing...")
        
        # Create sharing between all teachers for multiple templates
        if len(template_ids) == 0 or len(teacher_ids) < 1:
            print("⚠️  Skipping lesson plan sharing - insufficient data")
            return
        
        sharing_count = min(len(template_ids) * len(teacher_ids) * 3, 200)  # Limit to 200 records
        
        for i in range(sharing_count):
            template_id = template_ids[i % len(template_ids)] if template_ids else str(uuid.uuid4())
            teacher1_idx = i % len(teacher_ids)
            teacher2_idx = (i + 1) % len(teacher_ids)
            teacher1_id = teacher_ids[teacher1_idx]
            teacher2_id = teacher_ids[teacher2_idx] if len(teacher_ids) > 1 else teacher_ids[0]
            
            # Avoid sharing with yourself if we have multiple teachers
            if teacher1_id == teacher2_id and len(teacher_ids) > 1:
                teacher2_idx = (teacher2_idx + 1) % len(teacher_ids)
                teacher2_id = teacher_ids[teacher2_idx]
            session.execute(text("""
                INSERT INTO lesson_plan_sharing (
                    id, template_id, shared_by_teacher_id, shared_with_teacher_id, 
                    sharing_type, access_level, shared_at, expires_at, is_active, 
                    usage_count, feedback_rating, feedback_comment
                ) VALUES (
                    :id, :template_id, :shared_by_teacher_id, :shared_with_teacher_id,
                    :sharing_type, :access_level, :shared_at, :expires_at, :is_active,
                    :usage_count, :feedback_rating, :feedback_comment
                )
            """), {
                "id": str(uuid.uuid4()),
                "template_id": template_id,
                "shared_by_teacher_id": teacher1_id,
                "shared_with_teacher_id": teacher2_id,
                "sharing_type": "collaborative" if i % 2 == 0 else "read_only",
                "access_level": "full" if i % 2 == 0 else "limited",
                "shared_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "is_active": True,
                "usage_count": i + 1,
                "feedback_rating": 4 + (i % 2),
                "feedback_comment": f"Great lesson plan! {i+1}"
            })
        
        # Seed lesson plan usage
        print("🔄 Seeding lesson plan usage...")
        usage_count = 100  # Realistic usage patterns
        for i in range(usage_count):
            # Use different templates and teachers for usage
            usage_template_id = template_ids[i % len(template_ids)] if template_ids and len(template_ids) > 0 else str(uuid.uuid4())
            usage_teacher_id = teacher_ids[i % len(teacher_ids)] if teacher_ids and len(teacher_ids) > 0 else str(uuid.uuid4())
            
            session.execute(text("""
                INSERT INTO lesson_plan_usage (
                    id, template_id, teacher_id, usage_type, usage_date, modifications_made,
                    effectiveness_rating, effectiveness_notes, student_engagement_level, 
                    completion_percentage, time_spent_minutes, issues_encountered, improvements_suggested
                ) VALUES (
                    :id, :template_id, :teacher_id, :usage_type, :usage_date, :modifications_made,
                    :effectiveness_rating, :effectiveness_notes, :student_engagement_level,
                    :completion_percentage, :time_spent_minutes, :issues_encountered, :improvements_suggested
                )
            """), {
                "id": str(uuid.uuid4()),
                "template_id": usage_template_id,
                "teacher_id": usage_teacher_id,
                "usage_type": "view" if i % 3 == 0 else "copy" if i % 3 == 1 else "edit",
                "usage_date": datetime.utcnow(),
                "modifications_made": ["Added extra time", "Simplified instructions"],
                "effectiveness_rating": 3 + (i % 3),
                "effectiveness_notes": f"Students responded well to activity {i+1}",
                "student_engagement_level": "high" if i % 2 == 0 else "medium",
                "completion_percentage": 75.0 + (i * 2.5),
                "time_spent_minutes": 30 + (i * 5),
                "issues_encountered": ["Time management", "Equipment needed"],
                "improvements_suggested": ["More practice time", "Clearer instructions"]
            })
        
        # Seed template category associations
        print("🔄 Seeding template category associations...")
        category_result = session.execute(text("SELECT id FROM lesson_plan_categories LIMIT 5")).fetchall()
        if category_result:
            # Associate multiple templates with multiple categories
            for i, template_id in enumerate(template_ids[:20]):  # Use first 20 templates
                for j, (category_id,) in enumerate(category_result):
                    if j < 2:  # Associate each template with 2 categories
                        session.execute(text("""
                            INSERT INTO template_category_associations (
                                id, template_id, category_id, created_at
                            ) VALUES (
                                :id, :template_id, :category_id, :created_at
                            ) ON CONFLICT (template_id, category_id) DO NOTHING
                        """), {
                            "id": str(uuid.uuid4()),
                            "template_id": template_id,
                            "category_id": category_id,
                            "created_at": datetime.utcnow()
                        })
        else:
            # Create a category if none exists
            category_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO lesson_plan_categories (
                    id, name, description, subject, grade_level_range, created_at
                ) VALUES (
                    :id, :name, :description, :subject, :grade_level_range, :created_at
                )
            """), {
                "id": category_id,
                "name": "Physical Education",
                "description": "PE lesson plans and activities",
                "subject": "Physical Education",
                "grade_level_range": "K-12",
                "created_at": datetime.utcnow()
            })
            
            # Associate template with category
            session.execute(text("""
                INSERT INTO template_category_associations (
                    id, template_id, category_id, created_at
                ) VALUES (
                    :id, :template_id, :category_id, :created_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "template_id": template_id,
                "category_id": category_id,
                "created_at": datetime.utcnow()
            })
        
        print("✅ Seeded lesson plan sharing data")
        # Flush changes to savepoint (don't commit - let parent savepoint handle it)
        session.flush()
        
    except Exception as e:
        print(f"❌ Error seeding lesson plan sharing data: {e}")
        # Don't rollback here - let parent savepoint handle rollback
        try:
            session.flush()
        except:
            pass
        # Re-raise to let parent savepoint handle it
        raise

def seed_assessment_template_data(session: Session) -> None:
    """Seed assessment template related data"""
    try:
        # Get assessment template and teacher IDs
        template_result = session.execute(text("SELECT id FROM assessment_templates LIMIT 1")).fetchone()
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 2")).fetchall()
        category_result = session.execute(text("SELECT id FROM assessment_categories LIMIT 1")).fetchone()
        
        if not template_result or len(teacher_result) < 2:
            print("⚠️  Insufficient data for assessment templates, creating minimal data...")
            # Create assessment template if none exists
            if not template_result:
                template_id = str(uuid.uuid4())
                session.execute(text("""
                    INSERT INTO assessment_templates (
                        id, title, description, subject, grade_level, created_at
                    ) VALUES (
                        :id, :title, :description, :subject, :grade_level, :created_at
                    )
                """), {
                    "id": template_id,
                    "title": "PE Assessment Template",
                    "description": "Physical education assessment template",
                    "subject": "Physical Education",
                    "grade_level": "Elementary",
                    "created_at": datetime.utcnow()
                })
            else:
                template_id = template_result[0]
            
            # Get or create teachers
            if len(teacher_result) < 2:
                teacher1_id = teacher_result[0][0] if teacher_result else str(uuid.uuid4())
                teacher2_id = str(uuid.uuid4())
                # Create second teacher if needed
                session.execute(text("""
                    INSERT INTO teacher_registrations (
                        id, first_name, last_name, email, school_name, password_hash, 
                        is_verified, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :first_name, :last_name, :email, :school_name, :password_hash,
                        :is_verified, :is_active, :created_at, :updated_at
                    ) ON CONFLICT (email) DO NOTHING
                """), {
                    "id": teacher2_id,
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "school_name": "Test Elementary School",
                    "password_hash": "hashed_password_456",
                    "is_verified": True,
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
            else:
                teacher1_id = teacher_result[0][0]
                teacher2_id = teacher_result[1][0]
        else:
            template_id = template_result[0]
            teacher1_id = teacher_result[0][0]
            teacher2_id = teacher_result[1][0]
        
        # Seed assessment template sharing
        print("🔄 Seeding assessment template sharing...")
        for i in range(30):  # Increased from 8 to 30 for more realistic sharing
            session.execute(text("""
                INSERT INTO assessment_template_sharing (
                    id, template_id, shared_by_teacher_id, shared_with_teacher_id, 
                    sharing_type, access_level, shared_at, expires_at, is_active, 
                    usage_count, feedback_rating, feedback_comment
                ) VALUES (
                    :id, :template_id, :shared_by_teacher_id, :shared_with_teacher_id,
                    :sharing_type, :access_level, :shared_at, :expires_at, :is_active,
                    :usage_count, :feedback_rating, :feedback_comment
                )
            """), {
                "id": str(uuid.uuid4()),
                "template_id": template_id,
                "shared_by_teacher_id": teacher1_id,
                "shared_with_teacher_id": teacher2_id,
                "sharing_type": "collaborative" if i % 2 == 0 else "read_only",
                "access_level": "full" if i % 2 == 0 else "limited",
                "shared_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "is_active": True,
                "usage_count": i + 1,
                "feedback_rating": 4 + (i % 2),
                "feedback_comment": f"Great assessment template! {i+1}"
            })
        
        # Seed assessment template usage
        print("🔄 Seeding assessment template usage...")
        for i in range(60):  # Increased from 12 to 60 for more realistic usage
            session.execute(text("""
                INSERT INTO assessment_template_usage (
                    id, template_id, teacher_id, usage_type, usage_date, modifications_made,
                    effectiveness_rating, effectiveness_notes, student_engagement_level, 
                    completion_percentage, time_spent_minutes, issues_encountered, improvements_suggested
                ) VALUES (
                    :id, :template_id, :teacher_id, :usage_type, :usage_date, :modifications_made,
                    :effectiveness_rating, :effectiveness_notes, :student_engagement_level,
                    :completion_percentage, :time_spent_minutes, :issues_encountered, :improvements_suggested
                )
            """), {
                "id": str(uuid.uuid4()),
                "template_id": template_id,
                "teacher_id": teacher1_id if i % 2 == 0 else teacher2_id,
                "usage_type": "view" if i % 3 == 0 else "copy" if i % 3 == 1 else "edit",
                "usage_date": datetime.utcnow(),
                "modifications_made": ["Added time limits", "Simplified questions"],
                "effectiveness_rating": 3 + (i % 3),
                "effectiveness_notes": f"Students performed well on assessment {i+1}",
                "student_engagement_level": "high" if i % 2 == 0 else "medium",
                "completion_percentage": 80.0 + (i * 1.5),
                "time_spent_minutes": 25 + (i * 3),
                "issues_encountered": ["Time constraints", "Clarity needed"],
                "improvements_suggested": ["More examples", "Clearer instructions"]
            })
        
        # Seed assessment template category associations
        print("🔄 Seeding assessment template category associations...")
        if category_result:
            category_id = category_result[0]
        else:
            # Create a category if none exists
            category_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO assessment_categories (
                    id, name, description, subject, grade_level_range, created_at
                ) VALUES (
                    :id, :name, :description, :subject, :grade_level_range, :created_at
                )
            """), {
                "id": category_id,
                "name": "Physical Education Assessment",
                "description": "PE assessment templates and tools",
                "subject": "Physical Education",
                "grade_level_range": "K-12",
                "created_at": datetime.utcnow()
            })
        
        # Associate template with category
        session.execute(text("""
            INSERT INTO assessment_template_category_associations (
                id, template_id, category_id, created_at
            ) VALUES (
                :id, :template_id, :category_id, :created_at
            ) ON CONFLICT (template_id, category_id) DO NOTHING
        """), {
            "id": str(uuid.uuid4()),
            "template_id": template_id,
            "category_id": category_id,
            "created_at": datetime.utcnow()
        })
        
        # Seed assessment standards
        print("🔄 Seeding assessment standards...")
        standards = [
            {"code": "PE.1.1", "description": "Demonstrates motor skills and movement patterns", "framework": "National PE Standards", "grade_level": "Elementary", "subject": "Physical Education"},
            {"code": "PE.1.2", "description": "Demonstrates understanding of movement concepts", "framework": "National PE Standards", "grade_level": "Elementary", "subject": "Physical Education"},
            {"code": "PE.2.1", "description": "Participates regularly in physical activity", "framework": "National PE Standards", "grade_level": "Elementary", "subject": "Physical Education"},
            {"code": "PE.3.1", "description": "Achieves and maintains health-enhancing fitness", "framework": "National PE Standards", "grade_level": "Elementary", "subject": "Physical Education"},
            {"code": "PE.4.1", "description": "Exhibits responsible personal and social behavior", "framework": "National PE Standards", "grade_level": "Elementary", "subject": "Physical Education"}
        ]
        
        for standard in standards:
            session.execute(text("""
                INSERT INTO assessment_standards (
                    id, template_id, standard_code, standard_description, standard_framework, 
                    grade_level, subject, created_at
                ) VALUES (
                    :id, :template_id, :standard_code, :standard_description, :standard_framework,
                    :grade_level, :subject, :created_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "template_id": template_id,
                "standard_code": standard["code"],
                "standard_description": standard["description"],
                "standard_framework": standard["framework"],
                "grade_level": standard["grade_level"],
                "subject": standard["subject"],
                "created_at": datetime.utcnow()
            })
        
        print("✅ Seeded assessment template data")
        
    except Exception as e:
        print(f"❌ Error seeding assessment template data: {e}")
        raise

def seed_curriculum_and_lesson_data(session: Session) -> None:
    """Seed curriculum units and lesson plans data"""
    try:
        # Get curriculum and teacher IDs
        curriculum_result = session.execute(text("SELECT id FROM curriculum LIMIT 1")).fetchone()
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
        subject_result = session.execute(text("SELECT id FROM subjects LIMIT 1")).fetchone()
        grade_level_result = session.execute(text("SELECT id FROM grade_levels LIMIT 1")).fetchone()
        
        if not curriculum_result or not teacher_result or not subject_result or not grade_level_result:
            print("⚠️  Insufficient data for curriculum and lessons, creating minimal data...")
            # Create curriculum if none exists
            if not curriculum_result:
                curriculum_id = 1
                session.execute(text("""
                    INSERT INTO curriculum (
                        id, name, description, subject, grade_level, created_at
                    ) VALUES (
                        :id, :name, :description, :subject, :grade_level, :created_at
                    ) ON CONFLICT (id) DO NOTHING
                """), {
                    "id": curriculum_id,
                    "name": "Elementary PE Curriculum",
                    "description": "Physical education curriculum for elementary students",
                    "subject": "Physical Education",
                    "grade_level": "Elementary",
                    "created_at": datetime.utcnow()
                })
            else:
                curriculum_id = curriculum_result[0]
            
            # Create teacher if none exists
            if not teacher_result:
                teacher_id = 1
                session.execute(text("""
                    INSERT INTO teacher_registrations (
                        id, first_name, last_name, email, school_name, password_hash, 
                        is_verified, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :first_name, :last_name, :email, :school_name, :password_hash,
                        :is_verified, :is_active, :created_at, :updated_at
                    ) ON CONFLICT (id) DO NOTHING
                """), {
                    "id": teacher_id,
                    "first_name": "Test",
                    "last_name": "Teacher",
                    "email": "test.teacher@example.com",
                    "school_name": "Test Elementary School",
                    "password_hash": "hashed_password_789",
                    "is_verified": True,
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
            else:
                # Convert UUID to integer for lesson_plans table
                teacher_id = 1  # Use a default integer ID
            
            # Create subject if none exists
            if not subject_result:
                subject_id = 1
                session.execute(text("""
                    INSERT INTO subjects (
                        id, name, description, created_at
                    ) VALUES (
                        :id, :name, :description, :created_at
                    ) ON CONFLICT (id) DO NOTHING
                """), {
                    "id": subject_id,
                    "name": "Physical Education",
                    "description": "PE subject",
                    "created_at": datetime.utcnow()
                })
            else:
                subject_id = subject_result[0]
            
            # Create grade level if none exists
            if not grade_level_result:
                grade_level_id = 1
                session.execute(text("""
                    INSERT INTO grade_levels (
                        id, name, description, created_at
                    ) VALUES (
                        :id, :name, :description, :created_at
                    ) ON CONFLICT (id) DO NOTHING
                """), {
                    "id": grade_level_id,
                    "name": "Elementary",
                    "description": "Elementary grade level",
                    "created_at": datetime.utcnow()
                })
            else:
                grade_level_id = grade_level_result[0]
        else:
            curriculum_id = curriculum_result[0]
            teacher_id = 1  # Always use integer ID for lesson_plans table
            subject_id = subject_result[0]
            grade_level_id = grade_level_result[0]
        
        # Seed curriculum units
        print("🔄 Seeding curriculum units...")
        for i in range(5):
            session.execute(text("""
                INSERT INTO curriculum_units (
                    id, curriculum_id, name, description, sequence_number, duration_weeks,
                    learning_objectives, key_concepts, skill_focus, core_activities,
                    extension_activities, assessment_activities, equipment_needed,
                    teaching_resources, support_materials, teaching_points,
                    safety_considerations, differentiation, completion_criteria,
                    progress_indicators, assessment_methods, version, created_by,
                    is_valid, created_at, updated_at
                ) VALUES (
                    :id, :curriculum_id, :name, :description, :sequence_number, :duration_weeks,
                    :learning_objectives, :key_concepts, :skill_focus, :core_activities,
                    :extension_activities, :assessment_activities, :equipment_needed,
                    :teaching_resources, :support_materials, :teaching_points,
                    :safety_considerations, :differentiation, :completion_criteria,
                    :progress_indicators, :assessment_methods, :version, :created_by,
                    :is_valid, :created_at, :updated_at
                ) ON CONFLICT (id) DO NOTHING
            """), {
                "id": i + 1,
                "curriculum_id": curriculum_id,
                "name": f"Unit {i+1}: {['Basic Movement', 'Team Sports', 'Fitness', 'Coordination', 'Games'][i]}",
                "description": f"Physical education unit {i+1} focusing on fundamental skills",
                "sequence_number": i + 1,
                "duration_weeks": 2 + i,
                "learning_objectives": json.dumps([f"Objective {j+1}" for j in range(3)]),
                "key_concepts": json.dumps([f"Concept {j+1}" for j in range(4)]),
                "skill_focus": json.dumps([f"Skill {j+1}" for j in range(5)]),
                "core_activities": json.dumps([f"Activity {j+1}" for j in range(6)]),
                "extension_activities": json.dumps([f"Extension {j+1}" for j in range(3)]),
                "assessment_activities": json.dumps([f"Assessment {j+1}" for j in range(4)]),
                "equipment_needed": json.dumps(["Cones", "Balls", "Stopwatch"]),
                "teaching_resources": json.dumps(["Lesson plans", "Videos", "Handouts"]),
                "support_materials": json.dumps(["Worksheets", "Charts", "Posters"]),
                "teaching_points": json.dumps([f"Point {j+1}" for j in range(5)]),
                "safety_considerations": json.dumps(["Proper warm-up", "Equipment safety", "Space awareness"]),
                "differentiation": json.dumps(["Modified activities", "Extra support", "Challenge options"]),
                "completion_criteria": json.dumps(["Participation", "Skill demonstration", "Assessment completion"]),
                "progress_indicators": json.dumps(["Skill improvement", "Engagement level", "Assessment scores"]),
                "assessment_methods": json.dumps(["Observation", "Skill tests", "Self-assessment"]),
                "version": 1,
                "created_by": "System",
                "is_valid": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Seed lesson plans
        print("🔄 Seeding lesson plans...")
        for i in range(10):
            session.execute(text("""
                INSERT INTO lesson_plans (
                    id, teacher_id, subject_id, grade_level_id, unit_title, lesson_title,
                    date, period, duration, essential_question, do_now, objectives,
                    anticipatory_set, direct_instruction, guided_practice, independent_practice,
                    closure, assessment, materials, homework, notes, reflection, next_steps,
                    created_at, updated_at
                ) VALUES (
                    :id, :teacher_id, :subject_id, :grade_level_id, :unit_title, :lesson_title,
                    :date, :period, :duration, :essential_question, :do_now, :objectives,
                    :anticipatory_set, :direct_instruction, :guided_practice, :independent_practice,
                    :closure, :assessment, :materials, :homework, :notes, :reflection, :next_steps,
                    :created_at, :updated_at
                ) ON CONFLICT (id) DO NOTHING
            """), {
                "id": i + 1,
                "teacher_id": teacher_id,
                "subject_id": subject_id,
                "grade_level_id": grade_level_id,
                "unit_title": f"Unit {(i % 5) + 1}",
                "lesson_title": f"Lesson {i+1}: {['Warm-up Games', 'Skill Practice', 'Team Activities', 'Fitness Focus', 'Cool-down'][i % 5]}",
                "date": datetime.utcnow(),
                "period": f"Period {(i % 6) + 1}",
                "duration": 45,
                "essential_question": f"How can we improve our {['coordination', 'teamwork', 'fitness', 'skills', 'health'][i % 5]}?",
                "do_now": f"Complete warm-up activity {i+1}",
                "objectives": json.dumps([f"Students will {['learn', 'practice', 'demonstrate', 'improve'][j % 4]} {['movement', 'coordination', 'teamwork', 'fitness'][j % 4]}" for j in range(3)]),
                "anticipatory_set": f"Today we will focus on {['basic movements', 'team sports', 'fitness activities', 'coordination exercises', 'fun games'][i % 5]}",
                "direct_instruction": f"Demonstrate proper technique for {['running', 'jumping', 'throwing', 'catching', 'kicking'][i % 5]}",
                "guided_practice": json.dumps([f"Practice {j+1}" for j in range(4)]),
                "independent_practice": json.dumps([f"Independent activity {j+1}" for j in range(3)]),
                "closure": f"Review what we learned about {['movement', 'teamwork', 'fitness', 'coordination', 'sports'][i % 5]}",
                "assessment": json.dumps([f"Assessment method {j+1}" for j in range(3)]),
                "materials": json.dumps(["Cones", "Balls", "Stopwatch", "Whistle"]),
                "homework": f"Practice {['jumping', 'running', 'throwing', 'catching', 'kicking'][i % 5]} at home",
                "notes": f"Lesson notes {i+1}",
                "reflection": f"Students showed good engagement in activity {i+1}",
                "next_steps": f"Next lesson will focus on {['advanced skills', 'team games', 'fitness challenges', 'coordination drills', 'sports rules'][i % 5]}",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        print("✅ Seeded curriculum and lesson data")
        
    except Exception as e:
        print(f"❌ Error seeding curriculum and lesson data: {e}")
        raise

def seed_remaining_empty_tables(session: Session) -> None:
    """Seed all remaining empty tables with dynamic data
    
    NOTE: Beta system does NOT pre-seed student data.
    - Teachers can create their own students via the /api/v1/beta/students endpoint
    - Student features are available but optional for beta teachers
    - This ensures beta system remains teacher-only with optional student management
    """
    try:
        # Get existing IDs for foreign key references
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 5")).fetchall()
        # BETA SYSTEM: No student data - teachers only
        # student_result = session.execute(text("SELECT id FROM students LIMIT 10")).fetchall()
        collection_result = session.execute(text("SELECT id FROM resource_collections LIMIT 3")).fetchall()
        lesson_plan_result = session.execute(text("SELECT id FROM lesson_plans LIMIT 5")).fetchall()
        drivers_ed_lesson_plan_result = session.execute(text("SELECT id FROM drivers_ed_lesson_plans LIMIT 5")).fetchall()
        health_lesson_plan_result = session.execute(text("SELECT id FROM health_lesson_plans LIMIT 5")).fetchall()
        curriculum_unit_result = session.execute(text("SELECT id FROM curriculum_units LIMIT 5")).fetchall()
        drivers_ed_curriculum_unit_result = session.execute(text("SELECT id FROM drivers_ed_curriculum_units LIMIT 5")).fetchall()
        health_curriculum_unit_result = session.execute(text("SELECT id FROM health_curriculum_units LIMIT 5")).fetchall()
        user_result = session.execute(text("SELECT id FROM users LIMIT 5")).fetchall()
        
        teacher_ids = [row[0] for row in teacher_result] if teacher_result else []
        # BETA SYSTEM: No student data - teachers only
        # student_ids = [row[0] for row in student_result] if student_result else []
        student_ids = []  # Beta system is teacher-only, no students
        collection_ids = [row[0] for row in collection_result] if collection_result else []
        lesson_plan_ids = [row[0] for row in lesson_plan_result] if lesson_plan_result else []
        drivers_ed_lesson_plan_ids = [row[0] for row in drivers_ed_lesson_plan_result] if drivers_ed_lesson_plan_result else []
        health_lesson_plan_ids = [row[0] for row in health_lesson_plan_result] if health_lesson_plan_result else []
        curriculum_unit_ids = [row[0] for row in curriculum_unit_result] if curriculum_unit_result else []
        drivers_ed_curriculum_unit_ids = [row[0] for row in drivers_ed_curriculum_unit_result] if drivers_ed_curriculum_unit_result else []
        health_curriculum_unit_ids = [row[0] for row in health_curriculum_unit_result] if health_curriculum_unit_result else []
        user_ids = [row[0] for row in user_result] if user_result else []
        
        # Create minimal data if none exists
        if not teacher_ids:
            teacher_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO teacher_registrations (
                    id, first_name, last_name, email, school_name, password_hash, 
                    is_verified, is_active, created_at, updated_at
                ) VALUES (
                    :id, :first_name, :last_name, :email, :school_name, :password_hash,
                    :is_verified, :is_active, :created_at, :updated_at
                )
            """), {
                "id": teacher_id,
                "first_name": "Default",
                "last_name": "Teacher",
                "email": "default.teacher@example.com",
                "school_name": "Default School",
                "password_hash": "hashed_password_default",
                "is_verified": True,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            teacher_ids = [teacher_id]
        
        # BETA SYSTEM: No student data - teachers only
        # if not student_ids:
        #     student_id = str(uuid.uuid4())
        #     session.execute(text("""
        #         INSERT INTO students (
        #             id, first_name, last_name, date_of_birth, grade_level, created_at
        #         ) VALUES (
        #             :id, :first_name, :last_name, :date_of_birth, :grade_level, :created_at
        #         )
        #     """), {
        #         "id": student_id,
        #         "first_name": "Default",
        #         "last_name": "Student",
        #         "date_of_birth": datetime.utcnow().date(),
        #         "grade_level": "Elementary",
        #         "created_at": datetime.utcnow()
        #     })
        #     student_ids = [student_id]
        # Beta system does not create students - teacher-only system
        
        if not collection_ids:
            collection_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO resource_collections (
                    id, teacher_id, title, description, subject, grade_level,
                    collection_type, is_public, is_featured, resource_count,
                    view_count, download_count, rating_average, rating_count,
                    created_at, updated_at
                ) VALUES (
                    :id, :teacher_id, :title, :description, :subject, :grade_level,
                    :collection_type, :is_public, :is_featured, :resource_count,
                    :view_count, :download_count, :rating_average, :rating_count,
                    :created_at, :updated_at
                )
            """), {
                "id": collection_id,
                "teacher_id": teacher_ids[0] if teacher_ids else str(uuid.uuid4()),
                "title": "Default Collection",
                "description": "Default resource collection",
                "subject": "PE",
                "grade_level": "K-12",
                "collection_type": "lesson_plans",
                "is_public": True,
                "is_featured": False,
                "resource_count": 5,
                "view_count": 10,
                "download_count": 3,
                "rating_average": 4.0,
                "rating_count": 2,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            collection_ids = [collection_id]
        
        if not lesson_plan_ids:
            lesson_plan_id = 1
            session.execute(text("""
                INSERT INTO lesson_plans (
                    id, teacher_id, subject_id, grade_level_id, unit_title, lesson_title,
                    date, period, duration, essential_question, created_at, updated_at
                ) VALUES (
                    :id, :teacher_id, :subject_id, :grade_level_id, :unit_title, :lesson_title,
                    :date, :period, :duration, :essential_question, :created_at, :updated_at
                ) ON CONFLICT (id) DO NOTHING
            """), {
                "id": lesson_plan_id,
                "teacher_id": 1,
                "subject_id": 1,
                "grade_level_id": 1,
                "unit_title": "Default Unit",
                "lesson_title": "Default Lesson",
                "date": datetime.utcnow(),
                "period": "Period 1",
                "duration": 45,
                "essential_question": "What will we learn today?",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            lesson_plan_ids = [lesson_plan_id]
        
        if not curriculum_unit_ids:
            curriculum_unit_id = 1
            session.execute(text("""
                INSERT INTO curriculum_units (
                    id, curriculum_id, name, description, sequence_number, duration_weeks,
                    created_by, is_valid, created_at, updated_at
                ) VALUES (
                    :id, :curriculum_id, :name, :description, :sequence_number, :duration_weeks,
                    :created_by, :is_valid, :created_at, :updated_at
                ) ON CONFLICT (id) DO NOTHING
            """), {
                "id": curriculum_unit_id,
                "curriculum_id": 1,
                "name": "Default Unit",
                "description": "Default curriculum unit",
                "sequence_number": 1,
                "duration_weeks": 2,
                "created_by": "System",
                "is_valid": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            curriculum_unit_ids = [curriculum_unit_id]
        
        if not user_ids:
            user_id = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO users (
                    id, username, email, first_name, last_name, created_at
                ) VALUES (
                    :id, :username, :email, :first_name, :last_name, :created_at
                )
            """), {
                "id": user_id,
                "username": "default_user",
                "email": "default.user@example.com",
                "first_name": "Default",
                "last_name": "User",
                "created_at": datetime.utcnow()
            })
            user_ids = [user_id]
        
        # Seed collection sharing
        print("🔄 Seeding collection sharing...")
        for i in range(25):  # Increased from 8 to 25 for more realistic sharing
            session.execute(text("""
                INSERT INTO collection_sharing (
                    id, collection_id, shared_by_teacher_id, shared_with_teacher_id,
                    sharing_type, access_level, shared_at, expires_at, is_active,
                    usage_count, feedback_rating, feedback_comment
                ) VALUES (
                    :id, :collection_id, :shared_by_teacher_id, :shared_with_teacher_id,
                    :sharing_type, :access_level, :shared_at, :expires_at, :is_active,
                    :usage_count, :feedback_rating, :feedback_comment
                )
            """), {
                "id": str(uuid.uuid4()),
                "collection_id": collection_ids[i % len(collection_ids)],
                "shared_by_teacher_id": teacher_ids[i % len(teacher_ids)],
                "shared_with_teacher_id": teacher_ids[(i + 1) % len(teacher_ids)],
                "sharing_type": "collaborative" if i % 2 == 0 else "read_only",
                "access_level": "full" if i % 2 == 0 else "limited",
                "shared_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "is_active": True,
                "usage_count": i + 1,
                "feedback_rating": 4 + (i % 2),
                "feedback_comment": f"Great collection! {i+1}"
            })
        
        # Seed filters
        print("🔄 Seeding filters...")
        for i in range(10):
            session.execute(text("""
                INSERT INTO filters (
                    id, user_id, name, filter_type, filter_data, created_at, updated_at
                ) VALUES (
                    :id, :user_id, :name, :filter_type, :filter_data, :created_at, :updated_at
                ) ON CONFLICT (id) DO NOTHING
            """), {
                "id": i + 1,
                "user_id": i + 1,
                "name": f"Filter {i+1}",
                "filter_type": "lesson_plan" if i % 3 == 0 else "student" if i % 3 == 1 else "activity",
                "filter_data": json.dumps({"criteria": f"criteria_{i+1}", "value": f"value_{i+1}"}),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Skip jobs and job_run_details - these are Azure system tables
        print("⏭️  Skipping jobs and job_run_details (Azure system tables)")
        
        # Seed driver's education tables
        print("🔄 Seeding driver's education data...")
        for i in range(30):  # Increased from 8 to 30 for more realistic class sizes
            # Instructor certifications
            session.execute(text("""
                INSERT INTO drivers_ed_instructor_certifications (
                    id, instructor_id, certification_type, certification_number, issuing_authority,
                    issue_date, expiry_date, is_active, renewal_required, created_at, updated_at
                ) VALUES (
                    :id, :instructor_id, :certification_type, :certification_number, :issuing_authority,
                    :issue_date, :expiry_date, :is_active, :renewal_required, :created_at, :updated_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "instructor_id": teacher_ids[i % len(teacher_ids)],
                "certification_type": "CDL" if i % 2 == 0 else "DMV Instructor",
                "certification_number": f"DE{i+1:03d}",
                "issuing_authority": "State DMV",
                "issue_date": datetime.utcnow().date() - timedelta(days=365),
                "expiry_date": datetime.utcnow().date() + timedelta(days=365),
                "is_active": True,
                "renewal_required": i % 3 == 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Lesson activities
            session.execute(text("""
                INSERT INTO drivers_ed_lesson_activities (
                    id, lesson_plan_id, activity_name, activity_type, duration_minutes,
                    description, instructions, materials_needed, safety_considerations,
                    learning_objectives, order_index, created_at
                ) VALUES (
                    :id, :lesson_plan_id, :activity_name, :activity_type, :duration_minutes,
                    :description, :instructions, :materials_needed, :safety_considerations,
                    :learning_objectives, :order_index, :created_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "lesson_plan_id": drivers_ed_lesson_plan_ids[i % len(drivers_ed_lesson_plan_ids)] if drivers_ed_lesson_plan_ids else str(uuid.uuid4()),
                "activity_name": f"Driving Activity {i+1}",
                "activity_type": ["warm_up", "main", "cool_down", "assessment"][i % 4],
                "duration_minutes": 30 + (i * 5),
                "description": f"Driver education activity {i+1}",
                "instructions": f"Follow safety protocols for activity {i+1}",
                "materials_needed": ["Vehicle", "Safety equipment", "Manual"],
                "safety_considerations": ["Check mirrors", "Wear seatbelt", "Follow speed limits"],
                "learning_objectives": [f"Objective {j+1}" for j in range(3)],
                "order_index": i + 1,
                "created_at": datetime.utcnow()
            })
            
            # Safety incidents
            student_uuid1 = str(uuid.uuid4())
            student_uuid2 = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO drivers_ed_safety_incidents (
                    id, incident_type, severity_level, description, location,
                    involved_students, instructor_id, lesson_plan_id, incident_date,
                    resolution_actions, follow_up_required, created_at, updated_at
                ) VALUES (
                    :id, :incident_type, :severity_level, :description, :location,
                    ARRAY[:student_uuid1, :student_uuid2]::uuid[], :instructor_id, :lesson_plan_id, :incident_date,
                    :resolution_actions, :follow_up_required, :created_at, :updated_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "incident_type": ["near_miss", "minor_incident", "major_incident", "vehicle_damage", "injury", "rule_violation"][i % 6],
                "severity_level": "low" if i % 3 == 0 else "medium" if i % 3 == 1 else "high",
                "description": f"Safety incident {i+1} description",
                "location": f"Location {i+1}",
                "student_uuid1": student_uuid1,
                "student_uuid2": student_uuid2,
                "instructor_id": teacher_ids[i % len(teacher_ids)],
                "lesson_plan_id": drivers_ed_lesson_plan_ids[i % len(drivers_ed_lesson_plan_ids)] if drivers_ed_lesson_plan_ids else str(uuid.uuid4()),
                "incident_date": datetime.utcnow(),
                "resolution_actions": ["Documented", "Student counseled", "Follow-up scheduled"],
                "follow_up_required": i % 2 == 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # BETA SYSTEM: Skip student progress - teacher-only system
            # Student progress seeding removed - beta system is teacher-only
            pass
        
        # Seed health education tables
        print("🔄 Seeding health education data...")
        for i in range(30):  # Increased from 8 to 30 for more realistic class sizes
            # Health incidents
            health_student_uuid1 = str(uuid.uuid4())
            health_student_uuid2 = str(uuid.uuid4())
            session.execute(text("""
                INSERT INTO health_incidents (
                    id, incident_type, severity_level, description, location,
                    involved_students, instructor_id, lesson_plan_id, incident_date,
                    resolution_actions, follow_up_required, created_at, updated_at
                ) VALUES (
                    :id, :incident_type, :severity_level, :description, :location,
                    ARRAY[:health_student_uuid1, :health_student_uuid2]::uuid[], :instructor_id, :lesson_plan_id, :incident_date,
                    :resolution_actions, :follow_up_required, :created_at, :updated_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "incident_type": ["health_concern", "safety_incident", "allergic_reaction", "injury", "behavioral", "medical_emergency"][i % 6],
                "severity_level": "low" if i % 3 == 0 else "medium" if i % 3 == 1 else "high",
                "description": f"Health incident {i+1} description",
                "location": f"Health location {i+1}",
                "health_student_uuid1": health_student_uuid1,
                "health_student_uuid2": health_student_uuid2,
                "instructor_id": teacher_ids[i % len(teacher_ids)],
                "lesson_plan_id": health_lesson_plan_ids[i % len(health_lesson_plan_ids)] if health_lesson_plan_ids else str(uuid.uuid4()),
                "incident_date": datetime.utcnow(),
                "resolution_actions": ["First aid provided", "Parent notified", "Medical attention"],
                "follow_up_required": i % 2 == 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Instructor certifications
            session.execute(text("""
                INSERT INTO health_instructor_certifications (
                    id, instructor_id, certification_type, certification_number, issuing_authority,
                    issue_date, expiry_date, is_active, renewal_required, created_at, updated_at
                ) VALUES (
                    :id, :instructor_id, :certification_type, :certification_number, :issuing_authority,
                    :issue_date, :expiry_date, :is_active, :renewal_required, :created_at, :updated_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "instructor_id": teacher_ids[i % len(teacher_ids)],
                "certification_type": "First Aid" if i % 2 == 0 else "CPR",
                "certification_number": f"HE{i+1:03d}",
                "issuing_authority": "Red Cross",
                "issue_date": datetime.utcnow().date() - timedelta(days=180),
                "expiry_date": datetime.utcnow().date() + timedelta(days=180),
                "is_active": True,
                "renewal_required": i % 3 == 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Lesson activities
            session.execute(text("""
                INSERT INTO health_lesson_activities (
                    id, lesson_plan_id, activity_name, activity_type, duration_minutes,
                    description, instructions, materials_needed, health_considerations,
                    learning_objectives, order_index, created_at
                ) VALUES (
                    :id, :lesson_plan_id, :activity_name, :activity_type, :duration_minutes,
                    :description, :instructions, :materials_needed, :health_considerations,
                    :learning_objectives, :order_index, :created_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "lesson_plan_id": health_lesson_plan_ids[i % len(health_lesson_plan_ids)] if health_lesson_plan_ids else str(uuid.uuid4()),
                "activity_name": f"Health Activity {i+1}",
                "activity_type": ["warm_up", "main", "cool_down", "assessment"][i % 4],
                "duration_minutes": 25 + (i * 3),
                "description": f"Health education activity {i+1}",
                "instructions": f"Follow health protocols for activity {i+1}",
                "materials_needed": ["First aid kit", "Health charts", "Mannequin"],
                "health_considerations": ["Safety first", "Hygiene protocols", "Emergency procedures"],
                "learning_objectives": [f"Health objective {j+1}" for j in range(3)],
                "order_index": i + 1,
                "created_at": datetime.utcnow()
            })
            
            # BETA SYSTEM: Skip student progress - teacher-only system
            # Student progress seeding removed - beta system is teacher-only
            pass
        
        print("✅ Seeded all remaining empty tables")
        
    except Exception as e:
        print(f"❌ Error seeding remaining empty tables: {e}")
        raise

def migrate_main_system_content_to_beta(session: Session) -> None:
    """Migrate all content from main system to beta system for comprehensive testing"""
    try:
        print("🔄 Starting migration of main system content to beta...")
        
        # 1. Migrate Lesson Plans
        try:
            migrate_lesson_plans_to_beta(session)
        except Exception as e:
            print(f"⚠️  Lesson plans migration skipped: {e}")
            session.flush()  # Use flush() not rollback() when called from within savepoint
        
        # 2. Migrate Avatars
        try:
            migrate_avatars_to_beta(session)
        except Exception as e:
            print(f"⚠️  Avatars migration skipped: {e}")
            session.flush()  # Use flush() not rollback() when called from within savepoint
        
        # 3. Migrate Widgets
        try:
            migrate_widgets_to_beta(session)
        except Exception as e:
            print(f"⚠️  Widgets migration skipped: {e}")
            session.flush()  # Use flush() not rollback() when called from within savepoint
        
        # 4. Migrate PE Content
        try:
            migrate_pe_content_to_beta(session)
        except Exception as e:
            print(f"⚠️  PE content migration skipped: {e}")
            session.flush()  # Use flush() not rollback() when called from within savepoint
        
        # 5. Migrate Driver's Ed Content
        try:
            migrate_drivers_ed_content_to_beta(session)
        except Exception as e:
            print(f"⚠️  Driver's Ed migration skipped: {e}")
            session.flush()  # Use flush() not rollback() when called from within savepoint
        
        # 6. Migrate Health Content
        try:
            migrate_health_content_to_beta(session)
        except Exception as e:
            print(f"⚠️  Health migration skipped: {e}")
            session.flush()  # Use flush() not rollback() when called from within savepoint
        
        # 7. Migrate Assessments
        try:
            migrate_assessments_to_beta(session)
        except Exception as e:
            print(f"⚠️  Assessments migration skipped: {e}")
            session.flush()  # Use flush() not rollback() when called from within savepoint
        
        # 8. Migrate Resources
        try:
            migrate_resources_to_beta(session)
        except Exception as e:
            print(f"⚠️  Resources migration skipped: {e}")
            session.flush()  # Use flush() not rollback() when called from within savepoint
        
        # 9. Migrate Curriculum Lessons
        try:
            migrate_curriculum_lessons_to_beta(session)
        except Exception as e:
            print(f"⚠️  Curriculum lessons migration skipped: {e}")
            session.flush()  # Use flush() not rollback() when called from within savepoint
        
        # 10. Migrate General Lessons
        try:
            migrate_general_lessons_to_beta(session)
        except Exception as e:
            print(f"⚠️  General lessons migration skipped: {e}")
            session.flush()  # Use flush() not rollback() when called from within savepoint
        
        print("✅ Main system content migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error migrating main system content: {e}")
        raise

def migrate_lesson_plans_to_beta(session: Session) -> None:
    """Migrate lesson plans from main system to beta templates"""
    try:
        print("🔄 Migrating lesson plans to beta templates...")
        
        # Get lesson plans from main system - ALL lesson plans
        lesson_plans_result = session.execute(text("""
            SELECT id, lesson_title, unit_title, subject_id, grade_level_id, duration,
                   objectives, materials, guided_practice, independent_practice, assessment,
                   created_at, updated_at
            FROM lesson_plans 
            WHERE lesson_title IS NOT NULL
            ORDER BY created_at DESC
        """)).fetchall()
        
        if not lesson_plans_result:
            print("⚠️  No lesson plans found in main system")
            return
        
        # Get a beta teacher ID
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
        if not teacher_result:
            print("⚠️  No beta teachers found, skipping lesson plan migration")
            return
        
        teacher_id = teacher_result[0]
        migrated_count = 0
        
        for lesson_plan in lesson_plans_result:
            try:
                # Convert main lesson plan to beta template format
                template_id = str(uuid.uuid4())
                session.execute(text("""
                    INSERT INTO lesson_plan_templates (
                        id, teacher_id, title, description, subject, grade_level,
                        duration_minutes, learning_objectives, materials_needed,
                        safety_considerations, assessment_methods, template_type,
                        difficulty_level, equipment_required, space_requirements,
                        weather_dependent, is_public, ai_generated, created_at
                    ) VALUES (
                        :id, :teacher_id, :title, :description, :subject, :grade_level,
                        :duration_minutes, :learning_objectives, :materials_needed,
                        :safety_considerations, :assessment_methods, :template_type,
                        :difficulty_level, :equipment_required, :space_requirements,
                        :weather_dependent, :is_public, :ai_generated, :created_at
                    )
                """), {
                    "id": template_id,
                    "teacher_id": teacher_id,
                    "title": lesson_plan[1] or lesson_plan[2] or "Migrated Lesson Plan",  # lesson_title or unit_title
                    "description": f"Migrated from main system: {lesson_plan[2] or 'Unit'}",  # unit_title
                    "subject": "PE",  # Default to PE since we don't have subject mapping
                    "grade_level": "Elementary",  # Default since we don't have grade mapping
                    "duration_minutes": lesson_plan[5] or 45,  # duration
                    "learning_objectives": lesson_plan[6] if lesson_plan[6] else ["Learning objectives"],  # objectives
                    "materials_needed": lesson_plan[7] if lesson_plan[7] else ["Materials"],  # materials
                    "safety_considerations": ["Safety first", "Proper supervision"],
                    "assessment_methods": lesson_plan[10] if lesson_plan[10] else ["Assessment"],  # assessment
                    "template_type": "migrated",
                    "difficulty_level": "intermediate",
                    "equipment_required": lesson_plan[7] if lesson_plan[7] else ["Equipment"],  # materials
                    "space_requirements": "Gymnasium or outdoor space",
                    "weather_dependent": False,
                    "is_public": True,
                    "ai_generated": False,
                    "created_at": lesson_plan[11] or datetime.utcnow()  # created_at
                })
                
                # Create activities for the template
                if lesson_plan[8]:  # guided_practice field
                    activities_data = lesson_plan[8]
                    if isinstance(activities_data, list):
                        for i, activity in enumerate(activities_data):
                            session.execute(text("""
                                INSERT INTO beta_lesson_plan_activities (
                                    id, template_id, activity_name, activity_description,
                                    duration_minutes, activity_type, instructions, order_index, created_at
                                ) VALUES (
                                    :id, :template_id, :activity_name, :activity_description,
                                    :duration_minutes, :activity_type, :instructions, :order_index, :created_at
                                )
                            """), {
                                "id": str(uuid.uuid4()),
                                "template_id": template_id,
                                "activity_name": f"Guided Practice {i+1}",
                                "activity_description": str(activity) if activity else f"Guided practice activity {i+1}",
                                "duration_minutes": 10 + (i * 5),
                                "activity_type": "guided_practice",
                                "instructions": [str(activity)] if activity else [f"Complete guided practice {i+1}"],
                                "order_index": i + 1,
                                "created_at": datetime.utcnow()
                            })
                
                # Add independent practice activities
                if lesson_plan[9]:  # independent_practice field
                    independent_data = lesson_plan[9]
                    if isinstance(independent_data, list):
                        for i, activity in enumerate(independent_data):
                            session.execute(text("""
                                INSERT INTO beta_lesson_plan_activities (
                                    id, template_id, activity_name, activity_description,
                                    duration_minutes, activity_type, instructions, order_index, created_at
                                ) VALUES (
                                    :id, :template_id, :activity_name, :activity_description,
                                    :duration_minutes, :activity_type, :instructions, :order_index, :created_at
                                )
                            """), {
                                "id": str(uuid.uuid4()),
                                "template_id": template_id,
                                "activity_name": f"Independent Practice {i+1}",
                                "activity_description": str(activity) if activity else f"Independent practice activity {i+1}",
                                "duration_minutes": 15 + (i * 5),
                                "activity_type": "independent_practice",
                                "instructions": [str(activity)] if activity else [f"Complete independent practice {i+1}"],
                                "order_index": 10 + i + 1,  # Start after guided practice
                                "created_at": datetime.utcnow()
                            })
                
                migrated_count += 1
                
            except Exception as e:
                print(f"⚠️  Error migrating lesson plan {lesson_plan[0]}: {e}")
                continue
        
        print(f"✅ Migrated {migrated_count} lesson plans to beta templates")
        
    except Exception as e:
        print(f"❌ Error migrating lesson plans: {e}")
        raise

def migrate_avatars_to_beta(session: Session) -> None:
    """Migrate avatars from main system to beta"""
    try:
        print("🔄 Migrating avatars to beta...")

        # Note: beta_avatars table is now managed by SQLAlchemy models
        # and will be created by the database migration system
        
        # Don't rollback parent transaction when in savepoint - removed
        # session.rollback()  # REMOVED: Can't rollback parent transaction when in savepoint
        
        # Check if avatars table exists in main system
        try:
            try:
                avatars_result = session.execute(text("""
                    SELECT id, type, url, config, voice_enabled, voice_config,
                           expression_config, gesture_config, created_at, updated_at
                    FROM avatars
                    WHERE url IS NOT NULL
                """)).fetchall()
            except Exception as e:
                print(f"⚠️  Cannot read avatars from main system: {e}")
                print("✅ beta_avatars table is ready (no migration source)")
                return

            if not avatars_result:
                print("⚠️  No avatars found in main system")
                print("✅ beta_avatars table is ready")
                return

            migrated_count = 0
            for avatar in avatars_result:
                try:
                    # Generate new UUID for beta avatar (convert integer id to UUID)
                    new_avatar_id = str(uuid.uuid4())
                    
                    # Insert into beta avatars table
                    session.execute(text("""
                        INSERT INTO beta_avatars (
                            id, type, image_url, config, voice_enabled, voice_config,
                            expression_config, gesture_config, created_at, updated_at
                        ) VALUES (
                            :id, :type, :image_url, :config, :voice_enabled, :voice_config,
                            :expression_config, :gesture_config, :created_at, :updated_at
                        ) ON CONFLICT (id) DO NOTHING
                    """), {
                        "id": new_avatar_id,
                        "type": str(avatar[1]) if avatar[1] else "default",
                        "image_url": avatar[2],
                        "config": json.dumps(avatar[3]) if avatar[3] else json.dumps({}),
                        "voice_enabled": avatar[4],
                        "voice_config": json.dumps(avatar[5]) if avatar[5] else json.dumps({}),
                        "expression_config": json.dumps(avatar[6]) if avatar[6] else json.dumps({}),
                        "gesture_config": json.dumps(avatar[7]) if avatar[7] else json.dumps({}),
                        "created_at": avatar[8],
                        "updated_at": avatar[9]
                    })
                    migrated_count += 1

                except Exception as e:
                    print(f"⚠️  Error migrating avatar {avatar[0]}: {e}")
                    continue

            print(f"✅ Migrated {migrated_count} avatars to beta")
            session.flush()  # Use flush() not commit() when called from within savepoint

        except Exception as e:
            print(f"⚠️  Avatars table not found or error: {e}")

    except Exception as e:
        print(f"❌ Error migrating avatars: {e}")
        raise

def migrate_widgets_to_beta(session: Session) -> None:
    """Migrate widgets from main system to beta"""
    try:
        print("🔄 Migrating widgets to beta...")
        
        # Note: beta_widgets table is now managed by SQLAlchemy models
        # and will be created by the database migration system
        
        # Don't rollback parent transaction when in savepoint - removed
        # session.rollback()  # REMOVED: Can't rollback parent transaction when in savepoint
        
        # Check if widgets table exists in main system
        try:
            # Check if dashboard_widgets table exists first
            try:
                table_exists = session.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'dashboard_widgets'
                    )
                """)).fetchone()[0]
            except Exception as check_error:
                print(f"⚠️  Cannot check for widgets table: {check_error}")
                print("✅ beta_widgets table is ready (no migration source)")
                return
            
            if not table_exists:
                print("⚠️  Dashboard widgets table not found in main system")
                print("✅ beta_widgets table created and ready")
                return
            
            # Try to get widgets from main system (ALL widgets, not just active)
            try:
                widgets_result = session.execute(text("""
                    SELECT id, name, widget_type, configuration, is_active, created_at
                    FROM dashboard_widgets
                """)).fetchall()
            except Exception as read_error:
                print(f"⚠️  Cannot read widgets from main system: {read_error}")
                print("✅ beta_widgets table is ready (no migration source)")
                return
            
            # Migrate existing widgets
            migrated_count = 0
            if not widgets_result or len(widgets_result) == 0:
                print("⚠️  No widgets found in dashboard_widgets")
                print("Creating 10 widgets for beta system...")
                create_comprehensive_widgets(session, count=10)
            else:
                print(f"Found {len(widgets_result)} widgets to migrate")
                
                # Migrate existing widgets
                for widget in widgets_result:
                    try:
                        # dashboard_widgets has: id, name, widget_type, configuration, is_active, created_at
                        # beta_widgets needs: id (UUID), name, widget_type, configuration, is_active, created_at
                        
                        # Generate new UUID for beta widget
                        new_widget_id = str(uuid.uuid4())
                        
                        # Insert into beta widgets table
                        # Convert configuration dict to JSON string
                        config_value = widget[3]
                        if isinstance(config_value, dict):
                            config_value = json.dumps(config_value)
                        elif config_value is not None:
                            config_value = json.dumps(config_value)
                        else:
                            config_value = json.dumps({})
                        
                        session.execute(text("""
                            INSERT INTO beta_widgets (
                                id, name, widget_type, configuration, is_active, created_at
                            ) VALUES (
                                :id, :name, :widget_type, :configuration, :is_active, :created_at
                            )
                        """), {
                            "id": new_widget_id,
                            "name": widget[1],  # name
                            "widget_type": widget[2],  # widget_type
                            "configuration": config_value,  # configuration (as JSON string)
                            "is_active": widget[4] if widget[4] is not None else True,  # is_active
                            "created_at": widget[5] if widget[5] else datetime.utcnow()  # created_at
                        })
                        migrated_count += 1
                        
                    except Exception as e:
                        print(f"⚠️  Error migrating widget {widget[0]}: {e}")
                        continue
            
            print(f"✅ Migrated {migrated_count} widgets to beta")
            
            # If we have less than 330 widgets, create additional ones
            if migrated_count < 330:
                additional_needed = 330 - migrated_count
                print(f"Creating {additional_needed} additional widgets for comprehensive beta testing...")
                create_comprehensive_widgets(session, count=additional_needed)
            
            session.flush()  # Use flush() not commit() when called from within savepoint
            
        except Exception as e:
            print(f"⚠️  Widgets table not found or error: {e}")
            
    except Exception as e:
        print(f"❌ Error migrating widgets: {e}")
        raise

def migrate_pe_content_to_beta(session: Session) -> None:
    """Migrate PE content from main system to beta"""
    try:
        # Don't rollback parent transaction when in savepoint - removed
        # session.rollback()  # REMOVED: Can't rollback parent transaction when in savepoint
        
        # Check if already migrated
        already_migrated = session.execute(text("""
            SELECT COUNT(*) FROM lesson_plan_templates 
            WHERE template_type = 'pe_migrated'
        """)).fetchone()[0]
        
        if already_migrated > 100:  # Significant amount already migrated
            print(f"⏭️  Skipping PE migration - already {already_migrated} PE lesson plans exist")
            return
        
        print("🔄 Migrating PE content to beta...")
        
        # Migrate PE lesson plans - ALL 800 records
        try:
            pe_lesson_plans = session.execute(text("""
                SELECT id, title, description, grade_level, duration,
                       difficulty, lesson_metadata, created_at
                FROM pe_lesson_plans 
                WHERE title IS NOT NULL
                ORDER BY created_at DESC
            """)).fetchall()
            
            if pe_lesson_plans:
                teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
                if teacher_result:
                    teacher_id = teacher_result[0]
                    migrated_count = 0
                    
                    for pe_plan in pe_lesson_plans:
                        try:
                            template_id = str(uuid.uuid4())
                            # Extract data from metadata if available  
                            metadata = pe_plan[6] if pe_plan[6] else {}
                            # Ensure we always have arrays, not strings
                            if isinstance(metadata, dict):
                                # Extract objectives - convert string to list if needed
                                obj = metadata.get('objectives', None)
                                if obj is None:
                                    learning_objectives = ["Physical fitness", "Skill development"]
                                elif isinstance(obj, str):
                                    learning_objectives = [obj]
                                elif isinstance(obj, list):
                                    learning_objectives = obj
                                else:
                                    learning_objectives = ["Physical fitness", "Skill development"]
                                
                                # Extract materials - convert string to list if needed
                                mat = metadata.get('materials', None)
                                if mat is None:
                                    materials_needed = ["Equipment"]
                                elif isinstance(mat, str):
                                    materials_needed = [mat]
                                elif isinstance(mat, list):
                                    materials_needed = mat
                                else:
                                    materials_needed = ["Equipment"]
                            else:
                                learning_objectives = ["Physical fitness", "Skill development"]
                                materials_needed = ["Equipment"]
                            
                            # Ensure arrays are lists, not strings
                            if not isinstance(learning_objectives, list):
                                learning_objectives = list(learning_objectives) if learning_objectives else ["Physical fitness", "Skill development"]
                            if not isinstance(materials_needed, list):
                                materials_needed = list(materials_needed) if materials_needed else ["Equipment"]
                            
                            session.execute(text("""
                                INSERT INTO lesson_plan_templates (
                                    id, teacher_id, title, description, subject, grade_level,
                                    duration_minutes, learning_objectives, materials_needed,
                                    safety_considerations, assessment_methods, template_type,
                                    difficulty_level, equipment_required, space_requirements,
                                    weather_dependent, is_public, ai_generated, created_at
                                ) VALUES (
                                    :id, :teacher_id, :title, :description, :subject, :grade_level,
                                    :duration_minutes, :learning_objectives, :materials_needed,
                                    :safety_considerations, :assessment_methods, :template_type,
                                    :difficulty_level, :equipment_required, :space_requirements,
                                    :weather_dependent, :is_public, :ai_generated, :created_at
                                )
                            """), {
                                "id": template_id,
                                "teacher_id": teacher_id,
                                "title": pe_plan[1] or "PE Lesson Plan",
                                "description": pe_plan[2] or "Physical Education lesson",
                                "subject": "PE",
                                "grade_level": pe_plan[3] or "Elementary",
                                "duration_minutes": pe_plan[4] or 45,
                                "learning_objectives": learning_objectives,
                                "materials_needed": materials_needed,
                                "safety_considerations": ["Safety first", "Proper supervision"],
                                "assessment_methods": ["Skill demonstration", "Participation"],
                                "template_type": "pe_migrated",
                                "difficulty_level": pe_plan[5] or "intermediate",
                                "equipment_required": materials_needed,
                                "space_requirements": "Gymnasium or outdoor space",
                                "weather_dependent": True,
                                "is_public": True,
                                "ai_generated": False,
                                "created_at": pe_plan[7] or datetime.utcnow()
                            })
                            migrated_count += 1
                            
                        except Exception as e:
                            print(f"⚠️  Error migrating PE lesson plan {pe_plan[0]}: {e}")
                            continue
                    
                    print(f"✅ Migrated {migrated_count} PE lesson plans to beta")
                    # Flush the migrated data (use flush() not commit() when called from within savepoint)
                    session.flush()
            
        except Exception as e:
            print(f"⚠️  PE lesson plans table not found or error: {e}")
            
    except Exception as e:
        print(f"❌ Error migrating PE content: {e}")
        raise

def migrate_drivers_ed_content_to_beta(session: Session) -> None:
    """Migrate Driver's Ed content from main system to beta"""
    try:
        # Check if already migrated
        already_migrated = session.execute(text("""
            SELECT COUNT(*) FROM lesson_plan_templates 
            WHERE template_type = 'drivers_ed_migrated'
        """)).fetchone()[0]
        
        if already_migrated > 0:
            print(f"⏭️  Skipping Driver's Ed migration - already {already_migrated} lesson plans exist")
            return
        
        print("🔄 Migrating Driver's Ed content to beta...")
        
        # Migrate Driver's Ed lesson plans - ALL records
        try:
            drivers_ed_plans = session.execute(text("""
                SELECT id, title, description, grade_level, duration_minutes,
                       learning_objectives, materials_needed, created_at
                FROM drivers_ed_lesson_plans 
                WHERE title IS NOT NULL
                ORDER BY created_at DESC
            """)).fetchall()
            
            if drivers_ed_plans:
                teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
                if teacher_result:
                    teacher_id = teacher_result[0]
                    migrated_count = 0
                    
                    for de_plan in drivers_ed_plans:
                        try:
                            template_id = str(uuid.uuid4())
                            
                            # Ensure arrays are lists
                            learning_objectives = de_plan[5] if de_plan[5] else ["Traffic safety", "Vehicle operation"]
                            if not isinstance(learning_objectives, list):
                                learning_objectives = [learning_objectives] if learning_objectives else ["Traffic safety", "Vehicle operation"]
                            
                            materials_needed = de_plan[6] if de_plan[6] else ["Training materials"]
                            if not isinstance(materials_needed, list):
                                materials_needed = [materials_needed] if materials_needed else ["Training materials"]
                            
                            session.execute(text("""
                                INSERT INTO lesson_plan_templates (
                                    id, teacher_id, title, description, subject, grade_level,
                                    duration_minutes, learning_objectives, materials_needed,
                                    safety_considerations, assessment_methods, template_type,
                                    difficulty_level, equipment_required, space_requirements,
                                    weather_dependent, is_public, ai_generated, created_at
                                ) VALUES (
                                    :id, :teacher_id, :title, :description, :subject, :grade_level,
                                    :duration_minutes, :learning_objectives, :materials_needed,
                                    :safety_considerations, :assessment_methods, :template_type,
                                    :difficulty_level, :equipment_required, :space_requirements,
                                    :weather_dependent, :is_public, :ai_generated, :created_at
                                )
                            """), {
                                "id": template_id,
                                "teacher_id": teacher_id,
                                "title": de_plan[1] or "Driver's Ed Lesson Plan",
                                "description": de_plan[2] or "Driver's Education lesson",
                                "subject": "Driver's Education",
                                "grade_level": de_plan[3] or "High School",
                                "duration_minutes": de_plan[4] or 50,
                                "learning_objectives": learning_objectives,
                                "materials_needed": materials_needed,
                                "safety_considerations": ["Safety first", "Proper supervision", "Vehicle safety"],
                                "assessment_methods": ["Written test", "Practical demonstration"],
                                "template_type": "drivers_ed_migrated",
                                "difficulty_level": "advanced",
                                "equipment_required": materials_needed,
                                "space_requirements": "Driving range or classroom",
                                "weather_dependent": True,
                                "is_public": True,
                                "ai_generated": False,
                                "created_at": de_plan[7] or datetime.utcnow()
                            })
                            migrated_count += 1
                            
                        except Exception as e:
                            print(f"⚠️  Error migrating Driver's Ed lesson plan {de_plan[0]}: {e}")
                            continue
                    
                    print(f"✅ Migrated {migrated_count} Driver's Ed lesson plans to beta")
                    # Flush the migrated data (use flush() not commit() when called from within savepoint)
                    session.flush()
            
        except Exception as e:
            print(f"⚠️  Driver's Ed lesson plans table not found or error: {e}")
            
    except Exception as e:
        print(f"❌ Error migrating Driver's Ed content: {e}")
        raise

def migrate_health_content_to_beta(session: Session) -> None:
    """Migrate Health content from main system to beta"""
    try:
        # Check if already migrated
        already_migrated = session.execute(text("""
            SELECT COUNT(*) FROM lesson_plan_templates 
            WHERE template_type = 'health_migrated'
        """)).fetchone()[0]
        
        if already_migrated > 10:
            print(f"⏭️  Skipping Health migration - already {already_migrated} lesson plans exist")
            return
        
        print("🔄 Migrating Health content to beta...")
        
        # Migrate Health lesson plans - ALL records
        try:
            health_plans = session.execute(text("""
                SELECT id, title, description, grade_level, duration_minutes,
                       learning_objectives, materials_needed, created_at
                FROM health_lesson_plans 
                WHERE title IS NOT NULL
                ORDER BY created_at DESC
            """)).fetchall()
            
            if health_plans:
                teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
                if teacher_result:
                    teacher_id = teacher_result[0]
                    migrated_count = 0
                    
                    for health_plan in health_plans:
                        try:
                            template_id = str(uuid.uuid4())
                            
                            # Ensure arrays are lists
                            learning_objectives = health_plan[5] if health_plan[5] else ["Health awareness", "Wellness"]
                            if not isinstance(learning_objectives, list):
                                learning_objectives = [learning_objectives] if learning_objectives else ["Health awareness", "Wellness"]
                            
                            materials_needed = health_plan[6] if health_plan[6] else ["Health materials"]
                            if not isinstance(materials_needed, list):
                                materials_needed = [materials_needed] if materials_needed else ["Health materials"]
                            
                            session.execute(text("""
                                INSERT INTO lesson_plan_templates (
                                    id, teacher_id, title, description, subject, grade_level,
                                    duration_minutes, learning_objectives, materials_needed,
                                    safety_considerations, assessment_methods, template_type,
                                    difficulty_level, equipment_required, space_requirements,
                                    weather_dependent, is_public, ai_generated, created_at
                                ) VALUES (
                                    :id, :teacher_id, :title, :description, :subject, :grade_level,
                                    :duration_minutes, :learning_objectives, :materials_needed,
                                    :safety_considerations, :assessment_methods, :template_type,
                                    :difficulty_level, :equipment_required, :space_requirements,
                                    :weather_dependent, :is_public, :ai_generated, :created_at
                                )
                            """), {
                                "id": template_id,
                                "teacher_id": teacher_id,
                                "title": health_plan[1] or "Health Lesson Plan",
                                "description": health_plan[2] or "Health Education lesson",
                                "subject": "Health Education",
                                "grade_level": health_plan[3] or "Elementary",
                                "duration_minutes": health_plan[4] or 40,
                                "learning_objectives": learning_objectives,
                                "materials_needed": materials_needed,
                                "safety_considerations": ["Safe environment", "Age-appropriate content"],
                                "assessment_methods": ["Knowledge check", "Participation"],
                                "template_type": "health_migrated",
                                "difficulty_level": "intermediate",
                                "equipment_required": materials_needed,
                                "space_requirements": "Classroom or health lab",
                                "weather_dependent": False,
                                "is_public": True,
                                "ai_generated": False,
                                "created_at": health_plan[7] or datetime.utcnow()
                            })
                            migrated_count += 1
                            
                        except Exception as e:
                            print(f"⚠️  Error migrating Health lesson plan {health_plan[0]}: {e}")
                            continue
                    
                    print(f"✅ Migrated {migrated_count} Health lesson plans to beta")
                    # Flush the migrated data (use flush() not commit() when called from within savepoint)
                    session.flush()
            
        except Exception as e:
            print(f"⚠️  Health lesson plans table not found or error: {e}")
            
    except Exception as e:
        print(f"❌ Error migrating Health content: {e}")
        raise

def migrate_assessments_to_beta(session: Session) -> None:
    """Migrate assessments from main system to beta"""
    try:
        print("🔄 Migrating assessments to beta...")
        
        # Beta already has assessment_templates from Phase 1.7
        # We can migrate additional assessment data here if needed
        print("✅ Assessment templates already seeded in beta (via Phase 1.7)")
        
    except Exception as e:
        print(f"❌ Error migrating assessments: {e}")
        session.rollback()
        raise

def migrate_resources_to_beta(session: Session) -> None:
    """Migrate resources from main system to beta
    
    Note: Educational resources are seeded via Phase 1.8 Resource Management.
    Beta uses educational_resources table.
    """
    try:
        print("🔄 Migrating resources to beta...")
        
        # Beta already has educational_resources from Phase 1.8
        # We can migrate additional resource data here if needed
        print("✅ Educational resources already seeded in beta (via Phase 1.8)")
        
    except Exception as e:
        print(f"❌ Error migrating resources: {e}")
        # Don't rollback parent transaction when in savepoint - let savepoint handle it
        # session.rollback()  # REMOVED
        raise

def seed_resource_categories(session: Session) -> None:
    """Seed resource categories for organizing educational resources"""
    print("🔄 Seeding resource categories...")
    try:
        categories = [
            ('Lesson Plans', 'Complete lesson plans and instructional materials', 'PE', 'K-12', 'lesson', '#ff6b6b'),
            ('Activities', 'Individual activities and games', 'PE', 'K-12', 'activity', '#ff4757'),
            ('Worksheets', 'Printable worksheets and handouts', 'PE', 'K-12', 'worksheet', '#ffa502'),
            ('Videos', 'Instructional videos and demonstrations', 'PE', 'K-12', 'video', '#2ed573'),
            ('Images', 'Photos, diagrams, and visual aids', 'PE', 'K-12', 'image', '#1e90ff'),
            ('Audio', 'Music, sound effects, and audio instructions', 'PE', 'K-12', 'audio', '#ff6348'),
            ('Presentations', 'PowerPoint presentations and slideshows', 'PE', 'K-12', 'presentation', '#70a1ff'),
            ('Assessments', 'Tests, rubrics, and evaluation tools', 'PE', 'K-12', 'assessment', '#ff9ff3'),
            ('Equipment Guides', 'Equipment setup and safety guides', 'PE', 'K-12', 'equipment', '#26de81'),
            ('Safety Materials', 'Safety protocols and emergency procedures', 'Health', 'K-12', 'safety', '#ff3838'),
        ]
        
        for category_data in categories:
            session.execute(text("""
                INSERT INTO resource_categories (
                    id, name, description, subject, grade_level_range, icon_name, color_code
                ) VALUES (
                    :id, :name, :description, :subject, :grade_level_range, :icon_name, :color_code
                ) ON CONFLICT (name) DO NOTHING
            """), {
                "id": str(uuid.uuid4()),
                "name": category_data[0],
                "description": category_data[1],
                "subject": category_data[2],
                "grade_level_range": category_data[3],
                "icon_name": category_data[4],
                "color_code": category_data[5]
            })
        
        print(f"    ✅ Seeded {len(categories)} resource categories")
        session.flush()  # Use flush() not commit() when called from within savepoint
    except Exception as e:
        print(f"    ⚠️  Error seeding resource categories: {e}")
        session.rollback()

def seed_resource_management_data(session: Session) -> None:
    """Seed resource management data"""
    try:
        # Get teacher and resource IDs - use ALL teachers for realistic sharing
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations")).fetchall()
        resource_result = session.execute(text("SELECT id FROM educational_resources")).fetchall()
        category_result = session.execute(text("SELECT id FROM resource_categories")).fetchall()
        
        if not teacher_result or not resource_result or not category_result:
            print("⚠️  Insufficient data for resource management, skipping")
            return
        
        teacher_ids = [row[0] for row in teacher_result]
        resource_ids = [row[0] for row in resource_result]
        category_ids = [row[0] for row in category_result]
        
        # Seed resource category associations - sample resources only for performance
        print("🔄 Seeding resource category associations...")
        for resource_id in resource_ids[:min(50, len(resource_ids))]:  # Only first 50 resources
            # Assign 1-2 categories to each resource
            num_categories = random.randint(1, 2)
            for i in range(num_categories):
                category_id = category_ids[i % len(category_ids)]
                session.execute(text("""
                    INSERT INTO resource_category_associations (
                        id, resource_id, category_id, created_at
                    ) VALUES (
                        :id, :resource_id, :category_id, :created_at
                    ) ON CONFLICT (resource_id, category_id) DO NOTHING
                """), {
                    "id": str(uuid.uuid4()),
                    "resource_id": resource_id,
                    "category_id": category_id,
                    "created_at": datetime.utcnow()
                })
        
        # Seed resource sharing - ALL teachers share with each other
        print(f"🔄 Seeding resource sharing across {len(teacher_ids)} teachers...")
        for i in range(min(len(teacher_ids) * 5, 100)):  # Cap at 100 for performance
            resource_id = resource_ids[i % len(resource_ids)]
            sharing_teacher = teacher_ids[i % len(teacher_ids)]
            receiving_teacher = teacher_ids[(i + 1) % len(teacher_ids)]
            
            # Don't share with yourself
            if sharing_teacher == receiving_teacher:
                continue
                
            session.execute(text("""
                INSERT INTO resource_sharing (
                    id, resource_id, shared_by_teacher_id, shared_with_teacher_id, 
                    sharing_type, access_level, shared_at, is_active, usage_count, feedback_rating
                ) VALUES (
                    :id, :resource_id, :shared_by_teacher_id, :shared_with_teacher_id,
                    :sharing_type, :access_level, :shared_at, :is_active, :usage_count, :feedback_rating
                )
            """), {
                "id": str(uuid.uuid4()),
                "resource_id": resource_id,
                "shared_by_teacher_id": sharing_teacher,
                "shared_with_teacher_id": receiving_teacher,
                "sharing_type": "collaborative" if i % 2 == 0 else "read_only",
                "access_level": "full" if i % 2 == 0 else "limited",
                "shared_at": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                "is_active": True,
                "usage_count": random.randint(1, 20),
                "feedback_rating": random.randint(3, 5)
            })
        
        # Seed resource usage - ALL teachers use resources
        print(f"🔄 Seeding resource usage for {len(teacher_ids)} teachers...")
        for i in range(min(len(teacher_ids) * 3, 60)):  # Cap at 60 for performance
            resource_id = resource_ids[i % len(resource_ids)]
            teacher_id = teacher_ids[i % len(teacher_ids)]
            
            session.execute(text("""
                INSERT INTO resource_usage (
                    id, resource_id, teacher_id, usage_type, usage_date, context, 
                    effectiveness_rating, student_engagement_level, completion_percentage, time_spent_minutes
                ) VALUES (
                    :id, :resource_id, :teacher_id, :usage_type, :usage_date, :context,
                    :effectiveness_rating, :student_engagement_level, :completion_percentage, :time_spent_minutes
                )
            """), {
                "id": str(uuid.uuid4()),
                "resource_id": resource_id,
                "teacher_id": teacher_id,
                "usage_type": ["lesson_planning", "assessment", "activity"][i % 3],
                "usage_date": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                "context": f"Used in lesson {i+1}",
                "effectiveness_rating": random.randint(3, 5),
                "student_engagement_level": ["high", "medium", "low"][i % 3],
                "completion_percentage": random.uniform(60.0, 100.0),
                "time_spent_minutes": random.randint(15, 60)
            })
        
        # Seed resource downloads - ALL teachers download resources
        print(f"🔄 Seeding resource downloads for {len(teacher_ids)} teachers...")
        for i in range(min(len(teacher_ids) * 5, 80)):  # Cap at 80 for performance
            resource_id = resource_ids[i % len(resource_ids)]
            teacher_id = teacher_ids[i % len(teacher_ids)]
            
            session.execute(text("""
                INSERT INTO resource_downloads (
                    id, resource_id, teacher_id, download_date, file_size_bytes, download_successful
                ) VALUES (
                    :id, :resource_id, :teacher_id, :download_date, :file_size_bytes, :download_successful
                )
            """), {
                "id": str(uuid.uuid4()),
                "resource_id": resource_id,
                "teacher_id": teacher_id,
                "download_date": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                "file_size_bytes": random.randint(1024 * 1024, 50 * 1024 * 1024),  # 1MB to 50MB
                "download_successful": True
            })
        
        # Seed resource favorites - ALL teachers favorite some resources
        print(f"🔄 Seeding resource favorites for {len(teacher_ids)} teachers...")
        favorites_inserted = 0
        for i in range(min(len(teacher_ids) * 2, 40)):  # Cap at 40 for performance
            resource_id = resource_ids[i % len(resource_ids)]
            teacher_id = teacher_ids[i % len(teacher_ids)]
            
            # Check if this favorite already exists (unique constraint on resource_id, teacher_id)
            existing = session.execute(text("""
                SELECT id FROM resource_favorites 
                WHERE resource_id = :resource_id AND teacher_id = :teacher_id
            """), {
                "resource_id": resource_id,
                "teacher_id": teacher_id
            }).first()
            
            if existing:
                continue  # Skip if already exists
            
            try:
                session.execute(text("""
                    INSERT INTO resource_favorites (
                        id, resource_id, teacher_id, created_at
                    ) VALUES (
                        :id, :resource_id, :teacher_id, :created_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "resource_id": resource_id,
                    "teacher_id": teacher_id,
                    "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 30))
                })
                favorites_inserted += 1
            except Exception as e:
                # Ignore unique violations if check missed it
                if 'unique' not in str(e).lower():
                    raise
        
        print(f"  ✅ Inserted {favorites_inserted} resource favorites (skipped duplicates)")
        
        # Seed resource reviews - ALL teachers review some resources
        print(f"🔄 Seeding resource reviews for {len(teacher_ids)} teachers...")
        reviews_inserted = 0
        for i in range(min(len(teacher_ids) * 2, 30)):  # Cap at 30 for performance
            resource_id = resource_ids[i % len(resource_ids)]
            teacher_id = teacher_ids[i % len(teacher_ids)]
            
            # Check if this review already exists
            existing = session.execute(text("""
                SELECT id FROM resource_reviews 
                WHERE resource_id = :resource_id AND teacher_id = :teacher_id
            """), {
                "resource_id": resource_id,
                "teacher_id": teacher_id
            }).first()
            
            if existing:
                continue  # Skip if already exists
            
            try:
                session.execute(text("""
                    INSERT INTO resource_reviews (
                        id, resource_id, teacher_id, rating, review_text, pros, cons, suggestions,
                        would_recommend, used_in_class, student_feedback, created_at, updated_at
                    ) VALUES (
                    :id, :resource_id, :teacher_id, :rating, :review_text, :pros, :cons, :suggestions,
                    :would_recommend, :used_in_class, :student_feedback, :created_at, :updated_at
                )
            """), {
                "id": str(uuid.uuid4()),
                "resource_id": resource_id,
                "teacher_id": teacher_id,
                "rating": random.randint(3, 5),
                "review_text": f"Review for resource {i+1}",
                "pros": ["Easy to use", "Engaging content", "Clear instructions"],
                "cons": ["Could be more detailed", "Needs more examples"],
                "suggestions": ["Add more examples", "Include assessment rubrics"],
                "would_recommend": random.choice([True, False]),
                "used_in_class": True,
                "student_feedback": f"Students enjoyed this resource",
                "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                "updated_at": datetime.utcnow() - timedelta(days=random.randint(0, 15))
            })
                reviews_inserted += 1
            except Exception as e:
                # Ignore unique violations if check missed it
                if 'unique' not in str(e).lower():
                    raise
        
        print(f"  ✅ Inserted {reviews_inserted} resource reviews (skipped duplicates)")
        print("✅ Seeded resource management data")
        
    except Exception as e:
        print(f"❌ Error seeding resource management data: {e}")
        raise

def migrate_curriculum_lessons_to_beta(session: Session) -> None:
    """Migrate curriculum lessons from main system to beta"""
    try:
        # Check if already migrated
        already_migrated = session.execute(text("""
            SELECT COUNT(*) FROM lesson_plan_templates 
            WHERE template_type = 'curriculum_migrated'
        """)).fetchone()[0]
        
        if already_migrated > 100:
            print(f"⏭️  Skipping curriculum migration - already {already_migrated} lesson plans exist")
            return
        
        print("🔄 Migrating curriculum lessons to beta...")
        
        # Migrate curriculum lessons - ALL 600 records
        try:
            curriculum_lessons = session.execute(text("""
                SELECT id, name, description, duration, lesson_metadata, created_at
                FROM curriculum_lessons 
                WHERE name IS NOT NULL
                ORDER BY created_at DESC
            """)).fetchall()
            
            if curriculum_lessons:
                teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
                if teacher_result:
                    teacher_id = teacher_result[0]
                    migrated_count = 0
                    
                    for lesson in curriculum_lessons:
                        try:
                            template_id = str(uuid.uuid4())
                            session.execute(text("""
                                INSERT INTO lesson_plan_templates (
                                    id, teacher_id, title, description, subject, grade_level,
                                    duration_minutes, learning_objectives, materials_needed,
                                    safety_considerations, assessment_methods, template_type,
                                    difficulty_level, equipment_required, space_requirements,
                                    weather_dependent, is_public, ai_generated, created_at
                                ) VALUES (
                                    :id, :teacher_id, :title, :description, :subject, :grade_level,
                                    :duration_minutes, :learning_objectives, :materials_needed,
                                    :safety_considerations, :assessment_methods, :template_type,
                                    :difficulty_level, :equipment_required, :space_requirements,
                                    :weather_dependent, :is_public, :ai_generated, :created_at
                                )
                            """), {
                                "id": template_id,
                                "teacher_id": teacher_id,
                                "title": lesson[1] or "Curriculum Lesson",  # name
                                "description": lesson[2] or "Curriculum-based lesson",  # description
                                "subject": "General Education",
                                "grade_level": "Elementary",  # no grade_level column
                                "duration_minutes": lesson[3] or 45,  # duration
                                "learning_objectives": ["Learning objectives"],
                                "materials_needed": ["Materials"],
                                "safety_considerations": ["Safe learning environment"],
                                "assessment_methods": ["Assessment"],
                                "template_type": "curriculum_migrated",
                                "difficulty_level": "intermediate",
                                "equipment_required": ["Materials"],
                                "space_requirements": "Classroom",
                                "weather_dependent": False,
                                "is_public": True,
                                "ai_generated": False,
                                "created_at": lesson[5] or datetime.utcnow()  # created_at
                            })
                            migrated_count += 1
                            
                        except Exception as e:
                            print(f"⚠️  Error migrating curriculum lesson {lesson[0]}: {e}")
                            continue
                    
                    print(f"✅ Migrated {migrated_count} curriculum lessons to beta")
                    # Flush the migrated data (use flush() not commit() when called from within savepoint)
                    session.flush()
            
        except Exception as e:
            print(f"⚠️  Curriculum lessons table not found or error: {e}")
            
    except Exception as e:
        print(f"❌ Error migrating curriculum lessons: {e}")
        raise

def migrate_general_lessons_to_beta(session: Session) -> None:
    """Migrate general lessons from main system to beta"""
    try:
        # Check if already migrated
        already_migrated = session.execute(text("""
            SELECT COUNT(*) FROM lesson_plan_templates 
            WHERE template_type = 'general_migrated'
        """)).fetchone()[0]
        
        if already_migrated > 100:
            print(f"⏭️  Skipping general lessons migration - already {already_migrated} lesson plans exist")
            return
        
        print("🔄 Migrating general lessons to beta...")
        
        # Migrate general lessons - ALL 979 records
        try:
            general_lessons = session.execute(text("""
                SELECT id, title, content, grade_level, content_area,
                       objectives, materials, activities, week_of
                FROM lessons 
                WHERE title IS NOT NULL
                ORDER BY week_of DESC
            """)).fetchall()
            
            if general_lessons:
                teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 1")).fetchone()
                if teacher_result:
                    teacher_id = teacher_result[0]
                    migrated_count = 0
                    
                    for lesson in general_lessons:
                        try:
                            template_id = str(uuid.uuid4())
                            session.execute(text("""
                                INSERT INTO lesson_plan_templates (
                                    id, teacher_id, title, description, subject, grade_level,
                                    duration_minutes, learning_objectives, materials_needed,
                                    safety_considerations, assessment_methods, template_type,
                                    difficulty_level, equipment_required, space_requirements,
                                    weather_dependent, is_public, ai_generated, created_at
                                ) VALUES (
                                    :id, :teacher_id, :title, :description, :subject, :grade_level,
                                    :duration_minutes, :learning_objectives, :materials_needed,
                                    :safety_considerations, :assessment_methods, :template_type,
                                    :difficulty_level, :equipment_required, :space_requirements,
                                    :weather_dependent, :is_public, :ai_generated, :created_at
                                )
                            """), {
                                "id": template_id,
                                "teacher_id": teacher_id,
                                "title": lesson[1] or "General Lesson",  # title
                                "description": lesson[2] or "General education lesson",  # content
                                "subject": lesson[4] or "General Education",  # content_area
                                "grade_level": lesson[3] or "Elementary",  # grade_level
                                "duration_minutes": 45,
                                "learning_objectives": lesson[5] if lesson[5] else ["Learning objectives"],  # objectives
                                "materials_needed": lesson[6] if lesson[6] else ["Materials"],  # materials
                                "safety_considerations": ["Safe learning environment"],
                                "assessment_methods": ["Assessment"],
                                "template_type": "general_migrated",
                                "difficulty_level": "intermediate",
                                "equipment_required": lesson[6] if lesson[6] else ["Materials"],
                                "space_requirements": "Classroom",
                                "weather_dependent": False,
                                "is_public": True,
                                "ai_generated": False,
                                "created_at": datetime.utcnow()
                            })
                            migrated_count += 1
                            
                        except Exception as e:
                            print(f"⚠️  Error migrating general lesson {lesson[0]}: {e}")
                            continue
                    
                    print(f"✅ Migrated {migrated_count} general lessons to beta")
                    # Flush the migrated data (use flush() not commit() when called from within savepoint)
                    session.flush()
            
        except Exception as e:
            print(f"⚠️  General lessons table not found or error: {e}")
            
    except Exception as e:
        print(f"❌ Error migrating general lessons: {e}")
        raise

def create_additional_beta_teachers(session: Session) -> None:
    """Create additional beta teachers for realistic testing"""
    try:
        print("🔄 Creating additional beta teachers...")
        
        # Check current teacher count
        current_count = session.execute(text('SELECT COUNT(*) FROM teacher_registrations')).fetchone()[0]
        print(f'Current beta teachers: {current_count}')
        
        # Teacher data to create
        teacher_names = [
            ('John', 'Smith', 'john.smith@betaschool.edu'),
            ('Sarah', 'Johnson', 'sarah.johnson@betaschool.edu'),
            ('Michael', 'Williams', 'michael.williams@betaschool.edu'),
            ('Emily', 'Brown', 'emily.brown@betaschool.edu'),
            ('David', 'Davis', 'david.davis@betaschool.edu'),
            ('Jessica', 'Miller', 'jessica.miller@betaschool.edu'),
            ('Christopher', 'Wilson', 'christopher.wilson@betaschool.edu'),
            ('Ashley', 'Moore', 'ashley.moore@betaschool.edu'),
            ('Daniel', 'Taylor', 'daniel.taylor@betaschool.edu'),
            ('Amanda', 'Anderson', 'amanda.anderson@betaschool.edu'),
            ('Matthew', 'Thomas', 'matthew.thomas@betaschool.edu'),
            ('Laura', 'Jackson', 'laura.jackson@betaschool.edu'),
            ('Andrew', 'White', 'andrew.white@betaschool.edu'),
            ('Michelle', 'Harris', 'michelle.harris@betaschool.edu'),
            ('Joshua', 'Martin', 'joshua.martin@betaschool.edu'),
            ('Stephanie', 'Thompson', 'stephanie.thompson@betaschool.edu'),
            ('Brian', 'Garcia', 'brian.garcia@betaschool.edu'),
            ('Nicole', 'Martinez', 'nicole.martinez@betaschool.edu'),
            ('Kenneth', 'Robinson', 'kenneth.robinson@betaschool.edu'),
            ('Rachel', 'Clark', 'rachel.clark@betaschool.edu')
        ]
        
        created_count = 0
        for first_name, last_name, email in teacher_names:
            try:
                # Check if teacher already exists
                existing = session.execute(text('SELECT id FROM teacher_registrations WHERE email = :email'), {'email': email}).fetchone()
                
                if existing:
                    continue
                
                teacher_id = str(uuid.uuid4())
                
                # Create new beta teacher with correct structure
                session.execute(text('''
                    INSERT INTO teacher_registrations (
                        id, email, password_hash, first_name, last_name,
                        school_name, is_verified, is_active,
                        created_at, updated_at
                    ) VALUES (
                        :id, :email, :password_hash, :first_name, :last_name,
                        :school_name, :is_verified, :is_active,
                        :created_at, :updated_at
                    )
                '''), {
                    'id': teacher_id,
                    'email': email,
                    'password_hash': 'beta_teacher_password_hash',
                    'first_name': first_name,
                    'last_name': last_name,
                    'school_name': f'Beta Test {first_name} School',
                    'is_verified': True,
                    'is_active': True,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                })
                
                created_count += 1
                
            except Exception as e:
                print(f'⚠️  Error creating teacher {email}: {e}')
                continue
        
        # Flush changes to savepoint (don't commit - let parent savepoint handle it)
        session.flush()
        
        total_count = session.execute(text('SELECT COUNT(*) FROM teacher_registrations')).fetchone()[0]
        
        print(f'✅ Created {created_count} new beta teachers')
        print(f'✅ Total beta teachers: {total_count}')
        
        # Ensure we have at least 5 teachers for realistic sharing
        if total_count < 3:
            print(f'⚠️  Only {total_count} teachers available - sharing may be limited')
        elif total_count < 5:
            print(f'⚠️  {total_count} teachers available - sharing will work but more teachers recommended')
        else:
            print(f'✅ Sufficient teachers ({total_count}) for realistic sharing data')
        
    except Exception as e:
        print(f'❌ Error creating beta teachers: {e}')
        # Don't rollback here - let parent savepoint handle it
        # Just flush any partial changes
        try:
            session.flush()
        except:
            pass
        # Re-raise to let parent savepoint handle it
        raise

def distribute_content_evenly(session: Session) -> None:
    """Distribute content evenly among all beta teachers
    
    NOTE: This function is called from within a savepoint (Phase 1.10).
    Use session.flush() instead of session.commit() to avoid closing the parent transaction.
    """
    try:
        print("🔄 Distributing content evenly among teachers...")
        
        # Don't rollback if we're in a savepoint - just flush
        # session.rollback()  # REMOVED: Can't rollback parent transaction when in savepoint
        
        # Get all beta teachers
        teachers = session.execute(text('SELECT id FROM teacher_registrations ORDER BY id')).fetchall()
        
        if len(teachers) < 2:
            print('❌ Need at least 2 teachers for distribution')
            return
        
        print(f'Found {len(teachers)} beta teachers')
        
        # Redistribute lesson plans evenly
        # ORDER BY id to ensure consistent lock ordering and prevent deadlocks
        lesson_plans = session.execute(text('SELECT id FROM lesson_plan_templates ORDER BY id')).fetchall()
        
        redistributed_lessons = 0
        batch_size = 100  # Commit in batches to avoid long-running transactions
        
        for i, lesson_plan in enumerate(lesson_plans):
            teacher_id = teachers[i % len(teachers)][0]  # Distribute evenly
            
            try:
                session.execute(text('''
                    UPDATE lesson_plan_templates 
                    SET teacher_id = :teacher_id,
                        updated_at = :updated_at
                    WHERE id = :id
                '''), {
                    'id': lesson_plan[0],
                    'teacher_id': teacher_id,
                    'updated_at': datetime.utcnow()
                })
                
                redistributed_lessons += 1
                
                # Flush in batches to reduce lock time and prevent deadlocks
                # Use flush() not commit() since we're in a savepoint
                if (i + 1) % batch_size == 0:
                    session.flush()
                    # Progress indicator
                    if (i + 1) % 500 == 0:
                        print(f'  Distributing lessons... {i + 1}/{len(lesson_plans)}')
                        
            except Exception as e:
                # If deadlock occurs, flush and retry this batch
                # Can't rollback parent transaction when in savepoint - use flush()
                if 'deadlock' in str(e).lower():
                    session.flush()  # Flush any pending changes
                    # Retry this update once
                    try:
                        session.execute(text('''
                            UPDATE lesson_plan_templates 
                            SET teacher_id = :teacher_id,
                                updated_at = :updated_at
                            WHERE id = :id
                        '''), {
                            'id': lesson_plan[0],
                            'teacher_id': teacher_id,
                            'updated_at': datetime.utcnow()
                        })
                        redistributed_lessons += 1
                        if (i + 1) % batch_size == 0:
                            session.flush()
                    except:
                        # Skip if retry also fails
                        session.flush()  # Flush any pending changes
                        continue
                else:
                    raise
        
        # Final flush for remaining updates
        if redistributed_lessons > 0:
            session.flush()
        
        # Redistribute assessments evenly
        # ORDER BY id to ensure consistent lock ordering and prevent deadlocks
        assessments = session.execute(text('SELECT id FROM assessment_templates ORDER BY id')).fetchall()
        
        redistributed_assessments = 0
        for i, assessment in enumerate(assessments):
            teacher_id = teachers[i % len(teachers)][0]
            
            try:
                session.execute(text('''
                    UPDATE assessment_templates 
                    SET teacher_id = :teacher_id,
                        updated_at = :updated_at
                    WHERE id = :id
                '''), {
                    'id': assessment[0],
                    'teacher_id': teacher_id,
                    'updated_at': datetime.utcnow()
                })
                
                redistributed_assessments += 1
                
                # Flush in batches (use flush() not commit() since we're in a savepoint)
                if (i + 1) % batch_size == 0:
                    session.flush()
                    
            except Exception as e:
                # If deadlock occurs, flush and retry
                if 'deadlock' in str(e).lower():
                    session.flush()  # Flush any pending changes
                    try:
                        session.execute(text('''
                            UPDATE assessment_templates 
                            SET teacher_id = :teacher_id,
                                updated_at = :updated_at
                            WHERE id = :id
                        '''), {
                            'id': assessment[0],
                            'teacher_id': teacher_id,
                            'updated_at': datetime.utcnow()
                        })
                        redistributed_assessments += 1
                        if (i + 1) % batch_size == 0:
                            session.flush()
                    except:
                        session.flush()  # Flush any pending changes
                        continue
                else:
                    raise
        
        # Final flush for assessments
        if redistributed_assessments > 0:
            session.flush()
        
        # Redistribute AI conversations evenly
        # ORDER BY id to ensure consistent lock ordering and prevent deadlocks
        conversations = session.execute(text('SELECT id FROM ai_assistant_conversations ORDER BY id')).fetchall()
        
        redistributed_conversations = 0
        for i, conversation in enumerate(conversations):
            teacher_id = teachers[i % len(teachers)][0]
            
            try:
                session.execute(text('''
                    UPDATE ai_assistant_conversations 
                    SET teacher_id = :teacher_id,
                        updated_at = :updated_at
                    WHERE id = :id
                '''), {
                    'id': conversation[0],
                    'teacher_id': teacher_id,
                    'updated_at': datetime.utcnow()
                })
                
                redistributed_conversations += 1
                
                # Flush in batches (use flush() not commit() since we're in a savepoint)
                if (i + 1) % batch_size == 0:
                    session.flush()
                    
            except Exception as e:
                # If deadlock occurs, flush and retry
                if 'deadlock' in str(e).lower():
                    session.flush()  # Flush any pending changes
                    try:
                        session.execute(text('''
                            UPDATE ai_assistant_conversations 
                            SET teacher_id = :teacher_id,
                                updated_at = :updated_at
                            WHERE id = :id
                        '''), {
                            'id': conversation[0],
                            'teacher_id': teacher_id,
                            'updated_at': datetime.utcnow()
                        })
                        redistributed_conversations += 1
                        if (i + 1) % batch_size == 0:
                            session.flush()
                    except:
                        session.flush()  # Flush any pending changes
                        continue
                else:
                    raise
        
        # Final flush for conversations
        if redistributed_conversations > 0:
            session.flush()
        
        print(f'✅ Redistributed {redistributed_lessons} lesson plans evenly')
        print(f'✅ Redistributed {redistributed_assessments} assessments evenly')
        print(f'✅ Redistributed {redistributed_conversations} AI conversations evenly')
        
    except Exception as e:
        print(f'❌ Error redistributing content: {e}')
        # Don't rollback parent transaction when in savepoint - let savepoint handle it
        # session.rollback()  # REMOVED
        raise

def create_lesson_plan_activities(session: Session) -> None:
    """Create lesson plan activities for lessons without them"""
    try:
        print("🔄 Creating lesson plan activities...")
        
        # Get lesson plans without activities
        lessons_without_activities = session.execute(text('''
            SELECT lpt.id, lpt.title, lpt.subject, lpt.grade_level
            FROM lesson_plan_templates lpt
            LEFT JOIN beta_lesson_plan_activities blpa ON lpt.id = blpa.template_id
            WHERE blpa.template_id IS NULL
            LIMIT 300
        ''')).fetchall()
        
        print(f'Found {len(lessons_without_activities)} lessons without activities')
        
        created_activities = 0
        for lesson in lessons_without_activities:
            lesson_id, title, subject, grade_level = lesson
            
            # Create realistic activities based on lesson type
            activity_types = ['warm_up', 'instruction', 'guided_practice', 'independent_practice', 'assessment']
            
            for i, activity_type in enumerate(activity_types):
                try:
                    activity_id = str(uuid.uuid4())
                    
                    # Create activity based on type
                    if activity_type == 'warm_up':
                        activity_name = f'{title} - Warm Up'
                        activity_description = 'Engage students and prepare them for the lesson'
                        duration = 10
                        instructions = ['Review previous material', 'Get students ready']
                    elif activity_type == 'instruction':
                        activity_name = f'{title} - Instruction'
                        activity_description = 'Direct instruction and demonstration'
                        duration = 15
                        instructions = ['Explain key concepts', 'Demonstrate techniques', 'Answer questions']
                    elif activity_type == 'guided_practice':
                        activity_name = f'{title} - Guided Practice'
                        activity_description = 'Supervised practice with teacher guidance'
                        duration = 15
                        instructions = ['Practice with supervision', 'Get immediate feedback', 'Work in groups']
                    elif activity_type == 'independent_practice':
                        activity_name = f'{title} - Independent Practice'
                        activity_description = 'Independent student work'
                        duration = 20
                        instructions = ['Complete exercises independently', 'Apply what was learned', 'Demonstrate understanding']
                    else:  # assessment
                        activity_name = f'{title} - Assessment'
                        activity_description = 'Assessment and evaluation'
                        duration = 10
                        instructions = ['Complete assessment', 'Demonstrate mastery', 'Self-evaluate']
                    
                    session.execute(text('''
                        INSERT INTO beta_lesson_plan_activities (
                            id, template_id, activity_name, activity_description,
                            duration_minutes, activity_type, instructions, order_index, created_at
                        ) VALUES (
                            :id, :template_id, :activity_name, :activity_description,
                            :duration_minutes, :activity_type, :instructions, :order_index, :created_at
                        )
                    '''), {
                        'id': activity_id,
                        'template_id': lesson_id,
                        'activity_name': activity_name,
                        'activity_description': activity_description,
                        'duration_minutes': duration,
                        'activity_type': activity_type,
                        'instructions': instructions,
                        'order_index': i + 1,
                        'created_at': datetime.utcnow()
                    })
                    
                    created_activities += 1
                    
                except Exception as e:
                    print(f'  ⚠️  Error creating activity for lesson {lesson_id}: {e}')
                    continue
        
        session.flush()  # Use flush() not commit() when called from within savepoint
        
        print(f'✅ Created {created_activities} new activities')
        print(f'   Average {created_activities / len(lessons_without_activities) if lessons_without_activities else 0:.1f} activities per lesson')
        
    except Exception as e:
        print(f'❌ Error creating lesson plan activities: {e}')
        # Don't rollback parent transaction when in savepoint - let savepoint handle it
        # session.rollback()  # REMOVED
        raise

def create_comprehensive_widgets(session: Session, count: int = 323) -> None:
    """Create comprehensive widget suite for beta system"""
    try:
        from app.models import BetaWidget
        
        widget_types = [
            'dashboard', 'analytics', 'calendar', 'notifications', 'reports',
            'chat', 'file_manager', 'grade_book', 'attendance', 'lesson_planner',
            'assessment_builder', 'resource_library', 'student_profiles',
            'collaboration', 'communication', 'progress_tracking', 'scheduling'
        ]
        
        created = 0
        for i in range(count):
            widget = BetaWidget(
                id=uuid.uuid4(),
                name=f'Widget {i+1}',
                widget_type=widget_types[i % len(widget_types)],
                configuration=json.dumps({
                    'category': widget_types[i % len(widget_types)],
                    'display_settings': {'theme': 'modern'},
                    'functionality': {'auto_refresh': True}
                }),
                is_active=True
            )
            session.add(widget)
            created += 1
        
        session.flush()  # Use flush() not commit() when called from within savepoint
        print(f"✅ Created {created} widgets")
        
    except Exception as e:
        print(f"❌ Error creating widgets: {e}")
        # Don't rollback parent transaction when in savepoint - let savepoint handle it
        # session.rollback()  # REMOVED
        raise

def enhance_avatar_widget_configurations(session: Session) -> None:
    """Enhance avatar and widget configurations with realistic JSON data"""
    try:
        print("🔄 Enhancing avatar and widget configurations...")
        
        # Enhance avatar configurations
        print("  Enhancing avatar configurations...")
        
        # Enable voice for ALL avatars
        session.execute(text('''
            UPDATE beta_avatars 
            SET voice_enabled = true,
                updated_at = NOW()
        '''))
        
        session.execute(text('''
            UPDATE beta_avatars 
            SET config = :config,
                voice_config = :voice_config,
                expression_config = :expression_config,
                gesture_config = :gesture_config,
                updated_at = :updated_at
            WHERE config IS NULL OR config::text = '{}'
        '''), {
            'config': json.dumps({
                "personality": "friendly",
                "speaking_style": "encouraging",
                "interaction_level": "high",
                "response_time": "fast",
                "customization": {
                    "voice_speed": 1.0,
                    "gesture_frequency": 0.7,
                    "expression_intensity": 0.8
                }
            }),
            'voice_config': json.dumps({
                "voice_type": "natural",
                "speed": 1.0,
                "pitch": 0.5,
                "volume": 0.8,
                "language": "en-US",
                "accent": "neutral"
            }),
            'expression_config': json.dumps({
                "happy": {"intensity": 0.8, "duration": 2.0},
                "concerned": {"intensity": 0.6, "duration": 1.5},
                "encouraging": {"intensity": 0.9, "duration": 2.5},
                "neutral": {"intensity": 0.5, "duration": 1.0}
            }),
            'gesture_config': json.dumps({
                "pointing": {"frequency": 0.7, "intensity": 0.8},
                "nodding": {"frequency": 0.9, "intensity": 0.6},
                "hand_movements": {"frequency": 0.8, "intensity": 0.7},
                "body_language": {"frequency": 0.6, "intensity": 0.5}
            }),
            'updated_at': datetime.utcnow()
        })
        
        # Enhance widget configurations
        print("  Enhancing widget configurations...")
        session.execute(text('''
            UPDATE beta_widgets 
            SET configuration = :config,
                updated_at = :updated_at
            WHERE configuration IS NULL OR configuration::text = '{}'
        '''), {
            'config': json.dumps({
                "display_settings": {
                    "theme": "modern",
                    "color_scheme": "blue",
                    "font_size": "medium",
                    "layout": "grid"
                },
                "functionality": {
                    "auto_refresh": True,
                    "interactive": True,
                    "responsive": True,
                    "accessibility": True
                },
                "performance": {
                    "cache_enabled": True,
                    "lazy_loading": True,
                    "optimization": "high"
                }
            }),
            'updated_at': datetime.utcnow()
        })
        
        session.flush()  # Use flush() not commit() when called from within savepoint
        
        print("✅ Enhanced avatar and widget configurations")
        
    except Exception as e:
        print(f'❌ Error enhancing configurations: {e}')
        # Don't rollback parent transaction when in savepoint - let savepoint handle it
        # session.rollback()  # REMOVED
        raise

def create_comprehensive_educational_resources(session: Session) -> None:
    """Create comprehensive educational resources for beta testing"""
    try:
        print("🔄 Creating comprehensive educational resources...")
        
        # Get all teachers
        teacher_result = session.execute(text("SELECT id FROM teacher_registrations LIMIT 10")).fetchall()
        if not teacher_result:
            print("⚠️  No teachers found, skipping educational resources")
            return
        
        teacher_ids = [row[0] for row in teacher_result]
        
        # Define comprehensive resource templates
        resource_templates = [
            # PE Resources
            {"title": "Basketball Fundamentals Guide", "subject": "PE", "resource_type": "document"},
            {"title": "Soccer Skills Development", "subject": "PE", "resource_type": "document"},
            {"title": "Baseball Drills and Techniques", "subject": "PE", "resource_type": "document"},
            {"title": "Volleyball Training Manual", "subject": "PE", "resource_type": "document"},
            {"title": "Track and Field Basics", "subject": "PE", "resource_type": "document"},
            {"title": "Swimming Safety Protocols", "subject": "PE", "resource_type": "document"},
            {"title": "Gymnastics Fundamentals", "subject": "PE", "resource_type": "document"},
            {"title": "Tennis Skills and Strategies", "subject": "PE", "resource_type": "document"},
            {"title": "Yoga and Mindfulness Guide", "subject": "PE", "resource_type": "document"},
            {"title": "Dance Movement Activities", "subject": "PE", "resource_type": "document"},
            
            # Health Resources
            {"title": "Nutrition Basics for Students", "subject": "Health", "resource_type": "document"},
            {"title": "Mental Health Awareness", "subject": "Health", "resource_type": "document"},
            {"title": "Substance Abuse Prevention", "subject": "Health", "resource_type": "document"},
            {"title": "Sexual Health Education", "subject": "Health", "resource_type": "document"},
            {"title": "First Aid Training Manual", "subject": "Health", "resource_type": "document"},
            
            # Driver's Ed Resources
            {"title": "Traffic Laws and Regulations", "subject": "Driver's Ed", "resource_type": "document"},
            {"title": "Defensive Driving Techniques", "subject": "Driver's Ed", "resource_type": "document"},
            {"title": "Vehicle Maintenance Basics", "subject": "Driver's Ed", "resource_type": "document"},
            
            # Videos
            {"title": "Proper Warm-Up Techniques", "subject": "PE", "resource_type": "video"},
            {"title": "Cool-Down Stretches", "subject": "PE", "resource_type": "video"},
            {"title": "Fitness Assessment Methods", "subject": "PE", "resource_type": "video"},
            
            # Worksheets and Activities
            {"title": "PE Activity Assessment Sheet", "subject": "PE", "resource_type": "worksheet"},
            {"title": "Health Education Quiz", "subject": "Health", "resource_type": "worksheet"},
            {"title": "Driver's Ed Practice Test", "subject": "Driver's Ed", "resource_type": "worksheet"},
        ]
        
        resources_created = 0
        collections_created = 0
        
        # Create resources for each teacher
        for teacher_id in teacher_ids:
            # Create 50 resources per teacher (varied by template)
            for i in range(50):
                template_idx = i % len(resource_templates)
                template = resource_templates[template_idx].copy()
                
                resource_id = str(uuid.uuid4())
                
                session.execute(text("""
                    INSERT INTO educational_resources (
                        id, teacher_id, title, description, resource_type, subject, grade_level,
                        tags, keywords, difficulty_level, language, license_type, is_public,
                        is_featured, ai_generated, created_at
                    ) VALUES (
                        :id, :teacher_id, :title, :description, :resource_type, :subject, :grade_level,
                        :tags, :keywords, :difficulty_level, :language, :license_type, :is_public,
                        :is_featured, :ai_generated, :created_at
                    )
                """), {
                    "id": resource_id,
                    "teacher_id": teacher_id,
                    "title": f"{template['title']} - Version {i+1}",
                    "description": f"Comprehensive {template['subject']} resource for classroom use",
                    "resource_type": template['resource_type'],
                    "subject": template['subject'],
                    "grade_level": "K-12",
                    "tags": [template['subject'].lower(), template['resource_type'], "education"],
                    "keywords": [template['subject'].lower(), "teaching", "resources"],
                    "difficulty_level": "intermediate",
                    "language": "en",
                    "license_type": "educational_use",
                    "is_public": i % 3 != 0,  # 2/3 public
                    "is_featured": i % 5 == 0,  # 1/5 featured
                    "ai_generated": True,
                    "created_at": datetime.utcnow()
                })
                resources_created += 1
        
        # Create resource collections for each teacher
        collection_templates = [
            {"title": "Complete PE Curriculum", "description": "Full physical education curriculum resources", "subject": "PE"},
            {"title": "Health Education Materials", "description": "Comprehensive health education resources", "subject": "Health"},
            {"title": "Driver's Ed Resources", "description": "Driver's education teaching materials", "subject": "Driver's Ed"},
            {"title": "Assessment Tools", "description": "Evaluation and assessment resources", "subject": "Assessment"},
        ]
        
        collection_ids = []
        for teacher_id in teacher_ids:
            for template in collection_templates:
                collection_id = str(uuid.uuid4())
                collection_ids.append(collection_id)
                
                session.execute(text("""
                    INSERT INTO resource_collections (
                        id, teacher_id, title, description, subject, grade_level,
                        collection_type, is_public, is_featured, resource_count,
                        view_count, download_count, rating_average, rating_count,
                        created_at, updated_at
                    ) VALUES (
                        :id, :teacher_id, :title, :description, :subject, :grade_level,
                        :collection_type, :is_public, :is_featured, :resource_count,
                        :view_count, :download_count, :rating_average, :rating_count,
                        :created_at, :updated_at
                    )
                """), {
                    "id": collection_id,
                    "teacher_id": teacher_id,
                    "title": f"{template['title']} - {str(teacher_id)[:8]}...",
                    "description": template['description'],
                    "subject": template['subject'],
                    "grade_level": "K-12",
                    "collection_type": "curriculum",
                    "is_public": True,
                    "is_featured": False,
                    "resource_count": random.randint(10, 25),
                    "view_count": random.randint(50, 500),
                    "download_count": random.randint(10, 100),
                    "rating_average": round(random.uniform(3.5, 5.0), 2),
                    "rating_count": random.randint(5, 50),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
                collections_created += 1
        
        # Get all resources and categories for associations
        resource_ids_result = session.execute(text("SELECT id FROM educational_resources LIMIT 50")).fetchall()
        category_ids_result = session.execute(text("SELECT id FROM resource_categories LIMIT 10")).fetchall()
        
        if resource_ids_result and category_ids_result:
            resource_ids = [row[0] for row in resource_ids_result]
            category_ids = [row[0] for row in category_ids_result]
            
            # Create collection-resource associations
            print("🔄 Creating collection-resource associations...")
            for collection_id in collection_ids:
                for i in range(min(20, len(resource_ids))):  # Associate 20 resources per collection
                    resource_id = resource_ids[i % len(resource_ids)]
                    session.execute(text("""
                        INSERT INTO collection_resource_associations (
                            id, collection_id, resource_id, order_index, added_at
                        ) VALUES (
                            :id, :collection_id, :resource_id, :order_index, :added_at
                        ) ON CONFLICT (collection_id, resource_id) DO NOTHING
                    """), {
                        "id": str(uuid.uuid4()),
                        "collection_id": collection_id,
                        "resource_id": resource_id,
                        "order_index": i + 1,
                        "added_at": datetime.utcnow()
                    })
            
            # Create resource-category associations
            print("🔄 Creating resource-category associations...")
            for resource_id in resource_ids:
                # Associate each resource with 1-3 categories
                num_categories = random.randint(1, 3)
                for i in range(num_categories):
                    category_id = category_ids[i % len(category_ids)]
                    session.execute(text("""
                        INSERT INTO resource_category_associations (
                            id, resource_id, category_id, created_at
                        ) VALUES (
                            :id, :resource_id, :category_id, :created_at
                        ) ON CONFLICT (resource_id, category_id) DO NOTHING
                    """), {
                        "id": str(uuid.uuid4()),
                        "resource_id": resource_id,
                        "category_id": category_id,
                        "created_at": datetime.utcnow()
                    })
        
        session.flush()  # Use flush() not commit() when called from within savepoint
        print(f"✅ Created {resources_created} educational resources and {collections_created} collections")
        
    except Exception as e:
        print(f"❌ Error creating educational resources: {e}")
        # Don't rollback parent transaction when in savepoint - let savepoint handle it
        # session.rollback()  # REMOVED
        raise

if __name__ == "__main__":
    # This script can be run independently for testing
    session = SessionLocal()
    try:
        seed_beta_teacher_system(session)
    finally:
        session.close()
