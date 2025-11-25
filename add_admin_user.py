#!/usr/bin/env python3
"""
Script to add another admin user to the database.
This script allows you to create an admin user with custom details.

Usage:
    python add_admin_user.py <email> <password> [first_name] [last_name]
    
Or set environment variables:
    ADMIN_EMAIL=admin@example.com
    ADMIN_PASSWORD=secure-password
    ADMIN_FIRST_NAME=John
    ADMIN_LAST_NAME=Doe
    python add_admin_user.py
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file if it exists
env_file = project_root / '.env'
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment variables from .env file")

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.core.user import User
from app.models.teacher_registration import TeacherRegistration
from sqlalchemy.exc import IntegrityError
import uuid

def add_admin_user(email: str, password: str, first_name: str = "Admin", last_name: str = "User"):
    """Add an admin user account to the database."""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
                print(f"⚠️  User with email {email} already exists!")
                response = input(f"   Do you want to update this user to admin? (y/n): ").strip().lower()
                if response == 'y':
                    existing_user.role = "admin"
                    existing_user.is_superuser = True
                    existing_user.is_active = True
                    existing_user.first_name = first_name
                    existing_user.last_name = last_name
                    # Update password if provided
                    if password:
                        existing_user.password_hash = get_password_hash(password)
                    db.commit()
                    
                    # Also update/create in teacher_registrations table
                    teacher_reg = db.query(TeacherRegistration).filter(
                        TeacherRegistration.email == email
                    ).first()
                    
                    if teacher_reg:
                        teacher_reg.password_hash = existing_user.password_hash
                        teacher_reg.first_name = first_name
                        teacher_reg.last_name = last_name
                        teacher_reg.is_verified = True
                        teacher_reg.is_active = True
                    else:
                        teacher_reg = TeacherRegistration(
                            id=uuid.uuid4(),
                            email=email,
                            password_hash=existing_user.password_hash,
                            first_name=first_name,
                            last_name=last_name,
                            is_verified=True,
                            is_active=True
                        )
                        db.add(teacher_reg)
                    db.commit()
                    
                    print(f"✅ Updated user {email} to admin with full access!")
                    print(f"   Name: {first_name} {last_name}")
                    print(f"   Role: admin")
                    print(f"   Superuser: True")
                    print(f"   Active: True")
                    return existing_user
                else:
                    print("❌ Operation cancelled.")
                    return None
        else:
            # Create new admin user in both users and teacher_registrations tables
            hashed_password = get_password_hash(password)
            
            # Create in users table
            admin_user = User(
                email=email,
                password_hash=hashed_password,
                first_name=first_name,
                last_name=last_name,
                role="admin",
                is_superuser=True,
                is_active=True,
                disabled=False
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Also create in teacher_registrations table (required for login)
            teacher_reg = db.query(TeacherRegistration).filter(
                TeacherRegistration.email == email
            ).first()
            
            if not teacher_reg:
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
            else:
                # Update existing teacher_registration
                teacher_reg.password_hash = hashed_password
                teacher_reg.first_name = first_name
                teacher_reg.last_name = last_name
                teacher_reg.is_verified = True
                teacher_reg.is_active = True
                db.commit()
                print(f"✅ Updated teacher_registration for {email}")
            
            print(f"✅ Created admin user successfully!")
            print(f"   Email: {email}")
            print(f"   Name: {first_name} {last_name}")
            print(f"   Role: admin")
            print(f"   Superuser: True")
            print(f"   Active: True")
            print(f"   User ID: {admin_user.id}")
            print(f"   Teacher Registration ID: {teacher_reg.id}")
            return admin_user
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Error creating user: {e}")
        return None
    except Exception as e:
        db.rollback()
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

def list_existing_admins():
    """List all existing admin users."""
    db = SessionLocal()
    try:
        admins = db.query(User).filter(
            (User.role == "admin") | (User.is_superuser == True)
        ).all()
        
        if admins:
            print("\n📋 Existing Admin Users:")
            print("-" * 80)
            for admin in admins:
                print(f"  ID: {admin.id}")
                print(f"  Email: {admin.email}")
                print(f"  Name: {admin.first_name or 'N/A'} {admin.last_name or 'N/A'}")
                print(f"  Role: {admin.role}")
                print(f"  Superuser: {admin.is_superuser}")
                print(f"  Active: {admin.is_active}")
                print(f"  Created: {admin.created_at}")
                print("-" * 80)
        else:
            print("\n📋 No admin users found.")
    except Exception as e:
        print(f"❌ Error listing admins: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Show existing admins first
    list_existing_admins()
    
    # Get email and password from command line or environment variables
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
        first_name = sys.argv[3] if len(sys.argv) >= 4 else "Admin"
        last_name = sys.argv[4] if len(sys.argv) >= 5 else "User"
    else:
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        first_name = os.getenv("ADMIN_FIRST_NAME", "Admin")
        last_name = os.getenv("ADMIN_LAST_NAME", "User")
        
        if not email or not password:
            print("\n❌ Missing required parameters!")
            print("\nUsage: python add_admin_user.py <email> <password> [first_name] [last_name]")
            print("   Or set environment variables:")
            print("     ADMIN_EMAIL=admin@example.com")
            print("     ADMIN_PASSWORD=secure-password")
            print("     ADMIN_FIRST_NAME=John (optional)")
            print("     ADMIN_LAST_NAME=Doe (optional)")
            sys.exit(1)
    
    print(f"\n🔧 Creating admin account...")
    print(f"   Email: {email}")
    print(f"   Name: {first_name} {last_name}")
    
    user = add_admin_user(email, password, first_name, last_name)
    
    if user:
        print("\n✅ Success! The new admin can now log in with:")
        print(f"   Email: {email}")
        print(f"   Password: (the password you provided)")
        print("\n💡 Note: This account has full admin access.")
    else:
        print("\n❌ Failed to create admin account.")
        sys.exit(1)

