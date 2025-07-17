from sqlalchemy.orm import Session
from app.models.physical_education.class_ import PhysicalEducationClass
from app.core.database import Base, engine

def seed_classes():
    db = Session(engine)
    try:
        # Create sample physical education classes
        classes = [
            PhysicalEducationClass(
                name="9th Grade PE",
                description="Physical Education for 9th grade students",
                grade_level="9th",
                max_students=30
            ),
            PhysicalEducationClass(
                name="10th Grade PE",
                description="Physical Education for 10th grade students",
                grade_level="10th",
                max_students=30
            ),
            PhysicalEducationClass(
                name="11th Grade PE",
                description="Physical Education for 11th grade students",
                grade_level="11th",
                max_students=30
            ),
            PhysicalEducationClass(
                name="12th Grade PE",
                description="Physical Education for 12th grade students",
                grade_level="12th",
                max_students=30
            )
        ]

        # Add classes to database
        for class_ in classes:
            db.add(class_)
        
        db.commit()
        print("Successfully seeded physical education classes")
    except Exception as e:
        db.rollback()
        print(f"Error seeding classes: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_classes() 