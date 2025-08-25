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

def seed_comprehensive_lessons(session: Session) -> None:
    """Seed the database with comprehensive lesson data covering all grade levels."""
    print("Seeding comprehensive lessons...")
    
    # Get existing users and subject categories
    users = session.execute(text("SELECT id FROM users WHERE role = 'teacher'"))
    user_ids = [user[0] for user in users.fetchall()]
    
    subject_categories = session.execute(text("SELECT id FROM subject_categories"))
    subject_category_ids = [category[0] for category in subject_categories.fetchall()]
    
    if not user_ids or not subject_category_ids:
        print("Warning: No teachers or subject categories found. Skipping lesson seeding.")
        return
    
    # Start date for lessons
    start_date = datetime(2024, 1, 8)
    
    # Comprehensive lesson data aligned with our 6-school district structure
    lessons_data = []
    
    # Kindergarten Lessons (K) - Fundamental Movement Skills
    kindergarten_lessons = [
        {
            "title": "Kindergarten Movement Basics",
            "content": "Introduction to fundamental movement patterns for young learners",
            "grade_level": "K",
            "week_of": start_date,
            "content_area": "Fundamental Movement",
            "objectives": ["Develop basic locomotor skills", "Learn spatial awareness", "Practice following directions"],
            "materials": ["Cones", "Bean bags", "Music player", "Hula hoops"],
            "activities": ["Walking, running, jumping games", "Animal movement imitation", "Follow the leader", "Hula hoop exploration"],
            "assessment_criteria": "Observation of participation and basic skill demonstration",
            "status": "published",
            "version": 1
        },
        {
            "title": "Kindergarten Balance and Coordination",
            "content": "Developing balance and coordination through fun activities",
            "grade_level": "K",
            "week_of": start_date + timedelta(weeks=1),
            "content_area": "Balance and Coordination",
            "objectives": ["Improve balance skills", "Enhance coordination", "Build confidence"],
            "materials": ["Balance beams", "Yoga mats", "Bean bags", "Music"],
            "activities": ["Balance beam walking", "Bean bag balance", "Animal poses", "Freeze dance"],
            "assessment_criteria": "Ability to maintain balance and follow movement patterns",
            "status": "published",
            "version": 1
        },
        {
            "title": "Kindergarten Team Building Games",
            "content": "Introduction to cooperative play and team activities",
            "grade_level": "K",
            "week_of": start_date + timedelta(weeks=2),
            "content_area": "Team Building",
            "objectives": ["Learn cooperation skills", "Practice sharing", "Build social skills"],
            "materials": ["Large parachute", "Soft balls", "Cones", "Bean bags"],
            "activities": ["Parachute games", "Partner toss", "Group circle games", "Simple relay races"],
            "assessment_criteria": "Participation in group activities and cooperation",
            "status": "published",
            "version": 1
        }
    ]
    
    # Grade 1-2 Lessons - Building on Fundamentals
    grade_1_2_lessons = [
        {
            "title": "Grade 1-2 Team Building",
            "content": "Cooperative games and basic team sports introduction",
            "grade_level": "1-2",
            "week_of": start_date + timedelta(weeks=3),
            "content_area": "Team Sports",
            "objectives": ["Learn cooperation skills", "Practice basic throwing/catching", "Understand fair play"],
            "materials": ["Soft balls", "Hula hoops", "Cones", "Stopwatch"],
            "activities": ["Partner toss games", "Hula hoop challenges", "Simple relay races", "Team tag games"],
            "assessment_criteria": "Participation, cooperation, and basic skill demonstration",
            "status": "published",
            "version": 1
        },
        {
            "title": "Grade 1-2 Fitness Fundamentals",
            "content": "Introduction to basic fitness concepts and exercises",
            "grade_level": "1-2",
            "week_of": start_date + timedelta(weeks=4),
            "content_area": "Fitness Training",
            "objectives": ["Learn basic exercises", "Understand fitness concepts", "Build endurance"],
            "materials": ["Jump ropes", "Cones", "Music", "Stopwatch"],
            "activities": ["Jump rope basics", "Fitness stations", "Movement circuits", "Endurance games"],
            "assessment_criteria": "Participation in fitness activities and skill improvement",
            "status": "published",
            "version": 1
        },
        {
            "title": "Grade 1-2 Creative Movement",
            "content": "Expressive movement and dance-based activities",
            "grade_level": "1-2",
            "week_of": start_date + timedelta(weeks=5),
            "content_area": "Creative Movement",
            "objectives": ["Express creativity through movement", "Learn rhythm", "Build confidence"],
            "materials": ["Music player", "Scarves", "Ribbons", "Drums"],
            "activities": ["Scarf dancing", "Rhythm games", "Creative movement", "Dance routines"],
            "assessment_criteria": "Creativity in movement and rhythm awareness",
            "status": "published",
            "version": 1
        }
    ]
    
    # Grade 3-5 Lessons - Sports Skills and Fitness
    grade_3_5_lessons = [
        {
            "title": "Grade 3-5 Sports Fundamentals",
            "content": "Introduction to organized sports and fitness activities",
            "grade_level": "3-5",
            "week_of": start_date + timedelta(weeks=6),
            "content_area": "Sports Skills",
            "objectives": ["Master basic sports skills", "Learn game rules", "Develop fitness habits"],
            "materials": ["Basketballs", "Soccer balls", "Jump ropes", "Stopwatch", "Cones"],
            "activities": ["Basketball dribbling", "Soccer passing", "Jump rope challenges", "Fitness stations"],
            "assessment_criteria": "Skill demonstration, game participation, and fitness improvement",
            "status": "published",
            "version": 1
        },
        {
            "title": "Grade 3-5 Basketball Basics",
            "content": "Comprehensive basketball skill development",
            "grade_level": "3-5",
            "week_of": start_date + timedelta(weeks=7),
            "content_area": "Basketball",
            "objectives": ["Learn dribbling techniques", "Practice shooting", "Understand basic rules"],
            "materials": ["Basketballs", "Basketball hoops", "Cones", "Stopwatch"],
            "activities": ["Dribbling drills", "Shooting practice", "Passing games", "Mini-games"],
            "assessment_criteria": "Basketball skill demonstration and game participation",
            "status": "published",
            "version": 1
        },
        {
            "title": "Grade 3-5 Soccer Skills",
            "content": "Comprehensive soccer skill development",
            "grade_level": "3-5",
            "week_of": start_date + timedelta(weeks=8),
            "content_area": "Soccer",
            "objectives": ["Master ball control", "Learn passing techniques", "Understand positions"],
            "materials": ["Soccer balls", "Cones", "Goals", "Stopwatch"],
            "activities": ["Dribbling drills", "Passing practice", "Shooting practice", "Small-sided games"],
            "assessment_criteria": "Soccer skill demonstration and game understanding",
            "status": "published",
            "version": 1
        },
        {
            "title": "Grade 3-5 Fitness Challenge",
            "content": "Comprehensive fitness training and assessment",
            "grade_level": "3-5",
            "week_of": start_date + timedelta(weeks=9),
            "content_area": "Fitness Training",
            "objectives": ["Improve overall fitness", "Build strength", "Enhance endurance"],
            "materials": ["Fitness equipment", "Stopwatch", "Cones", "Resistance bands"],
            "activities": ["Circuit training", "Strength exercises", "Cardio intervals", "Fitness testing"],
            "assessment_criteria": "Fitness improvement and participation in all activities",
            "status": "published",
            "version": 1
        }
    ]
    
    # Middle School Lessons (6-8) - Advanced Skills and Fitness
    middle_school_lessons = [
        {
            "title": "Grade 6-8 Advanced Sports Skills",
            "content": "Intermediate level sports training and fitness development",
            "grade_level": "6-8",
            "week_of": start_date + timedelta(weeks=10),
            "content_area": "Advanced Sports",
            "objectives": ["Refine sports techniques", "Build endurance", "Learn strategy"],
            "materials": ["Sports equipment", "Fitness trackers", "Video analysis tools", "Cones"],
            "activities": ["Skill drills", "Scrimmage games", "Fitness testing", "Strategy sessions"],
            "assessment_criteria": "Skill improvement, game performance, and fitness metrics",
            "status": "published",
            "version": 1
        },
        {
            "title": "Middle School Fitness Program",
            "content": "Comprehensive fitness training for adolescent development",
            "grade_level": "6-8",
            "week_of": start_date + timedelta(weeks=11),
            "content_area": "Fitness Training",
            "objectives": ["Improve cardiovascular fitness", "Build strength", "Enhance flexibility"],
            "materials": ["Resistance bands", "Medicine balls", "Fitness equipment", "Stopwatch"],
            "activities": ["Circuit training", "Strength exercises", "Flexibility work", "Cardio intervals"],
            "assessment_criteria": "Fitness test results, strength gains, and endurance improvement",
            "status": "published",
            "version": 1
        },
        {
            "title": "Grade 6-8 Team Sports Strategy",
            "content": "Advanced team sports tactics and game strategy",
            "grade_level": "6-8",
            "week_of": start_date + timedelta(weeks=12),
            "content_area": "Team Strategy",
            "objectives": ["Learn game strategies", "Develop teamwork", "Improve decision making"],
            "materials": ["Sports equipment", "Whiteboard", "Video equipment", "Stopwatch"],
            "activities": ["Strategy sessions", "Tactical drills", "Game analysis", "Scrimmages"],
            "assessment_criteria": "Strategy understanding and application in games",
            "status": "published",
            "version": 1
        },
        {
            "title": "Grade 6-8 Individual Sports",
            "content": "Introduction to individual sports and personal fitness",
            "grade_level": "6-8",
            "week_of": start_date + timedelta(weeks=13),
            "content_area": "Individual Sports",
            "objectives": ["Learn individual sports", "Build self-motivation", "Develop personal goals"],
            "materials": ["Tennis rackets", "Badminton equipment", "Track equipment", "Stopwatch"],
            "activities": ["Tennis basics", "Badminton skills", "Track events", "Personal goal setting"],
            "assessment_criteria": "Individual sport skill development and goal achievement",
            "status": "published",
            "version": 1
        }
    ]
    
    # High School Lessons (9-12) - Specialized Training and Leadership
    high_school_lessons = [
        {
            "title": "High School Sports Specialization",
            "content": "Advanced training in specific sports and leadership development",
            "grade_level": "9-12",
            "week_of": start_date + timedelta(weeks=14),
            "content_area": "Sports Specialization",
            "objectives": ["Master advanced techniques", "Develop leadership skills", "Prepare for competition"],
            "materials": ["Advanced equipment", "Performance analysis tools", "Training facilities", "Video equipment"],
            "activities": ["Advanced skill work", "Tactical training", "Leadership exercises", "Competition prep"],
            "assessment_criteria": "Performance metrics, leadership demonstration, and competitive readiness",
            "status": "published",
            "version": 1
        },
        {
            "title": "High School Fitness and Wellness",
            "content": "Comprehensive fitness programming and health education",
            "grade_level": "9-12",
            "week_of": start_date + timedelta(weeks=15),
            "content_area": "Health and Fitness",
            "objectives": ["Achieve fitness goals", "Learn health principles", "Develop lifelong habits"],
            "materials": ["Fitness equipment", "Health resources", "Assessment tools", "Tracking apps"],
            "activities": ["Personalized training", "Health education", "Goal setting", "Progress tracking"],
            "assessment_criteria": "Goal achievement, health knowledge, and habit formation",
            "status": "published",
            "version": 1
        },
        {
            "title": "High School Strength Training",
            "content": "Advanced strength training and conditioning",
            "grade_level": "9-12",
            "week_of": start_date + timedelta(weeks=16),
            "content_area": "Strength Training",
            "objectives": ["Build muscular strength", "Improve power", "Learn proper form"],
            "materials": ["Free weights", "Machines", "Resistance bands", "Safety equipment"],
            "activities": ["Compound lifts", "Isolation exercises", "Power training", "Form practice"],
            "assessment_criteria": "Strength gains, proper form, and safety awareness",
            "status": "published",
            "version": 1
        },
        {
            "title": "High School Sports Psychology",
            "content": "Mental preparation and performance psychology",
            "grade_level": "9-12",
            "week_of": start_date + timedelta(weeks=17),
            "content_area": "Sports Psychology",
            "objectives": ["Develop mental toughness", "Learn focus techniques", "Build confidence"],
            "materials": ["Meditation apps", "Visualization tools", "Journal materials", "Assessment tools"],
            "activities": ["Meditation practice", "Visualization exercises", "Goal setting", "Performance analysis"],
            "assessment_criteria": "Mental skill development and performance improvement",
            "status": "published",
            "version": 1
        },
        {
            "title": "High School Nutrition and Recovery",
            "content": "Sports nutrition and recovery strategies",
            "grade_level": "9-12",
            "week_of": start_date + timedelta(weeks=18),
            "content_area": "Nutrition and Recovery",
            "objectives": ["Understand nutrition basics", "Learn recovery strategies", "Optimize performance"],
            "materials": ["Nutrition guides", "Recovery equipment", "Assessment tools", "Educational materials"],
            "activities": ["Nutrition education", "Recovery practice", "Meal planning", "Performance tracking"],
            "assessment_criteria": "Nutrition knowledge and recovery implementation",
            "status": "published",
            "version": 1
        }
    ]
    
    # Specialized Program Lessons
    specialized_lessons = [
        {
            "title": "Adaptive Physical Education",
            "content": "Modified activities for students with special needs",
            "grade_level": "K-12",
            "week_of": start_date + timedelta(weeks=19),
            "content_area": "Adaptive PE",
            "objectives": ["Provide inclusive activities", "Adapt to individual needs", "Build confidence"],
            "materials": ["Adaptive equipment", "Visual aids", "Modified games", "Support materials"],
            "activities": ["Modified sports", "Adaptive exercises", "Inclusive games", "Individual support"],
            "assessment_criteria": "Participation, skill development, and confidence building",
            "status": "published",
            "version": 1
        },
        {
            "title": "Outdoor Education",
            "content": "Nature-based physical activities and environmental education",
            "grade_level": "3-12",
            "week_of": start_date + timedelta(weeks=20),
            "content_area": "Outdoor Education",
            "objectives": ["Connect with nature", "Learn outdoor skills", "Build environmental awareness"],
            "materials": ["Outdoor equipment", "Safety gear", "Nature guides", "Maps"],
            "activities": ["Hiking", "Orienteering", "Nature games", "Environmental activities"],
            "assessment_criteria": "Outdoor skill development and environmental awareness",
            "status": "published",
            "version": 1
        },
        {
            "title": "Dance and Movement Arts",
            "content": "Creative dance and movement expression",
            "grade_level": "K-12",
            "week_of": start_date + timedelta(weeks=21),
            "content_area": "Dance and Movement",
            "objectives": ["Express creativity", "Learn dance techniques", "Build confidence"],
            "materials": ["Music equipment", "Dance space", "Costumes", "Mirrors"],
            "activities": ["Creative movement", "Dance routines", "Choreography", "Performance"],
            "assessment_criteria": "Creativity, technique, and performance quality",
            "status": "published",
            "version": 1
        },
        {
            "title": "Martial Arts and Self-Defense",
            "content": "Martial arts training and self-defense skills",
            "grade_level": "6-12",
            "week_of": start_date + timedelta(weeks=22),
            "content_area": "Martial Arts",
            "objectives": ["Learn self-defense", "Build discipline", "Develop respect"],
            "materials": ["Martial arts equipment", "Safety gear", "Training mats", "Instructional materials"],
            "activities": ["Basic techniques", "Forms practice", "Self-defense", "Discipline training"],
            "assessment_criteria": "Technique mastery, discipline, and respect demonstration",
            "status": "published",
            "version": 1
        },
        {
            "title": "Aquatic Sports and Water Safety",
            "content": "Swimming skills and water safety education",
            "grade_level": "K-12",
            "week_of": start_date + timedelta(weeks=23),
            "content_area": "Aquatic Sports",
            "objectives": ["Learn swimming skills", "Understand water safety", "Build confidence"],
            "materials": ["Pool equipment", "Safety equipment", "Swimming aids", "Instructional materials"],
            "activities": ["Swimming lessons", "Water safety", "Aquatic games", "Stroke development"],
            "assessment_criteria": "Swimming skill development and safety awareness",
            "status": "published",
            "version": 1
        }
    ]
    
    # Combine all lessons
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
    print(f"Successfully seeded {len(lessons_data)} comprehensive lessons!")

if __name__ == "__main__":
    session = next(get_db())
    seed_comprehensive_lessons(session) 