import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
from sqlalchemy.orm import Session
from pathlib import Path
from sqlalchemy import text

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import get_db
from app.core.config import settings
from app.services.education.models.lesson import Lesson
from app.models.core.subject import SubjectCategory
from app.dashboard.models import DashboardUser as User

def seed_daily_pe_curriculum(session: Session) -> None:
    """Seed the database with a comprehensive daily PE curriculum - 5 lessons per week for each grade level."""
    print("Seeding comprehensive daily PE curriculum...")
    
    # Get existing users and subject categories
    users = session.execute(text("SELECT id FROM users WHERE role = 'teacher'"))
    user_ids = [user[0] for user in users.fetchall()]
    
    subject_categories = session.execute(text("SELECT id FROM subject_categories"))
    subject_category_ids = [category[0] for category in subject_categories.fetchall()]
    
    if not user_ids or not subject_category_ids:
        print("Warning: No teachers or subject categories found. Skipping lesson seeding.")
        return
    
    # School year starts in September (36 weeks)
    school_year_start = datetime(2024, 9, 3)  # First Tuesday in September
    lessons_data = []
    
    # ============================================================================
    # KINDERGARTEN (K) - 36 WEEKS × 5 LESSONS PER WEEK = 180 LESSONS
    # ============================================================================
    
    print("Creating Kindergarten daily curriculum...")
    kindergarten_lessons = []
    
    for week in range(36):
        week_start = school_year_start + timedelta(weeks=week)
        
        # Monday - Skill Development
        monday_lesson = {
            "title": f"K Movement Skills - Week {week + 1} Monday",
            "content": f"Week {week + 1} Monday: Fundamental movement skill development",
            "grade_level": "K",
            "week_of": week_start,
            "content_area": "Fundamental Movement",
            "objectives": [
                "Develop basic locomotor skills",
                "Learn spatial awareness",
                "Practice following directions",
                "Build confidence in movement"
            ],
            "materials": ["Cones", "Bean bags", "Music player", "Hula hoops"],
            "activities": [
                "Walking, running, jumping games",
                "Animal movement imitation",
                "Follow the leader",
                "Spatial awareness activities"
            ],
            "assessment_criteria": "Observation of participation and basic skill demonstration",
            "status": "published",
            "version": 1
        }
        
        # Tuesday - Fitness Training
        tuesday_lesson = {
            "title": f"K Fitness Fun - Week {week + 1} Tuesday",
            "content": f"Week {week + 1} Tuesday: Age-appropriate fitness activities",
            "grade_level": "K",
            "week_of": week_start + timedelta(days=1),
            "content_area": "Fitness Training",
            "objectives": [
                "Build basic fitness habits",
                "Improve coordination",
                "Develop endurance",
                "Have fun while exercising"
            ],
            "materials": ["Jump ropes", "Cones", "Music", "Stopwatch"],
            "activities": [
                "Jump rope basics",
                "Fitness stations",
                "Movement circuits",
                "Endurance games"
            ],
            "assessment_criteria": "Participation in fitness activities and skill improvement",
            "status": "published",
            "version": 1
        }
        
        # Wednesday - Team Activities
        wednesday_lesson = {
            "title": f"K Team Time - Week {week + 1} Wednesday",
            "content": f"Week {week + 1} Wednesday: Cooperative play and team building",
            "grade_level": "K",
            "week_of": week_start + timedelta(days=2),
            "content_area": "Team Building",
            "objectives": [
                "Learn cooperation skills",
                "Practice sharing",
                "Build social skills",
                "Understand teamwork"
            ],
            "materials": ["Large parachute", "Soft balls", "Cones", "Bean bags"],
            "activities": [
                "Parachute games",
                "Partner toss",
                "Group circle games",
                "Simple relay races"
            ],
            "assessment_criteria": "Participation in group activities and cooperation",
            "status": "published",
            "version": 1
        }
        
        # Thursday - Creative Movement
        thursday_lesson = {
            "title": f"K Creative Moves - Week {week + 1} Thursday",
            "content": f"Week {week + 1} Thursday: Creative movement and self-expression",
            "grade_level": "K",
            "week_of": week_start + timedelta(days=3),
            "content_area": "Creative Movement",
            "objectives": [
                "Express creativity through movement",
                "Learn rhythm",
                "Build confidence",
                "Develop imagination"
            ],
            "materials": ["Music player", "Scarves", "Ribbons", "Drums"],
            "activities": [
                "Scarf dancing",
                "Rhythm games",
                "Creative movement",
                "Dance routines"
            ],
            "assessment_criteria": "Creativity in movement and rhythm awareness",
            "status": "published",
            "version": 1
        }
        
        # Friday - Assessment & Enrichment
        friday_lesson = {
            "title": f"K Fun Friday - Week {week + 1} Friday",
            "content": f"Week {week + 1} Friday: Assessment, review, and enrichment activities",
            "grade_level": "K",
            "week_of": week_start + timedelta(days=4),
            "content_area": "Assessment & Enrichment",
            "objectives": [
                "Review weekly skills",
                "Assess progress",
                "Provide enrichment",
                "Celebrate achievements"
            ],
            "materials": ["Assessment tools", "Enrichment materials", "Rewards", "Music"],
            "activities": [
                "Skill review games",
                "Progress assessment",
                "Enrichment activities",
                "Celebration time"
            ],
            "assessment_criteria": "Skill demonstration and progress review",
            "status": "published",
            "version": 1
        }
        
        kindergarten_lessons.extend([monday_lesson, tuesday_lesson, wednesday_lesson, thursday_lesson, friday_lesson])
    
    # ============================================================================
    # GRADES 1-2 - 36 WEEKS × 5 LESSONS PER WEEK = 180 LESSONS
    # ============================================================================
    
    print("Creating Grades 1-2 daily curriculum...")
    grade_1_2_lessons = []
    
    for week in range(36):
        week_start = school_year_start + timedelta(weeks=week)
        
        # Monday - Skill Development
        monday_lesson = {
            "title": f"Grade 1-2 Skills - Week {week + 1} Monday",
            "content": f"Week {week + 1} Monday: Building on fundamental skills",
            "grade_level": "1-2",
            "week_of": week_start,
            "content_area": "Skill Development",
            "objectives": [
                "Refine basic movement skills",
                "Learn new techniques",
                "Build confidence",
                "Track progress"
            ],
            "materials": ["Balls", "Cones", "Equipment", "Stopwatch"],
            "activities": [
                "Skill practice drills",
                "Technique work",
                "Progressive challenges",
                "Individual practice"
            ],
            "assessment_criteria": "Skill demonstration and technique improvement",
            "status": "published",
            "version": 1
        }
        
        # Tuesday - Fitness Training
        tuesday_lesson = {
            "title": f"Grade 1-2 Fitness - Week {week + 1} Tuesday",
            "content": f"Week {week + 1} Tuesday: Age-appropriate fitness development",
            "grade_level": "1-2",
            "week_of": week_start + timedelta(days=1),
            "content_area": "Fitness Training",
            "objectives": [
                "Improve fitness levels",
                "Build endurance",
                "Develop strength",
                "Learn healthy habits"
            ],
            "materials": ["Fitness equipment", "Resistance bands", "Stopwatch", "Cones"],
            "activities": [
                "Circuit training",
                "Strength exercises",
                "Cardio activities",
                "Fitness games"
            ],
            "assessment_criteria": "Fitness improvement and participation",
            "status": "published",
            "version": 1
        }
        
        # Wednesday - Team Sports
        wednesday_lesson = {
            "title": f"Grade 1-2 Team Sports - Week {week + 1} Wednesday",
            "content": f"Week {week + 1} Wednesday: Team sports and cooperative games",
            "grade_level": "1-2",
            "week_of": week_start + timedelta(days=2),
            "content_area": "Team Sports",
            "objectives": [
                "Learn team sports",
                "Practice cooperation",
                "Understand rules",
                "Build teamwork"
            ],
            "materials": ["Sports equipment", "Cones", "Goals", "Stopwatch"],
            "activities": [
                "Team games",
                "Sport-specific skills",
                "Cooperative challenges",
                "Small-sided games"
            ],
            "assessment_criteria": "Team participation and skill development",
            "status": "published",
            "version": 1
        }
        
        # Thursday - Individual Activities
        thursday_lesson = {
            "title": f"Grade 1-2 Individual - Week {week + 1} Thursday",
            "content": f"Week {week + 1} Thursday: Individual skill development and activities",
            "grade_level": "1-2",
            "week_of": week_start + timedelta(days=3),
            "content_area": "Individual Activities",
            "objectives": [
                "Develop individual skills",
                "Build self-confidence",
                "Practice independently",
                "Set personal goals"
            ],
            "materials": ["Individual equipment", "Practice areas", "Assessment tools"],
            "activities": [
                "Individual practice",
                "Skill challenges",
                "Personal goal setting",
                "Self-assessment"
            ],
            "assessment_criteria": "Individual skill improvement and goal achievement",
            "status": "published",
            "version": 1
        }
        
        # Friday - Assessment & Enrichment
        friday_lesson = {
            "title": f"Grade 1-2 Assessment - Week {week + 1} Friday",
            "content": f"Week {week + 1} Friday: Assessment, review, and enrichment",
            "grade_level": "1-2",
            "week_of": week_start + timedelta(days=4),
            "content_area": "Assessment & Enrichment",
            "objectives": [
                "Assess weekly progress",
                "Review skills learned",
                "Provide enrichment",
                "Plan next week"
            ],
            "materials": ["Assessment tools", "Review materials", "Enrichment activities"],
            "activities": [
                "Progress assessment",
                "Skill review",
                "Enrichment activities",
                "Goal setting"
            ],
            "assessment_criteria": "Progress assessment and skill review",
            "status": "published",
            "version": 1
        }
        
        grade_1_2_lessons.extend([monday_lesson, tuesday_lesson, wednesday_lesson, thursday_lesson, friday_lesson])
    
    # ============================================================================
    # GRADES 3-5 - 36 WEEKS × 5 LESSONS PER WEEK = 180 LESSONS
    # ============================================================================
    
    print("Creating Grades 3-5 daily curriculum...")
    grade_3_5_lessons = []
    
    for week in range(36):
        week_start = school_year_start + timedelta(weeks=week)
        
        # Monday - Skill Development
        monday_lesson = {
            "title": f"Grade 3-5 Skills - Week {week + 1} Monday",
            "content": f"Week {week + 1} Monday: Advanced skill development and technique",
            "grade_level": "3-5",
            "week_of": week_start,
            "content_area": "Skill Development",
            "objectives": [
                "Master advanced techniques",
                "Refine skills",
                "Build confidence",
                "Track progress"
            ],
            "materials": ["Advanced equipment", "Video analysis", "Stopwatch", "Cones"],
            "activities": [
                "Advanced skill drills",
                "Technique refinement",
                "Video analysis",
                "Progressive challenges"
            ],
            "assessment_criteria": "Advanced skill demonstration and technique mastery",
            "status": "published",
            "version": 1
        }
        
        # Tuesday - Fitness Training
        tuesday_lesson = {
            "title": f"Grade 3-5 Fitness - Week {week + 1} Tuesday",
            "content": f"Week {week + 1} Tuesday: Comprehensive fitness training",
            "grade_level": "3-5",
            "week_of": week_start + timedelta(days=1),
            "content_area": "Fitness Training",
            "objectives": [
                "Improve overall fitness",
                "Build strength and endurance",
                "Develop healthy habits",
                "Track fitness progress"
            ],
            "materials": ["Fitness equipment", "Resistance bands", "Stopwatch", "Assessment tools"],
            "activities": [
                "Circuit training",
                "Strength exercises",
                "Cardio intervals",
                "Fitness testing"
            ],
            "assessment_criteria": "Fitness improvement and participation in all activities",
            "status": "published",
            "version": 1
        }
        
        # Wednesday - Team Sports
        wednesday_lesson = {
            "title": f"Grade 3-5 Team Sports - Week {week + 1} Wednesday",
            "content": f"Week {week + 1} Wednesday: Team sports and competitive games",
            "grade_level": "3-5",
            "week_of": week_start + timedelta(days=2),
            "content_area": "Team Sports",
            "objectives": [
                "Master team sports skills",
                "Learn game strategies",
                "Practice teamwork",
                "Develop competitive spirit"
            ],
            "materials": ["Sports equipment", "Video equipment", "Strategy boards", "Stopwatch"],
            "activities": [
                "Team skill practice",
                "Game strategies",
                "Scrimmages",
                "Competitive games"
            ],
            "assessment_criteria": "Team sports skill demonstration and game participation",
            "status": "published",
            "version": 1
        }
        
        # Thursday - Individual Activities
        thursday_lesson = {
            "title": f"Grade 3-5 Individual - Week {week + 1} Thursday",
            "content": f"Week {week + 1} Thursday: Individual skill mastery and personal development",
            "grade_level": "3-5",
            "week_of": week_start + timedelta(days=3),
            "content_area": "Individual Activities",
            "objectives": [
                "Master individual skills",
                "Set personal goals",
                "Track individual progress",
                "Build self-motivation"
            ],
            "materials": ["Individual equipment", "Progress tracking tools", "Assessment materials"],
            "activities": [
                "Individual skill practice",
                "Personal goal setting",
                "Progress assessment",
                "Self-directed learning"
            ],
            "assessment_criteria": "Individual skill mastery and goal achievement",
            "status": "published",
            "version": 1
        }
        
        # Friday - Assessment & Enrichment
        friday_lesson = {
            "title": f"Grade 3-5 Assessment - Week {week + 1} Friday",
            "content": f"Week {week + 1} Friday: Comprehensive assessment and enrichment",
            "grade_level": "3-5",
            "week_of": week_start + timedelta(days=4),
            "content_area": "Assessment & Enrichment",
            "objectives": [
                "Assess weekly progress",
                "Review skills learned",
                "Provide enrichment opportunities",
                "Plan future goals"
            ],
            "materials": ["Assessment tools", "Review materials", "Enrichment activities"],
            "activities": [
                "Comprehensive assessment",
                "Skill review and practice",
                "Enrichment activities",
                "Goal setting and planning"
            ],
            "assessment_criteria": "Comprehensive progress assessment and skill review",
            "status": "published",
            "version": 1
        }
        
        grade_3_5_lessons.extend([monday_lesson, tuesday_lesson, wednesday_lesson, thursday_lesson, friday_lesson])
    
    # ============================================================================
    # MIDDLE SCHOOL (6-8) - 36 WEEKS × 5 LESSONS PER WEEK = 180 LESSONS
    # ============================================================================
    
    print("Creating Middle School daily curriculum...")
    middle_school_lessons = []
    
    for week in range(36):
        week_start = school_year_start + timedelta(weeks=week)
        
        # Monday - Skill Development
        monday_lesson = {
            "title": f"MS Skills - Week {week + 1} Monday",
            "content": f"Week {week + 1} Monday: Advanced skill development and technique mastery",
            "grade_level": "6-8",
            "week_of": week_start,
            "content_area": "Skill Development",
            "objectives": [
                "Master advanced techniques",
                "Refine skills to expert level",
                "Build confidence",
                "Track detailed progress"
            ],
            "materials": ["Advanced equipment", "Video analysis tools", "Performance trackers", "Stopwatch"],
            "activities": [
                "Expert skill drills",
                "Technique analysis",
                "Performance tracking",
                "Advanced challenges"
            ],
            "assessment_criteria": "Expert skill demonstration and technique mastery",
            "status": "published",
            "version": 1
        }
        
        # Tuesday - Fitness Training
        tuesday_lesson = {
            "title": f"MS Fitness - Week {week + 1} Tuesday",
            "content": f"Week {week + 1} Tuesday: Advanced fitness training and conditioning",
            "grade_level": "6-8",
            "week_of": week_start + timedelta(days=1),
            "content_area": "Fitness Training",
            "objectives": [
                "Achieve advanced fitness levels",
                "Build strength and power",
                "Develop endurance",
                "Track detailed progress"
            ],
            "materials": ["Advanced fitness equipment", "Performance trackers", "Assessment tools", "Stopwatch"],
            "activities": [
                "Advanced circuit training",
                "Strength and power exercises",
                "High-intensity intervals",
                "Comprehensive fitness testing"
            ],
            "assessment_criteria": "Advanced fitness achievement and detailed progress tracking",
            "status": "published",
            "version": 1
        }
        
        # Wednesday - Team Sports & Strategy
        wednesday_lesson = {
            "title": f"MS Team Sports - Week {week + 1} Wednesday",
            "content": f"Week {week + 1} Wednesday: Advanced team sports and strategic play",
            "grade_level": "6-8",
            "week_of": week_start + timedelta(days=2),
            "content_area": "Team Sports & Strategy",
            "objectives": [
                "Master team sports at advanced level",
                "Learn complex game strategies",
                "Develop leadership skills",
                "Build competitive excellence"
            ],
            "materials": ["Advanced sports equipment", "Strategy boards", "Video analysis", "Performance trackers"],
            "activities": [
                "Advanced team drills",
                "Strategic game planning",
                "Leadership development",
                "Competitive scrimmages"
            ],
            "assessment_criteria": "Advanced team sports mastery and strategic understanding",
            "status": "published",
            "version": 1
        }
        
        # Thursday - Individual Excellence
        thursday_lesson = {
            "title": f"MS Individual - Week {week + 1} Thursday",
            "content": f"Week {week + 1} Thursday: Individual excellence and personal mastery",
            "grade_level": "6-8",
            "week_of": week_start + timedelta(days=3),
            "content_area": "Individual Excellence",
            "objectives": [
                "Achieve individual mastery",
                "Set and achieve challenging goals",
                "Track detailed progress",
                "Build self-motivation"
            ],
            "materials": ["Individual equipment", "Progress tracking tools", "Assessment materials", "Goal setting tools"],
            "activities": [
                "Individual mastery practice",
                "Challenging goal setting",
                "Detailed progress assessment",
                "Self-directed excellence"
            ],
            "assessment_criteria": "Individual mastery achievement and challenging goal completion",
            "status": "published",
            "version": 1
        }
        
        # Friday - Assessment & Leadership
        friday_lesson = {
            "title": f"MS Assessment - Week {week + 1} Friday",
            "content": f"Week {week + 1} Friday: Comprehensive assessment and leadership development",
            "grade_level": "6-8",
            "week_of": week_start + timedelta(days=4),
            "content_area": "Assessment & Leadership",
            "objectives": [
                "Conduct comprehensive assessment",
                "Review and refine skills",
                "Develop leadership abilities",
                "Plan future excellence"
            ],
            "materials": ["Comprehensive assessment tools", "Leadership development materials", "Review resources"],
            "activities": [
                "Comprehensive assessment",
                "Skill refinement",
                "Leadership development",
                "Future planning"
            ],
            "assessment_criteria": "Comprehensive assessment and leadership development",
            "status": "published",
            "version": 1
        }
        
        middle_school_lessons.extend([monday_lesson, tuesday_lesson, wednesday_lesson, thursday_lesson, friday_lesson])
    
    # ============================================================================
    # HIGH SCHOOL (9-12) - 36 WEEKS × 5 LESSONS PER WEEK = 180 LESSONS
    # ============================================================================
    
    print("Creating High School daily curriculum...")
    high_school_lessons = []
    
    for week in range(36):
        week_start = school_year_start + timedelta(weeks=week)
        
        # Monday - Elite Skill Development
        monday_lesson = {
            "title": f"HS Elite Skills - Week {week + 1} Monday",
            "content": f"Week {week + 1} Monday: Elite skill development and mastery",
            "grade_level": "9-12",
            "week_of": week_start,
            "content_area": "Elite Skill Development",
            "objectives": [
                "Achieve elite skill levels",
                "Master advanced techniques",
                "Build competitive excellence",
                "Track elite performance"
            ],
            "materials": ["Elite equipment", "Advanced video analysis", "Performance trackers", "Expert coaching tools"],
            "activities": [
                "Elite skill drills",
                "Advanced technique mastery",
                "Performance optimization",
                "Competitive preparation"
            ],
            "assessment_criteria": "Elite skill demonstration and competitive readiness",
            "status": "published",
            "version": 1
        }
        
        # Tuesday - Elite Fitness Training
        tuesday_lesson = {
            "title": f"HS Elite Fitness - Week {week + 1} Tuesday",
            "content": f"Week {week + 1} Tuesday: Elite fitness training and conditioning",
            "grade_level": "9-12",
            "week_of": week_start + timedelta(days=1),
            "content_area": "Elite Fitness Training",
            "objectives": [
                "Achieve elite fitness levels",
                "Build championship conditioning",
                "Develop peak performance",
                "Track elite metrics"
            ],
            "materials": ["Elite fitness equipment", "Performance optimization tools", "Advanced assessment", "Recovery equipment"],
            "activities": [
                "Elite circuit training",
                "Championship conditioning",
                "Performance optimization",
                "Recovery and regeneration"
            ],
            "assessment_criteria": "Elite fitness achievement and championship readiness",
            "status": "published",
            "version": 1
        }
        
        # Wednesday - Elite Team Sports & Leadership
        wednesday_lesson = {
            "title": f"HS Elite Team Sports - Week {week + 1} Wednesday",
            "content": f"Week {week + 1} Wednesday: Elite team sports and leadership development",
            "grade_level": "9-12",
            "week_of": week_start + timedelta(days=2),
            "content_area": "Elite Team Sports & Leadership",
            "objectives": [
                "Master elite team sports",
                "Develop championship strategies",
                "Build leadership excellence",
                "Prepare for competition"
            ],
            "materials": ["Elite sports equipment", "Championship strategy tools", "Leadership development", "Video analysis"],
            "activities": [
                "Elite team drills",
                "Championship strategy",
                "Leadership excellence",
                "Competitive preparation"
            ],
            "assessment_criteria": "Elite team sports mastery and leadership excellence",
            "status": "published",
            "version": 1
        }
        
        # Thursday - Elite Individual Excellence
        thursday_lesson = {
            "title": f"HS Elite Individual - Week {week + 1} Thursday",
            "content": f"Week {week + 1} Thursday: Elite individual excellence and personal mastery",
            "grade_level": "9-12",
            "week_of": week_start + timedelta(days=3),
            "content_area": "Elite Individual Excellence",
            "objectives": [
                "Achieve elite individual mastery",
                "Set and achieve championship goals",
                "Track elite performance",
                "Build competitive excellence"
            ],
            "materials": ["Elite individual equipment", "Performance optimization tools", "Championship goal setting", "Elite assessment"],
            "activities": [
                "Elite individual practice",
                "Championship goal achievement",
                "Performance optimization",
                "Competitive excellence"
            ],
            "assessment_criteria": "Elite individual mastery and championship goal achievement",
            "status": "published",
            "version": 1
        }
        
        # Friday - Elite Assessment & Leadership
        friday_lesson = {
            "title": f"HS Elite Assessment - Week {week + 1} Friday",
            "content": f"Week {week + 1} Friday: Elite assessment and championship preparation",
            "grade_level": "9-12",
            "week_of": week_start + timedelta(days=4),
            "content_area": "Elite Assessment & Leadership",
            "objectives": [
                "Conduct elite assessment",
                "Optimize performance",
                "Develop championship mindset",
                "Plan competitive success"
            ],
            "materials": ["Elite assessment tools", "Performance optimization", "Championship planning", "Leadership development"],
            "activities": [
                "Elite performance assessment",
                "Performance optimization",
                "Championship mindset development",
                "Competitive success planning"
            ],
            "assessment_criteria": "Elite assessment and championship preparation",
            "status": "published",
            "version": 1
        }
        
        high_school_lessons.extend([monday_lesson, tuesday_lesson, wednesday_lesson, thursday_lesson, friday_lesson])
    
    # ============================================================================
    # SPECIALIZED PROGRAMS - ADDITIONAL ENRICHMENT LESSONS
    # ============================================================================
    
    print("Creating Specialized Programs curriculum...")
    specialized_lessons = []
    
    # Adaptive Physical Education - 72 lessons (2 per week for 36 weeks)
    for week in range(36):
        week_start = school_year_start + timedelta(weeks=week)
        
        # Adaptive PE - Tuesday
        adaptive_tuesday = {
            "title": f"Adaptive PE - Week {week + 1} Tuesday",
            "content": f"Week {week + 1} Tuesday: Modified activities for students with special needs",
            "grade_level": "K-12",
            "week_of": week_start + timedelta(days=1),
            "content_area": "Adaptive PE",
            "objectives": [
                "Provide inclusive activities",
                "Adapt to individual needs",
                "Build confidence",
                "Track progress"
            ],
            "materials": ["Adaptive equipment", "Visual aids", "Modified games", "Support materials"],
            "activities": [
                "Modified sports",
                "Adaptive exercises",
                "Inclusive games",
                "Individual support"
            ],
            "assessment_criteria": "Participation, skill development, and confidence building",
            "status": "published",
            "version": 1
        }
        
        # Adaptive PE - Thursday
        adaptive_thursday = {
            "title": f"Adaptive PE - Week {week + 1} Thursday",
            "content": f"Week {week + 1} Thursday: Additional adaptive activities and support",
            "grade_level": "K-12",
            "week_of": week_start + timedelta(days=3),
            "content_area": "Adaptive PE",
            "objectives": [
                "Reinforce adaptive skills",
                "Provide additional support",
                "Build independence",
                "Assess progress"
            ],
            "materials": ["Adaptive equipment", "Assessment tools", "Support materials", "Progress trackers"],
            "activities": [
                "Skill reinforcement",
                "Independent practice",
                "Progress assessment",
                "Additional support"
            ],
            "assessment_criteria": "Skill reinforcement and progress assessment",
            "status": "published",
            "version": 1
        }
        
        specialized_lessons.extend([adaptive_tuesday, adaptive_thursday])
    
    # ============================================================================
    # COMBINE ALL LESSONS
    # ============================================================================
    
    lessons_data = (kindergarten_lessons + grade_1_2_lessons + grade_3_5_lessons + 
                   middle_school_lessons + high_school_lessons + specialized_lessons)
    
    # Create lessons
    for lesson_data in lessons_data:
        # Randomly assign user and subject category
        import random
        user_id = random.choice(user_ids)
        subject_category_id = random.choice(subject_category_ids)
        
        lesson = Lesson(
            user_id=user_id,
            subject_category_id=subject_category_id,
            **lesson_data
        )
        session.add(lesson)
    
    session.commit()
    print(f"Successfully seeded {len(lessons_data)} comprehensive daily PE curriculum lessons!")
    print(f"Breakdown:")
    print(f"  - Kindergarten: {len(kindergarten_lessons)} lessons (5 per week)")
    print(f"  - Grades 1-2: {len(grade_1_2_lessons)} lessons (5 per week)")
    print(f"  - Grades 3-5: {len(grade_3_5_lessons)} lessons (5 per week)")
    print(f"  - Middle School: {len(middle_school_lessons)} lessons (5 per week)")
    print(f"  - High School: {len(high_school_lessons)} lessons (5 per week)")
    print(f"  - Specialized Programs: {len(specialized_lessons)} lessons (enrichment)")
    print(f"Total: {len(lessons_data)} lessons for complete daily PE program!")

if __name__ == "__main__":
    session = next(get_db())
    seed_daily_pe_curriculum(session) 