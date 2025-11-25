#!/usr/bin/env python3
"""
Sync TeacherRegistration records with User records.

This ensures that all seed users have corresponding TeacherRegistration records,
allowing admins to query any teacher by number.
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.models.core.user import User
from app.models.teacher_registration import TeacherRegistration
from app.core.security import get_password_hash
from sqlalchemy import func
import uuid
from datetime import datetime

def sync_teacher_registrations():
    """Create TeacherRegistration records for all Users that don't have them."""
    db = SessionLocal()
    
    try:
        print("="*80)
        print("SYNCING TEACHER REGISTRATIONS WITH USER RECORDS")
        print("="*80)
        
        # Get all users (excluding admins, we'll handle them separately)
        all_users = db.query(User).filter(
            User.email.notilike("%faraday-ai.com"),
            User.email.notilike("%eifis.com")
        ).order_by(User.id).all()
        
        print(f"\nFound {len(all_users)} users to sync...")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for user in all_users:
            # Check if TeacherRegistration exists
            teacher_reg = db.query(TeacherRegistration).filter(
                func.lower(TeacherRegistration.email) == func.lower(user.email)
            ).first()
            
            if teacher_reg:
                # Update existing TeacherRegistration to match User
                teacher_reg.first_name = user.first_name or teacher_reg.first_name
                teacher_reg.last_name = user.last_name or teacher_reg.last_name
                teacher_reg.is_active = user.is_active
                teacher_reg.is_verified = True
                teacher_reg.updated_at = datetime.utcnow()
                updated_count += 1
                print(f"✅ Updated: {user.email} (User.id={user.id} -> TeacherRegistration.id={teacher_reg.id})")
            else:
                # Create new TeacherRegistration
                teacher_reg = TeacherRegistration(
                    id=uuid.uuid4(),
                    email=user.email,
                    password_hash=user.password_hash or get_password_hash("default_password"),
                    first_name=user.first_name or "Teacher",
                    last_name=user.last_name or "User",
                    is_verified=True,
                    is_active=user.is_active,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(teacher_reg)
                created_count += 1
                print(f"✅ Created: {user.email} (User.id={user.id} -> TeacherRegistration.id={teacher_reg.id})")
        
        db.commit()
        
        print("\n" + "="*80)
        print("SYNC SUMMARY")
        print("="*80)
        print(f"✅ Created: {created_count} TeacherRegistration records")
        print(f"✅ Updated: {updated_count} TeacherRegistration records")
        print(f"⏭️  Skipped: {skipped_count} (already in sync)")
        print(f"📊 Total users processed: {len(all_users)}")
        
        # Verify sync
        print("\n" + "="*80)
        print("VERIFICATION")
        print("="*80)
        
        # Count users with TeacherRegistration
        users_with_tr = db.query(User).join(
            TeacherRegistration,
            func.lower(User.email) == func.lower(TeacherRegistration.email)
        ).count()
        
        total_users = db.query(User).filter(
            User.email.notilike("%faraday-ai.com"),
            User.email.notilike("%eifis.com")
        ).count()
        
        print(f"Users with TeacherRegistration: {users_with_tr}/{total_users}")
        
        if users_with_tr == total_users:
            print("✅ All users have TeacherRegistration records!")
        else:
            print(f"⚠️  {total_users - users_with_tr} users still missing TeacherRegistration records")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    sync_teacher_registrations()

