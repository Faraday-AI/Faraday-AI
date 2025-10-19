#!/usr/bin/env python3
"""
Migrate teachers to dashboard_users table
This ensures proper data flow: users -> teachers -> dashboard_users
"""

import os
import sys
sys.path.insert(0, '/app')

from sqlalchemy import create_engine, text
from datetime import datetime

def migrate_teachers_to_dashboard_users(session=None):
    """Migrate teachers data to dashboard_users table"""
    
    if session:
        # Use the provided session for transaction consistency
        conn = session.connection()
    else:
        # Connect to database directly
        DATABASE_URL = 'postgresql://faraday_admin:CodaMoeLuna31@faraday-ai-db.postgres.database.azure.com:5432/postgres?sslmode=require'
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
    
    try:
        print("🚀 MIGRATING TEACHERS TO DASHBOARD_USERS")
        print("=" * 60)
        
        # Check if dashboard_users table exists and has users
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM dashboard_users"))
            current_count = result.scalar()
            print(f"📊 Current dashboard_users count: {current_count}")
            
            # If dashboard_users already has users, skip teacher migration
            # as users are already migrated via the main user migration
            if current_count > 0:
                print("✅ Dashboard_users already populated via user migration, skipping teacher migration")
                return True
        except Exception as e:
            print(f"❌ Error checking dashboard_users table: {e}")
            return False
        
        # Check teachers table
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM teachers"))
            teacher_count = result.scalar()
            print(f"📊 Teachers to migrate: {teacher_count}")
        except Exception as e:
            print(f"❌ Error checking teachers table: {e}")
            return False
        
        if teacher_count == 0:
            print("⚠️  No teachers found to migrate")
            return True
        
        # Get dashboard_users table schema
        try:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'dashboard_users' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            print(f"📋 Dashboard_users columns: {[col[0] for col in columns]}")
        except Exception as e:
            print(f"❌ Error getting dashboard_users schema: {e}")
            return False
        
        # Get teachers data
        try:
            result = conn.execute(text("""
                SELECT id, first_name, last_name, email, created_at, updated_at
                FROM teachers
                ORDER BY id
            """))
            teachers = result.fetchall()
            print(f"📋 Found {len(teachers)} teachers to migrate")
        except Exception as e:
            print(f"❌ Error getting teachers data: {e}")
            return False
        
        # Migrate teachers to dashboard_users
        migrated_count = 0
        for teacher in teachers:
            try:
                # Check if teacher already exists in dashboard_users by core_user_id
                check_result = conn.execute(text("""
                    SELECT COUNT(*) FROM dashboard_users WHERE core_user_id = :core_user_id
                """), {'core_user_id': teacher[0]})
                
                if check_result.scalar() > 0:
                    print(f"⚠️  Teacher {teacher[0]} already exists in dashboard_users, skipping")
                    continue
                
                # Insert teacher into dashboard_users using core_user_id approach
                conn.execute(text("""
                    INSERT INTO dashboard_users (
                        core_user_id, full_name, email, hashed_password, role,
                        created_at, updated_at, is_active
                    ) VALUES (
                        :core_user_id, :full_name, :email, :hashed_password, :role,
                        :created_at, :updated_at, :is_active
                    )
                """), {
                    'core_user_id': teacher[0],  # Use teacher ID as core_user_id
                    'full_name': f"{teacher[1]} {teacher[2]}",  # Combine first and last name
                    'email': teacher[3],
                    'hashed_password': 'default_password_hash',  # Default password for development
                    'role': 'TEACHER',  # Default role for teachers
                    'created_at': teacher[4] or datetime.now(),
                    'updated_at': teacher[5] or datetime.now(),
                    'is_active': True
                })
                
                migrated_count += 1
                print(f"✅ Migrated teacher {teacher[0]}: {teacher[1]} {teacher[2]}")
                
            except Exception as e:
                print(f"❌ Error migrating teacher {teacher[0]}: {e}")
                continue
        
        # Commit changes only if we're using our own connection
        if not session:
            conn.commit()
        
        print(f"\n🎉 MIGRATION COMPLETE!")
        print(f"✅ Migrated {migrated_count} teachers to dashboard_users")
        
        # Verify migration
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM dashboard_users"))
            final_count = result.scalar()
            print(f"📊 Final dashboard_users count: {final_count}")
        except Exception as e:
            print(f"❌ Error verifying migration: {e}")
            if not session:
                conn.rollback()
            raise
        
        return True
        
    except Exception as e:
        print(f"❌ Error during teacher migration: {e}")
        if not session:
            conn.rollback()
        raise
    finally:
        if not session:
            conn.close()

if __name__ == "__main__":
    success = migrate_teachers_to_dashboard_users()
    if success:
        print("\n✅ Teacher to dashboard_users migration completed successfully!")
    else:
        print("\n❌ Teacher to dashboard_users migration failed!")
        sys.exit(1)
