#!/usr/bin/env python3
"""
Script to create teacher_registrations entries for admin users.
This is required for login to work since the login system uses teacher_registrations table.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.teacher_registration import TeacherRegistration
from sqlalchemy.exc import IntegrityError
import uuid

def create_teacher_registration(email: str, password: str, first_name: str, last_name: str):
    """Create or update teacher_registration entry."""
    db = SessionLocal()
    try:
        # Check if teacher_registration already exists
        teacher_reg = db.query(TeacherRegistration).filter(
            TeacherRegistration.email == email
        ).first()
        
        hashed_password = get_password_hash(password)
        
        if teacher_reg:
            # Update existing
            teacher_reg.password_hash = hashed_password
            teacher_reg.first_name = first_name
            teacher_reg.last_name = last_name
            teacher_reg.is_verified = True
            teacher_reg.is_active = True
            db.commit()
            print(f"✅ Updated teacher_registration for {email}")
            return teacher_reg
        else:
            # Create new
            teacher_reg = TeacherRegistration(
                id=uuid.uuid4(),
                email=email,
                password_hash=hashed_password,
                first_name=first_name,
                last_name=last_name,
                is_verified=True,
                is_active=True
            )
            db.add(teacher_reg)
            db.commit()
            db.refresh(teacher_reg)
            print(f"✅ Created teacher_registration for {email}")
            return teacher_reg
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Error creating teacher_registration: {e}")
        return None
    except Exception as e:
        db.rollback()
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    # Create both admin teacher_registrations
    admins = [
        {
            "email": "jmartucci@faraday-ai.com",
            "password": "Moebe@r31",
            "first_name": "Joe",
            "last_name": "Martucci"
        },
        {
            "email": "Mpolito@eifis.com",
            "password": "Faraday_@dmin_45",
            "first_name": "Michael",
            "last_name": "Polito"
        }
    ]
    
    print("🔧 Creating teacher_registrations for admin users...")
    print("=" * 80)
    
    for admin in admins:
        print(f"\nProcessing: {admin['email']}")
        result = create_teacher_registration(
            admin["email"],
            admin["password"],
            admin["first_name"],
            admin["last_name"]
        )
        if result:
            print(f"   ✅ Success! Can now login with email: {admin['email']}")
        else:
            print(f"   ❌ Failed to create teacher_registration")
    
    print("\n" + "=" * 80)
    print("✅ Done! Both admins should now be able to login.")
    print("\nLogin credentials:")
    print("  1. jmartucci@faraday-ai.com / Moebe@r31")
    print("  2. Mpolito@eifis.com / Faraday_@dmin_45")

