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

def seed_year_long_curriculum(session: Session) -> None:
    """Seed the database with a comprehensive year-long curriculum covering all grade levels."""
    print("Seeding comprehensive year-long curriculum...")
    
    # Get existing users and subject categories
    users = session.execute(text("SELECT id FROM users WHERE role = 'teacher'"))
    user_ids = [user[0] for user in users.fetchall()]
    
    subject_categories = session.execute(text("SELECT id FROM subject_categories"))
    subject_category_ids = [category[0] for category in subject_categories.fetchall()]
    
    if not user_ids or not subject_category_ids:
        print("Warning: No teachers or subject categories found. Skipping lesson seeding.")
        return
    
    # School year starts in September
    school_year_start = datetime(2024, 9, 3)  # First Tuesday in September
    lessons_data = []
    
    # ============================================================================
    # KINDERGARTEN (K) - 36 WEEKS OF FUNDAMENTAL MOVEMENT DEVELOPMENT
    # ============================================================================
    
    kindergarten_lessons = []
    for week in range(36):
        week_date = school_year_start + timedelta(weeks=week)
        
        if week < 8:  # Weeks 1-8: Basic Movement Introduction
            lesson = {
                "title": f"Kindergarten Movement Basics - Week {week + 1}",
                "content": f"Week {week + 1} of fundamental movement development for young learners",
                "grade_level": "K",
                "week_of": week_date,
                "content_area": "Fundamental Movement",
                "objectives": [
                    "Develop basic locomotor skills",
                    "Learn spatial awareness", 
                    "Practice following directions",
                    "Build confidence in movement"
                ],
                "materials": ["Cones", "Bean bags", "Music player", "Hula hoops", "Balance beams"],
                "activities": [
                    "Walking, running, jumping games",
                    "Animal movement imitation", 
                    "Follow the leader",
                    "Hula hoop exploration",
                    "Balance activities"
                ],
                "assessment_criteria": "Observation of participation and basic skill demonstration",
                "status": "published",
                "version": 1
            }
        elif week < 16:  # Weeks 9-16: Balance and Coordination
            lesson = {
                "title": f"Kindergarten Balance & Coordination - Week {week + 1}",
                "content": f"Week {week + 1} of balance and coordination development",
                "grade_level": "K",
                "week_of": week_date,
                "content_area": "Balance and Coordination",
                "objectives": [
                    "Improve balance skills",
                    "Enhance coordination",
                    "Build confidence",
                    "Develop body awareness"
                ],
                "materials": ["Balance beams", "Yoga mats", "Bean bags", "Music", "Cones"],
                "activities": [
                    "Balance beam walking",
                    "Bean bag balance",
                    "Animal poses",
                    "Freeze dance",
                    "Obstacle courses"
                ],
                "assessment_criteria": "Ability to maintain balance and follow movement patterns",
                "status": "published",
                "version": 1
            }
        elif week < 24:  # Weeks 17-24: Team Building and Cooperation
            lesson = {
                "title": f"Kindergarten Team Building - Week {week + 1}",
                "content": f"Week {week + 1} of cooperative play and team activities",
                "grade_level": "K",
                "week_of": week_date,
                "content_area": "Team Building",
                "objectives": [
                    "Learn cooperation skills",
                    "Practice sharing",
                    "Build social skills",
                    "Understand teamwork"
                ],
                "materials": ["Large parachute", "Soft balls", "Cones", "Bean bags", "Music"],
                "activities": [
                    "Parachute games",
                    "Partner toss",
                    "Group circle games",
                    "Simple relay races",
                    "Cooperative challenges"
                ],
                "assessment_criteria": "Participation in group activities and cooperation",
                "status": "published",
                "version": 1
            }
        else:  # Weeks 25-36: Creative Movement and Expression
            lesson = {
                "title": f"Kindergarten Creative Movement - Week {week + 1}",
                "content": f"Week {week + 1} of creative movement and self-expression",
                "grade_level": "K",
                "week_of": week_date,
                "content_area": "Creative Movement",
                "objectives": [
                    "Express creativity through movement",
                    "Learn rhythm",
                    "Build confidence",
                    "Develop imagination"
                ],
                "materials": ["Music player", "Scarves", "Ribbons", "Drums", "Props"],
                "activities": [
                    "Scarf dancing",
                    "Rhythm games",
                    "Creative movement",
                    "Dance routines",
                    "Story-based movement"
                ],
                "assessment_criteria": "Creativity in movement and rhythm awareness",
                "status": "published",
                "version": 1
            }
        
        kindergarten_lessons.append(lesson)
    
    # ============================================================================
    # GRADES 1-2 - 36 WEEKS OF BUILDING ON FUNDAMENTALS
    # ============================================================================
    
    grade_1_2_lessons = []
    for week in range(36):
        week_date = school_year_start + timedelta(weeks=week)
        
        if week < 9:  # Weeks 1-9: Team Building and Cooperation
            lesson = {
                "title": f"Grade 1-2 Team Building - Week {week + 1}",
                "content": f"Week {week + 1} of cooperative games and basic team sports introduction",
                "grade_level": "1-2",
                "week_of": week_date,
                "content_area": "Team Sports",
                "objectives": [
                    "Learn cooperation skills",
                    "Practice basic throwing/catching",
                    "Understand fair play",
                    "Build teamwork"
                ],
                "materials": ["Soft balls", "Hula hoops", "Cones", "Stopwatch", "Bean bags"],
                "activities": [
                    "Partner toss games",
                    "Hula hoop challenges",
                    "Simple relay races",
                    "Team tag games",
                    "Cooperative challenges"
                ],
                "assessment_criteria": "Participation, cooperation, and basic skill demonstration",
                "status": "published",
                "version": 1
            }
        elif week < 18:  # Weeks 10-18: Fitness Fundamentals
            lesson = {
                "title": f"Grade 1-2 Fitness Fundamentals - Week {week + 1}",
                "content": f"Week {week + 1} of basic fitness concepts and exercises",
                "grade_level": "1-2",
                "week_of": week_date,
                "content_area": "Fitness Training",
                "objectives": [
                    "Learn basic exercises",
                    "Understand fitness concepts",
                    "Build endurance",
                    "Develop healthy habits"
                ],
                "materials": ["Jump ropes", "Cones", "Music", "Stopwatch", "Resistance bands"],
                "activities": [
                    "Jump rope basics",
                    "Fitness stations",
                    "Movement circuits",
                    "Endurance games",
                    "Strength activities"
                ],
                "assessment_criteria": "Participation in fitness activities and skill improvement",
                "status": "published",
                "version": 1
            }
        elif week < 27:  # Weeks 19-27: Creative Movement and Dance
            lesson = {
                "title": f"Grade 1-2 Creative Movement - Week {week + 1}",
                "content": f"Week {week + 1} of expressive movement and dance-based activities",
                "grade_level": "1-2",
                "week_of": week_date,
                "content_area": "Creative Movement",
                "objectives": [
                    "Express creativity through movement",
                    "Learn rhythm",
                    "Build confidence",
                    "Develop coordination"
                ],
                "materials": ["Music player", "Scarves", "Ribbons", "Drums", "Props"],
                "activities": [
                    "Scarf dancing",
                    "Rhythm games",
                    "Creative movement",
                    "Dance routines",
                    "Movement stories"
                ],
                "assessment_criteria": "Creativity in movement and rhythm awareness",
                "status": "published",
                "version": 1
            }
        else:  # Weeks 28-36: Sports Introduction
            lesson = {
                "title": f"Grade 1-2 Sports Introduction - Week {week + 1}",
                "content": f"Week {week + 1} of basic sports skills and games",
                "grade_level": "1-2",
                "week_of": week_date,
                "content_area": "Sports Skills",
                "objectives": [
                    "Learn basic sports skills",
                    "Understand game rules",
                    "Practice teamwork",
                    "Build confidence"
                ],
                "materials": ["Balls", "Cones", "Goals", "Stopwatch", "Equipment"],
                "activities": [
                    "Ball handling",
                    "Simple games",
                    "Skill practice",
                    "Team activities",
                    "Fun competitions"
                ],
                "assessment_criteria": "Skill demonstration and game participation",
                "status": "published",
                "version": 1
            }
        
        grade_1_2_lessons.append(lesson)
    
    # ============================================================================
    # GRADES 3-5 - 36 WEEKS OF SPORTS SKILLS AND FITNESS
    # ============================================================================
    
    grade_3_5_lessons = []
    for week in range(36):
        week_date = school_year_start + timedelta(weeks=week)
        
        if week < 9:  # Weeks 1-9: Sports Fundamentals
            lesson = {
                "title": f"Grade 3-5 Sports Fundamentals - Week {week + 1}",
                "content": f"Week {week + 1} of organized sports and fitness activities",
                "grade_level": "3-5",
                "week_of": week_date,
                "content_area": "Sports Skills",
                "objectives": [
                    "Master basic sports skills",
                    "Learn game rules",
                    "Develop fitness habits",
                    "Build teamwork"
                ],
                "materials": ["Basketballs", "Soccer balls", "Jump ropes", "Stopwatch", "Cones"],
                "activities": [
                    "Basketball dribbling",
                    "Soccer passing",
                    "Jump rope challenges",
                    "Fitness stations",
                    "Skill games"
                ],
                "assessment_criteria": "Skill demonstration, game participation, and fitness improvement",
                "status": "published",
                "version": 1
            }
        elif week < 18:  # Weeks 10-18: Basketball Skills
            lesson = {
                "title": f"Grade 3-5 Basketball Skills - Week {week + 1}",
                "content": f"Week {week + 1} of comprehensive basketball skill development",
                "grade_level": "3-5",
                "week_of": week_date,
                "content_area": "Basketball",
                "objectives": [
                    "Learn dribbling techniques",
                    "Practice shooting",
                    "Understand basic rules",
                    "Develop game sense"
                ],
                "materials": ["Basketballs", "Basketball hoops", "Cones", "Stopwatch", "Goals"],
                "activities": [
                    "Dribbling drills",
                    "Shooting practice",
                    "Passing games",
                    "Mini-games",
                    "Skill challenges"
                ],
                "assessment_criteria": "Basketball skill demonstration and game participation",
                "status": "published",
                "version": 1
            }
        elif week < 27:  # Weeks 19-27: Soccer Skills
            lesson = {
                "title": f"Grade 3-5 Soccer Skills - Week {week + 1}",
                "content": f"Week {week + 1} of comprehensive soccer skill development",
                "grade_level": "3-5",
                "week_of": week_date,
                "content_area": "Soccer",
                "objectives": [
                    "Master ball control",
                    "Learn passing techniques",
                    "Understand positions",
                    "Develop teamwork"
                ],
                "materials": ["Soccer balls", "Cones", "Goals", "Stopwatch", "Equipment"],
                "activities": [
                    "Dribbling drills",
                    "Passing practice",
                    "Shooting practice",
                    "Small-sided games",
                    "Skill challenges"
                ],
                "assessment_criteria": "Soccer skill demonstration and game understanding",
                "status": "published",
                "version": 1
            }
        else:  # Weeks 28-36: Fitness Challenge
            lesson = {
                "title": f"Grade 3-5 Fitness Challenge - Week {week + 1}",
                "content": f"Week {week + 1} of comprehensive fitness training and assessment",
                "grade_level": "3-5",
                "week_of": week_date,
                "content_area": "Fitness Training",
                "objectives": [
                    "Improve overall fitness",
                    "Build strength",
                    "Enhance endurance",
                    "Track progress"
                ],
                "materials": ["Fitness equipment", "Stopwatch", "Cones", "Resistance bands", "Mats"],
                "activities": [
                    "Circuit training",
                    "Strength exercises",
                    "Cardio intervals",
                    "Fitness testing",
                    "Progress tracking"
                ],
                "assessment_criteria": "Fitness improvement and participation in all activities",
                "status": "published",
                "version": 1
            }
        
        grade_3_5_lessons.append(lesson)
    
    # ============================================================================
    # MIDDLE SCHOOL (6-8) - 36 WEEKS OF ADVANCED SKILLS AND FITNESS
    # ============================================================================
    
    middle_school_lessons = []
    for week in range(36):
        week_date = school_year_start + timedelta(weeks=week)
        
        if week < 9:  # Weeks 1-9: Advanced Sports Skills
            lesson = {
                "title": f"Grade 6-8 Advanced Sports Skills - Week {week + 1}",
                "content": f"Week {week + 1} of intermediate level sports training and fitness development",
                "grade_level": "6-8",
                "week_of": week_date,
                "content_area": "Advanced Sports",
                "objectives": [
                    "Refine sports techniques",
                    "Build endurance",
                    "Learn strategy",
                    "Develop leadership"
                ],
                "materials": ["Sports equipment", "Fitness trackers", "Video analysis tools", "Cones"],
                "activities": [
                    "Skill drills",
                    "Scrimmage games",
                    "Fitness testing",
                    "Strategy sessions",
                    "Performance analysis"
                ],
                "assessment_criteria": "Skill improvement, game performance, and fitness metrics",
                "status": "published",
                "version": 1
            }
        elif week < 18:  # Weeks 10-18: Fitness Program
            lesson = {
                "title": f"Grade 6-8 Fitness Program - Week {week + 1}",
                "content": f"Week {week + 1} of comprehensive fitness training for adolescent development",
                "grade_level": "6-8",
                "week_of": week_date,
                "content_area": "Fitness Training",
                "objectives": [
                    "Improve cardiovascular fitness",
                    "Build strength",
                    "Enhance flexibility",
                    "Track progress"
                ],
                "materials": ["Resistance bands", "Medicine balls", "Fitness equipment", "Stopwatch"],
                "activities": [
                    "Circuit training",
                    "Strength exercises",
                    "Flexibility work",
                    "Cardio intervals",
                    "Progress assessment"
                ],
                "assessment_criteria": "Fitness test results, strength gains, and endurance improvement",
                "status": "published",
                "version": 1
            }
        elif week < 27:  # Weeks 19-27: Team Sports Strategy
            lesson = {
                "title": f"Grade 6-8 Team Sports Strategy - Week {week + 1}",
                "content": f"Week {week + 1} of advanced team sports tactics and game strategy",
                "grade_level": "6-8",
                "week_of": week_date,
                "content_area": "Team Strategy",
                "objectives": [
                    "Learn game strategies",
                    "Develop teamwork",
                    "Improve decision making",
                    "Build leadership"
                ],
                "materials": ["Sports equipment", "Whiteboard", "Video equipment", "Stopwatch"],
                "activities": [
                    "Strategy sessions",
                    "Tactical drills",
                    "Game analysis",
                    "Scrimmages",
                    "Leadership exercises"
                ],
                "assessment_criteria": "Strategy understanding and application in games",
                "status": "published",
                "version": 1
            }
        else:  # Weeks 28-36: Individual Sports
            lesson = {
                "title": f"Grade 6-8 Individual Sports - Week {week + 1}",
                "content": f"Week {week + 1} of individual sports and personal fitness",
                "grade_level": "6-8",
                "week_of": week_date,
                "content_area": "Individual Sports",
                "objectives": [
                    "Learn individual sports",
                    "Build self-motivation",
                    "Develop personal goals",
                    "Track progress"
                ],
                "materials": ["Tennis rackets", "Badminton equipment", "Track equipment", "Stopwatch"],
                "activities": [
                    "Tennis basics",
                    "Badminton skills",
                    "Track events",
                    "Personal goal setting",
                    "Progress tracking"
                ],
                "assessment_criteria": "Individual sport skill development and goal achievement",
                "status": "published",
                "version": 1
            }
        
        middle_school_lessons.append(lesson)
    
    # ============================================================================
    # HIGH SCHOOL (9-12) - 36 WEEKS OF SPECIALIZED TRAINING AND LEADERSHIP
    # ============================================================================
    
    high_school_lessons = []
    for week in range(36):
        week_date = school_year_start + timedelta(weeks=week)
        
        if week < 9:  # Weeks 1-9: Sports Specialization
            lesson = {
                "title": f"Grade 9-12 Sports Specialization - Week {week + 1}",
                "content": f"Week {week + 1} of advanced training in specific sports and leadership development",
                "grade_level": "9-12",
                "week_of": week_date,
                "content_area": "Sports Specialization",
                "objectives": [
                    "Master advanced techniques",
                    "Develop leadership skills",
                    "Prepare for competition",
                    "Build teamwork"
                ],
                "materials": ["Advanced equipment", "Performance analysis tools", "Training facilities", "Video equipment"],
                "activities": [
                    "Advanced skill work",
                    "Tactical training",
                    "Leadership exercises",
                    "Competition prep",
                    "Performance analysis"
                ],
                "assessment_criteria": "Performance metrics, leadership demonstration, and competitive readiness",
                "status": "published",
                "version": 1
            }
        elif week < 18:  # Weeks 10-18: Fitness and Wellness
            lesson = {
                "title": f"Grade 9-12 Fitness and Wellness - Week {week + 1}",
                "content": f"Week {week + 1} of comprehensive fitness programming and health education",
                "grade_level": "9-12",
                "week_of": week_date,
                "content_area": "Health and Fitness",
                "objectives": [
                    "Achieve fitness goals",
                    "Learn health principles",
                    "Develop lifelong habits",
                    "Track progress"
                ],
                "materials": ["Fitness equipment", "Health resources", "Assessment tools", "Tracking apps"],
                "activities": [
                    "Personalized training",
                    "Health education",
                    "Goal setting",
                    "Progress tracking",
                    "Wellness assessment"
                ],
                "assessment_criteria": "Goal achievement, health knowledge, and habit formation",
                "status": "published",
                "version": 1
            }
        elif week < 27:  # Weeks 19-27: Strength Training
            lesson = {
                "title": f"Grade 9-12 Strength Training - Week {week + 1}",
                "content": f"Week {week + 1} of advanced strength training and conditioning",
                "grade_level": "9-12",
                "week_of": week_date,
                "content_area": "Strength Training",
                "objectives": [
                    "Build muscular strength",
                    "Improve power",
                    "Learn proper form",
                    "Track progress"
                ],
                "materials": ["Free weights", "Machines", "Resistance bands", "Safety equipment"],
                "activities": [
                    "Compound lifts",
                    "Isolation exercises",
                    "Power training",
                    "Form practice",
                    "Progress tracking"
                ],
                "assessment_criteria": "Strength gains, proper form, and safety awareness",
                "status": "published",
                "version": 1
            }
        else:  # Weeks 28-36: Sports Psychology and Leadership
            lesson = {
                "title": f"Grade 9-12 Sports Psychology - Week {week + 1}",
                "content": f"Week {week + 1} of mental preparation and performance psychology",
                "grade_level": "9-12",
                "week_of": week_date,
                "content_area": "Sports Psychology",
                "objectives": [
                    "Develop mental toughness",
                    "Learn focus techniques",
                    "Build confidence",
                    "Lead others"
                ],
                "materials": ["Meditation apps", "Visualization tools", "Journal materials", "Assessment tools"],
                "activities": [
                    "Meditation practice",
                    "Visualization exercises",
                    "Goal setting",
                    "Performance analysis",
                    "Leadership development"
                ],
                "assessment_criteria": "Mental skill development and performance improvement",
                "status": "published",
                "version": 1
            }
        
        high_school_lessons.append(lesson)
    
    # ============================================================================
    # SPECIALIZED PROGRAMS - ADDITIONAL LESSONS FOR SPECIAL NEEDS
    # ============================================================================
    
    specialized_lessons = []
    
    # Adaptive Physical Education - 18 weeks
    for week in range(18):
        week_date = school_year_start + timedelta(weeks=week)
        lesson = {
            "title": f"Adaptive Physical Education - Week {week + 1}",
            "content": f"Week {week + 1} of modified activities for students with special needs",
            "grade_level": "K-12",
            "week_of": week_date,
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
                "Individual support",
                "Progress assessment"
            ],
            "assessment_criteria": "Participation, skill development, and confidence building",
            "status": "published",
            "version": 1
        }
        specialized_lessons.append(lesson)
    
    # Outdoor Education - 12 weeks (spring and fall)
    for week in range(12):
        week_date = school_year_start + timedelta(weeks=week + 8)  # Start in November
        lesson = {
            "title": f"Outdoor Education - Week {week + 1}",
            "content": f"Week {week + 1} of nature-based physical activities and environmental education",
            "grade_level": "3-12",
            "week_of": week_date,
            "content_area": "Outdoor Education",
            "objectives": [
                "Connect with nature",
                "Learn outdoor skills",
                "Build environmental awareness",
                "Develop fitness"
            ],
            "materials": ["Outdoor equipment", "Safety gear", "Nature guides", "Maps", "Compasses"],
            "activities": [
                "Hiking",
                "Orienteering",
                "Nature games",
                "Environmental activities",
                "Outdoor fitness"
            ],
            "assessment_criteria": "Outdoor skill development and environmental awareness",
            "status": "published",
            "version": 1
        }
        specialized_lessons.append(lesson)
    
    # Dance and Movement Arts - 18 weeks
    for week in range(18):
        week_date = school_year_start + timedelta(weeks=week + 20)  # Start in February
        lesson = {
            "title": f"Dance and Movement Arts - Week {week + 1}",
            "content": f"Week {week + 1} of creative dance and movement expression",
            "grade_level": "K-12",
            "week_of": week_date,
            "content_area": "Dance and Movement",
            "objectives": [
                "Express creativity through movement",
                "Learn dance techniques",
                "Build confidence",
                "Develop coordination"
            ],
            "materials": ["Music equipment", "Dance space", "Costumes", "Mirrors", "Props"],
            "activities": [
                "Creative movement",
                "Dance routines",
                "Choreography",
                "Performance",
                "Movement exploration"
            ],
            "assessment_criteria": "Creativity, technique, and performance quality",
            "status": "published",
            "version": 1
        }
        specialized_lessons.append(lesson)
    
    # Martial Arts and Self-Defense - 12 weeks
    for week in range(12):
        week_date = school_year_start + timedelta(weeks=week + 38)  # Start in May
        lesson = {
            "title": f"Martial Arts and Self-Defense - Week {week + 1}",
            "content": f"Week {week + 1} of martial arts training and self-defense skills",
            "grade_level": "6-12",
            "week_of": week_date,
            "content_area": "Martial Arts",
            "objectives": [
                "Learn self-defense",
                "Build discipline",
                "Develop respect",
                "Improve fitness"
            ],
            "materials": ["Martial arts equipment", "Safety gear", "Training mats", "Instructional materials"],
            "activities": [
                "Basic techniques",
                "Forms practice",
                "Self-defense",
                "Discipline training",
                "Fitness development"
            ],
            "assessment_criteria": "Technique mastery, discipline, and respect demonstration",
            "status": "published",
            "version": 1
        }
        specialized_lessons.append(lesson)
    
    # Aquatic Sports and Water Safety - 12 weeks (summer session)
    for week in range(12):
        week_date = school_year_start + timedelta(weeks=week + 50)  # Start in August
        lesson = {
            "title": f"Aquatic Sports and Water Safety - Week {week + 1}",
            "content": f"Week {week + 1} of swimming skills and water safety education",
            "grade_level": "K-12",
            "week_of": week_date,
            "content_area": "Aquatic Sports",
            "objectives": [
                "Learn swimming skills",
                "Understand water safety",
                "Build confidence",
                "Develop fitness"
            ],
            "materials": ["Pool equipment", "Safety equipment", "Swimming aids", "Instructional materials"],
            "activities": [
                "Swimming lessons",
                "Water safety",
                "Aquatic games",
                "Stroke development",
                "Fitness activities"
            ],
            "assessment_criteria": "Swimming skill development and safety awareness",
            "status": "published",
            "version": 1
        }
        specialized_lessons.append(lesson)
    
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
    print(f"Successfully seeded {len(lessons_data)} comprehensive year-long curriculum lessons!")
    print(f"Breakdown:")
    print(f"  - Kindergarten: {len(kindergarten_lessons)} lessons")
    print(f"  - Grades 1-2: {len(grade_1_2_lessons)} lessons")
    print(f"  - Grades 3-5: {len(grade_3_5_lessons)} lessons")
    print(f"  - Middle School: {len(middle_school_lessons)} lessons")
    print(f"  - High School: {len(high_school_lessons)} lessons")
    print(f"  - Specialized Programs: {len(specialized_lessons)} lessons")

if __name__ == "__main__":
    session = next(get_db())
    seed_year_long_curriculum(session) 