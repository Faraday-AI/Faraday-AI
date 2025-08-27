#!/usr/bin/env python3
"""
Migrate users from the users table to dashboard_users table.
This is needed because lesson_plans references educational_teachers which references dashboard_users.
"""

import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal


def migrate_users_to_dashboard(session: Session) -> None:
    """Migrate users from users table to dashboard_users table."""
    print("Migrating users to dashboard_users table...")
    
    try:
        # Check if dashboard_users already has data
        result = session.execute(text("SELECT COUNT(*) FROM dashboard_users")).scalar()
        if result > 0:
            print(f"dashboard_users table already has {result} records. Will add missing users...")
        
        # Get existing dashboard user IDs to avoid duplicates
        existing_core_user_ids = session.execute(text("SELECT core_user_id FROM dashboard_users WHERE core_user_id IS NOT NULL")).fetchall()
        existing_core_user_ids = [row[0] for row in existing_core_user_ids]
        print(f"Found {len(existing_core_user_ids)} existing core_user_ids: {existing_core_user_ids}")
        
        # Get all users from users table
        users = session.execute(text("""
            SELECT id, email, password_hash, first_name, last_name, is_active, 
                   is_superuser, created_at, updated_at
            FROM users 
            ORDER BY id
        """)).fetchall()
        
        if not users:
            print("No users found in users table.")
            return
        
        print(f"Found {len(users)} users to migrate...")
        
        # Migrate each user
        migrated_count = 0
        for i, user in enumerate(users, 1):
            # Skip if user already exists in dashboard_users
            if user.id in existing_core_user_ids:
                print(f"  ⏭️  Skipping existing user {i}/{len(users)}: {user.first_name} {user.last_name} (already in dashboard_users)")
                continue
                
            try:
                # Create dashboard_user record
                full_name = f"{user.first_name} {user.last_name}"
                
                # Set role based on user type (assuming all are teachers for now)
                role = "TEACHER"
                
                # Create preferences JSON based on user data
                preferences = {
                    "department": "Physical Education",
                    "subjects": ["Physical Education"],
                    "grade_levels": ["K", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
                    "specialization": "Physical Education Teacher"
                }
                
                insert_query = text("""
                    INSERT INTO dashboard_users (
                        core_user_id, email, hashed_password, full_name, role, is_active,
                        is_superuser, preferences, created_at, updated_at
                    ) VALUES (
                        :core_user_id, :email, :hashed_password, :full_name, :role, :is_active,
                        :is_superuser, :preferences, :created_at, :updated_at
                    ) RETURNING id
                """)
                
                result = session.execute(insert_query, {
                    "core_user_id": user.id,
                    "email": user.email,
                    "hashed_password": user.password_hash,
                    "full_name": full_name,
                    "role": role,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                    "preferences": json.dumps(preferences),
                    "created_at": user.created_at or datetime.now(timezone.utc),
                    "updated_at": user.updated_at or datetime.now(timezone.utc)
                })
                
                dashboard_user_id = result.scalar()
                migrated_count += 1
                print(f"  ✅ Migrated user {i}/{len(users)}: {full_name} (ID: {dashboard_user_id})")
                
            except Exception as e:
                print(f"  ❌ Error migrating user {user.first_name} {user.last_name}: {e}")
                session.rollback()
                return
        
        session.commit()
        print(f"✅ Successfully migrated {migrated_count} new users to dashboard_users!")
        
        # Verify the migration
        count = session.execute(text("SELECT COUNT(*) FROM dashboard_users")).scalar()
        print(f"📊 Total dashboard_users in database: {count} records")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        session.rollback()


def main():
    """Main function to run the migration."""
    session = SessionLocal()
    try:
        migrate_users_to_dashboard(session)
    finally:
        session.close()


if __name__ == "__main__":
    main() 