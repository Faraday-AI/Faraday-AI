#!/usr/bin/env python3
"""
Script to create an admin user account.
Run this script to create yourself an admin account with full access.

Usage:
    python create_admin_user.py <your-email> <your-password>
    
Or set environment variables:
    ADMIN_EMAIL=your-email@example.com
    ADMIN_PASSWORD=your-secure-password
    python create_admin_user.py
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.core.user import User
from sqlalchemy.exc import IntegrityError

def create_admin_user(email: str, password: str):
    """Create an admin user account."""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            print(f"   Updating existing user to admin...")
            existing_user.role = "admin"
            existing_user.is_superuser = True
            existing_user.is_active = True
            # Update password if provided
            if password:
                existing_user.password_hash = hash_password(password)
            db.commit()
            print(f"✅ Updated user {email} to admin with full access!")
            return existing_user
        else:
            # Create new admin user
            hashed_password = hash_password(password)
            admin_user = User(
                email=email,
                password_hash=hashed_password,
                first_name="Admin",
                last_name="User",
                role="admin",
                is_superuser=True,
                is_active=True,
                disabled=False
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ Created admin user: {email}")
            print(f"   Role: admin")
            print(f"   Superuser: True")
            print(f"   Active: True")
            return admin_user
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Error creating user: {e}")
        return None
    except Exception as e:
        db.rollback()
        print(f"❌ Unexpected error: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    # Get email and password from command line or environment variables
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
    else:
        email = os.getenv("ADMIN_EMAIL")
        password = os.getenv("ADMIN_PASSWORD")
        
        if not email or not password:
            print("Usage: python create_admin_user.py <email> <password>")
            print("   Or set ADMIN_EMAIL and ADMIN_PASSWORD environment variables")
            sys.exit(1)
    
    print(f"Creating admin account for: {email}")
    user = create_admin_user(email, password)
    
    if user:
        print("\n✅ Success! You can now log in with:")
        print(f"   Email: {email}")
        print(f"   Password: (the password you provided)")
        print("\nNote: This account has full admin access and will not be charged.")
    else:
        print("\n❌ Failed to create admin account.")
        sys.exit(1)

